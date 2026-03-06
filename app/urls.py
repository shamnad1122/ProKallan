# urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="DetectSus API",
        default_version='v1',
        description="""
        # DetectSus Malpractice Detection System API
        
        Complete REST API for the DetectSus examination malpractice detection system.
        
        ## Features
        - **Authentication**: Session-based authentication with CSRF protection
        - **Malpractice Logs**: View and review detected malpractice incidents
        - **Lecture Halls**: Manage lecture halls and teacher assignments
        - **Camera Control**: Start/stop ML detection scripts
        - **Notifications**: Automatic email/SMS alerts to teachers
        
        ## Authentication
        All endpoints (except login/register) require authentication.
        Use `/api/auth/login/` to authenticate and receive a session cookie.
        
        ## Permissions
        - **Teacher**: Can view their assigned hall's malpractice logs
        - **Admin**: Full access to all endpoints including review and camera control
        """,
        terms_of_service="https://www.detectsus.com/terms/",
        contact=openapi.Contact(email="admin@detectsus.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger/OpenAPI documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints for React frontend
    path('api/', include('app.api_urls')),
    
    # Legacy template-based views (kept for backward compatibility)
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('home',views.home),
    path('',views.index),
    path('index', views.index, name='index'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('login/addlogin', views.addlogin, name='addlogin'),
    path('login/',views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('logout/',views.logout, name='logout'),
    path('malpractice_log/',views.malpractice_log, name='malpractice_log'),
    path('review_malpractice/', views.review_malpractice, name='review_malpractice'),
    path('manage-lecture-halls/', views.manage_lecture_halls, name='manage_lecture_halls'),
    path('view_teachers/', views.view_teachers, name='view_teachers'),
    path('run_cameras/', views.run_cameras_page, name='run_cameras_page'),
    path('trigger_camera_scripts/', views.trigger_camera_scripts, name='trigger_camera_scripts'),
    path('stop_camera_scripts/', views.stop_camera_scripts, name='stop_camera_scripts'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)