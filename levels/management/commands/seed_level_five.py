from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 5 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level5, created = Level.objects.get_or_create(
            level_code='level_5',
            defaults={
                'title': 'The Contract Conflict',
                'description': "It is decision time on our core produce contract. On paper, this looks like a straightforward choice, but the best overall deal might not be the best deal for our specific shelves. Your mission is to audit the category performance for both candidates and align their pricing strengths with our actual inventory mix.",
                'objective_text': "Analyze the margin breakdown, match it to the store's sales structure, and pick the partner that maximizes our real-world profit.",
                'briefing_title': 'The Contract Conflict',
                'briefing_text': 'Procurement needs a supplier decision today, and the Store Manager is ready to choose based on the summary line.',
                'briefing_hint': 'Do not let the headline average make the call for you. Check which supplier actually wins in the categories that matter most here.',
                'order': 5,
                'is_active': True,
            },
        )
        if not created:
            level5.title = 'The Contract Conflict'
            level5.description = "It is decision time on our core produce contract. On paper, this looks like a straightforward choice, but the best overall deal might not be the best deal for our specific shelves. Your mission is to audit the category performance for both candidates and align their pricing strengths with our actual inventory mix."
            level5.objective_text = "Analyze the margin breakdown, match it to the store's sales structure, and pick the partner that maximizes our real-world profit."
            level5.briefing_title = 'The Contract Conflict'
            level5.briefing_text = 'Procurement needs a supplier decision today, and the Store Manager is ready to choose based on the summary line.'
            level5.briefing_hint = 'Do not let the headline average make the call for you. Check which supplier actually wins in the categories that matter most here.'
            level5.order = 5
            level5.is_active = True
            level5.save()

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
                    'Supplier A is offering a 15% total margin across the board, while Supplier B is trailing at 12%. Let us sign with A and start padding the store bottom line immediately.'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'supplier_total',
                'title': 'Supplier Overall Profit Data',
                'content_type': 'table',
                'content_text': (
                    'Supplier A currently holds a 3% lead in total average margin compared to Supplier B. If we only look at the big-picture totals, Supplier A appears to be the more profitable partner for the year ahead.'
                ),
                'content_json': {
                    'headers': ['Supplier', 'Overall Profit Margin'],
                    'rows': [
                        ['Supplier A', '15%'],
                        ['Supplier B', '12%'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'supplier_margin_breakdown',
                'title': 'Supplier Category-Level Margin Breakdown',
                'content_type': 'table',
                'content_text': (
                    "This table shows each supplier's profit margin by produce category, alongside how much each category contributes to our store's total sales. To understand the real profit impact, consider not just which margin is higher, but where those margins apply in our actual sales mix."
                ),
                'content_json': {
                    'headers': ['Category', 'Product', 'Share of Store Sales', 'Supplier A Margin', 'Supplier B Margin'],
                    'rows': [
                        ['Fresh', 'Vegetables', '18%', '10%', '16%'],
                        ['Fresh', 'Meat & Poultry', '14%', '11%', '15%'],
                        ['Fresh', 'Seafood', '12%', '12%', '17%'],
                        ['Fresh', 'Fruits', '10%', '13%', '18%'],
                        ['Food', 'Ready-to-Cook & Instant Meals', '8%', '14%', '16%'],
                        ['Food', 'Rice, Grains & Cooking Oil', '10%', '20%', '6%'],
                        ['Food', 'Dairy Products', '8%', '18%', '7%'],
                        ['Daily Essentials', 'Personal & Home Care', '7%', '17%', '8%'],
                        ['Daily Essentials', 'Paper Goods & Tissues', '7%', '15%', '7%'],
                        ['Daily Essentials', 'Kitchen Supplies', '6%', '16%', '6%'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'store_category',
                'title': 'Store Fresh-Produce Category Structure',
                'content_type': 'table',
                'content_text': (
                    "Our store's revenue is concentrated in a small number of high-volume, high-value fresh categories. Any supplier advantage in these categories will have a disproportionate impact on total profit."
                ),
                'content_json': {
                    'headers': ['Category Group', 'Share of Store Sales'],
                    'rows': [
                        ['Top-Selling Fresh Categories', '80%'],
                        ['Remaining Categories', '20%'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level5).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level5,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level5,
            defaults={
                'title': 'Fresh Produce Supplier Decision',
                'target_text': "Final verdict: it is time to sign the contract. Which supplier should the store choose?",
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Select Supplier A', 'Select Supplier B'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_choose_b',
                'condition_json': {'selected_value': 'Select Supplier B'},
                'is_success': True,
                'message': (
                    "Absolute legend! You did not let the 15% Total Margin headline distract you. By drilling into the category data, you spotted that Supplier B actually outperforms in the high-impact categories that make up 80% of our business. You just navigated Simpson's Paradox like a pro and chose the supplier that maximizes real profit - not just the average on paper. The store's bottom line will thank you."
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_choose_a',
                'condition_json': {'selected_value': 'Select Supplier A'},
                'is_success': False,
                'message': (
                    "Ouch - you got caught in the average trap. While Supplier A had a higher total margin on paper, they actually underperformed in the high-margin categories where we do 80% of our business. By picking the bigger average instead of the better fit, we are actually going to see a profit drop this year."
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level5).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level5, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 5 seed data is ready.'))
