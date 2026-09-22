"""Tests for the Teacher-to-Admin Paper Processing workflow (report section 6.1 / 8.8-8.10)."""
import shutil, tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from institute.models import SchoolClass, Subject
from submissions.models import PaperSubmission
from notifications.models import Notification

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class SubmissionWorkflowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_user(username='a1', password='pass12345', role=User.Role.ADMIN)
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        klass = SchoolClass.objects.create(name='Class 7')
        self.subject = Subject.objects.create(school_class=klass, name='History')

    def _handwritten_file(self):
        return SimpleUploadedFile('handwritten.pdf', b'%PDF-1.4 test', content_type='application/pdf')

    def test_step1_submission_creates_admin_notification(self):
        submission = PaperSubmission.objects.create(
            teacher=self.teacher, subject=self.subject, exam_type='Unit Test 1',
            handwritten_pdf=self._handwritten_file(),
        )
        self.assertEqual(submission.status, PaperSubmission.Status.SUBMITTED)
        notif = Notification.objects.filter(user=self.admin, notif_type='SUBMISSION_RECEIVED')
        self.assertTrue(notif.exists())

    def test_step2_admin_processing_notifies_teacher_and_changes_status(self):
        submission = PaperSubmission.objects.create(
            teacher=self.teacher, subject=self.subject, exam_type='Unit Test 1',
            handwritten_pdf=self._handwritten_file(),
        )
        finalized = SimpleUploadedFile('final.pdf', b'%PDF-1.4 final', content_type='application/pdf')
        submission.mark_processed(self.admin, finalized)
        submission.refresh_from_db()

        self.assertEqual(submission.status, PaperSubmission.Status.PROCESSED)
        self.assertEqual(submission.processed_by, self.admin)
        self.assertTrue(Notification.objects.filter(user=self.teacher, notif_type='PAPER_READY').exists())

    def test_not_downloadable_until_paid(self):
        submission = PaperSubmission.objects.create(
            teacher=self.teacher, subject=self.subject, exam_type='Unit Test 1',
            handwritten_pdf=self._handwritten_file(),
        )
        finalized = SimpleUploadedFile('final.pdf', b'%PDF-1.4 final', content_type='application/pdf')
        submission.mark_processed(self.admin, finalized)
        self.assertFalse(submission.is_downloadable)

        submission.mark_paid()
        submission.refresh_from_db()
        self.assertTrue(submission.is_downloadable)
