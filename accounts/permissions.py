"""
Role-based access-control helpers used across every app.
Use the *_required decorators for function-based views and the
*RequiredMixin classes for class-based views.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


admin_required = role_required('ADMIN')
teacher_required = role_required('TEACHER')
coordinator_required = role_required('COORDINATOR')
staff_required = role_required('ADMIN', 'COORDINATOR')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'TEACHER'


class CoordinatorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'COORDINATOR'


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Admin or Coordinator."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ('ADMIN', 'COORDINATOR')
