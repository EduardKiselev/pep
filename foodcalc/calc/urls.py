# from django.contrib import admin
from django.urls import path
from calc import views

app_name = 'calc'

urlpatterns = [
    path('', views.index, name='index'),
    path('func/', views.food_search, name='func'),
    path('calc/<int:ration>/', views.calc, name='calc'),
    path('detail/<int:food_id>/',
         views.FoodDetailView.as_view(),
         name='food_detail'),
    path('profile/edit/', views.profile_update, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),
    path('animal/create/',
         views.AnimalCreateView.as_view(),
         name='animal_create'),
    path('animal/<int:pk>/edit/',
         views.AnimalUpdateView.as_view(),
         name='animal_update'),
    path('animal/<int:pk>/delete/',
         views.AnimalDeleteView.as_view(),
         name='animal_delete'),
    path('rec-nutr-lvl/', views.recnutrlvl, name='recnutrlvl'),
    path('ration_detail/<int:ration_id>',
         views.RationDetailView.as_view(),
         name='ration_detail'),
    path('ration_delete/<int:ration_id>',
         views.RationDeleteView.as_view(),
         name='ration_delete'),
    path('food_create/', views.FoodCreateView.as_view(), name='food_create'),
    path('food_update/<int:food_id>/', views.food_update, name='food_update'),
    path('food_search_by_name/', views.food_search_by_name, name='food_search_by_name'),
    path('food_delete/<int:pk>/', views.FoodDeleteView.as_view(), name='food_delete'),
]
