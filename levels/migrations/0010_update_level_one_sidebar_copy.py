from django.db import migrations


LEVEL_ONE_TITLE = 'The Strawberry Shuffle: Fresh & Fast'
LEVEL_ONE_DESCRIPTION = (
    "Think like a pro. Identify the real signals, ignore the noise, and pick the perfect order quantity. "
    "We're moving from 'wasting stock' to 'stacking profit.'"
)
LEVEL_ONE_OBJECTIVE = "Use your data tools to place a killer order. Let's minimize the trash and maximize the cash."


def update_level_one_sidebar_copy(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    Level.objects.filter(level_code='level_1').update(
        title=LEVEL_ONE_TITLE,
        description=LEVEL_ONE_DESCRIPTION,
        objective_text=LEVEL_ONE_OBJECTIVE,
    )


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [('levels', '0009_update_level_one_decision_copy')]

    operations = [migrations.RunPython(update_level_one_sidebar_copy, noop_reverse)]
