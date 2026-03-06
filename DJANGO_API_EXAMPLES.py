# Django API View Examples for React Frontend
# Add these to your app/views.py or create a new api_views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from .models import *
import json

# Helper function
def is_admin(user):
    return user.is_superuser


# ============================================
# Authentication Endpoints
# ============================================

@csrf_exempt
def login_api(request):
    """
    POST /login/addlogin
    Body: { "username": "...", "password": "..." }
    """
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_superuser': user.is_superuser,
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)


@login_required
def profile_api(request):
    """
    GET /profile/
    Returns user and profile data as JSON
    """
    try:
        teacher_profile = request.user.teacherprofile
        profile_data = {
            'phone': teacher_profile.phone,
            'profile_picture': teacher_profile.profile_picture.url if teacher_profile.profile_picture else None,
        }
        
        # Check if teacher has an assigned lecture hall
        try:
            lecture_hall = LectureHall.objects.get(assigned_teacher=request.user)
            profile_data['lecture_hall'] = {
                'id': lecture_hall.id,
                'hall_name': lecture_hall.hall_name,
                'building': lecture_hall.building,
            }
        except LectureHall.DoesNotExist:
            profile_data['lecture_hall'] = None
            
    except TeacherProfile.DoesNotExist:
        profile_data = None

    return JsonResponse({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_superuser': request.user.is_superuser,
        },
        'profile': profile_data,
    })


# ============================================
# Malpractice Log Endpoint
# ============================================

@login_required
def malpractice_log_api(request):
    """
    GET /malpractice_log/
    Returns malpractice logs with filters
    """
    # Get filter parameters
    date_filter = request.GET.get('date', '').strip()
    time_filter = request.GET.get('time', '').strip()
    malpractice_filter = request.GET.get('malpractice_type', '').strip()
    building_filter = request.GET.get('building', '').strip()
    query = request.GET.get('q', '').strip()
    faculty_filter = request.GET.get('faculty', '').strip()
    assignment_filter = request.GET.get('assigned', '').strip()
    review_filter = request.GET.get('review', '').strip() or 'not_reviewed'

    # Base queryset based on user role
    if request.user.is_superuser:
        logs = MalpraticeDetection.objects.all()
        # Apply review filter for admin
        if review_filter.lower() == 'reviewed':
            logs = logs.filter(verified=True)
        elif review_filter.lower() == 'not_reviewed':
            logs = logs.filter(verified=False)
    else:
        assigned_halls = LectureHall.objects.filter(assigned_teacher=request.user)
        logs = MalpraticeDetection.objects.filter(
            lecture_hall__in=assigned_halls,
            verified=True,
            is_malpractice=True
        )

    # Apply filters
    if date_filter:
        logs = logs.filter(date=date_filter)
    if time_filter:
        if time_filter.upper() == "FN":
            logs = logs.filter(time__lt="12:00:00")
        elif time_filter.upper() == "AN":
            logs = logs.filter(time__gte="12:00:00")
    if malpractice_filter:
        logs = logs.filter(malpractice=malpractice_filter)
    if building_filter:
        logs = logs.filter(lecture_hall__building=building_filter)
    if query:
        logs = logs.filter(lecture_hall__hall_name__icontains=query)
    if faculty_filter:
        logs = logs.filter(lecture_hall__assigned_teacher__id=faculty_filter)
    if assignment_filter:
        if assignment_filter.lower() == "assigned":
            logs = logs.filter(lecture_hall__assigned_teacher__isnull=False)
        elif assignment_filter.lower() == "unassigned":
            logs = logs.filter(lecture_hall__assigned_teacher__isnull=True)

    logs = logs.order_by('-date', '-time')

    # Serialize logs
    logs_data = []
    for log in logs:
        log_data = {
            'id': log.id,
            'date': str(log.date),
            'time': str(log.time),
            'malpractice': log.malpractice,
            'proof': log.proof.url if log.proof else None,
            'verified': log.verified,
            'is_malpractice': log.is_malpractice,
            'lecture_hall': {
                'id': log.lecture_hall.id,
                'hall_name': log.lecture_hall.hall_name,
                'building': log.lecture_hall.building,
            }
        }
        
        if log.lecture_hall.assigned_teacher:
            log_data['lecture_hall']['assigned_teacher'] = {
                'id': log.lecture_hall.assigned_teacher.id,
                'first_name': log.lecture_hall.assigned_teacher.first_name,
                'last_name': log.lecture_hall.assigned_teacher.last_name,
            }
        else:
            log_data['lecture_hall']['assigned_teacher'] = None
            
        logs_data.append(log_data)

    # Get metadata for filters
    buildings = list(LectureHall.objects.values_list('building', flat=True).distinct())
    faculty_list = []
    for user in User.objects.filter(teacherprofile__isnull=False, is_superuser=False):
        faculty_list.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

    return JsonResponse({
        'result': logs_data,
        'buildings': buildings,
        'faculty_list': faculty_list,
    })


# ============================================
# Lecture Halls Management Endpoint
# ============================================

@login_required
@user_passes_test(is_admin)
def manage_lecture_halls_api(request):
    """
    GET /manage-lecture-halls/
    POST /manage-lecture-halls/ (add hall or map teacher)
    """
    if request.method == 'GET':
        # Get filter parameters
        query = request.GET.get('q', '')
        building_filter = request.GET.get('building', '')
        assignment_filter = request.GET.get('assigned', '')

        # Get all lecture halls
        lecture_halls = LectureHall.objects.all()

        # Apply filters
        if query:
            lecture_halls = lecture_halls.filter(hall_name__icontains=query)
        if building_filter:
            lecture_halls = lecture_halls.filter(building=building_filter)
        if assignment_filter == "assigned":
            lecture_halls = lecture_halls.exclude(assigned_teacher=None)
        elif assignment_filter == "unassigned":
            lecture_halls = lecture_halls.filter(assigned_teacher=None)

        # Serialize halls
        halls_data = []
        for hall in lecture_halls:
            hall_data = {
                'id': hall.id,
                'hall_name': hall.hall_name,
                'building': hall.building,
            }
            
            if hall.assigned_teacher:
                hall_data['assigned_teacher'] = {
                    'id': hall.assigned_teacher.id,
                    'first_name': hall.assigned_teacher.first_name,
                    'last_name': hall.assigned_teacher.last_name,
                    'username': hall.assigned_teacher.username,
                }
            else:
                hall_data['assigned_teacher'] = None
                
            halls_data.append(hall_data)

        # Get teachers
        teachers = User.objects.filter(is_superuser=False)
        teachers_data = []
        for teacher in teachers:
            teachers_data.append({
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'username': teacher.username,
            })

        # Get buildings
        buildings = list(LectureHall.objects.values_list('building', flat=True).distinct())

        return JsonResponse({
            'lecture_halls': halls_data,
            'teachers': teachers_data,
            'buildings': buildings,
        })

    elif request.method == 'POST':
        # Handle add hall or map teacher
        if 'add_hall' in request.POST:
            hall_name = request.POST.get('hall_name')
            building = request.POST.get('building')
            
            if LectureHall.objects.filter(hall_name=hall_name, building=building).exists():
                return JsonResponse({
                    'success': False,
                    'error_message': f"Lecture Hall '{hall_name}' already exists in '{building}'."
                }, status=400)
            
            LectureHall.objects.create(hall_name=hall_name, building=building)
            return JsonResponse({'success': True})

        elif 'map_teacher' in request.POST:
            teacher_id = request.POST.get('teacher_id')
            hall_id = request.POST.get('hall_id')
            
            try:
                hall = LectureHall.objects.get(id=hall_id)
                teacher = User.objects.get(id=teacher_id)
                
                # Remove teacher from any other hall
                LectureHall.objects.filter(assigned_teacher=teacher).update(assigned_teacher=None)
                
                # Assign to new hall
                hall.assigned_teacher = teacher
                hall.save()
                
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================
# View Teachers Endpoint
# ============================================

@login_required
@user_passes_test(is_admin)
def view_teachers_api(request):
    """
    GET /view_teachers/
    Returns list of teachers with their assignments
    """
    assigned_filter = request.GET.get('assigned', '')
    building_filter = request.GET.get('building', '')

    teachers = User.objects.filter(is_superuser=False)

    # Apply filters
    if assigned_filter == 'assigned':
        teachers = teachers.filter(lecturehall__isnull=False)
    elif assigned_filter == 'unassigned':
        teachers = teachers.filter(lecturehall__isnull=True)

    if building_filter:
        teachers = teachers.filter(lecturehall__building=building_filter)

    # Serialize teachers
    teachers_data = []
    for teacher in teachers:
        teacher_data = {
            'id': teacher.id,
            'username': teacher.username,
            'email': teacher.email,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
        }
        
        try:
            lecture_hall = LectureHall.objects.get(assigned_teacher=teacher)
            teacher_data['lecturehall'] = {
                'id': lecture_hall.id,
                'hall_name': lecture_hall.hall_name,
                'building': lecture_hall.building,
            }
        except LectureHall.DoesNotExist:
            teacher_data['lecturehall'] = None
            
        teachers_data.append(teacher_data)

    # Get buildings
    buildings = list(LectureHall.objects.values_list('building', flat=True).distinct())

    return JsonResponse({
        'teachers': teachers_data,
        'buildings': buildings,
    })


# ============================================
# URL Configuration Example
# ============================================

"""
Add to app/urls.py:

urlpatterns = [
    # ... existing routes ...
    
    # API routes for React frontend
    path('api/login/', login_api, name='login_api'),
    path('api/profile/', profile_api, name='profile_api'),
    path('api/malpractice_log/', malpractice_log_api, name='malpractice_log_api'),
    path('api/manage-lecture-halls/', manage_lecture_halls_api, name='manage_lecture_halls_api'),
    path('api/view_teachers/', view_teachers_api, name='view_teachers_api'),
    
    # Keep existing routes for backward compatibility
    path('login/addlogin', addlogin, name='addlogin'),
    path('profile/', profile, name='profile'),
    # ...
]

Then update React frontend's lib/api.ts:
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  // ...
});
"""
