"""
Shared helper used by every other app (submissions, payments, papergen, ...)
to raise a notification without each app needing to know about email/DB details.
"""
from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def create_notification(user, message, notif_type='GENERAL', link=''):
    notification = Notification.objects.create(
        user=user, message=message, notif_type=notif_type, link=link
    )

    # Best-effort email notification as well (uses console backend in dev).
    if user.email:
        try:
            send_mail(
                subject=f"ExamGenie: {notification.get_notif_type_display()}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

    return notification
