from django.shortcuts import render

from core.navigation import build_progress_steps
from levels.models import Level

LEVEL_SUMMARY_ROWS = [
    {
        "level": 1,
        "title": "Fresh Produce Waste Crisis",
        "dimension": "Dimension 1: Generation and Recognition",
        "knowledge": "Signal vs. noise, source tracing",
        "difficulty": "Beginner",
    },
    {
        "level": 2,
        "title": "The Egg Inventory Tangle",
        "dimension": "Dimension 2: Processing and Management",
        "knowledge": "Format standardization and unit unification",
        "difficulty": "Beginner",
    },
    {
        "level": 3,
        "title": "The Promotion Profit Trap",
        "dimension": "Dimension 3: Analysis and Evaluation",
        "knowledge": "Survivorship bias",
        "difficulty": "Intermediate",
    },
    {
        "level": 4,
        "title": "The Revenue Mirage",
        "dimension": "Dimension 4: Presentation and Decision",
        "knowledge": "Baseline mismatch, chart-to-source-data verification",
        "difficulty": "Upper Intermediate",
    },
    {
        "level": 5,
        "title": "The Contract Conflict",
        "dimension": "Dimension 3: Analysis and Evaluation",
        "knowledge": "Simpson's paradox, scenario-fit data analysis",
        "difficulty": "Upper Intermediate",
    },
    {
        "level": 6,
        "title": "The Closing Time Crunch",
        "dimension": "Dimension 1: Generation and Recognition",
        "knowledge": "Sample representativeness, biased-sample judgment",
        "difficulty": "Advanced",
    },
    {
        "level": 7,
        "title": "The Delivery Disaster",
        "dimension": "Dimension 2: Processing and Management",
        "knowledge": "Format standardization, multi-unit conversion, duplicate cleanup",
        "difficulty": "Advanced (Final)",
    },
]


def build_certificate_context():
    total_levels = Level.objects.filter(is_active=True).count()
    return {
        "issued_at": "March 19, 2026",
        "available_levels": total_levels,
        "max_score": total_levels * 50,
        "final_score": 0,
        "score_rule": "50 points on the first correct attempt, 35 on the second, 20 on the third, and 10 from the fourth attempt onward.",
        "topbar_progress": build_progress_steps(total_levels, total_levels, complete_all=True),
        "progress_label": f"Completed {total_levels}/{total_levels}",
    }


def certificate_summary_view(request):
    context = build_certificate_context()
    context.update({
        "summary_rows": LEVEL_SUMMARY_ROWS,
        "help_title": "Learning Summary",
        "help_description": "Review the knowledge covered in each level before opening the graduation certificate.",
    })
    return render(request, "certificates/summary.html", context)


def certificate_view(request):
    context = build_certificate_context()
    context.update({
        "summary_rows": LEVEL_SUMMARY_ROWS,
        "help_title": "Certificate Help",
        "help_description": "Save your certificate as an image or return to the homepage to start over.",
    })
    return render(request, "certificates/certificate.html", context)
