from django.db import migrations


NEW_OBJECTIVE_TEXT = (
    'Use the clues you find to decide the right strawberry order for this week, '
    'reduce waste, and help the store earn more from this category.'
)


def update_level_one_objective_text(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    Level.objects.filter(level_code='level_1').update(objective_text=NEW_OBJECTIVE_TEXT)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [('levels', '0007_refresh_level_one_information_sources')]

    operations = [migrations.RunPython(update_level_one_objective_text, noop_reverse)]
