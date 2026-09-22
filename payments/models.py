from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    submission = models.ForeignKey(
        'submissions.PaperSubmission', on_delete=models.CASCADE, related_name='payments'
    )
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')

    gateway_order_id = models.CharField(max_length=100, blank=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    gateway_signature = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"Payment #{self.id} - {self.submission} - {self.status}"
