from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import StudentUserCreationForm
from posts.models import Post, Project
from posts.forms import PostForm


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
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        post_form = PostForm()

    posts = Post.objects.select_related('author').order_by('-created_at')[:20]
    projects = Project.objects.select_related('owner').filter(status='open').order_by('-created_at')[:10]

    context = {
        'posts': posts,
        'projects': projects,
        'post_form': post_form,
    }
    return render(request, 'home.html', context)


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})