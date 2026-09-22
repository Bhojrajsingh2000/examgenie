"""
PDF Export Module (report section 8.6).
Renders a GeneratedPaper into a print-ready question-paper PDF and a
separate answer-key PDF.

Tries WeasyPrint first (best rendering, needs system libs: libpango,
libcairo — available on a normal VPS/Linux server). Falls back
automatically to xhtml2pdf (pure-Python, no system libs needed) when
WeasyPrint isn't installed or its native libraries aren't available —
this is the case on platforms like PythonAnywhere's free/Hacker plans.
"""
import io

from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from .engine import shuffled_options


def _html_to_pdf_bytes(html_string):
    """Converts an HTML string to PDF bytes, preferring WeasyPrint and
    transparently falling back to xhtml2pdf if WeasyPrint is unavailable."""
    try:
        from weasyprint import HTML
        return HTML(string=html_string).write_pdf()
    except (ImportError, OSError):
        # OSError covers WeasyPrint being installed but missing native
        # libs (libpango/libcairo) — common on restricted hosts.
        from xhtml2pdf import pisa
        buffer = io.BytesIO()
        pisa.CreatePDF(src=html_string, dest=buffer)
        return buffer.getvalue()


def render_paper_pdf(paper):
    """Renders and saves both the question paper PDF and the answer key PDF
    for a single GeneratedPaper instance. Returns (paper_pdf_name, answer_key_pdf_name)."""
    questions = list(paper.questions_ordered)

    # Attach shuffled MCQ options for display purposes only.
    for pq in questions:
        pq.display_options = shuffled_options(pq.question)

    context = {
        'paper': paper,
        'blueprint': paper.blueprint,
        'subject': paper.blueprint.subject,
        'questions': questions,
        'total_marks': paper.blueprint.total_marks,
    }

    # ---- Question paper (no answers) ----
    paper_html = render_to_string('papergen/paper_pdf_template.html', context)
    paper_pdf_bytes = _html_to_pdf_bytes(paper_html)
    paper_filename = f"{paper.blueprint.subject.name}_{paper.blueprint.exam_type}_{paper.set_label}.pdf".replace(' ', '_')
    paper.pdf_file.save(paper_filename, ContentFile(paper_pdf_bytes), save=False)

    # ---- Answer key (with answers) ----
    key_html = render_to_string('papergen/answer_key_pdf_template.html', context)
    key_pdf_bytes = _html_to_pdf_bytes(key_html)
    key_filename = f"AnswerKey_{paper.blueprint.subject.name}_{paper.blueprint.exam_type}_{paper.set_label}.pdf".replace(' ', '_')
    paper.answer_key_file.save(key_filename, ContentFile(key_pdf_bytes), save=False)

    paper.save(update_fields=['pdf_file', 'answer_key_file'])
    return paper.pdf_file.name, paper.answer_key_file.name

