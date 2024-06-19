# from django.contrib import admin
from django.urls import path
from calc import views

app_name = 'calc'

urlpatterns = [
    path('', views.food_search, name='index'),
    path('calc/', views.calc, name='calc'),
]
