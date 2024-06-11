from django.contrib import admin
from django.urls import path, include
from calc import views

app_name = 'calc'

urlpatterns = [
    path('', views.index, name='index'),
]
