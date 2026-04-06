from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 7 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level7, created = Level.objects.get_or_create(
            level_code='level_7',
            defaults={
                'title': 'The Delivery Disaster',
                'description': "It's time for a 'Deep Clean.' High volume doesn't always mean high profit-especially when the data is double-counted and the units are mismatched. Your goal is to standardize the chaos, strip out the noise, and find the actual bottom line.",
                'objective_text': 'Standardize the raw platform feeds, delete the duplicates, and unify the measurement units to calculate the true Profit vs. Loss.',
                'briefing_title': 'The Delivery Disaster',
                'briefing_text': 'Delivery app A and Delivery app B are live, but finance says the order data is a mess and no one knows whether the channel is really making money.',
                'briefing_hint': 'Before you trust the order volume, clean the feed, normalize the units, and reconcile the real costs.',
                'order': 7,
                'is_active': True,
            },
        )
        if not created:
            level7.title = 'The Delivery Disaster'
            level7.description = "It's time for a 'Deep Clean.' High volume doesn't always mean high profit-especially when the data is double-counted and the units are mismatched. Your goal is to standardize the chaos, strip out the noise, and find the actual bottom line."
            level7.objective_text = 'Standardize the raw platform feeds, delete the duplicates, and unify the measurement units to calculate the true Profit vs. Loss.'
            level7.briefing_title = 'The Delivery Disaster'
            level7.briefing_text = 'Delivery app A and Delivery app B are live, but finance says the order data is a mess and no one knows whether the channel is really making money.'
            level7.briefing_hint = 'Before you trust the order volume, clean the feed, normalize the units, and reconcile the real costs.'
            level7.order = 7
            level7.is_active = True
            level7.save()

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
                    'The delivery tablets are buzzing non-stop! Between Delivery app A and Delivery app B, we are moving massive volume. Finance is stressed about the messy spreadsheets, but I say orders are orders - as long as the bags are going out the door, we are winning. Let us keep the momentum going!'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'takeout_raw',
                'title': 'Raw Multi-Platform Takeout Orders',
                'content_type': 'table',
                'content_text': "Digital Feed Audit: This is a total mess. We've got Meituan and Ele.me data bleeding into one sheet, duplicate IDs popping up, and units all over the place-dozens, portions, pieces... it's impossible to see our real sales volume in this state.",
                'content_json': {
                    'headers': ['Platform', 'Order ID', 'Timestamp', 'Item', 'Qty', 'Unit', 'Unit Price'],
                    'rows': [
                        ['Delivery app A', 'A-009871', '2026-03-28 18:42', 'Eggs', '1', 'dozen', '$4.80'],
                        ['Delivery app B', 'B-120044', '2026/03/28 18:44', 'Egg (grade A)', '12', 'pcs', '$0.40'],
                        ['Delivery app A', 'A-009872', '2026-03-28 19:03', 'Chicken wings', '2', 'portion', '$6.50'],
                        ['Delivery app B', 'B-120051', '2026/03/28 19:04', 'Wings', '4', 'pcs', '$1.62'],
                        ['Delivery app A', 'A-009873', '2026-03-28 19:20', 'Strawberries', '0.5', 'kg', '$7.00'],
                        ['Delivery app B', 'B-120066', '2026/03/28 19:21', 'Strawberries', '500', 'g', '$0.014'],
                        ['Delivery app A', 'A-009875', '2026-03-28 19:55', 'Eggs', '12', 'pcs', '$0.40'],
                        ['Delivery app A', 'A-009876', '2026-03-28 20:10', 'Eggs', '1', 'doz', '$4.80'],
                        ['Delivery app B', 'B-120090', '2026/03/28 20:11', 'Eggs', '1', 'dozen', '$4.80'],
                        ['Delivery app A', 'A-009877', '2026-03-28 20:40', 'Chicken wings', '2', 'PORTION', '$6.50'],
                        ['Delivery app B', 'B-120103', '2026/03/28 20:58', 'Eggs', '0', 'pcs', '$0.40'],
                        ['Delivery app A', 'A-009879', '2026-03-28 21:05', 'Chicken wings', '1', 'portion', '$6.50'],
                        ['Delivery app B', 'B-120103', '2026/03/28 20:58', 'Eggs', '0', 'pcs', '$0.40'],
                    ],
                    'duplicate_order_id': 'B-120103',
                },
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'unit_rule',
                'title': 'Data Processing Guide',
                'content_type': 'text',
                'content_text': "Cleanup Protocol: We can't trust the math until the data is clean. Step 1: Scrub the duplicate rows. Step 2: Normalize every unit into 'pieces' (1 dozen = 12, 1 portion = 2). Once the sheet is standardized, the real profit story will finally reveal itself.",
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'takeout_cost',
                'title': 'Takeout Operating Cost Data',
                'content_type': 'table',
                'content_text': "The Real Margin: Every order carries a 15% platform fee, plus $2 for packaging and a $5 delivery subsidy. Add in our $3,000 monthly fixed overhead, and we're burning cash fast. Unless our 'cleaned' order count is high enough, we're essentially paying for the privilege of delivering food.",
                'content_json': {
                    'headers': ['Cost Item', 'Value'],
                    'rows': [
                        ['Platform Fee', '15%'],
                        ['Packaging Cost', '$2 per order'],
                        ['Delivery Subsidy', '$5 per order'],
                        ['Monthly Fixed Operating Cost', '$3,000'],
                        ['Exercise Reconciliation Result', 'Cleaned revenue $800, monthly net loss $1,200'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level7).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level7,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level7,
            defaults={
                'title': 'Takeout Reconciliation Decision',
                'target_text': 'After cleaning the data and reconciling the costs, what is the real story of the delivery channel?',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Delivery Channel is Profitable', 'Delivery Channel is in Loss'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_takeout_loss',
                'condition_json': {'selected_value': 'Delivery Channel is in Loss'},
                'is_success': True,
                'message': "Absolute Legend! You scrubbed the data, deleted the 'ghost' orders, and finally made the units match. By cutting through the noise, you saw what the manager missed: this delivery channel is burning cash, not making it. You've officially reconciled the truth and earned your Graduation Certificate. The store is safe in your hands!",
                'score': 50,
                'next_action': 'certificate',
            },
            {
                'rule_name': 'fail_takeout_profit',
                'condition_json': {'selected_value': 'Delivery Channel is Profitable'},
                'is_success': False,
                'message': "Ouch-you got caught in the 'Volume Trap.' By missing those duplicate orders and mismatched units, the numbers looked better than they actually were. This operation is deep in the red, and keeping it open is just lighting money on fire. Remember: high volume is meaningless if the data behind it is a mess!",
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level7).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level7, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 7 seed data is ready.'))
