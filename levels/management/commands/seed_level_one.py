from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 1 MVP data for the supermarket decision game.'

    def handle(self, *args, **options):
        level1, created = Level.objects.get_or_create(
            level_code='level_1',
            defaults={
                'title': 'Fresh Produce Waste Crisis',
                'description': 'Identify key decision clues, remove misleading noise, and choose the best strawberry order quantity for next week to turn losses into profit.',
                'objective_text': 'Tips: Trace the source of the clues to judge whether they are real signals or misleading noise. Distinguish between information that could distort your decision and information that genuinely indicates risk.',
                'briefing_title': 'Fresh Produce Control Room',
                'briefing_text': 'Strawberry and lettuce spoilage is close to 25%, and the boss wants next week planned before more stock goes bad.',
                'briefing_hint': 'Start with the loss attribution evidence instead of the vanity revenue view. If DOC stays above shelf life, waste will continue.',
                'order': 1,
                'is_active': True,
            },
        )
        if not created:
            level1.title = 'Fresh Produce Waste Crisis'
            level1.description = 'Identify key decision clues, remove misleading noise, and choose the best strawberry order quantity for next week to turn losses into profit.'
            level1.objective_text = 'Tips: Trace the source of the clues to judge whether they are real signals or misleading noise. Distinguish between information that could distort your decision and information that genuinely indicates risk.'
            level1.briefing_title = 'Fresh Produce Control Room'
            level1.briefing_text = 'Strawberry and lettuce spoilage is close to 25%, and the boss wants next week planned before more stock goes bad.'
            level1.briefing_hint = 'Start with the loss attribution evidence instead of the vanity revenue view. If DOC stays above shelf life, waste will continue.'
            level1.order = 1
            level1.is_active = True
            level1.save()

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
                'item_code': 'npc_manager',
                'title': 'Store Manager',
                'content_type': 'text',
                'content_text': (
                    'Yesterday the strawberries sold out and the category looked hot. Should we order more this week '
                    'and keep the momentum going?'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['npc'],
                'item_code': 'npc_zhangjie',
                'title': 'Ms. Zhang',
                'content_type': 'text',
                'content_text': (
                    'A lot of people came in for strawberries because of the short video yesterday, but that rush is '
                    'already fading. I do not think the spike will last.'
                ),
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'order_and_sales_history',
                'title': 'Strawberry Daily Order and Sales History (Past 4 Weeks)',
                'content_type': 'image',
                'content_text': (
                    'Over the past month, daily strawberry orders stayed around 300 kg. Sales remained relatively stable over the last four weeks, averaging about 100 kg per day. Order volume stayed far above sales, which kept the wastage rate high. Yesterday, the last day of the most recent week, showed one unusually strong sales spike.'
                ),
                'content_json': {
                    'src': '/static/levels/level1/strawberry-order-vs-sales-wastage.svg',
                    'alt': 'Strawberry daily order, sales, and wastage chart',
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'social_media_clip',
                'title': 'Social Media Video Clip',
                'content_type': 'image',
                'content_text': (
                    'A local influencer posted a strawberry recommendation video yesterday, which drove a temporary '
                    'wave of extra foot traffic.'
                ),
                'content_json': {
                    'src': '/static/levels/level1/social-media-clip-v2.png',
                    'alt': 'Social media video clip',
                },
                'is_key_item': True,
                'sort_order': 4,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'weekly_rainfall',
                'title': 'Weekly Rainfall Forecast',
                'content_type': 'image',
                'content_text': (
                    'Rain is expected through most of next week, which could reduce store traffic compared with clear days.'
                ),
                'content_json': {
                    'src': '/static/levels/level1/weekly-rainfall.png',
                    'alt': 'Weekly rainfall forecast',
                },
                'is_key_item': True,
                'sort_order': 5,
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
                'title': 'How many kilograms of strawberries should we order for next week?',
                'target_text': 'Choose the order quantity that feels most reasonable after looking through the clues.',
                'decision_type': 'single_choice',
                'config_json': {'options': [50, 100, 300], 'unit': 'kg'},
            },
        )

        rules = [
            {
                'rule_name': 'success_100',
                'condition_json': {'selected_value': 100},
                'is_success': True,
                'message': (
                    'Congratulations. You successfully reduced strawberry waste and turned losses into profit. You showed strong data-recognition skills by tracing the source of the evidence, filtering out the short-term noise from the viral post, and identifying the signal of weaker sales in the rainy-week forecast.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_50',
                'condition_json': {'selected_value': 50},
                'is_success': False,
                'message': (
                    "Too bad. You ordered too little, so the shelves ran empty in the middle of the week and the store lost a large number of customers, which kept you from reaching the profit target. Although you did filter out the noise from the viral post, you were too conservative and overlooked the supermarket's baseline sales. You did not use the historical report to identify the core sales signal correctly."
                ),
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_300',
                'condition_json': {'selected_value': 300},
                'is_success': False,
                'message': (
                    'Too bad. Next week the online buzz will fade, and rainy weather will reduce store traffic, so a large number of strawberries will remain on the shelf and spoil, making the loss even worse. You treated a one-time event as if it were a lasting sales signal.'
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

