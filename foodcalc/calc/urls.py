# from django.contrib import admin
from django.urls import path
from calc import views

app_name = 'calc'

urlpatterns = [
    path('', views.index, name='index'),
    path('func/', views.food_search, name='func'),
    path('calc/', views.calc, name='calc'),
    path('detail/<int:food_id>/', views.FoodDetailView.as_view(), name='food_detail'),
    path('profile/edit/', views.profile_update, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),
    path('animal/create/', views.AnimalCreateView.as_view(), name='animal_create'),
    path('animal/<int:pk>/edit/', views.AnimalUpdateView.as_view(), name='animal_update'),
    path('animal/<int:pk>/delete/', views.AnimalDeleteView.as_view(), name='animal_delete'),
    path('rec-nutr-lvl/', views.recnutrlvl, name='recnutrlvl')
]
