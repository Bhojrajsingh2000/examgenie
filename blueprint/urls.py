from django.urls import path
from . import views

app_name = 'blueprint'

urlpatterns = [
    path('', views.blueprint_list, name='blueprint_list'),
    path('add/', views.blueprint_create, name='blueprint_create'),
    path('<int:pk>/', views.blueprint_detail, name='blueprint_detail'),
    path('<int:pk>/delete/', views.blueprint_delete, name='blueprint_delete'),
]
