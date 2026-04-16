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
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = StudentUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    # Posts más recientes
    posts = Post.objects.select_related('author').order_by('-created_at')[:20]

    # Proyectos abiertos más recientes
    projects = Project.objects.select_related('owner').filter(
        status='open'
    ).order_by('-created_at')[:10]

    context = {
        'posts': posts,
        'projects': projects,
    }
    return render(request, 'home.html', context)


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})
