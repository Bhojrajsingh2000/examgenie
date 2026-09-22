"""
Wires the submission workflow into the Notification Module (report 8.10):
  - New submission  -> notify all Admins.
  - Marked processed -> notify the submitting Teacher.
Payment confirmation notifications are triggered from the payments app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import User
from notifications.utils import create_notification
from .models import PaperSubmission


@receiver(post_save, sender=PaperSubmission)
def notify_on_submission(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            create_notification(
                user=admin,
                message=f"New paper submission from {instance.teacher.get_full_name() or instance.teacher.username} "
                        f"for {instance.subject} ({instance.exam_type}).",
                notif_type='SUBMISSION_RECEIVED',
                link=f"/submissions/admin/{instance.pk}/process/",
            )


_PREVIOUS_STATUS = {}


@receiver(pre_save, sender=PaperSubmission)
def _capture_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            _PREVIOUS_STATUS[instance.pk] = PaperSubmission.objects.get(pk=instance.pk).status
        except PaperSubmission.DoesNotExist:
            _PREVIOUS_STATUS[instance.pk] = None


@receiver(post_save, sender=PaperSubmission)
def notify_on_processed(sender, instance, created, **kwargs):
    if created:
        return
    previous = _PREVIOUS_STATUS.get(instance.pk)
    if previous == PaperSubmission.Status.SUBMITTED and instance.status == PaperSubmission.Status.PROCESSED:
        create_notification(
            user=instance.teacher,
            message=f"Your paper for {instance.subject} ({instance.exam_type}) has been digitised and is ready. "
                    f"Complete payment to download it.",
            notif_type='PAPER_READY',
            link=f"/payments/initiate/{instance.pk}/",
        )
