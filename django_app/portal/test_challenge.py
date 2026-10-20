from django.test import SimpleTestCase
from .challenge_engine import SCENARIOS, evaluate_game

class ChallengeEngineTests(SimpleTestCase):
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
