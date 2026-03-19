from django.db import migrations


def seed_level_one(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    InfoCategory = apps.get_model('levels', 'InfoCategory')
    LevelItem = apps.get_model('levels', 'LevelItem')
    DecisionConfig = apps.get_model('levels', 'DecisionConfig')
    ResultRule = apps.get_model('levels', 'ResultRule')

    level1, _ = Level.objects.get_or_create(
        level_code='level_1',
        defaults={
            'title': 'Fresh Produce Shrinkage Crisis',
            'description': 'Determine the best strawberry order quantity and bring the category back to profit.',
            'order': 1,
            'is_active': True,
        },
    )

    categories = {
        'npc': 'NPC',
        'report': 'Reports',
        'external': 'External Info',
    }
    resolved_categories = {}
    for code, name in categories.items():
        category, _ = InfoCategory.objects.get_or_create(code=code, defaults={'name': name})
        category.name = name
        category.save(update_fields=['name'])
        resolved_categories[code] = category

    items = [
        {
            'category': resolved_categories['npc'],
            'item_code': 'NPC_manager',
            'title': 'Store Manager',
            'content_type': 'text',
            'content_text': (
                'The strawberries sold out yesterday. Demand must be booming, so let us double next week\'s '
                'order and ride the momentum.'
            ),
            'is_key_item': True,
            'sort_order': 1,
        },
        {
            'category': resolved_categories['npc'],
            'item_code': 'NPC_cashier',
            'title': 'Ms. Zhang',
            'content_type': 'text',
            'content_text': (
                'A lot of customers came in yesterday because of an online video and immediately asked where '
                'the strawberries were. Hardly anyone asked today.'
            ),
            'is_key_item': True,
            'sort_order': 2,
        },
        {
            'category': resolved_categories['report'],
            'item_code': 'sales_trend',
            'title': 'Historical Strawberry Sales Trend',
            'content_type': 'chart',
            'content_text': (
                'Sales stayed relatively stable over the past four weeks, with a sharp spike yesterday that '
                'was about double the usual volume.'
            ),
            'content_json': {
                'x': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Yesterday'],
                'y': [180, 190, 175, 185, 360],
            },
            'is_key_item': True,
            'sort_order': 3,
        },
        {
            'category': resolved_categories['external'],
            'item_code': 'social_news',
            'title': 'Social Media Video Clip',
            'content_type': 'text',
            'content_text': (
                'A local influencer filmed a strawberry recommendation video outside the store yesterday, '
                'and it received more than 100k likes.'
            ),
            'is_key_item': True,
            'sort_order': 4,
        },
        {
            'category': resolved_categories['external'],
            'item_code': 'weather_forecast',
            'title': 'Rainfall Forecast for Next Week',
            'content_type': 'text',
            'content_text': 'Continuous rain is expected next week, and store traffic is projected to drop by 30%.',
            'is_key_item': True,
            'sort_order': 5,
        },
    ]

    for item in items:
        LevelItem.objects.update_or_create(level=level1, item_code=item['item_code'], defaults=item)

    DecisionConfig.objects.update_or_create(
        level=level1,
        defaults={
            'title': 'Weekly Strawberry Order Decision',
            'target_text': 'Based on the information above, decide how many kilograms of strawberries to order.',
            'decision_type': 'single_choice',
            'config_json': {'options': [100, 200, 300], 'unit': 'kg'},
        },
    )

    rules = [
        {
            'rule_name': 'success_200',
            'condition_json': {'selected_value': 200},
            'is_success': True,
            'message': (
                'Great job! You reduced strawberry shrinkage and brought the category back to profit. '
                'You filtered out the short-term influencer buzz and focused on the real demand trend.'
            ),
            'score': 50,
            'next_action': 'next_level',
        },
        {
            'rule_name': 'fail_100',
            'condition_json': {'selected_value': 100},
            'is_success': False,
            'message': (
                'Unfortunately, you ordered too little. The shelf was empty by midweek, and many customers '
                'left without buying anything.'
            ),
            'score': 0,
            'next_action': 'restart',
        },
        {
            'rule_name': 'fail_300',
            'condition_json': {'selected_value': 300},
            'is_success': False,
            'message': (
                'Unfortunately, the influencer buzz faded and rainy weather reduced store traffic. Too many '
                'strawberries were left unsold and spoiled on the shelf.'
            ),
            'score': 0,
            'next_action': 'restart',
        },
    ]

    for rule in rules:
        ResultRule.objects.update_or_create(level=level1, rule_name=rule['rule_name'], defaults=rule)


def unseed_level_one(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    Level.objects.filter(level_code='level_1').delete()


class Migration(migrations.Migration):
    dependencies = [('levels', '0001_initial')]

    operations = [migrations.RunPython(seed_level_one, unseed_level_one)]
