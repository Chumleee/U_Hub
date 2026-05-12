from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/apply/', views.apply_to_project, name='apply_to_project'),
    path('applications/<int:application_id>/accept/', views.accept_application, name='accept_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),
]