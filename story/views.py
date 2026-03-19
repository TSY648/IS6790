from django.shortcuts import redirect, render

from .content import LEVEL_STORIES


def opening_story_view(request):
    story_lines = [
        'You are a newly hired trainee manager at a neighborhood supermarket, and today is your first day on the job.',
        "The store manager says the store's performance has been unstable lately, and important decisions cannot rely on gut feeling alone.",
        'From today on, you will need to use data and information to make more reliable business decisions.',
        'Your first task is to decide how many strawberries to order for the coming week.',
    ]
    return render(
        request,
        'story/story.html',
        {
            'story_title': 'Opening Story',
            'story_lines': story_lines,
            'next_url': '/levels/1/',
            'button_label': 'Start Internship',
            'help_title': 'Settings & Help',
            'help_description': 'Read the opening setup, then enter the internship challenge when the story finishes.',
        },
    )


def level_story_view(request, level_order):
    story = LEVEL_STORIES.get(level_order)
    if not story:
        return redirect(f'/levels/{level_order}/')

    return render(
        request,
        'story/story.html',
        {
            'story_title': story['title'],
            'story_lines': story['story_lines'],
            'next_url': story['next_url'],
            'button_label': story['button_label'],
            'help_title': 'Settings & Help',
            'help_description': story['help_description'],
        },
    )
