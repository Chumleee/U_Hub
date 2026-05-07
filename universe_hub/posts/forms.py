from django import forms
from .models import Post, Project, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'attachment']
        labels = {
            'content': 'Contenido del post',
            'image': 'Agregar imagen',
            'attachment': 'Agregar archivo',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'post-input',
                'rows': 4,
                'placeholder': '¿Qué quieres compartir hoy?'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'post-file-input',
                'accept': 'image/*'
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'post-file-input',
                'accept': '.pdf,.txt,.doc,.docx'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        attachment = cleaned_data.get('attachment')

        if not content and not image and not attachment:
            raise forms.ValidationError(
                'La publicación debe tener texto, una imagen o un archivo.'
            )

        return cleaned_data


CAREER_CHOICES = [
    ('engineering', 'Ingeniería'),
    ('design', 'Diseño'),
    ('business', 'Negocios'),
    ('law', 'Derecho'),
    ('health', 'Salud'),
    ('arts', 'Artes'),
    ('other', 'Otra'),
]


class ProjectForm(forms.ModelForm):
    target_careers = forms.MultipleChoiceField(
        choices=CAREER_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Perfiles / Carreras buscadas'
    )

    required_skills = forms.CharField(
        required=False,
        label='Habilidades específicas necesarias',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ejemplo: Programación en Python, Liderazgo, Edición de video',
            'class': 'project-textarea',
        })
    )
    class Meta:
        model = Project
        fields = [
            'title',
            'problem_and_goal',
            'project_type',
            'stage',
            'vacancies',
            'target_careers',
            'required_skills',
            'work_mode',
            'application_deadline',
            'incentive',
        ]
        labels = {
            'title': 'Título del Proyecto',
            'problem_and_goal': 'Descripción del Problema y Objetivo',
            'project_type': 'Tipo de Proyecto',
            'stage': '¿Qué tan avanzado está el proyecto?',
            'vacancies': 'Personas requeridas (Vacantes)',
            'work_mode': 'Modalidad de trabajo',
            'application_deadline': 'Fecha límite para postularse',
            'incentive': 'Incentivo / Recompensa',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'App para encontrar estacionamiento en la universidad',
                'class': 'project-input',
            }),
            'problem_and_goal': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '¿Qué problema intentas resolver y qué quieres lograr?',
                'class': 'project-textarea',
            }),
            'project_type': forms.Select(attrs={
                'class': 'project-select',
            }),
            'stage': forms.Select(attrs={
                'class': 'project-select',
            }),
            'application_deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'project-input',
            }),
            'vacancies': forms.NumberInput(attrs={
                'min': 1,
                'max': 50,
                'class': 'project-input',
            }),
            'work_mode': forms.Select(attrs={
                'class': 'project-select',
            }),
            'incentive': forms.TextInput(attrs={
                'placeholder': 'Ejemplo: Créditos académicos, posible negocio o networking',
                'class': 'project-input',
            }),
        }

    def clean_vacancies(self):
        vacancies = self.cleaned_data.get('vacancies')
        if vacancies is not None and vacancies < 1:
            raise forms.ValidationError('Debe haber al menos 1 vacante.')
        return vacancies

    def clean_required_skills(self):
        skills = self.cleaned_data.get('required_skills', '').strip()
        return skills

    def save(self, commit=True):
        instance = super().save(commit=False)

        careers = self.cleaned_data.get('target_careers', [])
        instance.target_careers = ', '.join(careers)

        skills = self.cleaned_data.get('required_skills', '').strip()
        instance.required_skills = skills

        if commit:
            instance.save()

        return instance
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Escribe un comentario...',
                'class': 'comment-input',
            }),
        }
    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('El comentario no puede estar vacío.')
        return content