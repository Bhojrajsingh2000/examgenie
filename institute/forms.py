from django import forms
from .models import SchoolClass, Section, Subject, Chapter


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Class 10'})}


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['school_class', 'name']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['school_class', 'name', 'code']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['subject', 'name', 'sequence']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-control'}),
        }
