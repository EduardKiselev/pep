from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


# 404
def page_not_found(request, exception=''):
    return render(request, 'pages/404.html', status=404)


# 403
def csrf_failure(request, exception='', reason=''):
    return render(request, 'pages/403csrf.html', status=403)


# 500
def handler500(request):
    return render(request, 'pages/500.html', status=500)
