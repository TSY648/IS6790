from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 3 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level3, created = Level.objects.get_or_create(
            level_code='level_3',
            defaults={
                'title': 'The Promotion Trap',
                'description': 'The store feels busy and customers are happy. Before we extend anything, pressure-test the results: did the promo create profitable demand or just expensive activity?',
                'objective_text': 'Tally up the real costs, weigh the sales against the margins, and make the call: is it time to keep the promo going, or pull the plug before we go broke?',
                'briefing_title': 'Buy One Get One',
                'briefing_text': 'Weekend produce sales were loud, busy, and full of glowing reviews. The Store Manager wants to extend the BOGO deal right away.',
                'briefing_hint': 'Do not let five-star reviews make the decision for you. Check the full P&L before you greenlight anything.',
                'order': 3,
                'is_active': True,
            },
        )
        if not created:
            level3.title = 'The Promotion Trap'
            level3.description = 'The store feels busy and customers are happy. Before we extend anything, pressure-test the results: did the promo create profitable demand or just expensive activity?'
            level3.objective_text = 'Tally up the real costs, weigh the sales against the margins, and make the call: is it time to keep the promo going, or pull the plug before we go broke?'
            level3.briefing_title = 'Buy One Get One'
            level3.briefing_text = 'Weekend produce sales were loud, busy, and full of glowing reviews. The Store Manager wants to extend the BOGO deal right away.'
            level3.briefing_hint = 'Do not let five-star reviews make the decision for you. Check the full P&L before you greenlight anything.'
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
                    'The weekend promo was a total explosion! We got buried in 5-star reviews and the sales numbers looked incredible. There is no reason to stop now - let us run the same BOGO deal again this week!'
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
                    'Social Buzz: the campaign was a hit with the crowd, racking up over 20 glowing reviews over the weekend. Customers are loving the freebies - but can we afford to keep them happy at this price?'
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
                    'Check the volume: produce sales jumped 40% over our normal baseline. But keep your eyes peeled - most of that growth was in low-margin loss leaders. Remember, moving more boxes does not always mean moving more money.'
                ),
                'content_json': {
                    'headers': ['Metric', 'Before Promotion', 'During Promotion', 'Change'],
                    'rows': [
                        ['Fresh Produce Gross Sales', '$10,000', '$14,000', '+4,000'],
                        ['Low-Margin Traffic Items Share', '35%', '68%', '+33%'],
                    ],
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
                    'The bottom line: our overall margin tanked to 35% during the promo. Once you factor in the cost of the freebies and the extra labour, the department actually lost $500. This win is costing us serious cash.'
                ),
                'content_json': {
                    'table_title': 'Promotion Profit Table (Weekend P&L View)',
                    'headers': ['Line item', 'Baseline weekend', 'Promo weekend (BOGO)', 'Change'],
                    'rows': [
                        ['Gross sales (revenue)', '$10,000', '$13,800', '+$3,800'],
                        ['COGS (paid product cost)', '($6,000)', '($8,970)', '($2,970)'],
                        ['<strong>Gross profit (before promo costs)</strong>', '<strong>$4,000 (40%)</strong>', '<strong>$4,830 (35%)</strong>', '<strong>+$830</strong>'],
                        ['Less: BOGO “free item” cost (giveaway COGS)', '$0', '($2,550)', '($2,550)'],
                        ['Less: incremental labour / handling', '$0', '($2,780)', '($2,780)'],
                        ['<strong>Net profit (after promo costs)</strong>', '<strong>$4,000</strong>', '<strong>($500)</strong>', '<strong>($4,500)</strong>'],
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
                'title': 'Promotion Decision',
                'target_text': 'After reviewing the promo results end-to-end, what is the recommendation for next week?',
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
                    "Major win! You did not let those shiny 5-star reviews distract you from the bottom line. You spotted the survivorship bias and realized that while the sales looked huge, the profits were actually taking a hit. By pulling the plug on the promo, you just saved the store from a massive budget leak. Great eye!"
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_continue_promotion',
                'condition_json': {'selected_value': 'Continue Promotion'},
                'is_success': False,
                'message': (
                    "Tough break. You got caught up in the hype! By following the manager's lead and those happy customer reviews, you missed the real story: this campaign was actually draining our cash. It turns out that survivorship bias is tricky - if you only look at the happy fans, you miss the total loss on the balance sheet."
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
