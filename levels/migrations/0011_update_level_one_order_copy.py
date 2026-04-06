from django.db import migrations


DECISION_TARGET_TEXT = 'Ready to place the order? Choose the quantity that balances the buzz with the actual data.'

RULES = [
    {
        'rule_name': 'success_100',
        'condition_json': {'selected_value': 100},
        'is_success': True,
        'message': (
            'Nice win! You did not let a viral video distract you from the facts. '
            'Your order was perfectly timed to meet demand without the leftover mess. '
            'That is how you turn a profit!'
        ),
        'score': 50,
        'next_action': 'next_level',
    },
    {
        'rule_name': 'fail_50',
        'condition_json': {'selected_value': 50},
        'is_success': False,
        'message': (
            'Darn - you went a little too lean. The shelves were wiped out before the week even got started, '
            'and we left a ton of money on the table. You played it too safe and missed the rush!'
        ),
        'score': 0,
        'next_action': 'restart',
    },
    {
        'rule_name': 'fail_150',
        'condition_json': {'selected_value': 150},
        'is_success': False,
        'message': (
            'Ouch - that is a lot of leftovers. The viral hype fizzled out just as the rain started keeping people '
            'at home. You banked on that one-time spike lasting all week, and now the surplus is just hitting the '
            'bin. Next time, do not let a single like cloud the big picture!'
        ),
        'score': 0,
        'next_action': 'restart',
    },
]


def update_level_one_order_copy(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    DecisionConfig = apps.get_model('levels', 'DecisionConfig')
    ResultRule = apps.get_model('levels', 'ResultRule')

    level = Level.objects.filter(level_code='level_1').first()
    if not level:
        return

    DecisionConfig.objects.update_or_create(
        level=level,
        defaults={
            'title': 'How many kilograms of strawberries should we order for tomorrow?',
            'target_text': DECISION_TARGET_TEXT,
            'decision_type': 'single_choice',
            'config_json': {'options': [50, 100, 150], 'unit': 'kg'},
        },
    )

    active_rule_names = [rule['rule_name'] for rule in RULES]
    ResultRule.objects.filter(level=level).exclude(rule_name__in=active_rule_names).delete()

    for rule in RULES:
        ResultRule.objects.update_or_create(level=level, rule_name=rule['rule_name'], defaults=rule)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [('levels', '0010_update_level_one_sidebar_copy')]

    operations = [migrations.RunPython(update_level_one_order_copy, noop_reverse)]
