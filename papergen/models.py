from django.conf import settings
from django.db import models


class GeneratedPaper(models.Model):
    blueprint = models.ForeignKey('blueprint.Blueprint', on_delete=models.CASCADE, related_name='generated_papers')
    set_label = models.CharField(max_length=5, help_text="Set A, Set B, Set C ...")
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    generated_on = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='generated_papers/', blank=True, null=True)
    answer_key_file = models.FileField(upload_to='answer_keys/', blank=True, null=True)

    class Meta:
        ordering = ['-generated_on']

    def __str__(self):
        return f"{self.blueprint.subject} - {self.blueprint.get_exam_type_display()} - {self.set_label}"

    @property
    def questions_ordered(self):
        return self.paper_questions.select_related('question').order_by('question_order')


class PaperQuestion(models.Model):
    """Mapping table: which questions (and in what order) belong to a GeneratedPaper."""
    paper = models.ForeignKey(GeneratedPaper, on_delete=models.CASCADE, related_name='paper_questions')
    question = models.ForeignKey('question_bank.Question', on_delete=models.CASCADE, related_name='paper_appearances')
    question_order = models.PositiveIntegerField()

    class Meta:
        ordering = ['question_order']
        unique_together = ('paper', 'question_order')

    def __str__(self):
        return f"Q{self.question_order} of {self.paper}"
