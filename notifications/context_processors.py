"""Makes the unread notification count/list available in every template (bell icon in the navbar)."""
def unread_notifications(request):
    if not request.user.is_authenticated:
        return {}
    qs = request.user.notifications.filter(is_read=False)
    return {
        'unread_notifications': qs[:8],
        'unread_notifications_count': qs.count(),
    }
