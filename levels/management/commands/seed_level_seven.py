from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 7 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level7, created = Level.objects.get_or_create(
            level_code='level_7',
            defaults={
                'title': 'Multi-Platform Takeout Reconciliation Crisis',
                'description': 'Standardize raw takeout order data from Meituan and Ele.me, remove duplicate records, unify counting units, and reconcile the real profit or loss of the takeout business.',
                'objective_text': 'Clean the raw cross-platform takeout data, combine it with operating cost, and decide whether the takeout channel is actually profitable or loss-making.',
                'briefing_title': 'Takeout Reconciliation Desk',
                'briefing_text': 'The manager needs you to clean messy takeout order data and calculate the real operating result of the new delivery channels.',
                'briefing_hint': 'Remove duplicate orders, normalize every quantity into pieces, and compare the cleaned revenue with full channel cost.',
                'order': 7,
                'is_active': True,
            },
        )
        if not created:
            level7.title = 'Multi-Platform Takeout Reconciliation Crisis'
            level7.description = 'Standardize raw takeout order data from Meituan and Ele.me, remove duplicate records, unify counting units, and reconcile the real profit or loss of the takeout business.'
            level7.objective_text = 'Clean the raw cross-platform takeout data, combine it with operating cost, and decide whether the takeout channel is actually profitable or loss-making.'
            level7.briefing_title = 'Takeout Reconciliation Desk'
            level7.briefing_text = 'The manager needs you to clean messy takeout order data and calculate the real operating result of the new delivery channels.'
            level7.briefing_hint = 'Remove duplicate orders, normalize every quantity into pieces, and compare the cleaned revenue with full channel cost.'
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
                'category': resolved_categories['report'],
                'item_code': 'takeout_raw',
                'title': 'Raw Multi-Platform Takeout Orders',
                'content_type': 'table',
                'content_text': 'The raw order sheet mixes Meituan and Ele.me data. It contains 5 records, one duplicate order, and mixed units such as dozen, portion, and piece.',
                'content_json': {
                    'headers': ['Platform', 'Order ID', 'Item', 'Quantity', 'Unit', 'Revenue'],
                    'rows': [
                        ['Meituan', 'MT1001', 'Eggs', '1', 'Dozen', '$240'],
                        ['Meituan', 'MT1002', 'Eggs', '3', 'Portion', '$120'],
                        ['Ele.me', 'EM2001', 'Eggs', '10', 'Piece', '$200'],
                        ['Ele.me', 'EM2002', 'Eggs', '1', 'Dozen', '$240'],
                        ['Meituan', 'MT1002', 'Eggs', '3', 'Portion', '$120'],
                    ],
                    'duplicate_order_id': 'MT1002',
                },
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'unit_rule',
                'title': 'Takeout Unit Conversion Rule',
                'content_type': 'text',
                'content_text': 'Use a single unit for reconciliation: 1 dozen = 12 pieces, 1 portion = 2 pieces, and every order must be normalized into pieces before you calculate the result.',
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'takeout_cost',
                'title': 'Takeout Operating Cost Data',
                'content_type': 'table',
                'content_text': 'The takeout channel charges a 15% platform fee, packaging costs $2 per order, delivery subsidy costs $5 per order, and the monthly fixed operating cost is $3,000.',
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
                'sort_order': 3,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'takeout_guide',
                'title': 'Data Processing Guide',
                'content_type': 'text',
                'content_text': 'Step 1: remove the duplicate order row. Step 2: change every unit into piece. Once the cleaned dataset is consistent, the system will unlock the reconciliation decision.',
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
                'target_text': 'Complete the data cleanup, combine the cleaned orders with channel cost, and judge whether the takeout business is truly profitable or loss-making.',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Takeout Channel Profitable', 'Takeout Channel Loss-Making'],
                    'unit': 'USD',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_takeout_loss',
                'condition_json': {'selected_value': 'Takeout Channel Loss-Making'},
                'is_success': True,
                'message': 'Congratulations. You completed the cross-platform data cleanup, removed duplicate orders, unified the units, and correctly reconciled the real takeout result. The channel is loss-making, and you have earned the graduation certificate.',
                'score': 50,
                'next_action': 'certificate',
            },
            {
                'rule_name': 'fail_takeout_profit',
                'condition_json': {'selected_value': 'Takeout Channel Profitable'},
                'is_success': False,
                'message': 'Too bad. Your reconciliation missed the impact of duplicate orders, mixed units, and full channel cost. The takeout business is not profitable, and misjudging it would keep the supermarket trapped in a loss-making operation.',
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level7).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level7, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 7 seed data is ready.'))
