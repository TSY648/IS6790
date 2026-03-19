from django.shortcuts import render


def home_view(request):
    return render(
        request,
        'core/home.html',
        {
            'help_title': 'Settings & Help',
            'help_description': 'Review the core rules, supported environment, and placeholder audio setting for the training game.',
        },
    )
