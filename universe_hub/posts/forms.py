from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {
            'content': 'Contenido del post',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Comparte una idea, avance o solicitud académica...',
                'class': 'post-modal-textarea',
            }),
        }