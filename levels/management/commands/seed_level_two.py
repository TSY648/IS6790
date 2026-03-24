from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 2 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level2, created = Level.objects.get_or_create(
            level_code='level_2',
            defaults={
                'title': 'Egg Inventory Management Crisis',
                'description': 'Identify non-standard quantity units in egg sales and inventory data, standardize the records, and decide whether to reorder eggs without creating overstock or a shortage.',
                'objective_text': 'Unify the egg sales and inventory units, judge the real stock position, and make the correct ordering decision: do not reorder.',
                'briefing_title': 'Egg Inventory Review Desk',
                'briefing_text': 'The system shows an egg inventory value of only 100, and the store manager wants to place an urgent order for 50 cartons of eggs.',
                'briefing_hint': 'Do not accept the suggestion at face value. Standardize the inventory and sales units first, then judge whether stock is actually low.',
                'order': 2,
                'is_active': True,
            },
        )
        if not created:
            level2.title = 'Egg Inventory Management Crisis'
            level2.description = 'Identify non-standard quantity units in egg sales and inventory data, standardize the records, and decide whether to reorder eggs without creating overstock or a shortage.'
            level2.objective_text = 'Unify the egg sales and inventory units, judge the real stock position, and make the correct ordering decision: do not reorder.'
            level2.briefing_title = 'Egg Inventory Review Desk'
            level2.briefing_text = 'The system shows an egg inventory value of only 100, and the store manager wants to place an urgent order for 50 cartons of eggs.'
            level2.briefing_hint = 'Do not accept the suggestion at face value. Standardize the inventory and sales units first, then judge whether stock is actually low.'
            level2.order = 2
            level2.is_active = True
            level2.save()

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
                    '"Hurry and order 50 cartons. The system shows inventory is down to 100, so this week we will definitely run short if we do nothing."'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'egg_sales',
                'title': 'Egg Historical Sales Data (Last 4 Weeks)',
                'content_type': 'chart',
                'content_text': (
                    'Egg sales stayed stable over the last four weeks at roughly 100 eggs per week, with no major fluctuation.'
                ),
                'content_json': {
                    'x': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    'y': [95, 102, 98, 105],
                    'x_label': 'Week',
                    'y_label': 'Eggs Sold',
                },
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'egg_inventory',
                'title': 'Current Egg Inventory Data',
                'content_type': 'table',
                'content_text': (
                    'Current egg inventory: 100 cartons. Standardization hint: 1 carton = 10 eggs, but the system only shows the number and does not clearly label the unit.'
                ),
                'content_json': {
                    'headers': ['Item', 'Recorded Stock', 'Displayed Unit', 'Standardized Total'],
                    'rows': [
                        ['Egg inventory', '100', 'cartons', '1000 eggs'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 3,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level2).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level2,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level2,
            defaults={
                'title': 'Egg Reorder Decision',
                'target_text': 'Unify the egg sales and inventory units, judge the real stock position, and choose the correct action.',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Order', 'Do not order'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_do_not_order',
                'condition_json': {'selected_value': 'Do not order'},
                'is_success': True,
                'message': (
                    'Congratulations. You recognized that the egg sales and inventory records used different units, standardized them correctly, and made the right decision not to reorder. Standardizing the records helped you avoid unnecessary stock buildup and wasted purchasing cost.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_order',
                'condition_json': {'selected_value': 'Order'},
                'is_success': False,
                'message': (
                    "You failed this round. You made the reorder decision before standardizing the egg sales and inventory units and followed the manager's suggestion too quickly. The system's 100 was not a standardized quantity, and the real stock was 1,000 eggs, far above weekly demand."
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level2).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level2, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 2 seed data is ready.'))
