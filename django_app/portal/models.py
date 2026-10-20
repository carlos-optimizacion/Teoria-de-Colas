from django.conf import settings
from django.db import models
from django.utils import timezone

class UserProgress(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="decision_progress")
    xp=models.PositiveIntegerField(default=0)
    level=models.PositiveIntegerField(default=1)
    coins=models.PositiveIntegerField(default=0)
    completed_models=models.JSONField(default=list,blank=True)
    completed_scenarios=models.JSONField(default=list,blank=True)
    achievements=models.JSONField(default=list,blank=True)
    public_ranking=models.BooleanField(default=False)
    updated_at=models.DateTimeField(auto_now=True)

    @staticmethod
    def level_for_xp(xp):
        return max(1,1+int(xp)//500)

    def award(self,xp=0,coins=0,scenario=None,achievement=None):
        self.xp=max(0,self.xp+int(xp))
        self.coins=max(0,self.coins+int(coins))
        self.level=self.level_for_xp(self.xp)
        scenarios=list(self.completed_scenarios or [])
        if scenario and scenario not in scenarios: scenarios.append(scenario)
        self.completed_scenarios=scenarios
        achievements=list(self.achievements or [])
        if achievement and achievement not in achievements: achievements.append(achievement)
        self.achievements=achievements
        self.save()
        return self

class GameRun(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="queue_runs")
    session_key=models.CharField(max_length=64,blank=True,db_index=True)
    scenario=models.CharField(max_length=32,db_index=True)
    title=models.CharField(max_length=120)
    score=models.DecimalField(max_digits=5,decimal_places=1)
    passed=models.BooleanField(default=False)
    seed=models.PositiveIntegerField(default=2026)
    replications=models.PositiveSmallIntegerField(default=10)
    staffing=models.JSONField(default=list)
    actions=models.JSONField(default=list)
    metrics=models.JSONField(default=dict)
    config=models.JSONField(default=dict)
    created_at=models.DateTimeField(default=timezone.now,db_index=True)

    class Meta:
        ordering=["-created_at"]
        indexes=[models.Index(fields=["scenario","-score"],name="portal_game_scenari_1e2a04_idx")]

class SavedScenario(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="saved_queue_scenarios")
    name=models.CharField(max_length=100)
    scenario=models.CharField(max_length=32)
    payload=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering=["-updated_at"]
