from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 1 MVP data for the supermarket decision game.'

    def handle(self, *args, **options):
        level1, created = Level.objects.get_or_create(
            level_code='level_1',
            defaults={
                'title': 'Fresh Produce Waste Crisis',
                'description': 'Use loss attribution evidence to set a safer strawberry order and cut spoilage before it happens again.',
                'objective_text': 'Review the right report, compare DOC against shelf life, and choose the strawberry order quantity that protects both availability and profit.',
                'briefing_title': 'Fresh Produce Control Room',
                'briefing_text': 'Strawberry and lettuce spoilage is close to 25%, and the boss wants next week planned before more stock goes bad.',
                'briefing_hint': 'Start with the loss attribution evidence instead of the vanity revenue view. If DOC stays above shelf life, waste will continue.',
                'order': 1,
                'is_active': True,
            },
        )
        if not created:
            level1.title = 'Fresh Produce Waste Crisis'
            level1.description = 'Use loss attribution evidence to set a safer strawberry order and cut spoilage before it happens again.'
            level1.objective_text = 'Review the right report, compare DOC against shelf life, and choose the strawberry order quantity that protects both availability and profit.'
            level1.briefing_title = 'Fresh Produce Control Room'
            level1.briefing_text = 'Strawberry and lettuce spoilage is close to 25%, and the boss wants next week planned before more stock goes bad.'
            level1.briefing_hint = 'Start with the loss attribution evidence instead of the vanity revenue view. If DOC stays above shelf life, waste will continue.'
            level1.order = 1
            level1.is_active = True
            level1.save()

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
                'item_code': 'npc_manager_push',
                'title': 'Store Manager',
                'content_type': 'text',
                'content_text': (
                    'Yesterday we sold out. Demand must be peaking, so why not double the strawberry order and ride '
                    'the momentum for another week?'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['npc'],
                'item_code': 'npc_analyst_hint',
                'title': 'Produce Analyst',
                'content_type': 'text',
                'content_text': (
                    'Before we order anything, we should open the Loss Attribution Analysis report. A one-day spike '
                    'does not explain why spoilage has stayed high.'
                ),
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'total_revenue_dashboard',
                'title': 'Total Revenue Dashboard',
                'content_type': 'text',
                'content_text': (
                    'Yesterday looks exciting because total produce revenue jumped for one day, but this dashboard '
                    'does not explain which item is spoiling or whether inventory is sitting too long.'
                ),
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'loss_attribution_report',
                'title': 'Loss Attribution Analysis Report',
                'content_type': 'table',
                'content_text': (
                    'This is the report that explains the waste problem. Strawberries are currently sitting longer '
                    'than their shelf life allows.'
                ),
                'content_json': {
                    'headers': ['Item', 'Forecast Daily Sales', 'Current Inventory', 'DOC', 'Shelf Life', 'Risk'],
                    'rows': [
                        ['Strawberries', '26 kg', '90 kg', '3.5 days', '3 days', 'Waste risk'],
                        ['Organic Lettuce', '18 kg', '42 kg', '2.3 days', '2 days', 'Waste risk'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'four_week_sales_trend',
                'title': '4-Week Strawberry Sales Trend',
                'content_type': 'chart',
                'content_text': (
                    'The four-week pattern is stable, while yesterday is a clear one-day spike. The baseline demand '
                    'is much closer to the weekly trend than to the outlier.'
                ),
                'content_json': {
                    'x': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Yesterday'],
                    'y': [176, 182, 179, 184, 360],
                    'x_label': 'Period',
                    'y_label': 'Strawberry Sales (kg)',
                },
                'is_key_item': True,
                'sort_order': 5,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'influencer_clip',
                'title': 'Social Media Video Clip',
                'content_type': 'text',
                'content_text': (
                    'A local influencer happened to film outside the store yesterday, and the clip sent a temporary '
                    'rush of customers looking for strawberries. The traffic spike has already faded.'
                ),
                'is_key_item': True,
                'sort_order': 6,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'weather_forecast',
                'title': 'Rainfall Forecast for Next Week',
                'content_type': 'text',
                'content_text': (
                    'Rain is expected through most of next week, so total foot traffic should be softer than the '
                    'influencer day rather than stronger.'
                ),
                'is_key_item': True,
                'sort_order': 7,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'competitor_calendar',
                'title': 'Competitor Promotion Calendar',
                'content_type': 'text',
                'content_text': (
                    'The nearby competitor is ending its fruit coupon on Sunday. Demand may normalize slightly, but '
                    'there is no evidence of a lasting demand surge large enough to justify a doubled order.'
                ),
                'is_key_item': True,
                'sort_order': 8,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level1).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level1,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level1,
            defaults={
                'title': 'Weekly Strawberry Order Decision',
                'target_text': 'Approve the strawberry order quantity that best fits the trend and keeps expected DOC under shelf life.',
                'decision_type': 'single_choice',
                'config_json': {'options': [140, 180, 260], 'unit': 'kg'},
            },
        )

        rules = [
            {
                'rule_name': 'success_180',
                'condition_json': {'selected_value': 180},
                'is_success': True,
                'message': (
                    'Correct. You opened the loss attribution evidence, ignored the one-day spike, and chose an order '
                    'that brings DOC back under strawberry shelf life instead of chasing noise.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_140',
                'condition_json': {'selected_value': 140},
                'is_success': False,
                'message': (
                    'That correction was too aggressive. You solved the waste risk, but the shelf emptied too early '
                    'and regular demand was not fully covered.'
                ),
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_260',
                'condition_json': {'selected_value': 260},
                'is_success': False,
                'message': (
                    'That order still chases yesterday\'s spike. DOC stays too high for a short-life item, so the '
                    'department ends up with another week of preventable spoilage.'
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level1).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level1, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 1 seed data is ready.'))
