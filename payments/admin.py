from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'teacher', 'amount', 'status', 'gateway_payment_id', 'created_on')
    list_filter = ('status',)
