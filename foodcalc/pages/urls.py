from django.urls import path
from pages import views
from django.shortcuts import render

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPageView.as_view(), name='about'),
]


# 404
def page_not_found(request, exception=''):
    return render(request, 'pages/404.html', status=404)


# 403
def csrf_failure(request, exception='', reason=''):
    context = {
        'exception': exception,
        'reason': reason
    }
    return render(request, 'pages/403csrf.html', context, status=403)


# 500
def handler500(request):
    return render(request, 'pages/500.html', status=500)
