from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect(notification.link or 'notifications:notification_list')


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:notification_list')
