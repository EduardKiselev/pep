from django.urls import path
from animal import views

app_name = 'animal'

urlpatterns = [
    path('create/',
         views.AnimalCreateView.as_view(),
         name='animal_create'),
    path('<int:pk>/edit/',
         views.AnimalUpdateView.as_view(),
         name='animal_update'),
    path('<int:pk>/delete/',
         views.AnimalDeleteView.as_view(),
         name='animal_delete'),
]
