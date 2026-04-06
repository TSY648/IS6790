import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from core.navigation import build_progress_steps

from .models import Level

MAX_LEVEL_SCORE = 50
MIN_SUCCESS_SCORE = 10
ATTEMPT_PENALTY = 15


LEVEL_KNOWLEDGE_POINTS = {
    1: [
        'Not every loud signal reflects real demand.',
        'Stable sales patterns matter more than single-day results.',
        'A one-day spike does not define a long-term trend.',
    ],
    2: [
        'A number is meaningless without knowing its unit and definition.',
        'Clean, comparable data is the foundation of any sound operational decision.',
        'Standardization must come before judgment.',
    ],
    3: [
        'High volume does not guarantee profit.',
        'A large number is meaningless without its cost structure.',
        'Sales growth does not equal profit growth.',
    ],
    4: [
        'Spotting visual tricks from a zoomed-in chart baseline',
        'Fact-checking the graph against the cold hard numbers',
        'Ignoring the hype to find the real profit story',
        'Cleaning up messy units for a clear comparison',
    ],
    5: [
        'Always evaluate metrics within the context of your business structure - not in isolation.',
        "Overall results can be misleading: patterns at the aggregate level may reverse when broken down by category (Simpson's Paradox).",
        'The best decision comes from aligning performance with where value is generated.',
    ],
    6: [
        'Always check if your data represents the whole group.',
        'Watch out for loud but unrepresentative voices.',
        'Use structured sampling (stratified pilot) to uncover true patterns.',
        'Let evidence - not emotion - guide your decisions.',
    ],
    7: [
        'Scrubbing ghost orders to keep our records clean',
        'Syncing cross-platform data into one clear language',
        'Fact-checking the bottom line by matching costs to revenue',
        'Spotting biased signals to find the real story behind the noise',
    ],
}


def calculate_attempt_score(base_score, attempt_count):
    if base_score <= 0:
        return 0

    try:
        safe_attempt_count = max(int(attempt_count or 1), 1)
    except (TypeError, ValueError):
        safe_attempt_count = 1
    return max(base_score - ((safe_attempt_count - 1) * ATTEMPT_PENALTY), MIN_SUCCESS_SCORE)


@ensure_csrf_cookie
def level_view(request, level_order):
    level = get_object_or_404(Level, order=level_order, is_active=True)
    total_levels = Level.objects.filter(is_active=True).count()
    return render(
        request,
        'levels/level.html',
        {
            'level': level,
            'total_levels': total_levels,
            'topbar_progress': build_progress_steps(level.order, total_levels),
            'progress_label': f'Level {level.order}/{total_levels}',
            'help_title': 'Settings & Help',
            'help_description': 'Use the right panel to inspect evidence, then submit the decision you think best fits the data.',
        },
    )


@require_GET
def level_config_api(request, level_order):
    level = get_object_or_404(Level, order=level_order, is_active=True)

    items = [
        {
            'item_code': item.item_code,
            'title': item.title,
            'category': item.category.code,
            'content_type': item.content_type,
            'content_text': item.content_text,
            'content_json': item.content_json,
            'is_key_item': item.is_key_item,
            'is_initial_visible': item.is_initial_visible,
        }
        for item in level.items.select_related('category').all()
    ]

    decision = None
    if hasattr(level, 'decision'):
        decision = {
            'title': level.decision.title,
            'target_text': level.decision.target_text,
            'decision_type': level.decision.decision_type,
            'config_json': level.decision.config_json,
        }

    return JsonResponse(
        {
            'level': {
                'order': level.order,
                'title': level.title,
                'description': level.description,
            },
            'items': items,
            'decision': decision,
        }
    )


@require_POST
def submit_decision_api(request, level_order):
    level = get_object_or_404(Level, order=level_order, is_active=True)
    body = json.loads(request.body or '{}')
    selected_value = body.get('selected_value')
    level_one_path = body.get('level_one_path')
    level_two_path = body.get('level_two_path')
    level_three_path = body.get('level_three_path')
    level_four_path = body.get('level_four_path')
    level_five_path = body.get('level_five_path')
    level_six_path = body.get('level_six_path')
    attempt_count = body.get('attempt_count') or 1
    try:
        safe_attempt_count = max(int(attempt_count), 1)
    except (TypeError, ValueError):
        safe_attempt_count = 1

    if level.order == 1 and level_one_path == 'accept_manager':
        return JsonResponse(
            {
                'success': False,
                'message': "The rushed order failed. You acted on the manager's instinct before checking the evidence, so the decision was based on noise instead of cause.",
                'score': 0,
                'awarded_score': 0,
                'attempt_count': safe_attempt_count,
                'max_score': MAX_LEVEL_SCORE,
                'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
                'next_action': 'restart',
                'next_url': f'/levels/{level.order}/',
                'next_level_order': None,
                'action_label': 'Restart This Level',
                'knowledge_points': LEVEL_KNOWLEDGE_POINTS.get(1, []),
            }
        )

    if level.order == 2 and level_two_path == 'accept_manager':
        return JsonResponse(
            {
                'success': False,
                'message': "Not quite! You jumped the gun and followed the manager's gut feeling before checking the math. It turns out that 100 in the system was not 100 eggs - it was 100 cartons. Next time, always clean up the units before you pull the trigger.",
                'score': 0,
                'awarded_score': 0,
                'attempt_count': safe_attempt_count,
                'max_score': MAX_LEVEL_SCORE,
                'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
                'next_action': 'restart',
                'next_url': f'/levels/{level.order}/',
                'next_level_order': None,
                'action_label': 'Restart This Level',
                'knowledge_points': LEVEL_KNOWLEDGE_POINTS.get(2, []),
            }
        )

    if level.order == 3 and level_three_path == 'accept_manager':
        return JsonResponse(
            {
                'success': False,
                'message': 'Tough break. You got caught up in the hype before checking the full profit-and-loss view. The glowing reviews and higher sales did not mean the promo was healthy for the business.',
                'score': 0,
                'awarded_score': 0,
                'attempt_count': safe_attempt_count,
                'max_score': MAX_LEVEL_SCORE,
                'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
                'next_action': 'restart',
                'next_url': f'/levels/{level.order}/',
                'next_level_order': None,
                'action_label': 'Restart This Level',
                'knowledge_points': LEVEL_KNOWLEDGE_POINTS.get(3, []),
            }
        )

    if level.order == 4 and level_four_path == 'accept_manager':
        return JsonResponse(
            {
                'success': False,
                'message': 'Tough break. The chart got the best of you. You reacted to the visual jump before checking the baseline and the raw numbers behind it.',
                'score': 0,
                'awarded_score': 0,
                'attempt_count': safe_attempt_count,
                'max_score': MAX_LEVEL_SCORE,
                'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
                'next_action': 'restart',
                'next_url': f'/levels/{level.order}/',
                'next_level_order': None,
                'action_label': 'Restart This Level',
                'knowledge_points': LEVEL_KNOWLEDGE_POINTS.get(4, []),
            }
        )

    if level.order == 5 and level_five_path == 'accept_manager':
        return JsonResponse(
            {
                'success': False,
                'message': 'Ouch - you got caught in the average trap. The headline total looked better, but you skipped the category mix that actually drives this store.',
                'score': 0,
                'awarded_score': 0,
                'attempt_count': safe_attempt_count,
                'max_score': MAX_LEVEL_SCORE,
                'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
                'next_action': 'restart',
                'next_url': f'/levels/{level.order}/',
                'next_level_order': None,
                'action_label': 'Restart This Level',
                'knowledge_points': LEVEL_KNOWLEDGE_POINTS.get(5, []),
            }
        )

    if level.order == 6 and level_six_path == 'accept_manager':
        return JsonResponse(
            {
                'success': False,
                'message': 'Not quite. You acted on a loud, self-selected set of complaints before testing whether the late-night demand was really there.',
                'score': 0,
                'awarded_score': 0,
                'attempt_count': safe_attempt_count,
                'max_score': MAX_LEVEL_SCORE,
                'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
                'next_action': 'restart',
                'next_url': f'/levels/{level.order}/',
                'next_level_order': None,
                'action_label': 'Restart This Level',
                'knowledge_points': LEVEL_KNOWLEDGE_POINTS.get(6, []),
            }
        )

    matched_rule = None
    for rule in level.result_rules.all():
        if rule.condition_json.get('selected_value') == selected_value:
            matched_rule = rule
            break

    if not matched_rule:
        return JsonResponse(
            {'success': False, 'message': 'No matching rule was found. Please check the configuration.'},
            status=400,
        )

    next_action = matched_rule.next_action
    next_url = ''
    next_level_order = None
    action_label = 'OK'
    awarded_score = calculate_attempt_score(matched_rule.score, safe_attempt_count) if matched_rule.is_success else 0

    if matched_rule.is_success:
        if next_action == 'next_level':
            next_level = Level.objects.filter(order__gt=level.order, is_active=True).order_by('order').first()
            if next_level:
                next_level_order = next_level.order
                next_url = f'/story/level/{next_level.order}/'
                action_label = 'Go to Next Level'
            else:
                next_action = 'certificate'
                next_url = '/certificate/summary/'
                action_label = 'View Certificate'
        elif next_action == 'certificate':
            next_url = '/certificate/summary/'
            action_label = 'View Certificate'
    else:
        if next_action == 'restart':
            next_url = f'/levels/{level.order}/'
            action_label = 'Restart This Level'

    response_data = {
        'success': matched_rule.is_success,
        'message': matched_rule.message,
        'score': matched_rule.score,
        'awarded_score': awarded_score,
        'attempt_count': safe_attempt_count,
        'max_score': matched_rule.score or MAX_LEVEL_SCORE,
        'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
        'next_action': next_action,
        'next_url': next_url,
        'next_level_order': next_level_order,
        'action_label': action_label,
    }

    if level.order in LEVEL_KNOWLEDGE_POINTS:
        response_data['knowledge_points'] = LEVEL_KNOWLEDGE_POINTS[level.order]

    return JsonResponse(response_data)
