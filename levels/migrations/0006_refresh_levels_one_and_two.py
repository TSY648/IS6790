from django.db import migrations


def upsert_level(apps, level_data):
    Level = apps.get_model('levels', 'Level')
    InfoCategory = apps.get_model('levels', 'InfoCategory')
    LevelItem = apps.get_model('levels', 'LevelItem')
    DecisionConfig = apps.get_model('levels', 'DecisionConfig')
    ResultRule = apps.get_model('levels', 'ResultRule')

    level, created = Level.objects.get_or_create(
        level_code=level_data['level_code'],
        defaults={
            'title': level_data['title'],
            'description': level_data['description'],
            'objective_text': level_data['objective_text'],
            'briefing_title': level_data['briefing_title'],
            'briefing_text': level_data['briefing_text'],
            'briefing_hint': level_data['briefing_hint'],
            'order': level_data['order'],
            'is_active': True,
        },
    )

    if not created:
        level.title = level_data['title']
        level.description = level_data['description']
        level.objective_text = level_data['objective_text']
        level.briefing_title = level_data['briefing_title']
        level.briefing_text = level_data['briefing_text']
        level.briefing_hint = level_data['briefing_hint']
        level.order = level_data['order']
        level.is_active = True
        level.save()

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

    active_item_codes = [item['item_code'] for item in level_data['items']]
    LevelItem.objects.filter(level=level).exclude(item_code__in=active_item_codes).delete()

    for item in level_data['items']:
        defaults = {
            'category': resolved_categories[item['category']],
            'title': item['title'],
            'content_type': item['content_type'],
            'content_text': item['content_text'],
            'content_json': item.get('content_json', {}),
            'is_key_item': item.get('is_key_item', True),
            'sort_order': item['sort_order'],
            'is_initial_visible': True,
        }
        LevelItem.objects.update_or_create(level=level, item_code=item['item_code'], defaults=defaults)

    DecisionConfig.objects.update_or_create(
        level=level,
        defaults={
            'title': level_data['decision']['title'],
            'target_text': level_data['decision']['target_text'],
            'decision_type': 'single_choice',
            'config_json': level_data['decision']['config_json'],
        },
    )

    active_rule_names = [rule['rule_name'] for rule in level_data['rules']]
    ResultRule.objects.filter(level=level).exclude(rule_name__in=active_rule_names).delete()

    for rule in level_data['rules']:
        ResultRule.objects.update_or_create(level=level, rule_name=rule['rule_name'], defaults=rule)


def refresh_levels_one_and_two(apps, schema_editor):
    level_definitions = [
        {
            'level_code': 'level_1',
            'order': 1,
            'title': 'Fresh Produce Waste Crisis',
            'description': 'Determine the optimal order quantity for strawberries and achieve a turnaround in the profitability of this category.',
            'objective_text': 'Review the right report, compare DOC against shelf life, and choose the strawberry order quantity that protects both availability and profit.',
            'briefing_title': 'Fresh Produce Control Room',
            'briefing_text': 'Strawberry and lettuce spoilage is close to 25%, and the boss wants next week planned before more stock goes bad.',
            'briefing_hint': 'Start with the loss attribution evidence instead of the vanity revenue view. If DOC stays above shelf life, waste will continue.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_manager_push', 'title': 'Store Manager', 'content_type': 'text', 'content_text': 'Yesterday we sold out. Demand must be peaking, so why not double the strawberry order and ride the momentum for another week?', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_analyst_hint', 'title': 'Produce Analyst', 'content_type': 'text', 'content_text': 'Before we order anything, we should open the Loss Attribution Analysis report. A one-day spike does not explain why spoilage has stayed high.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'total_revenue_dashboard', 'title': 'Total Revenue Dashboard', 'content_type': 'text', 'content_text': 'Yesterday looks exciting because total produce revenue jumped for one day, but this dashboard does not explain which item is spoiling or whether inventory is sitting too long.', 'sort_order': 3},
                {'category': 'report', 'item_code': 'loss_attribution_report', 'title': 'Loss Attribution Analysis Report', 'content_type': 'table', 'content_text': 'This is the report that explains the waste problem. Strawberries are currently sitting longer than their shelf life allows.', 'content_json': {'headers': ['Item', 'Forecast Daily Sales', 'Current Inventory', 'DOC', 'Shelf Life', 'Risk'], 'rows': [['Strawberries', '26 kg', '90 kg', '3.5 days', '3 days', 'Waste risk'], ['Organic Lettuce', '18 kg', '42 kg', '2.3 days', '2 days', 'Waste risk']]}, 'sort_order': 4},
                {'category': 'report', 'item_code': 'four_week_sales_trend', 'title': '4-Week Strawberry Sales Trend', 'content_type': 'chart', 'content_text': 'The four-week pattern is stable, while yesterday is a clear one-day spike. The baseline demand is much closer to the weekly trend than to the outlier.', 'content_json': {'x': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Yesterday'], 'y': [176, 182, 179, 184, 360], 'x_label': 'Period', 'y_label': 'Strawberry Sales (kg)'}, 'sort_order': 5},
                {'category': 'external', 'item_code': 'influencer_clip', 'title': 'Social Media Video Clip', 'content_type': 'text', 'content_text': 'A local influencer happened to film outside the store yesterday, and the clip sent a temporary rush of customers looking for strawberries. The traffic spike has already faded.', 'sort_order': 6},
                {'category': 'external', 'item_code': 'weather_forecast', 'title': 'Rainfall Forecast for Next Week', 'content_type': 'text', 'content_text': 'Rain is expected through most of next week, so total foot traffic should be softer than the influencer day rather than stronger.', 'sort_order': 7},
                {'category': 'external', 'item_code': 'competitor_calendar', 'title': 'Competitor Promotion Calendar', 'content_type': 'text', 'content_text': 'The nearby competitor is ending its fruit coupon on Sunday. Demand may normalize slightly, but there is no evidence of a lasting demand surge large enough to justify a doubled order.', 'sort_order': 8},
            ],
            'decision': {
                'title': 'Weekly Strawberry Order Decision',
                'target_text': 'Approve the strawberry order quantity that best fits the trend and keeps expected DOC under shelf life.',
                'config_json': {'options': [140, 180, 260], 'unit': 'kg'},
            },
            'rules': [
                {'rule_name': 'success_180', 'condition_json': {'selected_value': 180}, 'is_success': True, 'message': 'Correct. You opened the loss attribution evidence, ignored the one-day spike, and chose an order that brings DOC back under strawberry shelf life instead of chasing noise.', 'score': 50, 'next_action': 'next_level'},
                {'rule_name': 'fail_140', 'condition_json': {'selected_value': 140}, 'is_success': False, 'message': 'That correction was too aggressive. You solved the waste risk, but the shelf emptied too early and regular demand was not fully covered.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_260', 'condition_json': {'selected_value': 260}, 'is_success': False, 'message': 'That order still chases yesterday\'s spike. DOC stays too high for a short-life item, so the department ends up with another week of preventable spoilage.', 'score': 0, 'next_action': 'restart'},
            ],
        },
        {
            'level_code': 'level_2',
            'order': 2,
            'title': 'Holiday Promotion Settlement',
            'description': 'Test whether the old promotion evidence really supports the new holiday audience before copying the plan.',
            'objective_text': 'Check who the survey represents, separate traffic context from promotion effect, and choose the holiday plan that actually fits evening office workers.',
            'briefing_title': 'Promotion Review Desk',
            'briefing_text': 'Marketing wants to reuse a high-scoring daytime promotion for the holiday evening crowd without changing the strategy.',
            'briefing_hint': 'Look for two traps: a biased survey sample and a sales spike that may be explained by context instead of the promotion itself.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_marketing_manager', 'title': 'Marketing Manager', 'content_type': 'text', 'content_text': 'The daytime holiday promotion scored 95% satisfaction, and sales jumped on the rainy campaign days. Let us copy it for the evening office crowd and move on.', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_evening_supervisor', 'title': 'Evening Shift Supervisor', 'content_type': 'text', 'content_text': 'Our evening office workers shop quickly after work. They react better to grab-and-go bundles than to the daytime signage used for retirees.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'promotion_satisfaction_summary', 'title': 'Promotion Satisfaction Summary', 'content_type': 'table', 'content_text': 'The headline satisfaction score is strong, but the audience mix behind it is not balanced.', 'content_json': {'headers': ['Audience Group', 'Satisfaction', 'Sample Share'], 'rows': [['Daytime seniors', '95%', '58%'], ['Mixed daytime adults', '68%', '30%'], ['Evening office workers', '42%', '12%']]}, 'sort_order': 3},
                {'category': 'report', 'item_code': 'survey_sampling_sheet', 'title': 'Survey Sampling Sheet', 'content_type': 'table', 'content_text': 'Most of the feedback came from daytime shoppers, so the survey is not representative of the new holiday target group.', 'content_json': {'headers': ['Collection Window', 'Location', 'Primary Respondents'], 'rows': [['10:00-12:00', 'Front produce aisle', 'Retirees and morning shoppers'], ['12:00-16:00', 'Coupon desk', 'Nearby daytime visitors'], ['17:00-21:00', 'After-work entrance', 'Very limited responses']]}, 'sort_order': 4},
                {'category': 'report', 'item_code': 'rain_day_sales_pattern', 'title': 'Rain-Day Sales Pattern', 'content_type': 'table', 'content_text': 'Sales were highest on the rainiest days, but that does not automatically prove the old promotion caused the increase.', 'content_json': {'headers': ['Day', 'Rainfall', 'Mall Footfall', 'Promotion Sales'], 'rows': [['Thursday', 'Low', 'Normal', '86'], ['Friday', 'High', 'Very high', '128'], ['Saturday', 'High', 'Very high', '134']]}, 'sort_order': 5},
                {'category': 'external', 'item_code': 'survey_details', 'title': 'Survey Demographic Note', 'content_type': 'text', 'content_text': 'The satisfaction team collected responses mostly from shoppers above 50 during daytime hours. That sample cannot stand in for after-work office workers.', 'sort_order': 6},
                {'category': 'external', 'item_code': 'traffic_context_note', 'title': 'Transit and Weather Context Note', 'content_type': 'text', 'content_text': 'On the two rainiest campaign days, a subway exit repair pushed office workers through the mall connector. The traffic spike happened at the same time as the promotion, so the promotion alone cannot explain the sales jump.', 'sort_order': 7},
            ],
            'decision': {
                'title': 'Holiday Promotion Decision',
                'target_text': 'Choose the holiday promotion plan that fits the evening office-worker audience without over-reading the old campaign data.',
                'config_json': {'options': ['Reuse the daytime senior promotion because the 95% score proves it works for everyone', 'Build a commuter-friendly evening combo and treat the rain-day spike as context, not proof the old plan always works', 'Expand the rainy-day giveaway because higher rainfall and higher sales clearly mean the promotion gets stronger in bad weather'], 'unit': ''},
            },
            'rules': [
                {'rule_name': 'success_evening_combo', 'condition_json': {'selected_value': 'Build a commuter-friendly evening combo and treat the rain-day spike as context, not proof the old plan always works'}, 'is_success': True, 'message': 'Excellent call. You caught both traps: the survey sample did not represent evening office workers, and the rain-day sales spike was confounded by unusual commuter traffic.', 'score': 50, 'next_action': 'next_level'},
                {'rule_name': 'fail_copy_daytime', 'condition_json': {'selected_value': 'Reuse the daytime senior promotion because the 95% score proves it works for everyone'}, 'is_success': False, 'message': 'That decision trusts a biased sample. High satisfaction from daytime retirees does not prove the same promotion fits evening office workers.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_spurious_weather', 'condition_json': {'selected_value': 'Expand the rainy-day giveaway because higher rainfall and higher sales clearly mean the promotion gets stronger in bad weather'}, 'is_success': False, 'message': 'That reads correlation as causation. Rainy campaign days also came with unusual commuter traffic, so you cannot treat the old promotion as the sole driver of the sales spike.', 'score': 0, 'next_action': 'restart'},
            ],
        },
    ]

    for level_data in level_definitions:
        upsert_level(apps, level_data)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [('levels', '0005_seed_levels_three_to_seven')]

    operations = [migrations.RunPython(refresh_levels_one_and_two, noop_reverse)]
