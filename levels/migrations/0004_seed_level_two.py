from django.db import migrations


def seed_level_two(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    InfoCategory = apps.get_model('levels', 'InfoCategory')
    LevelItem = apps.get_model('levels', 'LevelItem')
    DecisionConfig = apps.get_model('levels', 'DecisionConfig')
    ResultRule = apps.get_model('levels', 'ResultRule')

    level1 = Level.objects.filter(level_code='level_1').first()
    if level1:
        level1.objective_text = 'Identify the key factors affecting strawberry sales and decide the best order quantity for next week.'
        level1.briefing_title = 'Store Floor'
        level1.briefing_text = 'Welcome to Level 1. Start by reviewing the information sources on the right.'
        level1.briefing_hint = 'Your goal is to separate meaningful signals from distracting noise.'
        level1.save(update_fields=['objective_text', 'briefing_title', 'briefing_text', 'briefing_hint'])

    level2, _ = Level.objects.get_or_create(
        level_code='level_2',
        defaults={
            'title': 'Weekend Promotion Plan',
            'description': 'Check whether last week’s popular promotion can really be reused for a different customer group.',
            'objective_text': 'Review the evidence and choose the promotion plan that best fits evening office workers this weekend.',
            'briefing_title': 'Promotion Review Desk',
            'briefing_text': 'The store manager wants to repeat a daytime promotion that scored very well with older shoppers.',
            'briefing_hint': 'Your job is to verify whether that evidence also supports the evening crowd targeted this week.',
            'order': 2,
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
            'item_code': 'NPC_supervisor',
            'title': 'Store Manager',
            'content_type': 'text',
            'content_text': (
                'The promotion we ran for older daytime shoppers scored 95% satisfaction. Let us copy the same '
                'offer for evening office workers this weekend and move fast.'
            ),
            'is_key_item': True,
            'sort_order': 1,
        },
        {
            'category': resolved_categories['npc'],
            'item_code': 'NPC_cashier_weekend',
            'title': 'Evening Cashier',
            'content_type': 'text',
            'content_text': (
                'The evening crowd shops very differently. They come after work, move quickly, and care more about '
                'convenient bundles than the daytime discount signs.'
            ),
            'is_key_item': True,
            'sort_order': 2,
        },
        {
            'category': resolved_categories['report'],
            'item_code': 'survey_report',
            'title': 'Promotion Satisfaction Summary',
            'content_type': 'chart',
            'content_text': 'The original promotion received high satisfaction, but the sample came mostly from daytime shoppers.',
            'content_json': {
                'x': ['Daytime Seniors', 'Mixed Adults', 'Evening Workers'],
                'y': [95, 68, 41],
            },
            'is_key_item': True,
            'sort_order': 3,
        },
        {
            'category': resolved_categories['external'],
            'item_code': 'survey_details',
            'title': 'Survey Sampling Details',
            'content_type': 'text',
            'content_text': (
                'The survey was distributed from 10:00 to 17:00 on Saturday, and 70% of respondents were over '
                '50 years old. The sample does not match the evening office-worker audience.'
            ),
            'is_key_item': True,
            'sort_order': 4,
        },
        {
            'category': resolved_categories['external'],
            'item_code': 'basket_analysis',
            'title': 'Evening Basket Analysis',
            'content_type': 'text',
            'content_text': (
                'Average basket size looks high because of a few very large purchases, but 70% of evening shoppers '
                'spend closer to 30 yuan and prefer compact combo offers.'
            ),
            'is_key_item': True,
            'sort_order': 5,
        },
    ]

    for item in items:
        LevelItem.objects.update_or_create(level=level2, item_code=item['item_code'], defaults=item)

    DecisionConfig.objects.update_or_create(
        level=level2,
        defaults={
            'title': 'Weekend Promotion Decision',
            'target_text': 'Choose the promotion plan that best fits the evening office-worker audience.',
            'decision_type': 'single_choice',
            'config_json': {
                'options': [
                    'Copy the daytime senior promotion exactly',
                    'Design a lighter combo offer for evening workers',
                    'Launch a large spend-heavy premium bundle',
                ],
                'unit': '',
            },
        },
    )

    rules = [
        {
            'rule_name': 'success_evening_combo',
            'condition_json': {'selected_value': 'Design a lighter combo offer for evening workers'},
            'is_success': True,
            'message': (
                'Excellent call. You recognized that the original survey did not represent the evening audience, so '
                'you adapted the offer instead of copying it blindly.'
            ),
            'score': 50,
            'next_action': 'certificate',
        },
        {
            'rule_name': 'fail_copy_daytime',
            'condition_json': {'selected_value': 'Copy the daytime senior promotion exactly'},
            'is_success': False,
            'message': (
                'The copied promotion underperformed. High daytime satisfaction did not mean the same plan was a good '
                'fit for the evening crowd.'
            ),
            'score': 0,
            'next_action': 'restart',
        },
        {
            'rule_name': 'fail_premium_bundle',
            'condition_json': {'selected_value': 'Launch a large spend-heavy premium bundle'},
            'is_success': False,
            'message': (
                'The premium bundle was too ambitious. A few large baskets distorted the average, and most evening '
                'shoppers were looking for smaller, faster purchases.'
            ),
            'score': 0,
            'next_action': 'restart',
        },
    ]

    for rule in rules:
        ResultRule.objects.update_or_create(level=level2, rule_name=rule['rule_name'], defaults=rule)


def unseed_level_two(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    Level.objects.filter(level_code='level_2').delete()


class Migration(migrations.Migration):
    dependencies = [('levels', '0003_level_briefing_fields')]

    operations = [migrations.RunPython(seed_level_two, unseed_level_two)]
