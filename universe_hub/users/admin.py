from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentUser

class StudentUserAdmin(UserAdmin):
    # Esto añade tus campos a la lista de la tabla
    list_display = ('username', 'email', 'university', 'major', 'is_staff')
    
    # Esto añade los campos dentro del formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Académica', {'fields': ('university', 'major', 'semester')}),
    )

admin.site.register(StudentUser, StudentUserAdmin)
