from rest_framework import routers
from rest_framework.authtoken import views
from django.contrib import admin
from django.urls import include, path

from api.views import FoodViewSet, NutrientQuantityViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('food', FoodViewSet)
router.register('nq', NutrientQuantityViewSet)
# router.register(r'achievements', AchievementViewSet)

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),
    path('', include(router.urls)),
]
