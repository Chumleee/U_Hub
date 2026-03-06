from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StudentUser


class StudentUserCreationForm(UserCreationForm):
    university = forms.CharField(max_length=150, required=False, help_text="Universidad (opcional)")
    major = forms.CharField(max_length=150, required=False, help_text="Carrera (opcional)")
    semester = forms.IntegerField(min_value=1, max_value=20, initial=1, help_text="Semestre actual")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Biografía corta")

    class Meta:
        model = StudentUser
        fields = ('username', 'email', 'university', 'major', 'semester', 'bio', 'password1', 'password2')
