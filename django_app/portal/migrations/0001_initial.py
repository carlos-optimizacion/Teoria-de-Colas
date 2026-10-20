from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name="UserProgress",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("xp",models.PositiveIntegerField(default=0)),("level",models.PositiveIntegerField(default=1)),("coins",models.PositiveIntegerField(default=0)),
            ("completed_models",models.JSONField(blank=True,default=list)),("completed_scenarios",models.JSONField(blank=True,default=list)),
            ("achievements",models.JSONField(blank=True,default=list)),("updated_at",models.DateTimeField(auto_now=True)),
            ("user",models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name="decision_progress",to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="GameRun",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("session_key",models.CharField(blank=True,db_index=True,max_length=64)),("scenario",models.CharField(db_index=True,max_length=32)),
            ("title",models.CharField(max_length=120)),("score",models.DecimalField(decimal_places=1,max_digits=5)),("passed",models.BooleanField(default=False)),
            ("seed",models.PositiveIntegerField(default=2026)),("replications",models.PositiveSmallIntegerField(default=10)),
            ("staffing",models.JSONField(default=list)),("actions",models.JSONField(default=list)),("metrics",models.JSONField(default=dict)),("config",models.JSONField(default=dict)),
            ("created_at",models.DateTimeField(db_index=True,default=django.utils.timezone.now)),
            ("user",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="queue_runs",to=settings.AUTH_USER_MODEL)),
        ],options={"ordering":["-created_at"]}),
        migrations.CreateModel(name="SavedScenario",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("name",models.CharField(max_length=100)),
            ("scenario",models.CharField(max_length=32)),("payload",models.JSONField(default=dict)),("created_at",models.DateTimeField(auto_now_add=True)),("updated_at",models.DateTimeField(auto_now=True)),
            ("user",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="saved_queue_scenarios",to=settings.AUTH_USER_MODEL)),
        ],options={"ordering":["-updated_at"]}),
        migrations.AddIndex(model_name="gamerun",index=models.Index(fields=["scenario","-score"],name="portal_game_scenari_1e2a04_idx")),
    ]
