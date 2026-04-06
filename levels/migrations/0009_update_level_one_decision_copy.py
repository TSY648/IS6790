from django.db import migrations


DECISION_TITLE = 'How many kilograms of strawberries should we order for tomorrow?'
DECISION_TARGET_TEXT = 'Choose the order quantity that feels most reasonable after looking through the clues.'
DECISION_CONFIG = {'options': [100, 200, 300], 'unit': 'kg'}

RULES = [
    {
        'rule_name': 'success_200',
        'condition_json': {'selected_value': 200},
        'is_success': True,
        'message': (
            'Nice work! You filtered out the social media hype, focused on the real sales pattern, '
            'and chose an order that cuts waste and helps the strawberry category make money again.'
        ),
        'score': 50,
        'next_action': 'next_level',
    },
    {
        'rule_name': 'fail_100',
        'condition_json': {'selected_value': 100},
        'is_success': False,
        'message': (
            'Not quite. You ordered too little, so the shelves ran empty too early in the week and '
            'the store missed a lot of sales.'
        ),
        'score': 0,
        'next_action': 'restart',
    },
    {
        'rule_name': 'fail_300',
        'condition_json': {'selected_value': 300},
        'is_success': False,
        'message': (
            'Not quite. The online buzz faded and rainy weather reduced foot traffic, so too many '
            'strawberries were left on the shelf and spoiled. You treated a one-time spike like it would last.'
        ),
        'score': 0,
        'next_action': 'restart',
    },
]


def update_level_one_decision_copy(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    DecisionConfig = apps.get_model('levels', 'DecisionConfig')
    ResultRule = apps.get_model('levels', 'ResultRule')

    level = Level.objects.filter(level_code='level_1').first()
    if not level:
        return

    DecisionConfig.objects.update_or_create(
        level=level,
        defaults={
            'title': DECISION_TITLE,
            'target_text': DECISION_TARGET_TEXT,
            'decision_type': 'single_choice',
            'config_json': DECISION_CONFIG,
        },
    )

    active_rule_names = [rule['rule_name'] for rule in RULES]
    ResultRule.objects.filter(level=level).exclude(rule_name__in=active_rule_names).delete()

    for rule in RULES:
        ResultRule.objects.update_or_create(level=level, rule_name=rule['rule_name'], defaults=rule)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [('levels', '0008_update_level_one_objective_text')]

    operations = [migrations.RunPython(update_level_one_decision_copy, noop_reverse)]
