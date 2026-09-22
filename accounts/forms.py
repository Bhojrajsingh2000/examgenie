from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class ExamGenieLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserCreateForm(UserCreationForm):
    """Used by the Administrator to create Teacher / Coordinator accounts."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'subjects']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('subjects',):
                field.widget.attrs.setdefault('class', 'form-control')
