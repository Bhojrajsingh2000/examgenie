from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.views.decorators.csrf import csrf_exempt

from submissions.models import PaperSubmission
from notifications.utils import create_notification
from .models import Payment
from .gateway import PaymentGatewayClient, PaymentGatewayError

signer = TimestampSigner(salt='examgenie-secure-download')


@login_required
def initiate_payment(request, submission_pk):
    """Step 3/4 of the workflow: Teacher pays to unlock the finalized paper."""
    submission = get_object_or_404(
        PaperSubmission, pk=submission_pk, teacher=request.user, status=PaperSubmission.Status.PROCESSED
    )
    amount = settings.PAPER_DOWNLOAD_PRICE

    payment = Payment.objects.create(
        submission=submission, teacher=request.user, amount=amount, status=Payment.Status.PENDING
    )

    gateway = PaymentGatewayClient()
    try:
        order = gateway.create_order(amount_rupees=amount, receipt=f"submission-{submission.pk}-payment-{payment.pk}")
    except PaymentGatewayError as exc:
        messages.error(request, f"Could not initiate payment: {exc}")
        return redirect('submissions:my_submissions')

    payment.gateway_order_id = order['id']
    payment.save(update_fields=['gateway_order_id'])

    context = {
        'submission': submission,
        'payment': payment,
        'order_id': order['id'],
        'amount_paise': int(amount * 100),
        'razorpay_key_id': settings.RAZORPAY_KEY_ID or 'rzp_test_dev',
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_callback(request, payment_pk):
    """
    Handles the browser-side callback after checkout (Razorpay Checkout.js posts here).
    In production this is normally paired with a server-to-server webhook (payment_webhook)
    as the source of truth; the callback is used here to immediately update the UI.
    """
    payment = get_object_or_404(Payment, pk=payment_pk, teacher=request.user)
    gateway = PaymentGatewayClient()

    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', payment.gateway_order_id)
    razorpay_signature = request.POST.get('razorpay_signature', '')

    verified = gateway.verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

    if verified:
        payment.gateway_payment_id = razorpay_payment_id
        payment.gateway_signature = razorpay_signature
        payment.status = Payment.Status.SUCCESS
        payment.save()

        payment.submission.mark_paid()
        create_notification(
            user=payment.teacher,
            message=f"Payment successful for {payment.submission.subject}. Your paper is ready to download.",
            notif_type='PAYMENT_SUCCESS',
            link=f"/payments/download/{payment.submission.pk}/",
        )
        messages.success(request, "Payment successful! You can now download your paper.")
        return redirect('payments:payment_success', payment_pk=payment.pk)

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=['status'])
    create_notification(
        user=payment.teacher,
        message=f"Payment failed for {payment.submission.subject}. Please try again.",
        notif_type='PAYMENT_FAILED',
    )
    messages.error(request, "Payment verification failed. Please try again.")
    return redirect('payments:payment_failed', payment_pk=payment.pk)


@csrf_exempt
def payment_webhook(request):
    """
    Server-to-server webhook endpoint for the Payment Gateway (source of truth).
    Configure this URL in the Razorpay dashboard. Signature verification of the
    raw webhook payload should be added here using RAZORPAY webhook secret in production.
    """
    # NOTE: production implementation must verify `X-Razorpay-Signature` header
    # against settings.RAZORPAY_WEBHOOK_SECRET before trusting this payload.
    return JsonResponse({'status': 'received'})


@login_required
def payment_success(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk, teacher=request.user)
    return render(request, 'payments/payment_success.html', {'payment': payment})


@login_required
def payment_failed(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk, teacher=request.user)
    return render(request, 'payments/payment_failed.html', {'payment': payment})


@login_required
def get_secure_download_link(request, submission_pk):
    """Generates a signed, time-limited download token \u2014 only after payment succeeds."""
    submission = get_object_or_404(
        PaperSubmission, pk=submission_pk, teacher=request.user, status=PaperSubmission.Status.PAID
    )
    token = signer.sign(str(submission.pk))
    return render(request, 'payments/download_ready.html', {'submission': submission, 'token': token})


@login_required
def secure_download(request, submission_pk, token):
    """Validates the signed token (and its expiry window) before serving the finalized PDF."""
    submission = get_object_or_404(PaperSubmission, pk=submission_pk, teacher=request.user)
    max_age = settings.DOWNLOAD_LINK_EXPIRY_MINUTES * 60
    try:
        unsigned = signer.unsign(token, max_age=max_age)
    except SignatureExpired:
        messages.error(request, "This download link has expired. Please generate a new one.")
        return redirect('payments:get_secure_download_link', submission_pk=submission.pk)
    except BadSignature:
        raise Http404("Invalid download link.")

    if unsigned != str(submission.pk) or not submission.is_downloadable:
        raise Http404("Download not available.")

    return FileResponse(
        submission.finalized_pdf.open('rb'), as_attachment=True,
        filename=submission.finalized_pdf.name.split('/')[-1]
    )
