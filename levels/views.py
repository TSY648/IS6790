import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from .models import Level


def level_view(request, level_order):
    level = get_object_or_404(Level, order=level_order, is_active=True)
    return render(request, 'levels/level.html', {'level': level})


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

    matched_rule = None
    for rule in level.result_rules.all():
        if rule.condition_json.get('selected_value') == selected_value:
            matched_rule = rule
            break

    if not matched_rule:
        return JsonResponse({'success': False, 'message': '没有匹配到规则，请检查配置。'}, status=400)

    return JsonResponse(
        {
            'success': matched_rule.is_success,
            'message': matched_rule.message,
            'score': matched_rule.score,
            'next_action': matched_rule.next_action,
        }
    )
