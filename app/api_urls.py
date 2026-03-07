"""
API URL configuration - all routes under /api/
"""
from django.urls import path
from app.api_views import views

urlpatterns = [
    # Public
    path('', views.api_home),
    path('home/', views.api_home),
    path('login/', views.api_login),
    path('register/teacher/', views.api_teacher_register),

    # Auth (session-based)
    path('logout/', views.api_logout),
    path('profile/', views.api_profile),
    path('profile/edit/', views.api_edit_profile),
    path('profile/change-password/', views.api_change_password),

    # Malpractice
    path('malpractice-log/', views.api_malpractice_log),
    path('malpractice-log/review/', views.api_review_malpractice),

    # Admin
    path('manage-lecture-halls/', views.api_manage_lecture_halls),
    path('view-teachers/', views.api_view_teachers),
    path('run-cameras/', views.api_run_cameras_page),
    path('cameras/trigger/', views.api_trigger_camera_scripts),
    path('cameras/stop/', views.api_stop_camera_scripts),
]
