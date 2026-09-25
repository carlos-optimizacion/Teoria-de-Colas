import io
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from simulation_core import simulate_queue, simulate_mms


class PortalTests(TestCase):
    def test_all_pages_render(self):
        names = [
            "portal:home", "portal:fundamentals", "portal:mm1", "portal:mms", "portal:mmsk",
            "portal:mm1c", "portal:mmstotal", "portal:erlangb", "portal:mg1", "portal:dd1",
            "portal:cases", "portal:simple", "portal:complex", "portal:comparator",
            "portal:economics", "portal:sizing", "portal:validator", "portal:endtoend",
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def post_json(self, name, payload):
        return self.client.post(reverse(name), data=json.dumps(payload), content_type="application/json")

    def test_model_api_supports_all_model_families(self):
        samples = {
            "mm1": {}, "mms": {"servers": 2}, "mmsk": {"servers": 2, "capacity": 7},
            "mm1c": {"waiting_places": 4}, "mmstotal": {"servers": 2, "capacity": 7},
            "erlangb": {"servers": 3}, "mg1": {"cv": 1.4}, "dd1": {"n": 10},
        }
        for model, extra in samples.items():
            payload = {"model": model, "t_llegada": 10, "t_atencion": 8, "horizon": 120, "replications": 3, **extra}
            response = self.post_json("portal:model_api", payload)
            with self.subTest(model=model):
                self.assertEqual(response.status_code, 200)
                body = response.json()
                self.assertTrue(body["ok"])
                self.assertIn("analytic", body)
                self.assertIn("interpretation", body)

    def test_finite_model_reports_blocking_and_probabilities(self):
        body = self.post_json("portal:model_api", {"model":"mmsk","t_llegada":4,"t_atencion":10,"servers":2,"capacity":5,"replications":2,"horizon":120}).json()
        self.assertGreater(body["analytic"]["p_block"], 0)
        self.assertEqual(len(body["analytic"]["probs"]), 6)

    def test_erlang_b_has_zero_queue(self):
        body = self.post_json("portal:model_api", {"model":"erlangb","t_llegada":4,"t_atencion":10,"servers":3,"replications":2,"horizon":120}).json()
        self.assertEqual(body["analytic"]["wq_min"], 0)
        self.assertGreaterEqual(body["analytic"]["p_block"], 0)

    def test_dd1_returns_sequence(self):
        body = self.post_json("portal:model_api", {"model":"dd1","t_llegada":8,"t_atencion":9,"n":12}).json()
        self.assertEqual(len(body["sequence"]), 12)
        self.assertGreater(body["sequence"][-1]["Espera (min)"], 0)

    def test_compare_api(self):
        response = self.post_json("portal:compare_api", {"a":{"model":"mms","t_llegada":8,"t_atencion":12,"servers":2},"b":{"model":"mms","t_llegada":8,"t_atencion":12,"servers":3},"meta_wq":10,"meta_block":0.05})
        self.assertEqual(response.status_code, 200)
        self.assertIn("a", response.json())

    def test_economic_and_sizing_apis(self):
        common = {"t_llegada":8,"t_atencion":12,"max_servers":10,"meta_wq":10}
        econ = self.post_json("portal:economic_api", {**common,"cost_staff":25,"cost_wait":15})
        self.assertEqual(econ.status_code, 200)
        self.assertIn("recommended", econ.json())
        sizing = self.post_json("portal:sizing_api", {**common,"meta_p_wait":0.9,"sla_threshold":10,"sla_target":0.8})
        self.assertEqual(sizing.status_code, 200)
        self.assertIn("rows", sizing.json())

    def test_end_to_end_api(self):
        response = self.post_json("portal:end_to_end_api", {"t_llegada":8,"t_atencion":12,"current_servers":2,"max_servers":10,"cost_staff":25,"cost_wait":15,"meta_wq":10,"meta_p_wait":0.9})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("actual", body)
        self.assertIn("recommended", body)
        self.assertIn("marginal", body)

    def test_validator_csv(self):
        csv_data = "interarrival_min,service_min\n5,4\n7,6\n4,5\n6,8\n8,7\n"
        upload = SimpleUploadedFile("sample.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post(reverse("portal:validator_api"), {"file": upload})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["ok"])
        self.assertIn("arrival", body)
        self.assertIn("service", body)

    def test_simulation_reproducible_and_finite_capacity(self):
        a = simulate_mms(10, 8, 2, horizon_min=120, replications=3, seed=99)
        b = simulate_mms(10, 8, 2, horizon_min=120, replications=3, seed=99)
        self.assertEqual(a["wq_min"], b["wq_min"])
        finite = simulate_queue(3, 10, 2, horizon_min=120, replications=3, seed=10, capacity=3)
        self.assertGreaterEqual(finite["p_block"], 0)

    def test_gamma_service_simulation(self):
        result = simulate_queue(12, 8, 1, horizon_min=120, replications=2, seed=11, service_distribution="gamma", service_cv=1.5)
        self.assertGreaterEqual(result["wq_min"], 0)
