# from django.contrib import admin
from django.urls import path
from calc import views

app_name = 'calc'

urlpatterns = [
    path('', views.food_search, name='index'),
    path('calc/', views.calc, name='calc'),
    path('detail/<int:food_id>/', views.FoodDetailView.as_view(), name='food_detail'),
   # path('profile/edit/', views.profile_update, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),
]
