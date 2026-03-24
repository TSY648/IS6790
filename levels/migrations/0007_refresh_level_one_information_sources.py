from django.db import migrations


def refresh_level_one_information_sources(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')
    InfoCategory = apps.get_model('levels', 'InfoCategory')
    LevelItem = apps.get_model('levels', 'LevelItem')

    level = Level.objects.filter(level_code='level_1').first()
    if not level:
        return

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
            'category': resolved_categories['report'],
            'item_code': 'strawberry_order_history',
            'title': 'Strawberry Order History',
            'content_type': 'table',
            'content_text': 'Strawberry order volumes have stayed fairly steady across the last four weeks, with no sustained increase in replenishment.',
            'content_json': {
                'headers': ['Week', 'Product', 'Order Quantity (kg)'],
                'rows': [
                    ['Week 1', 'Strawberry', '197.49'],
                    ['Week 2', 'Strawberry', '209.01'],
                    ['Week 3', 'Strawberry', '204.64'],
                    ['Week 4', 'Strawberry', '201.97'],
                ],
            },
            'sort_order': 1,
        },
        {
            'category': resolved_categories['report'],
            'item_code': 'strawberry_sales_trend',
            'title': 'Strawberry Sales Trend Chart',
            'content_type': 'image',
            'content_text': 'Sales were stable over the past four weeks, with a single unusual jump yesterday.',
            'content_json': {
                'src': '/static/levels/level1/strawberry-sales-trend.svg',
                'alt': 'Strawberry sales trend chart',
            },
            'sort_order': 2,
        },
        {
            'category': resolved_categories['npc'],
            'item_code': 'npc_manager',
            'title': 'Store Manager',
            'content_type': 'text',
            'content_text': 'Yesterday the strawberries sold out and the category looked hot. Should we order more this week and keep the momentum going?',
            'sort_order': 3,
        },
        {
            'category': resolved_categories['npc'],
            'item_code': 'npc_zhangjie',
            'title': 'Ms. Zhang',
            'content_type': 'text',
            'content_text': 'A lot of people came in for strawberries because of the short video yesterday, but that rush is already fading. I do not think the spike will last.',
            'sort_order': 4,
        },
        {
            'category': resolved_categories['external'],
            'item_code': 'social_media_clip',
            'title': 'Social Media Video Clip',
            'content_type': 'image',
            'content_text': 'A local influencer posted a strawberry recommendation video yesterday, which drove a temporary wave of extra foot traffic.',
            'content_json': {
                'src': '/static/levels/level1/social-media-clip.png',
                'alt': 'Social media video clip',
            },
            'sort_order': 5,
        },
        {
            'category': resolved_categories['external'],
            'item_code': 'weekly_rainfall',
            'title': 'Weekly Rainfall Forecast',
            'content_type': 'image',
            'content_text': 'Rain is expected through most of next week, which could reduce store traffic compared with clear days.',
            'content_json': {
                'src': '/static/levels/level1/weekly-rainfall.png',
                'alt': 'Weekly rainfall forecast',
            },
            'sort_order': 6,
        },
    ]

    active_item_codes = [item['item_code'] for item in items]
    LevelItem.objects.filter(level=level).exclude(item_code__in=active_item_codes).delete()

    for item in items:
        defaults = {
            'category': item['category'],
            'title': item['title'],
            'content_type': item['content_type'],
            'content_text': item['content_text'],
            'content_json': item.get('content_json', {}),
            'is_key_item': True,
            'is_initial_visible': True,
            'sort_order': item['sort_order'],
        }
        LevelItem.objects.update_or_create(level=level, item_code=item['item_code'], defaults=defaults)


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [('levels', '0006_refresh_levels_one_and_two')]

    operations = [migrations.RunPython(refresh_level_one_information_sources, noop_reverse)]
