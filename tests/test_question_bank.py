"""Tests for the Question Bank Module (report section 8.3)."""
import io
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from institute.models import SchoolClass, Subject, Chapter
from question_bank.models import Question
from question_bank.utils import bulk_import_questions


class QuestionBankTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        self.klass = SchoolClass.objects.create(name='Class 9')
        self.subject = Subject.objects.create(school_class=self.klass, name='Science')
        self.chapter = Chapter.objects.create(subject=self.subject, name='Light', sequence=1)

    def test_create_question(self):
        q = Question.objects.create(
            chapter=self.chapter, question_text='What is refraction?', question_type='SHORT',
            answer='Bending of light', marks=3, difficulty='MEDIUM', created_by=self.teacher,
        )
        self.assertEqual(q.subject, self.subject)
        self.assertIn(q, Question.objects.filter(chapter=self.chapter))

    def test_bulk_import_csv(self):
        csv_content = (
            "question_text,question_type,options,answer,marks,difficulty\n"
            "What is gravity?,SHORT,,A force of attraction,2,EASY\n"
            "Pick the primary colour,MCQ,\"[\"\"Red\"\", \"\"Green\"\", \"\"Blue\"\"]\",Red,1,EASY\n"
        )
        file_obj = SimpleUploadedFile('questions.csv', csv_content.encode('utf-8'), content_type='text/csv')
        created, errors = bulk_import_questions(file_obj, self.chapter, self.teacher)
        self.assertEqual(created, 2)
        self.assertEqual(Question.objects.filter(chapter=self.chapter).count(), 2)

    def test_bulk_import_missing_column_reports_error(self):
        csv_content = "question_text,question_type,answer\nIncomplete row,SHORT,ans\n"
        file_obj = SimpleUploadedFile('bad.csv', csv_content.encode('utf-8'), content_type='text/csv')
        created, errors = bulk_import_questions(file_obj, self.chapter, self.teacher)
        self.assertEqual(created, 0)
        self.assertTrue(errors)
