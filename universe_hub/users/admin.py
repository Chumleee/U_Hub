from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentUser


@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Academic info', {
            'fields': ('university', 'major', 'semester', 'bio'),
        }),
    )