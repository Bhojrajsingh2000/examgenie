from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class ExamGenieUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('ExamGenie Role', {'fields': ('role', 'phone', 'subjects')}),
    )
