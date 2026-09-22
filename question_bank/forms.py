from django import forms
from .models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['chapter', 'question_type', 'question_text', 'options', 'answer', 'marks', 'difficulty']
        widgets = {
            'chapter': forms.Select(attrs={'class': 'form-select'}),
            'question_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_question_type'}),
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'options': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'For MCQ only \u2014 JSON list, e.g. ["Paris", "London", "Rome", "Berlin"]'
            }),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('question_type') == Question.QuestionType.MCQ and not cleaned.get('options'):
            self.add_error('options', "MCQ questions must include an options list.")
        return cleaned


class QuestionFilterForm(forms.Form):
    chapter = forms.CharField(required=False)
    difficulty = forms.ChoiceField(required=False, choices=[('', 'Any')] + list(Question.Difficulty.choices))
    question_type = forms.ChoiceField(required=False, choices=[('', 'Any')] + list(Question.QuestionType.choices))
    q = forms.CharField(required=False, label='Search text')


class BulkImportForm(forms.Form):
    chapter = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'class': 'form-select'}))
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.csv'}),
        help_text="Excel/CSV with columns: question_text, question_type, options, answer, marks, difficulty"
    )

    def __init__(self, *args, **kwargs):
        from institute.models import Chapter
        super().__init__(*args, **kwargs)
        self.fields['chapter'].queryset = Chapter.objects.select_related('subject').all()
