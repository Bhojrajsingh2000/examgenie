from django.conf import settings
from django.db import models


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = 'MCQ', 'Multiple Choice'
        SHORT = 'SHORT', 'Short Answer'
        LONG = 'LONG', 'Long Answer'

    class Difficulty(models.TextChoices):
        EASY = 'EASY', 'Easy'
        MEDIUM = 'MEDIUM', 'Medium'
        HARD = 'HARD', 'Hard'

    chapter = models.ForeignKey('institute.Chapter', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QuestionType.choices, default=QuestionType.SHORT)
    options = models.JSONField(
        blank=True, null=True,
        help_text='For MCQ only: list of options, e.g. ["Paris", "London", "Rome", "Berlin"]'
    )
    answer = models.TextField(help_text="Correct answer / model answer used for the answer key.")
    marks = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_date = models.DateField(null=True, blank=True, help_text="Last time this question appeared in a generated paper.")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['chapter', 'difficulty', 'question_type']),
        ]

    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.question_text[:60]}"

    @property
    def subject(self):
        return self.chapter.subject
