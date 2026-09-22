"""Tests for the Paper Generation Engine and PDF Export (report sections 8.5, 8.6)."""
import shutil, tempfile
from django.test import TestCase, override_settings

from accounts.models import User
from institute.models import SchoolClass, Subject, Chapter
from question_bank.models import Question
from blueprint.models import Blueprint
from papergen.engine import generate_paper_sets, InsufficientQuestionsError
from papergen.pdf_export import render_paper_pdf

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PaperGenerationTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.coord = User.objects.create_user(username='c1', password='pass12345', role=User.Role.COORDINATOR)
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        klass = SchoolClass.objects.create(name='Class 8')
        self.subject = Subject.objects.create(school_class=klass, name='English')
        self.chapter = Chapter.objects.create(subject=self.subject, name='Grammar', sequence=1)

        for i in range(5):
            Question.objects.create(chapter=self.chapter, question_text=f'Q{i}', question_type='SHORT',
                                     answer='a', marks=2, difficulty='EASY', created_by=self.teacher)

        self.structure = [{"difficulty": "EASY", "question_type": "SHORT", "marks": 2, "count": 5}]
        self.blueprint = Blueprint.objects.create(
            subject=self.subject, exam_type='UNIT_TEST', total_marks=10,
            structure=self.structure, created_by=self.coord,
        )

    def test_generate_single_set_uses_all_available_questions(self):
        papers = generate_paper_sets(self.blueprint, num_sets=1, generated_by=self.coord)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].paper_questions.count(), 5)

    def test_generate_multiple_sets_creates_distinct_labels(self):
        papers = generate_paper_sets(self.blueprint, num_sets=3, generated_by=self.coord)
        labels = [p.set_label for p in papers]
        self.assertEqual(len(labels), len(set(labels)), "Set labels must be unique")

    def test_insufficient_questions_raises(self):
        # Require more questions than exist in the bank.
        self.blueprint.structure = [{"difficulty": "HARD", "question_type": "LONG", "marks": 5, "count": 10}]
        self.blueprint.save()
        with self.assertRaises(InsufficientQuestionsError):
            generate_paper_sets(self.blueprint, num_sets=1, generated_by=self.coord)

    def test_last_used_date_updated_after_generation(self):
        generate_paper_sets(self.blueprint, num_sets=1, generated_by=self.coord)
        used = Question.objects.filter(chapter=self.chapter, last_used_date__isnull=False)
        self.assertEqual(used.count(), 5)

    def test_pdf_export_creates_files(self):
        papers = generate_paper_sets(self.blueprint, num_sets=1, generated_by=self.coord)
        paper_name, key_name = render_paper_pdf(papers[0])
        self.assertTrue(paper_name.endswith('.pdf'))
        self.assertTrue(key_name.endswith('.pdf'))
        papers[0].refresh_from_db()
        self.assertTrue(papers[0].pdf_file)
        self.assertTrue(papers[0].answer_key_file)
