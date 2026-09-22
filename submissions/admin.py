from django.contrib import admin
from .models import PaperSubmission


@admin.register(PaperSubmission)
class PaperSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'subject', 'exam_type', 'status', 'submitted_on', 'processed_by')
    list_filter = ('status', 'subject')
