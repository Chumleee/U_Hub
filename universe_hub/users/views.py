from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import StudentUserCreationForm
from .models import StudentUser

from posts.models import Post, Project
from posts.forms import PostForm, ProjectForm


def register(request):
    if request.method == 'POST':
        form = StudentUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = StudentUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    post_form = PostForm()
    project_form = ProjectForm()

    if request.method == 'POST':
        if 'create_post' in request.POST:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('home')

        elif 'create_project' in request.POST:
            project_form = ProjectForm(request.POST)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.owner = request.user
                project.save()
                project_form.save_m2m()
                return redirect('home')

    posts = Post.objects.select_related('author').order_by('-created_at')[:20]
    projects = Project.objects.select_related('owner').filter(
        status='open'
    ).order_by('-created_at')[:10]

    return render(request, 'home.html', {
        'post_form': post_form,
        'project_form': project_form,
        'posts': posts,
        'projects': projects,
    })


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})