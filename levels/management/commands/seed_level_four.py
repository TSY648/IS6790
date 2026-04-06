from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 4 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level4, created = Level.objects.get_or_create(
            level_code='level_4',
            defaults={
                'title': 'The Chart Trap',
                'description': 'Cross-check a headline visual against the raw figures: confirm the real month-over-month change, sanity-check the scale and baseline choices, and make a budget recommendation that holds up outside a slide deck.',
                'objective_text': 'Validate the chart against the underlying numbers, compute the true month-over-month change, and recommend the next marketing budget level.',
                'briefing_title': 'The $10,000 Verdict',
                'briefing_text': 'The Store Manager is ready to increase the marketing budget after seeing a dramatic-looking revenue chart.',
                'briefing_hint': 'Before anyone touches the budget, check the raw numbers behind the graph and make sure the chart is not playing tricks on you.',
                'order': 4,
                'is_active': True,
            },
        )
        if not created:
            level4.title = 'The Chart Trap'
            level4.description = 'Cross-check a headline visual against the raw figures: confirm the real month-over-month change, sanity-check the scale and baseline choices, and make a budget recommendation that holds up outside a slide deck.'
            level4.objective_text = 'Validate the chart against the underlying numbers, compute the true month-over-month change, and recommend the next marketing budget level.'
            level4.briefing_title = 'The $10,000 Verdict'
            level4.briefing_text = 'The Store Manager is ready to increase the marketing budget after seeing a dramatic-looking revenue chart.'
            level4.briefing_hint = 'Before anyone touches the budget, check the raw numbers behind the graph and make sure the chart is not playing tricks on you.'
            level4.order = 4
            level4.is_active = True
            level4.save()

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
                    'The chart suggests revenue is trending up this month. I want to scale marketing next month.'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'chart_revenue',
                'title': 'Monthly Revenue Growth Trend',
                'content_type': 'image',
                'content_text': (
                    'Revenue moved from $82,000 to $83,000 this month. Because of how the chart is zoomed in, it looks like a massive upward climb. Do not let the steep angle fool you - look at the actual numbers on the side.'
                ),
                'content_json': {
                    'src': '/static/levels/level4/monthly-revenue-growth-trend.png',
                    'alt': 'Monthly revenue growth trend',
                },
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'raw_revenue',
                'title': 'Raw Revenue Data Table',
                'content_type': 'table',
                'content_text': (
                    "The hard numbers: revenue is $83,000, which is only $1,000 more than last month. That's a tiny 1.2% nudge, not the 'dramatic leap' the manager thinks he's seeing. It's basically business as usual."
                ),
                'content_json': {
                    'headers': ['Metric', 'Current Month Data', 'Analysis Notes'],
                    'rows': [
                        ['Total Marketing Spend', '$1,000', 'Budget for social ads & local flyers.'],
                        ['Total Revenue Growth', '$2,500', "Compared to last month's baseline."],
                        ['Total Store Traffic', '4,000 Shoppers', 'Total unique visitors this month.'],
                        ['Campaign Leads', '0.5% (20 Shoppers)', "Customers using the campaign's promo code."],
                    ],
                    'axis_fixer': {
                        'button_label': 'Show Full Scale (Start at $0)',
                        'reset_label': 'Back to Distorted View',
                        'before_src': '/static/levels/level4/monthly-revenue-growth-trend.png',
                        'after_src': '/static/levels/level4/monthly-revenue-growth-full-scale.svg',
                        'before_alt': 'Dual-axis distorted monthly revenue growth chart',
                        'after_alt': 'Full-scale monthly revenue growth chart starting at zero',
                        'success_text': 'Baseline reset applied. The dramatic jump flattens out once the chart starts at $0.',
                        'reset_text': 'Distorted view restored. The zoomed baseline makes the change look much bigger again.',
                    },
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'marketing_cost',
                'title': 'Marketing Budget and Revenue Relation Data',
                'content_type': 'table',
                'content_text': (
                    'Did marketing do this? We spent $5,000 on ads, but that $1,000 revenue bump was not even caused by the campaign. Most of our growth came from natural foot traffic. Doubling the budget here might just be throwing money away.'
                ),
                'content_json': {
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['Marketing Budget This Month', '$5,000'],
                        ['Revenue Increase', '$1,000'],
                        ['Primary Driver', 'Natural foot traffic'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level4).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level4,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level4,
            defaults={
                'title': 'Marketing Budget Decision',
                'target_text': "Decision time: does a $1,000 revenue bump justify doubling our spend? Now that you have spotted the misleading baseline, how should we play the next marketing move?",
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Double Budget', 'Maintain Budget', 'Reduce Budget'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_maintain_budget',
                'condition_json': {'selected_value': 'Maintain Budget'},
                'is_success': True,
                'message': (
                    'Nailed it! You did not let that steep chart angle fool you. By spotting the misleading baseline, you realized that a 1.2% nudge is not explosive growth - and definitely does not justify doubling the budget. By maintaining our current spend, you protected our profits and kept us from wasting cash on hype.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_double_budget',
                'condition_json': {'selected_value': 'Double Budget'},
                'is_success': False,
                'message': (
                    'Tough break - the chart got the best of you! That rocket-ship rise was actually a visual trick caused by a shifted baseline. You treated a tiny 1.2% bump like a massive breakthrough, and now we are doubling our costs for almost zero gain. Next time, always check the Y-axis before you open the wallet!'
                ),
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_reduce_budget',
                'condition_json': {'selected_value': 'Reduce Budget'},
                'is_success': False,
                'message': (
                    'A bit too cautious! While you were right not to fall for the massive jump, cutting the budget entirely was a step too far. We still have steady traffic coming in, and slashing the spend now could choke off our stable growth. The sweet spot was staying the course.'
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level4).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level4, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 4 seed data is ready.'))
