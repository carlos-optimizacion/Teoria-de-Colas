import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import GameRun, SavedScenario, UserProgress

class ProductPersistenceTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="tester",password="StrongPass123!")
        self.client.login(username="tester",password="StrongPass123!")

    def test_run_persists_and_progress_awards_once(self):
        payload={"scenario":"banco","staffing":[3]*8,"replications":2,"seed":100}
        first=self.client.post("/api/challenge/",data=json.dumps(payload),content_type="application/json")
        self.assertEqual(first.status_code,200)
        data=first.json();self.assertTrue(data["ok"]);self.assertTrue(GameRun.objects.filter(user=self.user,id=data["run_id"]).exists())
        progress=UserProgress.objects.get(user=self.user);xp1=progress.xp
        second=self.client.post("/api/challenge/",data=json.dumps(payload),content_type="application/json")
        self.assertEqual(second.status_code,200)
        progress.refresh_from_db();self.assertGreater(progress.xp,xp1)
        self.assertLessEqual(progress.xp-xp1,100)

    def test_saved_scenario_and_exports(self):
        response=self.client.post("/api/scenario/save/",data=json.dumps({"name":"Plan A","scenario":"banco","payload":{"staffing":[4]*8}}),content_type="application/json")
        self.assertEqual(response.status_code,200);self.assertEqual(SavedScenario.objects.filter(user=self.user).count(),1)
        run=GameRun.objects.create(user=self.user,scenario="banco",title="Banco",score=82.5,passed=True,metrics={"sla":.95,"avg_wait":3.2,"total_cost":400},staffing=[4]*8,actions=[],config={})
        for fmt,content_type in (("json","application/json"),("csv","text/csv"),("pdf","application/pdf")):
            r=self.client.get(reverse("portal:run_export",args=[run.id,fmt]))
            self.assertEqual(r.status_code,200);self.assertTrue(r["Content-Type"].startswith(content_type))

    def test_progress_leaderboard_reports_and_login(self):
        GameRun.objects.create(user=self.user,scenario="banco",title="Banco",score=90,passed=True,metrics={},staffing=[],actions=[],config={})
        for name in ("progress","leaderboard","reports"):
            self.assertEqual(self.client.get(reverse("portal:"+name)).status_code,200)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("portal:progress")).status_code,302)
        self.assertEqual(self.client.get(reverse("portal:leaderboard")).status_code,200)
