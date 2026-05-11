from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import StudentUserCreationForm
from .models import StudentUser

from posts.models import Post, Project, Like, Comment
from posts.forms import PostForm, ProjectForm, CommentForm


def register(request):
    if request.method == 'POST':
        form = StudentUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            user = form.save()  # Guarda el StudentUser en MySQL
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = StudentUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    user = request.user
    post_form = PostForm()
    project_form = ProjectForm()
    comment_form = CommentForm()
    
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
                return redirect('home')

    posts = Post.objects.select_related('author').prefetch_related(
        'likes',
        'comments__author'
    ).order_by('-created_at')[:20]

    liked_post_ids = set(
        Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    )

    return render(request, 'home.html', context, {
        'post_form': post_form,
        'project_form': project_form,
        'comment_form': comment_form,
        'posts': posts,
        'projects': projects,
        'liked_post_ids': liked_post_ids,
    })

@login_required
# --- NUEVA VISTA PARA COMPLETAR PERFIL ---
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

@login_required
def toggle_like(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(user=request.user, post=post).first()
    liked = False

    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': post.likes.count(),
    })

@login_required
def add_comment(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        return JsonResponse({
            'success': True,
            'comment': {
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
            },
            'comments_count': post.comments.count(),
        })

    return JsonResponse({
        'success': False,
        'errors': form.errors,
    }, status=400)

@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

