from django.contrib.auth.models import AbstractUser
from django.db import models


class StudentUser(AbstractUser):
    university = models.CharField(max_length=150, blank=True)
    major = models.CharField(max_length=150, blank=True)     # carrera
    semester = models.PositiveSmallIntegerField(default=1)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.major}"

class Follow(models.Model):
    follower = models.ForeignKey(
        StudentUser,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        StudentUser,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} → {self.following}"
