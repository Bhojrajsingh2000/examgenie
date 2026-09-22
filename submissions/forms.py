from django import forms
from .models import PaperSubmission


class SubmissionForm(forms.ModelForm):
    """Step 1 of the workflow: Teacher Login & Submission."""
    class Meta:
        model = PaperSubmission
        fields = ['subject', 'exam_type', 'notes', 'handwritten_pdf']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Half-Yearly Exam'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'handwritten_pdf': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher is not None:
            # Teachers can only submit for subjects assigned to them.
            self.fields['subject'].queryset = teacher.subjects.all()

    def clean_handwritten_pdf(self):
        f = self.cleaned_data['handwritten_pdf']
        if not f.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Please upload a PDF file.")
        if f.size > 15 * 1024 * 1024:
            raise forms.ValidationError("File too large (max 15 MB).")
        return f


class AdminProcessForm(forms.Form):
    """Step 2 of the workflow: Admin Processing (upload finalized digital PDF)."""
    finalized_pdf = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )

    def clean_finalized_pdf(self):
        f = self.cleaned_data['finalized_pdf']
        if not f.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Please upload a PDF file.")
        return f
