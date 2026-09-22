from django.urls import path
from . import views

app_name = 'papergen'

urlpatterns = [
    path('generate/', views.generate_form, name='generate_form'),
    path('', views.paper_list, name='paper_list'),
    path('<int:pk>/preview/', views.paper_preview, name='paper_preview'),
    path('<int:pk>/download/', views.download_paper, name='download_paper'),
    path('<int:pk>/download-key/', views.download_answer_key, name='download_answer_key'),
]
