from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth import views as auth_views

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.handler500'
handler403 = 'pages.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls', namespace='pages')),
    path('animal/', include('animal.urls', namespace='animal')),
    path('food/', include('food.urls', namespace='food')),
    path('', include('calc.urls', namespace='calc')),
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm,
        success_url=reverse_lazy('calc:index'),),
        name='registration'),
    path('auth/', include('django.contrib.auth.urls')),
]

auth_urls = ([
    path(
        'login/',
        auth_views.LoginView.as_view(),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name='registration/logout.html'
        ),
        name='logout',
    ),
    path(
        'signup/',
        CreateView.as_view(
            form_class=UserCreationForm,
            success_url='/',
            template_name='registration/signup.html',
        ),
        name='signup'
    ),
], 'users')

urlpatterns += [path('auth/', include(auth_urls))]

if settings.DEBUG:
    import debug_toolbar
    # Добавить к списку urlpatterns список адресов из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
