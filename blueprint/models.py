from django.db import models


class Blueprint(models.Model):
    """
    Defines the pattern of a paper: total marks and a structured
    breakdown of how many questions of each type/difficulty/marks
    should be picked from the question bank.
    """
    class ExamType(models.TextChoices):
        UNIT_TEST = 'UNIT_TEST', 'Unit Test'
        HALF_YEARLY = 'HALF_YEARLY', 'Half-Yearly'
        FINAL = 'FINAL', 'Final Examination'

    subject = models.ForeignKey('institute.Subject', on_delete=models.CASCADE, related_name='blueprints')
    exam_type = models.CharField(max_length=20, choices=ExamType.choices)
    total_marks = models.PositiveIntegerField()
    structure = models.JSONField(
        help_text=(
            'List of requirement rows, e.g. '
            '[{"difficulty": "EASY", "question_type": "MCQ", "marks": 1, "count": 5}, '
            '{"difficulty": "MEDIUM", "question_type": "SHORT", "marks": 3, "count": 5}, '
            '{"difficulty": "HARD", "question_type": "LONG", "marks": 5, "count": 4}]'
        )
    )
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.get_exam_type_display()} ({self.total_marks} marks)"

    def structure_total_marks(self):
        return sum(row['marks'] * row['count'] for row in self.structure)

    def structure_total_questions(self):
        return sum(row['count'] for row in self.structure)
