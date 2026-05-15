from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q

from .forms import StudentUserCreationForm
from .models import StudentUser

from posts.models import Post, Project, Like, Comment, ProjectApplication
from posts.forms import PostForm, ProjectForm, CommentForm
from .forms import StudentUserCreationForm, StudentUserUpdateForm
from posts.models import Post, Project, ProjectApplication


CAREER_LABELS = {
    'arts': 'Artes',
    'business': 'Negocios',
    'design': 'Diseño',
    'engineering': 'Ingeniero',
    'health': 'Salud',
    'law': 'Derecho',
    'other': 'Otros',
}


def register(request):
    if request.method == 'POST':
        form = StudentUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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

    if not user.is_staff:
        university_exists = user.university and user.university.strip()
        major_exists = user.major and user.major.strip()

        if not university_exists or not major_exists:
            return redirect('complete_profile')

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

    selected_careers = request.GET.getlist('career')

    base_projects = Project.objects.select_related('owner').filter(
        status='open'
    )

    raw_careers = sorted({
        career.strip()
        for value in base_projects.values_list('target_careers', flat=True)
        if value
        for career in value.split(',')
        if career.strip()
    })

    available_careers = [
        {
            'value': career,
            'label': CAREER_LABELS.get(career, career.replace('_', ' ').title())
        }
        for career in raw_careers
    ]

    projects = base_projects

    if selected_careers:
        career_query = Q()
        for career in selected_careers:
            career_query |= Q(target_careers__icontains=career)

        projects = projects.filter(career_query)

    projects = projects.order_by('-created_at')[:10]

    liked_post_ids = set(
        Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    )

    pending_requests = ProjectApplication.objects.select_related(
        'applicant',
        'project'
    ).filter(
        project__owner=request.user,
        status='pending'
    ).order_by('-created_at')

    my_applications = ProjectApplication.objects.select_related(
        'project',
        'project__owner'
    ).filter(
        applicant=request.user
    ).exclude(
        status='accepted'
    ).order_by('-created_at')

    joined_projects = ProjectApplication.objects.select_related(
        'project',
        'project__owner'
    ).filter(
        applicant=request.user,
        status='accepted'
    ).order_by('-created_at')

    selected_career_labels = [
        CAREER_LABELS.get(career, career.replace('_', ' ').title())
        for career in selected_careers
    ]

    context = {
        'post_form': post_form,
        'project_form': project_form,
        'comment_form': comment_form,
        'posts': posts,
        'available_careers': available_careers,
        'selected_careers': selected_careers,
        'projects': projects,
        'liked_post_ids': liked_post_ids,
        'pending_requests': pending_requests,
        'pending_requests_count': pending_requests.count(),
        'my_applications': my_applications,
        'joined_projects': joined_projects,
        'selected_career_labels': selected_career_labels,
    }

    return render(request, 'home.html', context)


@login_required
def complete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.university = request.POST.get('university')
        user.major = request.POST.get('major')
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
def project_detail(request, project_id):
    project = get_object_or_404(Project.objects.select_related('owner'), id=project_id)

    existing_application = ProjectApplication.objects.filter(
        project=project,
        applicant=request.user
    ).first()

    is_owner = project.owner == request.user

    context = {
        'project': project,
        'existing_application': existing_application,
        'is_owner': is_owner,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def apply_to_project(request, project_id):
    if request.method != 'POST':
        return redirect('project_detail', project_id=project_id)

    project = get_object_or_404(Project, id=project_id)

    if project.owner == request.user:
        messages.warning(request, 'No puedes solicitar entrar a tu propio proyecto.')
        return redirect('project_detail', project_id=project.id)

    application, created = ProjectApplication.objects.get_or_create(
        project=project,
        applicant=request.user,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, 'Tu solicitud fue enviada correctamente.')
    else:
        if application.status == 'pending':
            messages.info(request, 'Ya habías enviado una solicitud a este proyecto.')
        elif application.status == 'accepted':
            messages.success(request, 'Ya formas parte de este proyecto.')
        elif application.status == 'rejected':
            messages.warning(request, 'Tu solicitud anterior fue rechazada.')

    return redirect('project_detail', project_id=project.id)

@login_required
def accept_application(request, application_id):
    if request.method != 'POST':
        return redirect('home')

    application = get_object_or_404(
        ProjectApplication.objects.select_related('project', 'applicant'),
        id=application_id
    )

    if application.project.owner != request.user:
        messages.error(request, 'No tienes permiso para aceptar esta solicitud.')
        return redirect('home')

    if application.status != 'pending':
        messages.info(request, 'Esta solicitud ya fue procesada.')
        return redirect('home')

    project = application.project

    if project.vacancies <= 0:
        project.status = 'closed'
        project.save(update_fields=['status'])
        messages.warning(request, 'Este proyecto ya no tiene vacantes disponibles.')
        return redirect('home')

    application.status = 'accepted'
    application.save(update_fields=['status'])

    project.vacancies -= 1

    if project.vacancies <= 0:
        project.vacancies = 0
        project.status = 'closed'
        project.save(update_fields=['vacancies', 'status'])
    else:
        project.save(update_fields=['vacancies'])

    messages.success(
        request,
        f'{application.applicant.username} fue aceptado en "{project.title}".'
    )
    return redirect('home')


@login_required
def reject_application(request, application_id):
    if request.method != 'POST':
        return redirect('home')

    application = get_object_or_404(
        ProjectApplication.objects.select_related('project', 'applicant'),
        id=application_id
    )

    if application.project.owner != request.user:
        messages.error(request, 'No tienes permiso para rechazar esta solicitud.')
        return redirect('home')

    if application.status != 'pending':
        messages.info(request, 'Esta solicitud ya fue procesada.')
        return redirect('home')

    application.status = 'rejected'
    application.save(update_fields=['status'])

    messages.warning(
        request,
        f'{application.applicant.username} fue rechazado en "{application.project.title}".'
    )
    return redirect('home')

@login_required
def profile(request):
    user_profile = request.user 

    # --- Lógica para procesar las fotos (POST) ---
    if request.method == 'POST':
        # Revisamos si viene la foto de portada
        if 'cover_photo' in request.FILES:
            user_profile.cover_photo = request.FILES['cover_photo']
            user_profile.save()
            
        # Revisamos si viene la foto de perfil
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            
        return redirect('profile')

    # --- Lógica para obtener actividad (GET) ---
    
    # 1. Publicaciones hechas por el usuario
    user_posts = Post.objects.filter(author=user_profile)
    
    # 2. Proyectos que el usuario ha creado
    user_projects = Project.objects.filter(owner=user_profile)
    
    # 3. Proyectos donde es colaborador (solicitudes aceptadas)
    joined_projects = ProjectApplication.objects.filter(
        applicant=user_profile, 
        status='accepted'
    )
    liked_post_ids = request.user.likes.values_list('post_id', flat=True)
    context = {
        'user_profile': user_profile,
        'is_own_profile': True,
        'user_posts': user_posts,
        'user_projects': user_projects,
        'joined_projects': joined_projects,
        'liked_post_ids': liked_post_ids,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # VITAL: request.FILES debe estar presente
        form = StudentUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado con éxito!')
            return redirect('profile')
        else:
            # Esto imprimirá los errores en tu terminal de VS Code para que sepamos qué falla
            print(form.errors) 
    else:
        form = StudentUserUpdateForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})