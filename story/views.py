from django.shortcuts import redirect, render

from .content import LEVEL_STORIES


def opening_story_view(request):
    story_lines = [
        'Congrats on the new job! As Trainee Manager, you\'re here to bring some logic to the aisles.',
        "The boss is done with 'hunches' - it’s time to let the data do the talking.",
        'First up: The produce section.',
        'Analyze the trends and decide on our strawberry order for the week. Make it count!',
    ]
    return render(
        request,
        'story/story.html',
        {
            'story_title': 'Opening Story',
            'story_lines': story_lines,
            'next_url': '/levels/1/',
            'button_label': 'Start',
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
