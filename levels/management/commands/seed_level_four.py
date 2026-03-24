from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 4 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level4, created = Level.objects.get_or_create(
            level_code='level_4',
            defaults={
                'title': 'Revenue Growth Misread Crisis',
                'description': 'Identify the misleading baseline in a revenue chart, compare the chart with the raw revenue data and marketing relationship, and decide how the marketing budget should be adjusted.',
                'objective_text': 'Verify the raw data behind the chart, judge the real revenue increase, and choose whether to double, maintain, or reduce the marketing budget.',
                'briefing_title': 'Marketing Budget Review Desk',
                'briefing_text': "The store manager saw a dramatic revenue-growth chart and wants to expand next month's marketing budget immediately.",
                'briefing_hint': 'Do not trust the visual jump alone. Compare the chart baseline with the raw revenue and budget relationship first.',
                'order': 4,
                'is_active': True,
            },
        )
        if not created:
            level4.title = 'Revenue Growth Misread Crisis'
            level4.description = 'Identify the misleading baseline in a revenue chart, compare the chart with the raw revenue data and marketing relationship, and decide how the marketing budget should be adjusted.'
            level4.objective_text = 'Verify the raw data behind the chart, judge the real revenue increase, and choose whether to double, maintain, or reduce the marketing budget.'
            level4.briefing_title = 'Marketing Budget Review Desk'
            level4.briefing_text = "The store manager saw a dramatic revenue-growth chart and wants to expand next month's marketing budget immediately."
            level4.briefing_hint = 'Do not trust the visual jump alone. Compare the chart baseline with the raw revenue and budget relationship first.'
            level4.order = 4
            level4.is_active = True
            level4.save()

        categories = {
            'npc': 'Colleagues',
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
                    '"Revenue surged this month. The whole chart is climbing fast, so if we double the marketing budget next month, we should earn even more."'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'chart_revenue',
                'title': 'Misleading Revenue Growth Chart',
                'content_type': 'chart',
                'content_text': (
                    "The chart starts its Y-axis at 80,000 and displays this month's revenue moving from 82,000 to 83,000, creating the visual impression of a dramatic surge."
                ),
                'content_json': {
                    'x': ['Last Month', 'This Month'],
                    'y': [82000, 83000],
                    'x_label': 'Month',
                    'y_label': 'Revenue (Y-axis starts at 80,000)',
                },
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'raw_revenue',
                'title': 'Raw Revenue Data Table',
                'content_type': 'table',
                'content_text': (
                    "This month's revenue is 83,000, up only 1,000 from last month's 82,000. That is a normal 1.2% increase, not a dramatic leap."
                ),
                'content_json': {
                    'headers': ['Month', 'Revenue', 'Change', 'Growth Rate'],
                    'rows': [
                        ['Last Month', '$82,000', '-', '-'],
                        ['This Month', '$83,000', '+$1,000', '1.2%'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'marketing_cost',
                'title': 'Marketing Budget and Revenue Relation Data',
                'content_type': 'table',
                'content_text': (
                    "This month's marketing budget was $5,000, but the revenue increase was not directly caused by extra marketing. Most growth came from natural community traffic."
                ),
                'content_json': {
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['Marketing Budget This Month', '$5,000'],
                        ['Revenue Increase', '$1,000'],
                        ['Primary Driver', 'Natural community traffic'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level4).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level4,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level4,
            defaults={
                'title': 'Marketing Budget Decision',
                'target_text': 'Identify the baseline mismatch, judge the true revenue change, and choose the most reasonable budget adjustment.',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Double Budget', 'Maintain Budget', 'Reduce Budget'],
                    'unit': 'USD',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_maintain_budget',
                'condition_json': {'selected_value': 'Maintain Budget'},
                'is_success': True,
                'message': (
                    'Congratulations. You identified the misleading chart baseline, recognized that the apparent surge was only a modest increase, and discovered that revenue was not strongly driven by marketing. Maintaining the budget avoids unnecessary cost waste.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_double_budget',
                'condition_json': {'selected_value': 'Double Budget'},
                'is_success': False,
                'message': (
                    "Too bad. You were misled by the chart's baseline mismatch and treated a 1.2% increase like explosive growth. Doubling the marketing budget would raise cost without protecting overall profit."
                ),
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_reduce_budget',
                'condition_json': {'selected_value': 'Reduce Budget'},
                'is_success': False,
                'message': (
                    'Too bad. You were too conservative. The modest revenue growth still benefits from maintaining the current budget, and reducing it could weaken stable customer traffic. Maintaining the budget is the most reasonable choice.'
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level4).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level4, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 4 seed data is ready.'))
