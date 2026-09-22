"""Tests for the Payment Gateway Integration & Pay-to-Download Module (report section 8.11)."""
import shutil, tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner, SignatureExpired

from accounts.models import User
from institute.models import SchoolClass, Subject
from submissions.models import PaperSubmission
from payments.models import Payment
from payments.gateway import PaymentGatewayClient

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA, RAZORPAY_KEY_ID='', RAZORPAY_KEY_SECRET='')
class PaymentGatewayTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        self.admin = User.objects.create_user(username='a1', password='pass12345', role=User.Role.ADMIN)
        klass = SchoolClass.objects.create(name='Class 6')
        self.subject = Subject.objects.create(school_class=klass, name='Geography')
        self.submission = PaperSubmission.objects.create(
            teacher=self.teacher, subject=self.subject, exam_type='Final',
            handwritten_pdf=SimpleUploadedFile('h.pdf', b'%PDF-1.4', content_type='application/pdf'),
        )
        self.submission.mark_processed(
            self.admin, SimpleUploadedFile('f.pdf', b'%PDF-1.4', content_type='application/pdf')
        )

    def test_dev_fallback_order_creation(self):
        gateway = PaymentGatewayClient()
        order = gateway.create_order(amount_rupees=49.0, receipt='r1')
        self.assertIn('id', order)
        self.assertEqual(order['amount'], 4900)

    def test_dev_fallback_signature_always_verifies(self):
        gateway = PaymentGatewayClient()
        self.assertTrue(gateway.verify_signature('order_x', 'pay_x', 'sig_x'))

    def test_successful_payment_unlocks_download(self):
        payment = Payment.objects.create(
            submission=self.submission, teacher=self.teacher, amount=49.0,
            status=Payment.Status.SUCCESS, gateway_payment_id='pay_dev_1',
        )
        self.submission.mark_paid()
        self.submission.refresh_from_db()
        self.assertTrue(self.submission.is_downloadable)
        self.assertEqual(payment.status, Payment.Status.SUCCESS)

    def test_secure_token_round_trip(self):
        signer = TimestampSigner(salt='examgenie-secure-download')
        token = signer.sign(str(self.submission.pk))
        value = signer.unsign(token, max_age=1800)
        self.assertEqual(value, str(self.submission.pk))

    def test_secure_token_expires(self):
        signer = TimestampSigner(salt='examgenie-secure-download')
        token = signer.sign(str(self.submission.pk))
        with self.assertRaises(SignatureExpired):
            signer.unsign(token, max_age=-1)  # already expired
