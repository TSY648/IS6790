from django.core.management.base import BaseCommand

from levels.models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


class Command(BaseCommand):
    help = 'Seed Level 1 MVP data for the supermarket decision game.'

    def handle(self, *args, **options):
        level1, created = Level.objects.get_or_create(
            level_code='level_1',
            defaults={
                'title': '生鲜蔬果损耗危机',
                'description': '确定草莓的最佳订货量，完成品类扭亏为盈。',
                'order': 1,
                'is_active': True,
            },
        )
        if not created:
            level1.title = '生鲜蔬果损耗危机'
            level1.description = '确定草莓的最佳订货量，完成品类扭亏为盈。'
            level1.order = 1
            level1.is_active = True
            level1.save()

        npc, _ = InfoCategory.objects.get_or_create(code='npc', defaults={'name': 'NPC'})
        report, _ = InfoCategory.objects.get_or_create(code='report', defaults={'name': '报表'})
        external, _ = InfoCategory.objects.get_or_create(code='external', defaults={'name': '外部信息'})

        items = [
            {
                'category': npc,
                'item_code': 'NPC_manager',
                'title': '店长',
                'content_type': 'text',
                'content_text': '小王，昨天草莓直接卖空了！看来这周行情大好，我们趁热打铁，把下周订货量直接翻倍，肯定能赚回来！',
                'is_key_item': True,
                'sort_order': 1,
            },
            {
                'category': npc,
                'item_code': 'NPC_cashier',
                'title': '张姐',
                'content_type': 'text',
                'content_text': '昨天好多人都是看了网上的视频来的，一进门就问草莓在哪，今天就没几个人问了。',
                'is_key_item': True,
                'sort_order': 2,
            },
            {
                'category': report,
                'item_code': 'sales_trend',
                'title': '草莓历史销售趋势图',
                'content_type': 'chart',
                'content_text': '过去4周销量平稳波动，昨日出现一个明显的销量翻倍尖刺。',
                'content_json': {
                    'x': ['第1周', '第2周', '第3周', '第4周', '昨天'],
                    'y': [180, 190, 175, 185, 360],
                },
                'is_key_item': True,
                'sort_order': 3,
            },
            {
                'category': external,
                'item_code': 'social_news',
                'title': '社交媒体视频剪报',
                'content_type': 'text',
                'content_text': '本地网红昨日在店门口拍摄了草莓推荐视频，获赞 10w+。',
                'is_key_item': True,
                'sort_order': 4,
            },
            {
                'category': external,
                'item_code': 'weather_forecast',
                'title': '未来一周降雨量',
                'content_type': 'text',
                'content_text': '未来一周连续降雨，预计到店客流下降30%。',
                'is_key_item': True,
                'sort_order': 5,
            },
        ]

        for item in items:
            LevelItem.objects.update_or_create(
                level=level1,
                item_code=item['item_code'],
                defaults=item,
            )

        DecisionConfig.objects.update_or_create(
            level=level1,
            defaults={
                'title': '草莓每周期订货量决策',
                'target_text': '请根据已有信息，决定本周草莓应订货多少斤。',
                'decision_type': 'single_choice',
                'config_json': {'options': [100, 200, 300], 'unit': '斤'},
            },
        )

        rules = [
            {
                'rule_name': 'success_200',
                'condition_json': {'selected_value': 200},
                'is_success': True,
                'message': '恭喜！您成功降低了草莓损耗率，实现了扭亏为盈！您精准识别了网红流量带来的噪音，抓住了销量的核心趋势，用数据做出了正确的决策！',
                'score': 50,
                'next_action': 'next_level',
            },
            {
                'rule_name': 'fail_100',
                'condition_json': {'selected_value': 100},
                'is_success': False,
                'message': '很遗憾，您订货量太少，周中货架就已经空了，流失了大量顾客。',
                'score': 0,
                'next_action': 'restart',
            },
            {
                'rule_name': 'fail_300',
                'condition_json': {'selected_value': 300},
                'is_success': False,
                'message': '很遗憾，下周网红热度消退，加上雨天客流下降，大量草莓直接烂在了货架上。',
                'score': 0,
                'next_action': 'restart',
            },
        ]

        for rule in rules:
            ResultRule.objects.update_or_create(level=level1, rule_name=rule['rule_name'], defaults=rule)

        self.stdout.write(self.style.SUCCESS('Level 1 seed data is ready.'))
