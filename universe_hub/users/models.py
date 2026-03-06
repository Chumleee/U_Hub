from django.contrib.auth.models import AbstractUser
from django.db import models


class StudentUser(AbstractUser):
    university = models.CharField(max_length=150, blank=True)
    major = models.CharField(max_length=150, blank=True)     # carrera
    semester = models.PositiveSmallIntegerField(default=1)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} - {self.major}"
