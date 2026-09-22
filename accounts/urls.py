from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.ExamGenieLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/create/', views.create_user, name='create_user'),
]
