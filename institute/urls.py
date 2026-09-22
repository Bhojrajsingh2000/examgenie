from django.urls import path
from . import views

app_name = 'institute'

urlpatterns = [
    path('classes/', views.class_list, name='class_list'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('sections/', views.section_list, name='section_list'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    path('chapters/', views.chapter_list, name='chapter_list'),
    path('chapters/<int:pk>/delete/', views.chapter_delete, name='chapter_delete'),
]
