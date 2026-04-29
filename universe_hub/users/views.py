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
    # --- LÓGICA CORREGIDA ---
    # Si NO es administrador Y NO tiene perfil completo, lo mandamos al formulario
    if not request.user.is_staff and (not request.user.university or not request.user.major):
        return redirect('complete_profile')
    # ------------------------

    posts = Post.objects.select_related('author').order_by('-created_at')[:20]
    projects = Project.objects.select_related('owner').filter(
        status='open'
    ).order_by('-created_at')[:10]

    context = {
        'posts': posts,
        'projects': projects,
    }
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