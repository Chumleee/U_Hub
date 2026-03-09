from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentUser, Follow  # ← IMPORTAR AQUÍ


@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Academic info', {
            'fields': ('university', 'major', 'semester', 'bio'),
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
