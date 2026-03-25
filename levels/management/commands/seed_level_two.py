from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 2 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level2, created = Level.objects.get_or_create(
            level_code='level_2',
            defaults={
                'title': 'Egg Inventory Management Crisis',
                'description': 'Identify and standardize the non-standard units used in egg sales and inventory data. Based on the standardized records, judge the real stock position and decide whether to reorder eggs, avoiding both stock buildup and overstock losses while also preventing egg stockouts and controlling unnecessary purchasing cost.',
                'objective_text': 'Standardize the egg sales and inventory units, judge the real inventory position, and make the correct decision about whether to reorder eggs.',
                'briefing_title': 'Egg Inventory Review Desk',
                'briefing_text': 'The system shows an egg inventory value of only 100, and the store manager wants to place an urgent order for 50 cartons of eggs.',
                'briefing_hint': 'Do not accept the suggestion at face value. Standardize the inventory and sales units first, then judge whether stock is actually low.',
                'order': 2,
                'is_active': True,
            },
        )
        if not created:
            level2.title = 'Egg Inventory Management Crisis'
            level2.description = 'Identify and standardize the non-standard units used in egg sales and inventory data. Based on the standardized records, judge the real stock position and decide whether to reorder eggs, avoiding both stock buildup and overstock losses while also preventing egg stockouts and controlling unnecessary purchasing cost.'
            level2.objective_text = 'Standardize the egg sales and inventory units, judge the real inventory position, and make the correct decision about whether to reorder eggs.'
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
                'content_type': 'table',
                'content_text': (
                    'Weekly egg sales remained relatively stable over the last four weeks, averaging around 150 units with no major fluctuation.'
                ),
                'content_json': {
                    'headers': ['Week', 'Egg Sales Volume (Units)'],
                    'rows': [
                        ['Week 1', '140'],
                        ['Week 2', '155'],
                        ['Week 3', '157'],
                        ['Week 4', '150'],
                    ],
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
                    'The current inventory table shows mixed product units across the store. Eggs are recorded as 152 units on Monday and rise to 365 units on Sunday, while other products use kg. The system uses non-standard labels, so you must identify what the egg unit really means before deciding whether to reorder.'
                ),
                'content_json': {
                    'headers': ['Product Name', 'Margin Type', 'Unit', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'rows': [
                        ['Eggs', 'Low Margin', 'Units', '152', '148', '155', '150', '160', '350', '365'],
                        ['Bananas', 'Low Margin', 'kg', '200', '195', '210', '190', '220', '380', '400'],
                        ['Cabbage', 'Low Margin', 'kg', '150', '140', '145', '155', '150', '290', '310'],
                        ['Fuji Apples', 'Normal', 'kg', '150', '155', '140', '145', '160', '165', '175'],
                        ['Roma Tomatoes', 'Normal', 'kg', '150', '145', '150', '160', '155', '160', '160'],
                        ['Ribeye Steak', 'High Margin', 'Units', '100', '95', '110', '105', '115', '125', '130'],
                        ['Strawberries', 'High Margin', 'kg', '148', '142', '140', '145', '140', '150', '300'],
                        ['DAILY TOTAL', '-', '-', '1050', '1020', '1060', '1050', '1100', '1620', '1840'],
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
