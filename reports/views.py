from django.db.models import Count, Sum, Q
from django.shortcuts import render

from accounts.permissions import staff_required, admin_required
from papergen.models import GeneratedPaper
from submissions.models import PaperSubmission
from payments.models import Payment


@staff_required
def generation_log(request):
    """History of every paper generated \u2014 who, when, for which class/subject/exam."""
    papers = GeneratedPaper.objects.select_related(
        'blueprint', 'blueprint__subject', 'generated_by'
    ).order_by('-generated_on')

    subject_id = request.GET.get('subject')
    if subject_id:
        papers = papers.filter(blueprint__subject_id=subject_id)

    return render(request, 'reports/generation_log.html', {'papers': papers})


@admin_required
def submission_log(request):
    """Full audit trail of the Teacher-to-Admin workflow, with status breakdown."""
    submissions = PaperSubmission.objects.select_related('teacher', 'subject', 'processed_by').order_by('-submitted_on')
    status_counts = submissions.values('status').annotate(total=Count('id'))
    return render(request, 'reports/submission_log.html', {
        'submissions': submissions, 'status_counts': status_counts,
    })


@admin_required
def payment_log(request):
    """Payment history and revenue summary for the pay-to-download workflow."""
    payments = Payment.objects.select_related('submission', 'teacher').order_by('-created_on')
    total_revenue = payments.filter(status=Payment.Status.SUCCESS).aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'reports/payment_log.html', {
        'payments': payments, 'total_revenue': total_revenue,
    })
