"""Root URL configuration for ExamGenie."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('institute/', include('institute.urls')),
    path('questions/', include('question_bank.urls')),
    path('blueprints/', include('blueprint.urls')),
    path('papers/', include('papergen.urls')),
    path('submissions/', include('submissions.urls')),
    path('notifications/', include('notifications.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
