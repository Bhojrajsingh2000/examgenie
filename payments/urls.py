from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:submission_pk>/', views.initiate_payment, name='initiate_payment'),
    path('callback/<int:payment_pk>/', views.payment_callback, name='payment_callback'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
    path('success/<int:payment_pk>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_pk>/', views.payment_failed, name='payment_failed'),
    path('download-link/<int:submission_pk>/', views.get_secure_download_link, name='get_secure_download_link'),
    path('download/<int:submission_pk>/<str:token>/', views.secure_download, name='secure_download'),
]
