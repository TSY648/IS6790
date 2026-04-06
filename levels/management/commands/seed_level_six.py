from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 6 data for the supermarket decision game.'

    def handle(self, *args, **options):
        level6, created = Level.objects.get_or_create(
            level_code='level_6',
            defaults={
                'title': 'The Closing Time Crunch',
                'description': "Just because 10 people are loud does not mean the wider customer base agrees. In this level, you will test whether the complaint sample is skewed, then review a late-night pilot to estimate the real demand before making a permanent change.",
                'objective_text': 'Design the pilot, analyze the results (traffic, basket size, and incremental profit vs. extra costs), and make the final call: should we permanently extend closing time from 10 PM to midnight?',
                'briefing_title': 'The Closing Time Crunch',
                'briefing_text': 'The Store Manager wants to move closing time to midnight after a burst of customer complaints.',
                'briefing_hint': 'Do not let a loud sample make the decision. Check the broader evidence before changing store hours.',
                'order': 6,
                'is_active': True,
            },
        )
        if not created:
            level6.title = 'The Closing Time Crunch'
            level6.description = "Just because 10 people are loud does not mean the wider customer base agrees. In this level, you will test whether the complaint sample is skewed, then review a late-night pilot to estimate the real demand before making a permanent change."
            level6.objective_text = 'Design the pilot, analyze the results (traffic, basket size, and incremental profit vs. extra costs), and make the final call: should we permanently extend closing time from 10 PM to midnight?'
            level6.briefing_title = 'The Closing Time Crunch'
            level6.briefing_text = 'The Store Manager wants to move closing time to midnight after a burst of customer complaints.'
            level6.briefing_hint = 'Do not let a loud sample make the decision. Check the broader evidence before changing store hours.'
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
                    "I've been flooded with complaints-10 people say we close too early. If we push our closing time to midnight, we can keep customers happy and scoop up extra sales. It's a win-win, right?"
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
                'sort_order': 4,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'flow_heatmap',
                'title': 'Pilot report (10 PM-12 AM)',
                'content_type': 'table',
                'content_text': (
                    'We ran a 2-week trial with extended hours until midnight, using a simple stratified sample: 10 weeknights (Mon-Fri) and 4 weekend nights (Sat-Sun). This stratified approach ensures we capture both weekday and weekend behaviors, avoiding bias from any single day-type. Weeknight results were mixed, but weekends were strong. Overall, the late-night window delivered positive net profit after covering extra costs.'
                ),
                'content_json': {
                    'headers': ['Group (Stratum)', 'Avg customers (10 PM-12 AM)', 'Avg incremental gross profit', 'Avg incremental cost', 'Avg net profit'],
                    'rows': [
                        ['Weeknights (10 nights)', '8 / night', '$170', '$150', '+$20'],
                        ['Weekend nights (4 nights)', '22 / night', '$420', '$180', '+$240'],
                        ['<strong>Pilot weighted average</strong>', '<strong>12 / night</strong>', '<strong>$241</strong>', '<strong>$159</strong>', '<strong>+$82</strong>'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': resolved_categories['report'],
                'item_code': 'night_cost',
                'title': 'Cost Breakdown (10 PM-12 AM)',
                'content_type': 'table',
                'content_text': (
                    'This table shows the estimated extra operating costs for staying open two more hours each night.'
                ),
                'content_json': {
                    'headers': ['Cost item (10 PM-12 AM)', 'Assumption', 'Incremental cost'],
                    'rows': [
                        ['Staffing', '2 staff x 2 hours', '$110'],
                        ['Security', '1 guard x 2 hours', '$40'],
                        ['Utilities', 'Lights, refrigeration, cleaning', '$10'],
                        ['<strong>Total incremental cost</strong>', '<strong>Per night</strong>', '<strong>$160</strong>'],
                    ],
                },
                'is_key_item': True,
                'sort_order': 3,
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
                'title': 'Closing-Time Decision',
                'target_text': 'Decision Time: Based on the representative 2-week pilot (not just the 10 complaints), what should the store do about closing time?',
                'decision_type': 'single_choice',
                'config_json': {
                    'options': ['Extend Business Hours to Midnight', 'Do Not Extend Business Hours'],
                    'unit': '',
                },
            },
        )

        rules = [
            {
                'rule_name': 'success_extend',
                'condition_json': {'selected_value': 'Extend Business Hours to Midnight'},
                'is_success': True,
                'message': (
                    'Spot on! You did not let a tiny, self-selected set of complaints drive a costly decision. You designed a representative pilot (weeknights + weekends), then used the results to make a call that holds up. The data shows the 10 PM-12 AM window is net profitable on average - especially on weekends - so extending closing time to midnight is a smart move.'
                ),
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_do_not_extend',
                'condition_json': {'selected_value': 'Do Not Extend Business Hours'},
                'is_success': False,
                'message': (
                    "Not quite. Either you switched hours based only on a loud, skewed complaint sample, or you refused to extend hours even after the representative pilot showed positive net profit. In operations, anecdotes can mislead - but so can ignoring good evidence once you've collected it. The right move is to follow the pilot's representative results."
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
