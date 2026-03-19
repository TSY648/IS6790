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

    for rule in level_data['rules']:
        ResultRule.objects.update_or_create(level=level, rule_name=rule['rule_name'], defaults=rule)


def seed_levels_three_to_seven(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    ResultRule = apps.get_model('levels', 'ResultRule')

    level2 = Level.objects.filter(level_code='level_2').first()
    if level2:
        level2.title = 'Weekend Promotion Plan'
        level2.description = "Check whether last week's popular promotion can really be reused for a different customer group."
        level2.objective_text = 'Review the evidence and choose the promotion plan that best fits evening office workers this weekend.'
        level2.briefing_title = 'Promotion Review Desk'
        level2.briefing_text = 'The store manager wants to repeat a daytime promotion that scored very well with older shoppers.'
        level2.briefing_hint = 'Your job is to verify whether that evidence also supports the evening crowd targeted this week.'
        level2.save(update_fields=['title', 'description', 'objective_text', 'briefing_title', 'briefing_text', 'briefing_hint'])
        ResultRule.objects.filter(level=level2, rule_name='success_evening_combo').update(next_action='next_level')

    level_definitions = [
        {
            'level_code': 'level_3',
            'order': 3,
            'title': 'Supplier Order Merge Sprint',
            'description': 'Merge two supplier sheets into one clean Double 11 order without unit or duplication mistakes.',
            'objective_text': 'Choose the merge plan that standardizes formats, removes duplicates, and protects the restocking budget.',
            'briefing_title': 'Supplier Reconciliation Desk',
            'briefing_text': 'Two suppliers sent overlapping order sheets for the same campaign, and finance needs one clean approval file.',
            'briefing_hint': 'Watch for unit mismatches, duplicate products, and shortcuts that push the mess downstream.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_procurement_lead', 'title': 'Procurement Lead', 'content_type': 'text', 'content_text': 'We are short on time. If the two sheets look close enough, we could just submit both and let finance sort it out later.', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_finance_warning', 'title': 'Finance Clerk', 'content_type': 'text', 'content_text': 'If duplicate items or mixed units slip through, the campaign budget could be blown before orders even arrive.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'supplier_a_snapshot', 'title': 'Supplier A Sheet Snapshot', 'content_type': 'text', 'content_text': 'Supplier A lists cola in cases, bottled tea in cartons, and snack trays in RMB.', 'sort_order': 3},
                {'category': 'report', 'item_code': 'conversion_memo', 'title': 'Unit Conversion Memo', 'content_type': 'text', 'content_text': 'The approved standard is cartons for drinks, trays for snacks, and all costs converted to RMB before approval.', 'sort_order': 4},
                {'category': 'external', 'item_code': 'duplicate_sku_alert', 'title': 'Duplicate SKU Alert', 'content_type': 'text', 'content_text': 'Coca-Cola 500ml and Coke 500ml are the same product in the catalog and must be merged instead of counted twice.', 'sort_order': 5},
            ],
            'decision': {
                'title': 'Final Merge Decision',
                'target_text': 'Choose the safest approval plan for the Double 11 supplier order.',
                'config_json': {'options': ['Normalize units and merge duplicate SKUs before approval', 'Submit both supplier sheets separately and let finance reconcile later', 'Delete any item that looks duplicated to stay under budget'], 'unit': ''},
            },
            'rules': [
                {'rule_name': 'success_clean_merge', 'condition_json': {'selected_value': 'Normalize units and merge duplicate SKUs before approval'}, 'is_success': True, 'message': 'Correct. You standardized the data before acting on it, which kept the budget accurate and prevented duplicate stock.', 'score': 50, 'next_action': 'next_level'},
                {'rule_name': 'fail_split_submission', 'condition_json': {'selected_value': 'Submit both supplier sheets separately and let finance reconcile later'}, 'is_success': False, 'message': 'That shortcut pushes the data mess downstream. Mixed standards and duplicates are still unresolved, so the order remains unreliable.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_delete_guess', 'condition_json': {'selected_value': 'Delete any item that looks duplicated to stay under budget'}, 'is_success': False, 'message': 'Removing items by guess creates a different error: under-ordering. Data cleaning requires standardization and evidence, not blind deletion.', 'score': 0, 'next_action': 'restart'},
            ],
        },
        {
            'level_code': 'level_4',
            'order': 4,
            'title': 'Pricing Anomaly Audit',
            'description': 'Investigate an impossible POS outlier and decide how the transaction should be handled.',
            'objective_text': 'Choose the anomaly response that fixes the record and keeps the audit trail trustworthy.',
            'briefing_title': 'Audit Review Desk',
            'briefing_text': 'A cola appears to have sold for 10,000 yuan, and finance wants a clean explanation before the books close.',
            'briefing_hint': 'Do not treat every outlier the same. Decide whether this is noise, a correction case, or a real business event.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_audit_lead', 'title': 'Audit Lead', 'content_type': 'text', 'content_text': 'We need a decision quickly, but whatever we do must still be traceable if the transaction is reviewed later.', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_cashier_note', 'title': 'Cashier Note', 'content_type': 'text', 'content_text': 'I remember ringing up several drinks in a rush, and I may have keyed the decimal point incorrectly while clearing the line.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'pos_anomaly_chart', 'title': 'POS Amount Log', 'content_type': 'chart', 'content_text': 'One transaction sits far outside the normal sales range for bottled drinks.', 'content_json': {'x': ['Tx 1', 'Tx 2', 'Tx 3', 'Tx 4'], 'y': [8, 12, 9, 10000]}, 'sort_order': 3},
                {'category': 'report', 'item_code': 'metadata_record', 'title': 'Metadata Record', 'content_type': 'text', 'content_text': 'The system can store source register, operator, and correction reason. Missing metadata leaves the audit history incomplete.', 'sort_order': 4},
                {'category': 'external', 'item_code': 'cctv_summary', 'title': 'CCTV Summary', 'content_type': 'text', 'content_text': 'The review shows one customer carrying only a few drinks through Register 2, not a premium bulk purchase.', 'sort_order': 5},
            ],
            'decision': {
                'title': 'Anomaly Handling Decision',
                'target_text': 'Choose how the suspicious transaction should be handled.',
                'config_json': {'options': ['Correct the outlier as a cashier input error and annotate the record', 'Delete the outlier immediately without leaving any note', 'Keep the outlier as a real premium purchase'], 'unit': ''},
            },
            'rules': [
                {'rule_name': 'success_correct_and_annotate', 'condition_json': {'selected_value': 'Correct the outlier as a cashier input error and annotate the record'}, 'is_success': True, 'message': 'Correct. You treated the outlier as a correctable error and preserved the metadata needed for traceability.', 'score': 50, 'next_action': 'next_level'},
                {'rule_name': 'fail_delete_without_trace', 'condition_json': {'selected_value': 'Delete the outlier immediately without leaving any note'}, 'is_success': False, 'message': 'The amount may be wrong, but deleting it without annotation destroys the audit trail and makes the dataset less trustworthy.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_keep_as_real_sale', 'condition_json': {'selected_value': 'Keep the outlier as a real premium purchase'}, 'is_success': False, 'message': 'That treats a clear anomaly as business reality. The supporting evidence shows this was not a valid high-value transaction.', 'score': 0, 'next_action': 'restart'},
            ],
        },
        {
            'level_code': 'level_5',
            'order': 5,
            'title': 'Bonus Review Debate',
            'description': 'Pick the fairest performance summary before quarterly employee bonuses are finalized.',
            'objective_text': 'Choose the summary approach that reflects the real team distribution instead of a distorted headline number.',
            'briefing_title': 'People Operations Desk',
            'briefing_text': 'HR wants a quick answer on bonus fairness, but the commission data is highly uneven and not everyone stayed long enough to be heard.',
            'briefing_hint': 'Look for the metric that best represents the team and remember which voices are missing from the sample.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_hr_manager', 'title': 'HR Manager', 'content_type': 'text', 'content_text': 'The average commission looks strong this quarter. We could probably use that as the headline metric for the bonus discussion.', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_shift_lead', 'title': 'Shift Lead', 'content_type': 'text', 'content_text': 'Most staff cluster far below the top earners, so the average feels much higher than what the typical employee actually experiences.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'commission_distribution', 'title': 'Commission Distribution', 'content_type': 'chart', 'content_text': 'A few standout earners pull the mean upward, while most of the team is concentrated around a lower band.', 'content_json': {'x': ['Top 3', 'Middle Group', 'Typical Range'], 'y': [120, 55, 30]}, 'sort_order': 3},
                {'category': 'report', 'item_code': 'exit_interviews', 'title': 'Exit Interview Summary', 'content_type': 'text', 'content_text': 'Several employees who left earlier in the quarter are absent from the current morale survey, even though pay fairness was part of their reason for leaving.', 'sort_order': 4},
                {'category': 'external', 'item_code': 'loyal_staff_survey', 'title': 'Current Staff Survey', 'content_type': 'text', 'content_text': 'The internal survey mostly reflects current high performers who stayed through the quarter and does not capture the views of leavers.', 'sort_order': 5},
            ],
            'decision': {
                'title': 'Bonus Metric Decision',
                'target_text': 'Choose the fairest interpretation for the bonus review meeting.',
                'config_json': {'options': ['Use the median commission and note that current surveys exclude people who already left', 'Use the average commission because top performers show the team ceiling', 'Rely on feedback from current high performers only'], 'unit': ''},
            },
            'rules': [
                {'rule_name': 'success_median_and_missing_group', 'condition_json': {'selected_value': 'Use the median commission and note that current surveys exclude people who already left'}, 'is_success': True, 'message': 'Correct. The median better represents the typical employee, and you also recognized that the visible survey misses people who already left.', 'score': 50, 'next_action': 'next_level'},
                {'rule_name': 'fail_average_bias', 'condition_json': {'selected_value': 'Use the average commission because top performers show the team ceiling'}, 'is_success': False, 'message': 'That lets a few extreme earners distort the story. The average is not the best representation of the team in this distribution.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_survivorship', 'condition_json': {'selected_value': 'Rely on feedback from current high performers only'}, 'is_success': False, 'message': 'That is classic survivorship bias. The people who stayed are visible, but the employees who left are also part of the quarter you are evaluating.', 'score': 0, 'next_action': 'restart'},
            ],
        },
        {
            'level_code': 'level_6',
            'order': 6,
            'title': 'Branch Comparison Review',
            'description': 'Decide which branch is truly improving after separating aggregate totals from segment performance.',
            'objective_text': 'Choose the branch recommendation that accounts for category mix instead of trusting the headline total alone.',
            'briefing_title': 'Regional Review Room',
            'briefing_text': 'Leadership wants one answer on which branch is stronger, but the raw totals and the category splits do not point in the same direction.',
            'briefing_hint': 'Compare the segments before trusting the combined number. The aggregate may reverse the underlying story.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_regional_manager', 'title': 'Regional Manager', 'content_type': 'text', 'content_text': 'Store A still has the higher total sales line, so my first instinct is to call it the stronger branch.', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_category_lead', 'title': 'Category Lead', 'content_type': 'text', 'content_text': 'When you compare fresh and general merchandise separately, Store B is improving faster in both categories.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'aggregate_branch_totals', 'title': 'Aggregate Branch Totals', 'content_type': 'chart', 'content_text': 'Store A still shows the stronger overall total because it carries a heavier share of the larger category.', 'content_json': {'x': ['Store A Total', 'Store B Total'], 'y': [520, 500]}, 'sort_order': 3},
                {'category': 'report', 'item_code': 'segmented_growth', 'title': 'Segmented Category Growth', 'content_type': 'text', 'content_text': 'Within both fresh and general merchandise, Store B has the higher growth rate. The category mix changes the aggregate picture.', 'sort_order': 4},
                {'category': 'external', 'item_code': 'event_context', 'title': 'Local Event Context', 'content_type': 'text', 'content_text': 'A temporary event boosted Store A\'s larger category volume, but it did not improve category-level growth quality.', 'sort_order': 5},
            ],
            'decision': {
                'title': 'Branch Performance Decision',
                'target_text': 'Choose which branch should be recognized as stronger after the full review.',
                'config_json': {'options': ['Choose Store A because its aggregate total is still higher', 'Choose Store B because it performs better after category-level segmentation', 'Call the branches equal because outside events affected both'], 'unit': ''},
            },
            'rules': [
                {'rule_name': 'success_segmented_branch_b', 'condition_json': {'selected_value': 'Choose Store B because it performs better after category-level segmentation'}, 'is_success': True, 'message': 'Correct. The aggregate total hides the reversal. After segmentation, Store B shows the stronger underlying performance.', 'score': 50, 'next_action': 'next_level'},
                {'rule_name': 'fail_aggregate_only', 'condition_json': {'selected_value': 'Choose Store A because its aggregate total is still higher'}, 'is_success': False, 'message': 'That choice ignores the category mix problem. The combined total masks the fact that Store B outperforms in both segments.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_equal_call', 'condition_json': {'selected_value': 'Call the branches equal because outside events affected both'}, 'is_success': False, 'message': 'External events matter, but they do not erase the segmented pattern. The more defensible conclusion still comes from the category-level comparison.', 'score': 0, 'next_action': 'restart'},
            ],
        },
        {
            'level_code': 'level_7',
            'order': 7,
            'title': 'Board Presentation Day',
            'description': 'Choose the final communication strategy for leadership and frontline audiences without distorting the evidence.',
            'objective_text': 'Select the presentation approach that keeps the chart honest, matches the audience, and supports a clear claim-evidence-reasoning argument.',
            'briefing_title': 'Executive Presentation Room',
            'briefing_text': 'Your final task is to present a store decision clearly to leadership while also preparing something useful for operations.',
            'briefing_hint': 'The best answer combines truthful visuals, audience fit, and a defensible recommendation.',
            'items': [
                {'category': 'npc', 'item_code': 'npc_board_chair', 'title': 'Board Chair', 'content_type': 'text', 'content_text': 'Give us a recommendation we can trust quickly. Do not bury the decision in noise.', 'sort_order': 1},
                {'category': 'npc', 'item_code': 'npc_store_supervisor', 'title': 'Store Supervisor', 'content_type': 'text', 'content_text': 'My team needs a practical action list, not the same dense slide deck the investors will read.', 'sort_order': 2},
                {'category': 'report', 'item_code': 'truncated_sales_chart', 'title': 'Truncated Sales Chart', 'content_type': 'chart', 'content_text': 'This version starts the Y-axis high, which makes a small improvement look far larger than it really is.', 'content_json': {'x': ['Before', 'After'], 'y': [96, 98]}, 'sort_order': 3},
                {'category': 'report', 'item_code': 'raw_margin_table', 'title': 'Raw Margin Table', 'content_type': 'text', 'content_text': 'The raw numbers support a modest improvement, but only when the recommendation is explained with the right claim and evidence.', 'sort_order': 4},
                {'category': 'external', 'item_code': 'cer_checklist', 'title': 'CER Checklist', 'content_type': 'text', 'content_text': 'A strong argument states the claim, points to the supporting evidence, and explains why that evidence justifies the recommendation.', 'sort_order': 5},
            ],
            'decision': {
                'title': 'Presentation Strategy Decision',
                'target_text': 'Choose the final presentation approach for leadership and store teams.',
                'config_json': {'options': ['Reuse the dramatic truncated chart for every audience', 'Use a zero-based chart, tailor the level of detail, and support the recommendation with claim-evidence-reasoning', 'Send the same dense spreadsheet to stockers and investors so everyone gets the full detail'], 'unit': ''},
            },
            'rules': [
                {'rule_name': 'success_honest_tailored_cer', 'condition_json': {'selected_value': 'Use a zero-based chart, tailor the level of detail, and support the recommendation with claim-evidence-reasoning'}, 'is_success': True, 'message': 'Excellent work. You finished the program with an honest chart, the right audience framing, and a clear CER argument.', 'score': 50, 'next_action': 'certificate'},
                {'rule_name': 'fail_exaggerated_chart', 'condition_json': {'selected_value': 'Reuse the dramatic truncated chart for every audience'}, 'is_success': False, 'message': 'That exaggerates the improvement and weakens trust. Presentation quality depends on both visual integrity and audience fit.', 'score': 0, 'next_action': 'restart'},
                {'rule_name': 'fail_same_dense_sheet', 'condition_json': {'selected_value': 'Send the same dense spreadsheet to stockers and investors so everyone gets the full detail'}, 'is_success': False, 'message': 'Giving every audience the same artifact ignores what each group actually needs. Good data communication is tailored, not one-size-fits-all.', 'score': 0, 'next_action': 'restart'},
            ],
        },
    ]

    for level_data in level_definitions:
        upsert_level(apps, level_data)


def unseed_levels_three_to_seven(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    Level.objects.filter(level_code__in=['level_3', 'level_4', 'level_5', 'level_6', 'level_7']).delete()


class Migration(migrations.Migration):
    dependencies = [('levels', '0004_seed_level_two')]

    operations = [migrations.RunPython(seed_levels_three_to_seven, unseed_levels_three_to_seven)]
