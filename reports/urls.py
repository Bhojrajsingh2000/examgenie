from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generation/', views.generation_log, name='generation_log'),
    path('submissions/', views.submission_log, name='submission_log'),
    path('payments/', views.payment_log, name='payment_log'),
]
