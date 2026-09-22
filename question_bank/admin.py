from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter', 'question_type', 'difficulty', 'marks', 'created_by', 'last_used_date')
    list_filter = ('difficulty', 'question_type', 'chapter__subject')
    search_fields = ('question_text',)
