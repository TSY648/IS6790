from django.http import JsonResponse


def progress_ping(request):
    return JsonResponse({'ok': True})
