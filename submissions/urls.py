from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('submit/', views.submit_paper, name='submit_paper'),
    path('my/', views.my_submissions, name='my_submissions'),
    path('<int:pk>/handwritten/', views.view_handwritten, name='view_handwritten'),

    path('admin/pending/', views.pending_submissions, name='pending_submissions'),
    path('admin/all/', views.all_submissions, name='all_submissions'),
    path('admin/<int:pk>/process/', views.process_submission, name='process_submission'),
]
