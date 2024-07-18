from django.urls import path
from calc import views

app_name = 'calc'

urlpatterns = [
    path('', views.index, name='index'),
    path('calc/<int:ration>/', views.calc, name='calc'),
    path('profile/edit/', views.profile_update, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),
    path('rec-nutr-lvl/', views.recnutrlvl, name='recnutrlvl'),
    path('ration_detail/<int:ration_id>',
         views.RationDetailView.as_view(),
         name='ration_detail'),
    path('ration_delete/<int:ration_id>',
         views.RationDeleteView.as_view(),
         name='ration_delete'),
    path('export/', views.data_export, name='export'),
    path('import/', views.data_import, name='import'),
    path('rations/', views.SearchRationListView.as_view(),
         name='ration_list')
     
]
