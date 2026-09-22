"""WSGI config for the ExamGenie project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examgenie.settings')
application = get_wsgi_application()
