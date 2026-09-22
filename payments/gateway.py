"""
Payment Gateway Integration & Pay-to-Download Module (report section 8.11).

Thin wrapper around the Razorpay SDK so the rest of the app (views, tests)
never talks to the third-party library directly. Swap this file's internals
to plug in a different provider (Stripe, PayU, ...) without touching views.
"""
import razorpay
from django.conf import settings


class PaymentGatewayError(Exception):
    pass


class PaymentGatewayClient:
    def __init__(self):
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            self._client = None
        else:
            self._client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, amount_rupees, receipt):
        """Creates a Razorpay order. Amount must be sent to Razorpay in paise (INR * 100)."""
        if self._client is None:
            # Local/dev fallback so the flow is testable without real gateway keys.
            return {'id': f'order_dev_{receipt}', 'amount': int(amount_rupees * 100), 'currency': 'INR'}
        try:
            return self._client.order.create({
                'amount': int(amount_rupees * 100),
                'currency': 'INR',
                'receipt': receipt,
                'payment_capture': 1,
            })
        except Exception as exc:
            raise PaymentGatewayError(str(exc)) from exc

    def verify_signature(self, order_id, payment_id, signature):
        """Verifies the callback signature Razorpay sends back to the browser after checkout."""
        if self._client is None:
            # Dev fallback: accept anything so the pay-to-download flow can be exercised locally.
            return True
        try:
            self._client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
