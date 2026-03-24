from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 5 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level5, created = Level.objects.get_or_create(
            level_code='level_5',
            defaults={
                'title': 'Supplier Choice Conflict Crisis',
                'description': "Identify Simpson's paradox in supplier selection, compare overall supplier profit with category-level profit, and choose the supplier that best fits the supermarket's fresh-produce mix.",
                'objective_text': "Analyze both suppliers' total profit and detailed category profit, match them to the store's fresh-produce structure, and choose the supplier that produces the best real profit outcome.",
                'briefing_title': 'Supplier Selection Review Desk',
                'briefing_text': 'The current core fresh-produce supplier contract is expiring, and the store manager wants your support in choosing the next supplier.',
                'briefing_hint': "Do not trust the higher overall margin alone. Compare subgroup profit with the store's actual category mix.",
                'order': 5,
                'is_active': True,
            },
        )
        if not created:
            level5.title = 'Supplier Choice Conflict Crisis'
            level5.description = "Identify Simpson's paradox in supplier selection, compare overall supplier profit with category-level profit, and choose the supplier that best fits the supermarket's fresh-produce mix."
            level5.objective_text = "Analyze both suppliers' total profit and detailed category profit, match them to the store's fresh-produce structure, and choose the supplier that produces the best real profit outcome."
            level5.briefing_title = 'Supplier Selection Review Desk'
            level5.briefing_text = 'The current core fresh-produce supplier contract is expiring, and the store manager wants your support in choosing the next supplier.'
            level5.briefing_hint = "Do not trust the higher overall margin alone. Compare subgroup profit with the store's actual category mix."
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
                    '"Supplier A has a total profit margin of 15%, while Supplier B is only at 12%. Let us just choose Supplier A and help the store make more money."'
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
                    'Supplier A shows an overall profit margin of 15%, while Supplier B shows 12%. Looking only at the total number makes A appear better.'
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
                'item_code': 'supplier_detail',
                'title': 'Supplier Category-Level Profit Data',
                'content_type': 'table',
                'content_text': (
                    'At the category level, Supplier B performs much better in high-margin fresh categories, while Supplier A performs better only in low-margin categories.'
                ),
                'content_json': {
                    'headers': ['Supplier', 'High-Margin Categories', 'Low-Margin Categories'],
                    'rows': [
                        ['Supplier A', '8%', '25%'],
                        ['Supplier B', '20%', '5%'],
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
                    "The supermarket's fresh-produce mix is dominated by high-margin categories, which account for 80% of the business, while low-margin categories account for only 20%."
                ),
                'content_json': {
                    'headers': ['Category Mix', 'Store Share'],
                    'rows': [
                        ['High-Margin Fresh Categories', '80%'],
                        ['Low-Margin Fresh Categories', '20%'],
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
                'target_text': "Recognize Simpson's paradox, combine the supplier data with the store's actual category mix, and choose the supplier that produces the better real profit outcome.",
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Choose Supplier A', 'Choose Supplier B'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_choose_b',
                'condition_json': {'selected_value': 'Choose Supplier B'},
                'is_success': True,
                'message': (
                    "Congratulations. You recognized Simpson's paradox in the supplier comparison and were not misled by the overall profit figure alone. Because the supermarket is dominated by high-margin categories, Supplier B delivers the better real profit outcome."
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_choose_a',
                'condition_json': {'selected_value': 'Choose Supplier A'},
                'is_success': False,
                'message': (
                    "Too bad. You followed the higher overall profit figure and missed the category-level structure. Since 80% of the store's fresh produce is high-margin, choosing Supplier A would lower real profit significantly."
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
