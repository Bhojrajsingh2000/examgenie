from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from accounts.permissions import admin_required
from .models import SchoolClass, Section, Subject, Chapter
from .forms import SchoolClassForm, SectionForm, SubjectForm, ChapterForm


@admin_required
def class_list(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class added.")
            return redirect('institute:class_list')
    else:
        form = SchoolClassForm()
    classes = SchoolClass.objects.prefetch_related('sections', 'subjects').all()
    return render(request, 'institute/class_list.html', {'classes': classes, 'form': form})


@admin_required
def class_delete(request, pk):
    get_object_or_404(SchoolClass, pk=pk).delete()
    messages.success(request, "Class deleted.")
    return redirect('institute:class_list')


@admin_required
def section_list(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Section added.")
            return redirect('institute:section_list')
    else:
        form = SectionForm()
    sections = Section.objects.select_related('school_class').all()
    return render(request, 'institute/section_list.html', {'sections': sections, 'form': form})


@admin_required
def subject_list(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject added.")
            return redirect('institute:subject_list')
    else:
        form = SubjectForm()
    subjects = Subject.objects.select_related('school_class').prefetch_related('chapters').all()
    return render(request, 'institute/subject_list.html', {'subjects': subjects, 'form': form})


@admin_required
def subject_delete(request, pk):
    get_object_or_404(Subject, pk=pk).delete()
    messages.success(request, "Subject deleted.")
    return redirect('institute:subject_list')


@admin_required
def chapter_list(request):
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Chapter added.")
            return redirect('institute:chapter_list')
    else:
        form = ChapterForm()
    chapters = Chapter.objects.select_related('subject').all()
    return render(request, 'institute/chapter_list.html', {'chapters': chapters, 'form': form})


@admin_required
def chapter_delete(request, pk):
    get_object_or_404(Chapter, pk=pk).delete()
    messages.success(request, "Chapter deleted.")
    return redirect('institute:chapter_list')
