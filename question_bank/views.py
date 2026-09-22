from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import teacher_required, staff_required
from .models import Question
from .forms import QuestionForm, QuestionFilterForm, BulkImportForm
from .utils import bulk_import_questions


@teacher_required
def question_list(request):
    questions = Question.objects.select_related('chapter', 'chapter__subject').filter(created_by=request.user)
    filter_form = QuestionFilterForm(request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('chapter'):
            questions = questions.filter(chapter__name__icontains=data['chapter'])
        if data.get('difficulty'):
            questions = questions.filter(difficulty=data['difficulty'])
        if data.get('question_type'):
            questions = questions.filter(question_type=data['question_type'])
        if data.get('q'):
            questions = questions.filter(question_text__icontains=data['q'])

    paginator = Paginator(questions, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'question_bank/question_list.html', {'page_obj': page, 'filter_form': filter_form})


@teacher_required
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            messages.success(request, "Question added to the bank.")
            return redirect('question_bank:question_list')
    else:
        form = QuestionForm()
    return render(request, 'question_bank/question_form.html', {'form': form, 'mode': 'Add'})


@teacher_required
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated.")
            return redirect('question_bank:question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'question_bank/question_form.html', {'form': form, 'mode': 'Edit'})


@teacher_required
def question_delete(request, pk):
    get_object_or_404(Question, pk=pk, created_by=request.user).delete()
    messages.success(request, "Question deleted.")
    return redirect('question_bank:question_list')


@staff_required
def bulk_import(request):
    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            created, errors = bulk_import_questions(
                form.cleaned_data['file'], form.cleaned_data['chapter'], request.user
            )
            if created:
                messages.success(request, f"{created} question(s) imported successfully.")
            for err in errors:
                messages.warning(request, err)
            return redirect('question_bank:bulk_import')
    else:
        form = BulkImportForm()
    return render(request, 'question_bank/bulk_import.html', {'form': form})
