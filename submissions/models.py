from django.conf import settings
from django.db import models
from django.utils import timezone


def handwritten_upload_path(instance, filename):
    return f"handwritten_submissions/{instance.teacher_id}/{filename}"


def finalized_upload_path(instance, filename):
    return f"finalized_papers/{instance.teacher_id}/{filename}"


class PaperSubmission(models.Model):
    """
    Implements the Teacher-to-Admin Paper Processing workflow:
    Teacher submits a handwritten PDF -> Admin transcribes & uploads the
    finalized digital PDF -> Teacher pays -> Teacher downloads.
    """
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        PROCESSED = 'PROCESSED', 'Processed'
        PAID = 'PAID', 'Paid & Downloaded'

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='paper_submissions')
    subject = models.ForeignKey('institute.Subject', on_delete=models.CASCADE, related_name='submissions')
    exam_type = models.CharField(max_length=100, help_text="e.g. Unit Test 1, Half-Yearly, Final")
    notes = models.TextField(blank=True, help_text="Any instructions for the Admin.")

    handwritten_pdf = models.FileField(upload_to=handwritten_upload_path)
    finalized_pdf = models.FileField(upload_to=finalized_upload_path, blank=True, null=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUBMITTED)

    submitted_on = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='processed_submissions'
    )

    class Meta:
        ordering = ['-submitted_on']

    def __str__(self):
        return f"{self.subject} submission by {self.teacher} [{self.status}]"

    def mark_processed(self, admin_user, finalized_pdf_file):
        self.finalized_pdf = finalized_pdf_file
        self.status = self.Status.PROCESSED
        self.processed_by = admin_user
        self.processed_on = timezone.now()
        self.save(update_fields=['finalized_pdf', 'status', 'processed_by', 'processed_on'])

    def mark_paid(self):
        self.status = self.Status.PAID
        self.save(update_fields=['status'])

    @property
    def is_downloadable(self):
        return self.status == self.Status.PAID and bool(self.finalized_pdf)
