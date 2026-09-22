from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for ExamGenie.
    Every user has exactly one role which drives dashboard routing
    and access control across the whole system.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        TEACHER = 'TEACHER', 'Teacher'
        COORDINATOR = 'COORDINATOR', 'Exam Coordinator'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TEACHER)
    phone = models.CharField(max_length=15, blank=True)
    subjects = models.ManyToManyField(
        'institute.Subject', blank=True, related_name='teachers',
        help_text="Subjects this teacher is authorised to manage."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher_role(self):
        return self.role == self.Role.TEACHER

    @property
    def is_coordinator_role(self):
        return self.role == self.Role.COORDINATOR
