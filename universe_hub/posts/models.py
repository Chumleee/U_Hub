from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_project = models.BooleanField(default=False)  # False = post normal, True = project teaser

    def __str__(self):
        return f"Post #{self.id} by {self.author}"

class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Abierto a colaboración'),
        ('in_progress', 'En desarrollo'),
        ('closed', 'Cerrado'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300)
    description = models.TextField()
    required_skills = models.TextField(
        help_text='Lista de habilidades requeridas separadas por comas'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Garantizar que al menos uno de post o project esté definido
        from django.core.exceptions import ValidationError
        if not self.post and not self.project:
            raise ValidationError('El comentario debe pertenecer a un post o a un proyecto.')

    def __str__(self):
        target = self.post or self.project
        return f"Comment by {self.author} on {target}"

class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} ♥ Post #{self.post_id}"

