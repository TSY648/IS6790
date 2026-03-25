from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 3 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level3, created = Level.objects.get_or_create(
            level_code='level_3',
            defaults={
                'title': 'Promotion Effect Misjudgment Crisis',
                'description': 'Identify the survivorship bias in fresh-produce promotions, where partial hot-sales feedback hides the overall profit loss, then judge the real promotion effect and decide whether the campaign should continue.',
                'objective_text': 'Analyze the full promotion dataset, judge the real campaign result, and decide whether the promotion should continue or stop.',
                'briefing_title': 'Promotion Performance Review Desk',
                'briefing_text': 'Weekend sales in fresh produce rose sharply during the buy-one-get-one campaign, and the store manager wants to keep the same promotion going.',
                'briefing_hint': 'Do not confuse strong reviews and sales growth with a healthy campaign result. Check the profit outcome before deciding.',
                'order': 3,
                'is_active': True,
            },
        )
        if not created:
            level3.title = 'Promotion Effect Misjudgment Crisis'
            level3.description = 'Identify the survivorship bias in fresh-produce promotions, where partial hot-sales feedback hides the overall profit loss, then judge the real promotion effect and decide whether the campaign should continue.'
            level3.objective_text = 'Analyze the full promotion dataset, judge the real campaign result, and decide whether the promotion should continue or stop.'
            level3.briefing_title = 'Promotion Performance Review Desk'
            level3.briefing_text = 'Weekend sales in fresh produce rose sharply during the buy-one-get-one campaign, and the store manager wants to keep the same promotion going.'
            level3.briefing_hint = 'Do not confuse strong reviews and sales growth with a healthy campaign result. Check the profit outcome before deciding.'
            level3.order = 3
            level3.is_active = True
            level3.save()

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
                    '"The weekend promotion exploded. We received a lot of positive reviews, and sales looked great. Let us continue the same buy-one-get-one promotion this week too."'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'promo_feedback',
                'title': 'Promotion Customer Reviews',
                'content_type': 'text',
                'content_text': (
                    'The campaign received more than 20 positive reviews over the weekend. Customers praised the low prices, freshness, and value, and some comments said they would buy again.'
                ),
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'promo_sales',
                'title': 'Promotion Gross Sales Data',
                'content_type': 'table',
                'content_text': (
                    'Weekend fresh-produce gross sales rose 40% compared with a normal weekday baseline, but most of the growth came from low-margin traffic-driving items. Higher sales volume does not automatically mean higher profit.'
                ),
                'content_json': {
                    'headers': ['Metric', 'Before Promotion', 'During Promotion', 'Change'],
                    'rows': [
                        ['Fresh Produce Gross Sales', '$10,000', '$14,000', '+40%'],
                        ['Low-Margin Traffic Items Share', '35%', '68%', '+33 pts'],
                    ],
                    'src': '/static/levels/level3/promotion-gross-sales-trend.svg',
                    'alt': 'Daily sales trend of fresh products last week',
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'promo_profit',
                'title': 'Promotion Gross Profit Data',
                'content_type': 'table',
                'content_text': (
                    'During the promotion, overall fresh-produce gross margin fell to 35%. After subtracting promotional subsidy and labor cost, the category lost $500 overall.'
                ),
                'content_json': {
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['Gross Margin During Promotion', '35%'],
                        ['Promotional Subsidy', '$300'],
                        ['Extra Labor Cost', '$200'],
                        ['Net Profit Impact', '-$500'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level3).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level3,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level3,
            defaults={
                'title': 'Fresh Produce Promotion Decision',
                'target_text': 'Identify the survivorship bias in the promotion evidence, judge the real campaign outcome, and decide whether the promotion should continue.',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Continue Promotion', 'Stop Promotion'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_stop_promotion',
                'condition_json': {'selected_value': 'Stop Promotion'},
                'is_success': True,
                'message': (
                    'Congratulations. You recognized the survivorship bias in the promotion evidence and were not misled by partial feedback. The promotion increased gross sales, but real profit fell, so stopping it prevents further losses.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_continue_promotion',
                'condition_json': {'selected_value': 'Continue Promotion'},
                'is_success': False,
                'message': (
                    "Too bad. You were misled by the survivorship bias in the store manager's feedback, ignored the total profit loss caused by the campaign, and chose to continue a promotion that would keep expanding the loss."
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level3).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level3, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 3 seed data is ready.'))
