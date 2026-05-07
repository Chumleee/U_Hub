from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import StudentUserCreationForm  # ← Cambio aquí
from .models import StudentUser

from posts.models import Post, Project


def register(request):
    if request.method == 'POST':
        form = StudentUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el StudentUser en MySQL
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
       
    else:
        form = StudentUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    user = request.user
    
    # 1. Verificación de perfil (Solo para estudiantes, no para staff)
    if not user.is_staff:
        # Verificamos si los campos están vacíos o son solo espacios
        university_exists = user.university and user.university.strip()
        major_exists = user.major and user.major.strip()
        
        if not university_exists or not major_exists:
            # IMPORTANTE: El 'return' debe estar aquí para que la función termine
            return redirect('complete_profile')

    # 2. Si pasó la validación (o es staff), ejecutamos la lógica del feed
    posts = Post.objects.select_related('author').order_by('-created_at')[:20]
    projects = Project.objects.select_related('owner').filter(
        status='open'
    ).order_by('-created_at')[:10]

    context = {
        'posts': posts,
        'projects': projects,
    }
    
    # 3. Este es el return que Django necesita si todo sale bien
    return render(request, 'home.html', context)


# --- NUEVA VISTA PARA COMPLETAR PERFIL ---
@login_required
def complete_profile(request):
    if request.method == 'POST':
        user = request.user
        # Guardamos lo que el usuario escriba en el formulario
        user.university = request.POST.get('university')
        user.major = request.POST.get('major')
        # También podrías pedir el semestre si quieres que no quede en 0
        user.semester = request.POST.get('semester', 1) 
        user.save()
        return redirect('home')
    
    return render(request, 'users/complete_profile.html')