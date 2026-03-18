from django.shortcuts import render


def opening_story_view(request):
    story_lines = [
        '你是新入职的社区超市实习经理，今天是你上岗的第一天。',
        '店长说：门店最近经营波动很大，很多决策不能只靠经验拍脑袋。',
        '从今天开始，你需要通过数据和信息做出更稳妥的经营判断。',
        '你的第一项任务，是处理草莓订货量的问题。',
    ]
    return render(request, 'story/story.html', {'story_lines': story_lines})
