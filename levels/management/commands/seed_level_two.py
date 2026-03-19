from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 2 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level2, created = Level.objects.get_or_create(
            level_code='level_2',
            defaults={
                'title': 'Holiday Promotion Settlement',
                'description': 'Test whether the old promotion evidence really supports the new holiday audience before copying the plan.',
                'objective_text': 'Check who the survey represents, separate traffic context from promotion effect, and choose the holiday plan that actually fits evening office workers.',
                'briefing_title': 'Promotion Review Desk',
                'briefing_text': 'Marketing wants to reuse a high-scoring daytime promotion for the holiday evening crowd without changing the strategy.',
                'briefing_hint': 'Look for two traps: a biased survey sample and a sales spike that may be explained by context instead of the promotion itself.',
                'order': 2,
                'is_active': True,
            },
        )
        if not created:
            level2.title = 'Holiday Promotion Settlement'
            level2.description = 'Test whether the old promotion evidence really supports the new holiday audience before copying the plan.'
            level2.objective_text = 'Check who the survey represents, separate traffic context from promotion effect, and choose the holiday plan that actually fits evening office workers.'
            level2.briefing_title = 'Promotion Review Desk'
            level2.briefing_text = 'Marketing wants to reuse a high-scoring daytime promotion for the holiday evening crowd without changing the strategy.'
            level2.briefing_hint = 'Look for two traps: a biased survey sample and a sales spike that may be explained by context instead of the promotion itself.'
            level2.order = 2
            level2.is_active = True
            level2.save()

        categories = {
            'npc': 'NPC',
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
                'item_code': 'npc_marketing_manager',
                'title': 'Marketing Manager',
                'content_type': 'text',
                'content_text': (
                    'The daytime holiday promotion scored 95% satisfaction, and sales jumped on the rainy campaign '
                    'days. Let us copy it for the evening office crowd and move on.'
                ),
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': resolved_categories['npc'],
                'item_code': 'npc_evening_supervisor',
                'title': 'Evening Shift Supervisor',
                'content_type': 'text',
                'content_text': (
                    'Our evening office workers shop quickly after work. They react better to grab-and-go bundles '
                    'than to the daytime signage used for retirees.'
                ),
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'promotion_satisfaction_summary',
                'title': 'Promotion Satisfaction Summary',
                'content_type': 'table',
                'content_text': (
                    'The headline satisfaction score is strong, but the audience mix behind it is not balanced.'
                ),
                'content_json': {
                    'headers': ['Audience Group', 'Satisfaction', 'Sample Share'],
                    'rows': [
                        ['Daytime seniors', '95%', '58%'],
                        ['Mixed daytime adults', '68%', '30%'],
                        ['Evening office workers', '42%', '12%'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'survey_sampling_sheet',
                'title': 'Survey Sampling Sheet',
                'content_type': 'table',
                'content_text': (
                    'Most of the feedback came from daytime shoppers, so the survey is not representative of the new '
                    'holiday target group.'
                ),
                'content_json': {
                    'headers': ['Collection Window', 'Location', 'Primary Respondents'],
                    'rows': [
                        ['10:00-12:00', 'Front produce aisle', 'Retirees and morning shoppers'],
                        ['12:00-16:00', 'Coupon desk', 'Nearby daytime visitors'],
                        ['17:00-21:00', 'After-work entrance', 'Very limited responses'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 4,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'rain_day_sales_pattern',
                'title': 'Rain-Day Sales Pattern',
                'content_type': 'table',
                'content_text': (
                    'Sales were highest on the rainiest days, but that does not automatically prove the old promotion '
                    'caused the increase.'
                ),
                'content_json': {
                    'headers': ['Day', 'Rainfall', 'Mall Footfall', 'Promotion Sales'],
                    'rows': [
                        ['Thursday', 'Low', 'Normal', '86'],
                        ['Friday', 'High', 'Very high', '128'],
                        ['Saturday', 'High', 'Very high', '134'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 5,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'survey_details',
                'title': 'Survey Demographic Note',
                'content_type': 'text',
                'content_text': (
                    'The satisfaction team collected responses mostly from shoppers above 50 during daytime hours. '
                    'That sample cannot stand in for after-work office workers.'
                ),
                'is_key_item': True,
                'sort_order': 6,
            },
            {
                'category': resolved_categories['external'],
                'item_code': 'traffic_context_note',
                'title': 'Transit and Weather Context Note',
                'content_type': 'text',
                'content_text': (
                    'On the two rainiest campaign days, a subway exit repair pushed office workers through the mall '
                    'connector. The traffic spike happened at the same time as the promotion, so the promotion alone '
                    'cannot explain the sales jump.'
                ),
                'is_key_item': True,
                'sort_order': 7,
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
                'title': 'Holiday Promotion Decision',
                'target_text': 'Choose the holiday promotion plan that fits the evening office-worker audience without over-reading the old campaign data.',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': [
                        'Reuse the daytime senior promotion because the 95% score proves it works for everyone',
                        'Build a commuter-friendly evening combo and treat the rain-day spike as context, not proof the old plan always works',
                        'Expand the rainy-day giveaway because higher rainfall and higher sales clearly mean the promotion gets stronger in bad weather',
                    ],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_evening_combo',
                'condition_json': {'selected_value': 'Build a commuter-friendly evening combo and treat the rain-day spike as context, not proof the old plan always works'},
                'is_success': True,
                'message': (
                    'Excellent call. You caught both traps: the survey sample did not represent evening office workers, '
                    'and the rain-day sales spike was confounded by unusual commuter traffic.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_copy_daytime',
                'condition_json': {'selected_value': 'Reuse the daytime senior promotion because the 95% score proves it works for everyone'},
                'is_success': False,
                'message': (
                    'That decision trusts a biased sample. High satisfaction from daytime retirees does not prove the '
                    'same promotion fits evening office workers.'
                ),
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_spurious_weather',
                'condition_json': {'selected_value': 'Expand the rainy-day giveaway because higher rainfall and higher sales clearly mean the promotion gets stronger in bad weather'},
                'is_success': False,
                'message': (
                    'That reads correlation as causation. Rainy campaign days also came with unusual commuter traffic, '
                    'so you cannot treat the old promotion as the sole driver of the sales spike.'
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
