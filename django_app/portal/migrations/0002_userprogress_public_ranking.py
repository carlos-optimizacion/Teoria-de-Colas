from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[("portal","0001_initial")]
    operations=[migrations.AddField(model_name="userprogress",name="public_ranking",field=models.BooleanField(default=False))]
