from django.shortcuts import render

from core.navigation import build_progress_steps
from levels.models import Level


def certificate_view(request):
    total_levels = Level.objects.filter(is_active=True).count()
    return render(
        request,
        'certificates/certificate.html',
        {
            'issued_at': 'March 19, 2026',
            'available_levels': total_levels,
            'max_score': total_levels * 50,
            'final_score': 0,
            'score_rule': '50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.',
            'topbar_progress': build_progress_steps(total_levels, total_levels, complete_all=True),
            'progress_label': f'Completed {total_levels}/{total_levels}',
            'help_title': 'Certificate Help',
            'help_description': 'Save your certificate as an image or return to the homepage to start over.',
        },
    )
