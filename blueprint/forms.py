import json
from django import forms
from .models import Blueprint


class BlueprintForm(forms.ModelForm):
    structure = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 6,
            'placeholder': '[{"difficulty": "EASY", "question_type": "MCQ", "marks": 1, "count": 5}, ...]'
        }),
        help_text="JSON list describing marks/difficulty/type distribution."
    )

    class Meta:
        model = Blueprint
        fields = ['subject', 'exam_type', 'total_marks', 'structure']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_structure(self):
        raw = self.cleaned_data['structure']
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError("Structure must be valid JSON.")
        if not isinstance(data, list) or not data:
            raise forms.ValidationError("Structure must be a non-empty JSON list.")
        for row in data:
            for key in ('difficulty', 'question_type', 'marks', 'count'):
                if key not in row:
                    raise forms.ValidationError(f"Each row must include '{key}'.")
        return data

    def clean(self):
        cleaned = super().clean()
        structure = cleaned.get('structure')
        total_marks = cleaned.get('total_marks')
        if structure and total_marks:
            computed = sum(row['marks'] * row['count'] for row in structure)
            if computed != total_marks:
                raise forms.ValidationError(
                    f"Structure adds up to {computed} marks, which does not match Total Marks ({total_marks})."
                )
        return cleaned
