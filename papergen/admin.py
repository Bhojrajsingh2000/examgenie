from django.contrib import admin
from .models import GeneratedPaper, PaperQuestion


class PaperQuestionInline(admin.TabularInline):
    model = PaperQuestion
    extra = 0


@admin.register(GeneratedPaper)
class GeneratedPaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'blueprint', 'set_label', 'generated_by', 'generated_on')
    inlines = [PaperQuestionInline]
