from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('levels', '0002_seed_level_one')]

    operations = [
        migrations.AddField(
            model_name='level',
            name='briefing_hint',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='level',
            name='briefing_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='level',
            name='briefing_title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='level',
            name='objective_text',
            field=models.TextField(blank=True),
        ),
    ]
