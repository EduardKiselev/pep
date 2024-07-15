from django.urls import path
from food import views

app_name = 'food'

urlpatterns = [
     path('detail/<int:food_id>/',
          views.FoodDetailView.as_view(),
          name='food_detail'),
     path('func/', views.food_search, name='func'),
     path('create/', views.food_create,
          name='food_create'),        
     path('update/<int:food_id>/', views.food_update,
          name='food_update'),
     path('search_by_name/', views.food_search_by_name,
          name='food_search_by_name'),
     path('delete/<int:pk>/', views.FoodDeleteView.as_view(),
          name='food_delete'),
]
