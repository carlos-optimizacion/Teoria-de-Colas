from django.test import TestCase
from django.urls import reverse

from simulation_core import simulate_mms


class PortalTests(TestCase):
    def test_home_and_models_render(self):
        for name in ("portal:home", "portal:mm1", "portal:mms"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_queue_api_returns_analytic_and_simulation(self):
        response = self.client.post(
            reverse("portal:queue_api"),
            data='{"model":"mms","t_llegada":10,"t_atencion":8,"servers":2,"horizon":240,"replications":10}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertIn("analytic", payload)
        self.assertIn("simulation", payload)
        self.assertGreaterEqual(payload["simulation"]["wq_min"], 0)

    def test_simulation_is_reproducible(self):
        a = simulate_mms(10, 8, 2, horizon_min=120, replications=5, seed=99)
        b = simulate_mms(10, 8, 2, horizon_min=120, replications=5, seed=99)
        self.assertEqual(a["wq_min"], b["wq_min"])
