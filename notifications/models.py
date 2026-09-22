from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotifType(models.TextChoices):
        SUBMISSION_RECEIVED = 'SUBMISSION_RECEIVED', 'Submission Received'
        PAPER_READY = 'PAPER_READY', 'Paper Ready'
        PAYMENT_SUCCESS = 'PAYMENT_SUCCESS', 'Payment Successful'
        PAYMENT_FAILED = 'PAYMENT_FAILED', 'Payment Failed'
        GENERAL = 'GENERAL', 'General'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notif_type = models.CharField(max_length=25, choices=NotifType.choices, default=NotifType.GENERAL)
    link = models.CharField(max_length=255, blank=True, help_text="Where clicking the notification should take the user.")
    is_read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"[{self.get_notif_type_display()}] {self.message[:50]}"
