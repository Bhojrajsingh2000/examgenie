from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ExamGenieLoginForm, UserCreateForm
from .permissions import admin_required
from question_bank.models import Question
from papergen.models import GeneratedPaper
from submissions.models import PaperSubmission
from blueprint.models import Blueprint


class ExamGenieLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = ExamGenieLoginForm
    redirect_authenticated_user = True


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """Routes each role to a tailored dashboard with relevant summary data."""
    user = request.user

    if user.role == 'ADMIN':
        context = {
            'pending_submissions': PaperSubmission.objects.filter(status='SUBMITTED').count(),
            'total_questions': Question.objects.count(),
            'total_papers_generated': GeneratedPaper.objects.count(),
        }
        return render(request, 'accounts/dashboard_admin.html', context)

    if user.role == 'TEACHER':
        context = {
            'my_questions': Question.objects.filter(created_by=user).count(),
            'my_submissions': PaperSubmission.objects.filter(teacher=user).order_by('-submitted_on')[:5],
        }
        return render(request, 'accounts/dashboard_teacher.html', context)

    # COORDINATOR
    context = {
        'blueprints': Blueprint.objects.count(),
        'recent_papers': GeneratedPaper.objects.order_by('-generated_on')[:5],
    }
    return render(request, 'accounts/dashboard_coordinator.html', context)


@admin_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect('accounts:create_user')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/create_user.html', {'form': form})
