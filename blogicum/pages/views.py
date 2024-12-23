from django.shortcuts import render


def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def page_500(request):
    return render(request, 'pages/500.html', status=500)


def page_403(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
