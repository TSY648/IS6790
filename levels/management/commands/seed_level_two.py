from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 2 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level2, created = Level.objects.get_or_create(
            level_code='level_2',
            defaults={
                'title': 'Egg Inventory Check',
                'description': "Don't get tripped up by the numbers. Identify the messy units in our egg reports, standardize the data, and make the final call. Your goal: keep the shelves full without wasting cash on stock we do not need.",
                'objective_text': 'Clean up the data, find the real inventory count, and decide: to order, or not to order?',
                'briefing_title': 'Egg Inventory Check',
                'briefing_text': 'The dashboard says eggs are down to 100 on hand, and the Store Manager wants a 50-carton emergency order right away.',
                'briefing_hint': 'Pause before you panic. Clean up the units first, then figure out what that 100 really means.',
                'order': 2,
                'is_active': True,
            },
        )
        if not created:
            level2.title = 'Egg Inventory Check'
            level2.description = "Don't get tripped up by the numbers. Identify the messy units in our egg reports, standardize the data, and make the final call. Your goal: keep the shelves full without wasting cash on stock we do not need."
            level2.objective_text = 'Clean up the data, find the real inventory count, and decide: to order, or not to order?'
            level2.briefing_title = 'Egg Inventory Check'
            level2.briefing_text = 'The dashboard says eggs are down to 100 on hand, and the Store Manager wants a 50-carton emergency order right away.'
            level2.briefing_hint = 'Pause before you panic. Clean up the units first, then figure out what that 100 really means.'
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
                    "Hurry and get 50 cartons ordered! The system is showing only 100 left in stock. If we sit on our hands, we are going to be staring at empty shelves by the weekend."
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'egg_sales',
                'title': 'Egg Historical Sales Data',
                'content_type': 'table',
                'content_text': (
                    "Check the trends: egg sales have been rock-steady for the last month, averaging about 150 units a week without any weird spikes. Use this as your normal to see if our current stock actually stacks up."
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
                'title': 'Current Egg Inventory Data (Raw - mixed units)',
                'content_type': 'table',
                'content_text': (
                    "Heads up - our inventory units are a total mess. The records show 152 units on Monday jumping to 100 on Sunday, while other sections are using kg. The labels are not standard, so you'll need to crack the code on what 'units' actually means here before you hit that order button."
                ),
                'content_json': {
                    'headers': ['Date', 'System "On Hand"', 'Unit label in system', 'Notes from backroom staff'],
                    'rows': [
                        ['Mon', '152', 'eggs', 'Floor count recorded as individual eggs (pieces).'],
                        ['Wed', '30', 'cartons', 'Backroom received a case of 30 cartons (12 eggs per carton).'],
                        ['Sat', '16', 'dozen', 'Weekend stocktake logged in dozens (1 dozen = 12 eggs).'],
                        ['Sun (today)', '100', 'units', 'Dashboard label is vague. In this store, "units" usually means cartons (not individual eggs).'],
                    ],
                    'footer_lines': [
                        'Standardization key (for the player to infer/apply): 1 carton = 12 eggs; 1 dozen = 12 eggs.',
                        'Checkpoint: If "100 units" = 100 cartons, that is 1,200 eggs on hand - far above the ~150 eggs/week baseline - so the correct decision is Do Not Place Order.',
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
                'target_text': 'Ready to lock it in? Should we pull the trigger on those 50 cartons?',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Place Order', 'Do Not Place Order'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_do_not_order',
                'condition_json': {'selected_value': 'Do Not Place Order'},
                'is_success': True,
                'message': (
                    'Spot on! You saw right through the unit mess and realized we were not actually running low. By standardizing those records, you made the smart call to hold off on the order. You just saved the store from a massive overstock headache and kept our purchasing costs right where they belong. Nice work!'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_order',
                'condition_json': {'selected_value': 'Place Order'},
                'is_success': False,
                'message': (
                    "Not quite! You jumped the gun and followed the manager's gut feeling before checking the math. It turns out that 100 in the system was not 100 eggs - it was 100 cartons! With 1,200 eggs actually in the back, we are way overstocked for the week. Next time, always clean up the units before you pull the trigger."
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
