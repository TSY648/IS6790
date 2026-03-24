from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 6 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level6, created = Level.objects.get_or_create(
            level_code='level_6',
            defaults={
                'title': 'Late-Night Sampling Crisis',
                'description': 'Identify the survivorship bias created by late-night complaint samples, judge whether the sample represents the full customer-flow picture, and decide whether to extend operating hours.',
                'objective_text': 'Analyze customer flow, complaint representativeness, and operating cost to decide whether the supermarket should extend business hours.',
                'briefing_title': 'Late-Night Operations Review Desk',
                'briefing_text': 'The manager wants to extend the store schedule from 10 PM to midnight after receiving several late-night customer complaints.',
                'briefing_hint': 'Do not trust the complaint sample alone. Compare it with full-day traffic and late-night operating cost first.',
                'order': 6,
                'is_active': True,
            },
        )
        if not created:
            level6.title = 'Late-Night Sampling Crisis'
            level6.description = 'Identify the survivorship bias created by late-night complaint samples, judge whether the sample represents the full customer-flow picture, and decide whether to extend operating hours.'
            level6.objective_text = 'Analyze customer flow, complaint representativeness, and operating cost to decide whether the supermarket should extend business hours.'
            level6.briefing_title = 'Late-Night Operations Review Desk'
            level6.briefing_text = 'The manager wants to extend the store schedule from 10 PM to midnight after receiving several late-night customer complaints.'
            level6.briefing_hint = 'Do not trust the complaint sample alone. Compare it with full-day traffic and late-night operating cost first.'
            level6.order = 6
            level6.is_active = True
            level6.save()

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
                    '"Many customers are complaining that we close too early. If we extend our hours to midnight, we can keep them and earn more night sales."'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'night_complain',
                'title': 'Late-Night Customer Complaints',
                'content_type': 'text',
                'content_text': (
                    'The store recently received 10 late-night complaints, all saying that closing at 10 PM is too early and asking for extended hours.'
                ),
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'flow_heatmap',
                'title': 'Full-Day Customer Flow Heatmap',
                'content_type': 'chart',
                'content_text': (
                    'Customer traffic is dense before 8 PM, drops sharply after 8 PM, and averages fewer than 5 customers per hour from 10 PM to midnight.'
                ),
                'content_json': {
                    'x': ['8:00-12:00', '12:00-16:00', '16:00-20:00', '20:00-22:00', '22:00-24:00'],
                    'y': [36, 48, 62, 18, 4],
                    'x_label': 'Time Period',
                    'y_label': 'Average Customers per Hour',
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'night_cost',
                'title': 'Extended-Hours Cost Data',
                'content_type': 'table',
                'content_text': (
                    'Extending operations by 2 hours raises labor, security, and utility cost by about $200 per day, while expected late-night profit is under $50 per day.'
                ),
                'content_json': {
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['Extra Operating Time', '2 hours'],
                        ['Extra Daily Cost', '$200'],
                        ['Expected Late-Night Profit', '< $50 per day'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'store_hour',
                'title': 'Current Store Operating Hours',
                'content_type': 'text',
                'content_text': 'The supermarket currently operates from 8:00 AM to 10:00 PM.',
                'is_key_item': True,
                'sort_order': 5,
            },
        ]

        active_item_codes = [item['item_code'] for item in items]
        LevelItem.objects.filter(level=level6).exclude(item_code__in=active_item_codes).delete()

        for item in items:
            LevelItem.objects.update_or_create(
                level=level6,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level6,
            defaults={
                'title': 'Supermarket Operating-Hours Decision',
                'target_text': 'Judge whether the complaint sample is representative, compare full customer flow with operating cost, and decide whether the supermarket should extend its hours.',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Extend Operating Hours', 'Do Not Extend Operating Hours'],
                    'unit': 'hours',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_do_not_extend',
                'condition_json': {'selected_value': 'Do Not Extend Operating Hours'},
                'is_success': True,
                'message': (
                    'Congratulations. You recognized that the late-night complaints were a biased sample, checked the full-day traffic pattern, and found that late-night demand is too weak to cover the extra labor and utility cost. Not extending hours avoids unnecessary waste.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_extend',
                'condition_json': {'selected_value': 'Extend Operating Hours'},
                'is_success': False,
                'message': (
                    'Too bad. You treated the late-night complaint sample as if it represented the whole customer base and ignored the real traffic pattern. Customer flow after 10 PM is too low, so extending hours would create a daily loss.'
                ),
                'score': 0,
                'next_action': 'restart',
            },
        ]

        active_rule_names = [rule['rule_name'] for rule in rules]
        ResultRule.objects.filter(level=level6).exclude(rule_name__in=active_rule_names).delete()

        for rule in rules:
            ResultRule.objects.update_or_create(level=level6, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 6 seed data is ready.'))
