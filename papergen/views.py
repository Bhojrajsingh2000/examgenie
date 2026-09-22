from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import staff_required
from blueprint.models import Blueprint
from .engine import generate_paper_sets, InsufficientQuestionsError
from .pdf_export import render_paper_pdf
from .models import GeneratedPaper


@staff_required
def generate_form(request):
    blueprints = Blueprint.objects.select_related('subject').all()
    if request.method == 'POST':
        blueprint = get_object_or_404(Blueprint, pk=request.POST.get('blueprint'))
        num_sets = int(request.POST.get('num_sets', 1))
        try:
            papers = generate_paper_sets(blueprint, num_sets, request.user)
        except InsufficientQuestionsError as exc:
            messages.error(request, f"Cannot generate paper: {exc}")
            return redirect('papergen:generate_form')

        for paper in papers:
            render_paper_pdf(paper)

        messages.success(request, f"{len(papers)} paper set(s) generated successfully.")
        return redirect('papergen:paper_list')

    return render(request, 'papergen/generate_form.html', {'blueprints': blueprints})


@staff_required
def paper_list(request):
    papers = GeneratedPaper.objects.select_related('blueprint', 'blueprint__subject').all()
    return render(request, 'papergen/paper_list.html', {'papers': papers})


@staff_required
def paper_preview(request, pk):
    paper = get_object_or_404(GeneratedPaper, pk=pk)
    return render(request, 'papergen/paper_preview.html', {'paper': paper, 'questions': paper.questions_ordered})


@staff_required
def download_paper(request, pk):
    paper = get_object_or_404(GeneratedPaper, pk=pk)
    if not paper.pdf_file:
        raise Http404("PDF not generated yet.")
    return FileResponse(paper.pdf_file.open('rb'), as_attachment=True, filename=paper.pdf_file.name.split('/')[-1])


@staff_required
def download_answer_key(request, pk):
    paper = get_object_or_404(GeneratedPaper, pk=pk)
    if not paper.answer_key_file:
        raise Http404("Answer key not generated yet.")
    return FileResponse(paper.answer_key_file.open('rb'), as_attachment=True, filename=paper.answer_key_file.name.split('/')[-1])
