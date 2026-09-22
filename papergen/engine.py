"""
Paper Generation Engine
========================
Core algorithm of the Paper Generation Engine module (report section 8.5).

Given a Blueprint, this module:
  1. Reads the blueprint's structure (list of {difficulty, question_type, marks, count}).
  2. For each requirement row, queries the Question Bank filtered by the
     blueprint's subject + difficulty + question_type + marks, preferring
     questions that have NOT been used recently (last_used_date older than
     settings.QUESTION_REUSE_COOLDOWN_DAYS, or never used).
  3. Randomly samples the required number of questions for each row.
  4. Repeats the whole process once per requested "set" (Set A, Set B, Set C...),
     shuffling final question order (and, for MCQs, option order) per set so
     that no two sets look identical even if some questions repeat.
  5. Persists a GeneratedPaper + ordered PaperQuestion rows per set and
     updates each used question's last_used_date.
"""
import random
import string
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from question_bank.models import Question
from .models import GeneratedPaper, PaperQuestion


class InsufficientQuestionsError(Exception):
    """Raised when the question bank does not have enough questions to satisfy a blueprint row."""
    def __init__(self, row, available, required):
        self.row = row
        self.available = available
        self.required = required
        super().__init__(
            f"Not enough questions for {row}: need {required}, only {available} available."
        )


def _candidate_pool(subject, row, cooldown_days):
    """Return a queryset of questions matching one blueprint requirement row,
    ordered so that never-used / least-recently-used questions come first."""
    cutoff = timezone.now().date() - timedelta(days=cooldown_days)
    qs = Question.objects.filter(
        chapter__subject=subject,
        difficulty=row['difficulty'],
        question_type=row['question_type'],
        marks=row['marks'],
    )
    fresh = qs.filter(models_q_last_used_before(cutoff))
    return qs, fresh


def models_q_last_used_before(cutoff):
    from django.db.models import Q
    return Q(last_used_date__isnull=True) | Q(last_used_date__lt=cutoff)


def _pick_questions_for_row(subject, row, cooldown_days):
    all_qs, fresh_qs = _candidate_pool(subject, row, cooldown_days)
    required = row['count']

    fresh_list = list(fresh_qs)
    if len(fresh_list) >= required:
        return random.sample(fresh_list, required)

    # Not enough "fresh" questions -> top up with recently used ones as a fallback
    all_list = list(all_qs)
    if len(all_list) < required:
        raise InsufficientQuestionsError(row, len(all_list), required)

    chosen = fresh_list[:]
    remaining_pool = [q for q in all_list if q not in chosen]
    random.shuffle(remaining_pool)
    chosen.extend(remaining_pool[: required - len(chosen)])
    return chosen


def _next_set_label(existing_count):
    """Set A, Set B, Set C, ... Set Z, then AA, AB, ..."""
    letters = string.ascii_uppercase
    idx = existing_count
    label = ''
    idx += 1
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        label = letters[rem] + label
    return f"Set {label}"


@transaction.atomic
def generate_paper_sets(blueprint, num_sets, generated_by):
    """
    Generates `num_sets` distinct GeneratedPaper objects for the given blueprint.
    Returns a list of GeneratedPaper instances (without PDFs rendered yet;
    call pdf_export.render_paper_pdf() separately for each).
    """
    cooldown_days = getattr(settings, 'QUESTION_REUSE_COOLDOWN_DAYS', 45)
    subject = blueprint.subject
    existing_sets = blueprint.generated_papers.count()

    created_papers = []
    used_question_ids = set()

    for i in range(num_sets):
        # Build the pool of selected questions for this set, row by row.
        selected_by_row = []
        for row in blueprint.structure:
            picked = _pick_questions_for_row(subject, row, cooldown_days)
            selected_by_row.append(picked)

        # Flatten and shuffle the overall order for this set.
        flat_questions = [q for row_qs in selected_by_row for q in row_qs]
        random.shuffle(flat_questions)

        set_label = _next_set_label(existing_sets + i)
        paper = GeneratedPaper.objects.create(
            blueprint=blueprint,
            set_label=set_label,
            generated_by=generated_by,
        )

        for order, question in enumerate(flat_questions, start=1):
            PaperQuestion.objects.create(paper=paper, question=question, question_order=order)
            used_question_ids.add(question.id)

        created_papers.append(paper)

    # Mark all questions used across every generated set with today's date,
    # so the cooldown window correctly reduces their chance of near-term reuse.
    Question.objects.filter(id__in=used_question_ids).update(last_used_date=timezone.now().date())

    return created_papers


def shuffled_options(question):
    """Returns a shuffled copy of an MCQ's options for display, without mutating the DB record."""
    if question.question_type != Question.QuestionType.MCQ or not question.options:
        return question.options
    options = list(question.options)
    random.shuffle(options)
    return options
