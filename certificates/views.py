from django.shortcuts import render


def certificate_view(request):
    return render(request, 'certificates/certificate.html')
