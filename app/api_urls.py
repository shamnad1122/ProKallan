# api_urls.py - API URL patterns for React frontend
from django.urls import path
from . import api_views

urlpatterns = [
    # Auth endpoints
    path('csrf/', api_views.get_csrf_token, name='api_csrf_token'),
    path('auth/login/', api_views.api_login, name='api_login'),
    path('auth/logout/', api_views.api_logout, name='api_logout'),
    path('auth/register/', api_views.api_register, name='api_register'),
    path('auth/user/', api_views.api_current_user, name='api_current_user'),
    
    # Profile endpoints
    path('profile/update/', api_views.api_update_profile, name='api_update_profile'),
    path('profile/change-password/', api_views.api_change_password, name='api_change_password'),
    
    # Malpractice log endpoints
    path('malpractice-logs/', api_views.api_malpractice_logs, name='api_malpractice_logs'),
    path('malpractice-logs/review/', api_views.api_review_malpractice, name='api_review_malpractice'),
    
    # Lecture hall endpoints
    path('lecture-halls/', api_views.api_lecture_halls, name='api_lecture_halls'),
    path('lecture-halls/add/', api_views.api_add_lecture_hall, name='api_add_lecture_hall'),
    path('lecture-halls/assign/', api_views.api_assign_teacher, name='api_assign_teacher'),
    
    # Teacher endpoints
    path('teachers/', api_views.api_teachers, name='api_teachers'),
    
    # Camera control endpoints
    path('cameras/start/', api_views.api_start_cameras, name='api_start_cameras'),
    path('cameras/stop/', api_views.api_stop_cameras, name='api_stop_cameras'),
]
