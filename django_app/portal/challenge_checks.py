from django.test import TestCase
from .challenge_engine import SCENARIOS, evaluate_game

class ChallengeEngineTests(TestCase):
    def test_five_missions(self):
        self.assertEqual(len(SCENARIOS), 5)
        for key,scenario in SCENARIOS.items():
            r=evaluate_game({"scenario":key,"staffing":[min(5,scenario["max_servers"])]*8,"replications":2,"seed":321})
            m=r["metrics"]
            self.assertAlmostEqual(m["arrivals"],m["admitted"]+m["blocked"])
            self.assertAlmostEqual(m["admitted"],m["completed"]+m["unserved_at_close"])
            self.assertTrue(0<=m["sla"]<=1)
            self.assertTrue(0<=m["utilization"]<=1.0)
            self.assertTrue(0<=r["score"]<=100)
            self.assertTrue(all(x>=0 for x in (m["staff_cost"],m["waiting_cost"],m["lost_cost"])))
    def test_determinism_and_budget(self):
        p={"scenario":"banco","staffing":[3]*8,"seed":77,"replications":2}
        self.assertEqual(evaluate_game(p),evaluate_game(p))
    def test_invalid_staff(self):
        with self.assertRaises(ValueError):
            evaluate_game({"staffing":[2,3]})
        with self.assertRaises(ValueError):
            evaluate_game({"staffing":[2.5]*8})
    def test_view(self):
        self.assertEqual(self.client.get("/challenge/").status_code,200)
        r=self.client.post("/api/challenge/",data='{"scenario":"banco","staffing":[3,3,3,3,3,3,3,3],"replications":2}',content_type="application/json")
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.json()["ok"])

    def test_dynamic_intervention_preserves_past(self):
        start={"scenario":"banco","staffing":[3]*8,"replications":2,"seed":87}
        plain=evaluate_game(start)
        dynamic=evaluate_game({**start,"actions":[{"minute":240,"servers":6}]})
        self.assertEqual(plain["metrics"]["arrivals"],dynamic["metrics"]["arrivals"])
        self.assertGreater(dynamic["metrics"]["staff_cost"],plain["metrics"]["staff_cost"])
        self.assertEqual(plain["metrics"]["staff_cost"],552)
        self.assertEqual(dynamic["metrics"]["staff_cost"],828)
        before=lambda r:[(f["t"],f["kind"],f["client"],f["queue_ids"],f["servers"])
            for f in r["events"] if f["t"]<240]
        self.assertEqual(before(plain),before(dynamic))

    def test_each_snapshot_has_consistent_clients(self):
        result=evaluate_game({"scenario":"hospital","staffing":[5]*8,"replications":2})
        for frame in result["events"]:
            self.assertEqual(frame["busy"],sum(x is not None for x in frame["servers"]))
            self.assertLessEqual(len(frame["queue_ids"]),frame["queue"])
            self.assertLessEqual(frame["blocked"],frame["arrivals"])
        last=result["events"][-1]
        self.assertEqual(last["kind"],"end")
        self.assertEqual(last["t"],480)

    def test_action_validation_and_api(self):
        p={"scenario":"banco","staffing":[3]*8,"actions":[{"minute":200,"servers":5},{"minute":190,"servers":4}]}
        with self.assertRaises(ValueError):
            evaluate_game(p)
        for wrong in [float("nan"),1.5,False,0,900]:
            with self.subTest(wrong=wrong):
                with self.assertRaises(ValueError):
                    evaluate_game({"scenario":"banco","staffing":[wrong]*8})
        import json
        response=self.client.post("/api/challenge/",data=json.dumps({
            "scenario":"banco","staffing":[3]*8,"actions":[{"minute":240,"servers":4}],
            "replications":2}),content_type="application/json")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["actions"],[{"minute":240,"servers":4}])
        self.assertGreater(len(response.json()["events"]),10)

    def test_unified_app_is_same_portal(self):
        from django.urls import reverse
        response=self.client.get(reverse("portal:aplicativo_app"))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'id="challenge-config"')
        self.assertContains(response,'id="scene-shell"')
        self.assertContains(response,'img/scenarios/banco.svg')
        self.assertContains(response,'id="classic-lab"')

    def test_original_simulator_has_visual_asset(self):
        response=self.client.get("/simular/colas/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"data-scene-art")
        self.assertContains(response,"banco.svg")

    def test_challenge_template_loads_json_configuration(self):
        response=self.client.get("/challenge/")
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'id="challenge-config"')
        self.assertContains(response,'id="challenge-scrub"')
        self.assertContains(response,'id="classic-lab"')
        self.assertContains(response,'js/classic-lab.js')
        self.assertContains(response,'M/M/s/K')

    def test_patience_abandonment_and_priority_are_reproducible(self):
        payload={"scenario":"supermercado","staffing":[1]*8,"replications":2,"seed":2026,
                 "patience_min":0.2,"priority_share":0.30}
        a=evaluate_game(payload); b=evaluate_game(payload)
        self.assertEqual(a,b)
        self.assertGreater(a["metrics"]["abandoned"],0)
        self.assertAlmostEqual(a["metrics"]["admitted"],
            a["metrics"]["completed"]+a["metrics"]["abandoned"]+a["metrics"]["unserved_at_close"])
        self.assertEqual(a["options"]["priority_share"],0.3)
        self.assertEqual(a["options"]["patience_min"],0.2)
        self.assertTrue(any(frame.get("kind")=="abandon" for frame in a["events"]))

    def test_advanced_options_validation(self):
        with self.assertRaises(ValueError):
            evaluate_game({"scenario":"banco","staffing":[3]*8,"priority_share":1.2})
        with self.assertRaises(ValueError):
            evaluate_game({"scenario":"banco","staffing":[3]*8,"patience_min":-1})

    def test_operational_overrides_change_real_simulation(self):
        base={"scenario":"banco","staffing":[3]*8,"replications":2,"seed":123}
        standard=evaluate_game(base)
        costly=evaluate_game({**base,"staff_hour":100,"arrival_min":2,"service_min":5,"capacity":12,"sla_min":8,"sla_target":.8})
        self.assertEqual(costly["config"]["staff_hour"],100)
        self.assertEqual(costly["config"]["capacity"],12)
        self.assertGreater(costly["metrics"]["staff_cost"],standard["metrics"]["staff_cost"])
        self.assertNotEqual(costly["metrics"]["arrivals"],standard["metrics"]["arrivals"])
        with self.assertRaises(ValueError):
            evaluate_game({**base,"capacity":0})
