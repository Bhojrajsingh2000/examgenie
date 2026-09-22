from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import teacher_required, admin_required
from .models import PaperSubmission
from .forms import SubmissionForm, AdminProcessForm


@teacher_required
def submit_paper(request):
    """Step 1: Teacher Login & Submission."""
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.teacher = request.user
            submission.save()
            messages.success(request, "Paper submitted. The admin has been notified and will process it shortly.")
            return redirect('submissions:my_submissions')
    else:
        form = SubmissionForm(teacher=request.user)
    return render(request, 'submissions/submit_form.html', {'form': form})


@teacher_required
def my_submissions(request):
    submissions = PaperSubmission.objects.filter(teacher=request.user).select_related('subject')
    return render(request, 'submissions/my_submissions.html', {'submissions': submissions})


@admin_required
def pending_submissions(request):
    """Admin's queue of papers awaiting transcription (Status = SUBMITTED)."""
    submissions = PaperSubmission.objects.filter(
        status=PaperSubmission.Status.SUBMITTED
    ).select_related('teacher', 'subject')
    return render(request, 'submissions/admin_pending_list.html', {'submissions': submissions})


@admin_required
def all_submissions(request):
    submissions = PaperSubmission.objects.select_related('teacher', 'subject').all()
    return render(request, 'submissions/admin_all_list.html', {'submissions': submissions})


@admin_required
def process_submission(request, pk):
    """Step 2: Admin Processing \u2014 transcribe & upload the finalized digital PDF."""
    submission = get_object_or_404(PaperSubmission, pk=pk, status=PaperSubmission.Status.SUBMITTED)
    if request.method == 'POST':
        form = AdminProcessForm(request.POST, request.FILES)
        if form.is_valid():
            submission.mark_processed(request.user, form.cleaned_data['finalized_pdf'])
            messages.success(request, "Finalized paper uploaded. The teacher has been notified.")
            return redirect('submissions:pending_submissions')
    else:
        form = AdminProcessForm()
    return render(request, 'submissions/admin_process_form.html', {'form': form, 'submission': submission})


@teacher_required
def view_handwritten(request, pk):
    submission = get_object_or_404(PaperSubmission, pk=pk)
    if submission.teacher_id != request.user.id and request.user.role != 'ADMIN':
        raise Http404
    return FileResponse(submission.handwritten_pdf.open('rb'), filename=submission.handwritten_pdf.name.split('/')[-1])
