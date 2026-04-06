from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 1 MVP data for the supermarket decision game.'

    def handle(self, *args, **options):
        level1, created = Level.objects.get_or_create(
            level_code='level_1',
            defaults={
                'title': 'The Strawberry Shuffle: Fresh & Fast',
                'description': "Think like a pro. Identify the real signals, ignore the noise, and pick the perfect order quantity. We're moving from 'wasting stock' to 'stacking profit.'",
                'objective_text': "Use your data tools to place a killer order. Let's minimize the trash and maximize the cash.",
                'briefing_title': 'Fresh Produce Control Room',
                'briefing_text': 'Strawberry and lettuce spoilage is close to 25%, and the boss wants next week planned before more stock goes bad.',
                'briefing_hint': 'Start with the loss attribution evidence instead of the vanity revenue view. If DOC stays above shelf life, waste will continue.',
                'order': 1,
                'is_active': True,
            },
        )
        if not created:
            level1.title = 'The Strawberry Shuffle: Fresh & Fast'
            level1.description = "Think like a pro. Identify the real signals, ignore the noise, and pick the perfect order quantity. We're moving from 'wasting stock' to 'stacking profit.'"
            level1.objective_text = "Use your data tools to place a killer order. Let's minimize the trash and maximize the cash."
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
                    'Strawberries flew off the shelves yesterday and we were close to a stockout. I don\'t want a repeat of that so I am leaning towards increasing this week\'s order.'
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
                    'Yesterday\'s strawberry rush was just \'viral\' heat. It\'s already cooling off. I don\'t think this demand is going to last through the week.'
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
                    'Over the past week, the daily purchase quantity of strawberries has remained at 150kg. The sales volume has been relatively stable, averaging about 100kg per day. On the last day of the past week (yesterday), there was an exceptionally strong sales peak.'
                ),
                'content_json': {
                    'src': '/static/levels/level1/strawberry-order-vs-sales-wastage.png',
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
                    'A local influencer gave our strawberries a shoutout yesterday! It brought in a huge wave of shoppers.'
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
                    'src': '/static/levels/level1/weekly-rainfall.jpg',
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
                'title': 'How many kilograms of strawberries should we order for tomorrow?',
                'target_text': 'Ready to place the order? Choose the quantity that balances the buzz with the actual data.',
                'decision_type': 'single_choice',
                'config_json': {'options': [50, 100, 150], 'unit': 'kg'},
            },
        )

        rules = [
            {
                'rule_name': 'success_100',
                'condition_json': {'selected_value': 100},
                'is_success': True,
                'message': (
                    'Nice win! You did not let a viral video distract you from the facts. Your order was perfectly timed to meet demand without the leftover mess. That is how you turn a profit!'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_50',
                'condition_json': {'selected_value': 50},
                'is_success': False,
                'message': (
                    'Darn - you went a little too lean. The shelves were wiped out before the week even got started, and we left a ton of money on the table. You played it too safe and missed the rush!'
                ),
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_150',
                'condition_json': {'selected_value': 150},
                'is_success': False,
                'message': (
                    'Ouch - that is a lot of leftovers. The viral hype fizzled out just as the rain started keeping people at home. You banked on that one-time spike lasting all week, and now the surplus is just hitting the bin. Next time, do not let a single like cloud the big picture!'
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

