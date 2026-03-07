"""
API views for DetectSus - REST-style JSON responses.
All endpoints return JSON; no template rendering.
"""
import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from app.models import TeacherProfile, LectureHall, MalpraticeDetection
from app.utils import send_sms_notification, ssh_run_script, local_run_script, RUNNING_SCRIPTS
from app.serializers import (
    UserSerializer,
    TeacherProfileSerializer,
    LectureHallSerializer,
    MalpraticeDetectionSerializer,
    TeacherRegisterSerializer,
    EditProfileSerializer,
)
from .responses import success_response, error_response

import threading
import time


def _is_admin(user):
    return user.is_superuser


# =============================================================================
# Public / Unauthenticated
# =============================================================================


@api_view(['GET'])
@permission_classes([AllowAny])
def api_home(request):
    """Health/landing endpoint."""
    return success_response({
        'message': 'DetectSus API',
        'version': '1.0',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Login: authenticate and create session.
    Expects: { "username": "...", "password": "..." }
    Returns user data on success.
    """
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return error_response('Invalid JSON', status.HTTP_400_BAD_REQUEST)

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return error_response('Username and password required', status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return error_response('Invalid credentials', status.HTTP_401_UNAUTHORIZED)

    auth_login(request, user)
    return success_response({
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_teacher_register(request):
    """
    Register a new teacher.
    Expects multipart/form-data: first_name, last_name, email, username, password, phone, profile_picture
    """
    serializer = TeacherRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    if User.objects.filter(username=data['username']).exists():
        return error_response('Username already exists', status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=data['email']).exists():
        return error_response('Email already exists', status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    profile = TeacherProfile(user=user, phone=data['phone'], profile_picture=data['profile_picture'])
    profile.save()

    return success_response({'user_id': user.id, 'username': user.username}, status.HTTP_201_CREATED)


# =============================================================================
# Authenticated (session-based for now; JWT-ready)
# =============================================================================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Logout and clear session."""
    auth_logout(request)
    return success_response({'message': 'Logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    """Get current user profile."""
    user = request.user
    try:
        profile = user.teacherprofile
        profile_data = TeacherProfileSerializer(profile).data
    except TeacherProfile.DoesNotExist:
        profile_data = None

    return success_response({
        'user': UserSerializer(user).data,
        'profile': profile_data,
        'is_admin': user.is_superuser,
    })


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_edit_profile(request):
    """GET: return current profile for editing. PUT/PATCH: update profile."""
    user = request.user
    teacher_profile, _ = TeacherProfile.objects.get_or_create(user=user)

    if request.method == 'GET':
        return success_response({
            'user': UserSerializer(user).data,
            'profile': {
                'phone': teacher_profile.phone,
                'profile_picture': teacher_profile.profile_picture.url if teacher_profile.profile_picture else None,
            },
        })

    # PUT / PATCH
    serializer = EditProfileSerializer(data=request.data, partial=(request.method == 'PATCH'))
    if not serializer.is_valid():
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    user.save()

    if 'phone' in data:
        teacher_profile.phone = data['phone']
    if 'profile_picture' in data:
        teacher_profile.profile_picture = data['profile_picture']
    teacher_profile.save()

    return success_response({'message': 'Profile updated'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    """Change password. Expects: old_password, new_password1, new_password2."""
    form = PasswordChangeForm(user=request.user, data=request.data)
    if not form.is_valid():
        errors = form.errors.get_json_data()
        return error_response(errors, status.HTTP_400_BAD_REQUEST)

    user = form.save()
    update_session_auth_hash(request, user)
    return success_response({'message': 'Password changed successfully'})


# =============================================================================
# Malpractice Log
# =============================================================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_malpractice_log(request):
    """
    List malpractice logs with filters.
    Query params: date, time (FN|AN), malpractice_type, building, q (hall search),
    faculty, assigned (assigned|unassigned), review (reviewed|not_reviewed)
    """
    date_filter = request.GET.get('date', '').strip()
    time_filter = request.GET.get('time', '').strip()
    malpractice_filter = request.GET.get('malpractice_type', '').strip()
    building_filter = request.GET.get('building', '').strip()
    query = request.GET.get('q', '').strip()
    faculty_filter = request.GET.get('faculty', '').strip()
    assignment_filter = request.GET.get('assigned', '').strip()
    review_filter = request.GET.get('review', '').strip() or 'not_reviewed'

    if request.user.is_superuser:
        logs = MalpraticeDetection.objects.all()
        if review_filter.lower() == 'reviewed':
            logs = logs.filter(verified=True)
        elif review_filter.lower() == 'not_reviewed':
            logs = logs.filter(verified=False)
    else:
        assigned_halls = LectureHall.objects.filter(assigned_teacher=request.user)
        logs = MalpraticeDetection.objects.filter(
            lecture_hall__in=assigned_halls,
            verified=True,
            is_malpractice=True,
        )

    if date_filter:
        logs = logs.filter(date=date_filter)
    if time_filter:
        if time_filter.upper() == 'FN':
            logs = logs.filter(time__lt='12:00:00')
        elif time_filter.upper() == 'AN':
            logs = logs.filter(time__gte='12:00:00')
    if malpractice_filter:
        logs = logs.filter(malpractice=malpractice_filter)
    if building_filter:
        logs = logs.filter(lecture_hall__building=building_filter)
    if query:
        logs = logs.filter(lecture_hall__hall_name__icontains=query)
    if faculty_filter:
        logs = logs.filter(lecture_hall__assigned_teacher__id=faculty_filter)
    if assignment_filter:
        if assignment_filter.lower() == 'assigned':
            logs = logs.filter(lecture_hall__assigned_teacher__isnull=False)
        elif assignment_filter.lower() == 'unassigned':
            logs = logs.filter(lecture_hall__assigned_teacher__isnull=True)

    logs = logs.order_by('-date', '-time')

    record_count = logs.count()
    alert = False
    if 'record_count' in request.session:
        if request.session['record_count'] < record_count:
            alert = True
        request.session['record_count'] = record_count
    else:
        request.session['record_count'] = record_count

    return success_response({
        'result': MalpraticeDetectionSerializer(logs, many=True).data,
        'alert': alert,
        'is_admin': request.user.is_superuser,
        'buildings': list(LectureHall.objects.values_list('building', flat=True).distinct()),
        'faculty_list': UserSerializer(
            User.objects.filter(teacherprofile__isnull=False, is_superuser=False),
            many=True,
        ).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_review_malpractice(request):
    """
    Admin only. Review a malpractice log.
    Expects: { "proof": "filename.mp4", "decision": "yes" | "no" }
    """
    if not request.user.is_superuser:
        return error_response('Admin only', status.HTTP_403_FORBIDDEN)

    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return error_response('Invalid JSON', status.HTTP_400_BAD_REQUEST)

    proof_filename = data.get('proof')
    decision = data.get('decision')

    if not proof_filename or decision not in ['yes', 'no']:
        return error_response('Invalid data: proof and decision (yes|no) required', status.HTTP_400_BAD_REQUEST)

    try:
        log = MalpraticeDetection.objects.get(proof=proof_filename)
    except MalpraticeDetection.DoesNotExist:
        return error_response('Malpractice log not found', status.HTTP_404_NOT_FOUND)

    log.verified = True
    log.is_malpractice = (decision == 'yes')
    log.save()

    if log.is_malpractice and log.lecture_hall and log.lecture_hall.assigned_teacher:
        teacher_user = log.lecture_hall.assigned_teacher
        try:
            teacher_profile = teacher_user.teacherprofile
        except TeacherProfile.DoesNotExist:
            teacher_profile = None

        subject = 'Malpractice Alert: New Case Reviewed'
        message_body = (
            f"Dear {teacher_user.get_full_name() or teacher_user.username},\n\n"
            f"A malpractice has been detected in your classroom and has been approved by the examination cell.\n\n"
            f"Details:\n"
            f"- Date: {log.date}\n"
            f"- Time: {log.time}\n"
            f"- Type: {log.malpractice}\n"
            f"- Lecture Hall: {log.lecture_hall.building} - {log.lecture_hall.hall_name}\n\n"
            f"You can view the recorded video proof from your DetectSus portal.\n\n"
            f"Best regards,\nDetectSus Team"
        )
        try:
            send_mail(subject, message_body, settings.EMAIL_HOST_USER, [teacher_user.email], fail_silently=False)
        except Exception as e:
            print(f"[ERROR] Email sending failed: {e}")

        if teacher_profile and teacher_profile.phone:
            sms_body = (
                f"\nDear {teacher_user.get_full_name() or teacher_user.username},\n\n"
                f"Malpractice Alert\n"
                f"{log.date} | {log.time}\n"
                f"{log.malpractice} detected in {log.lecture_hall.building}-{log.lecture_hall.hall_name}.\n"
                f"\nCheck DetectSus for video proof."
            )
            try:
                send_sms_notification(f"+91{teacher_profile.phone.strip()}", sms_body)
            except Exception as e:
                print(f"[ERROR] SMS sending failed: {e}")

    return success_response({'success': True})


# =============================================================================
# Manage Lecture Halls (Admin)
# =============================================================================


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_manage_lecture_halls(request):
    """
    GET: list lecture halls with filters.
    POST: add hall ({ hall_name, building }) or map teacher ({ hall_id, teacher_id }).
    """
    if not request.user.is_superuser:
        return error_response('Admin only', status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        query = request.GET.get('q', '')
        building_filter = request.GET.get('building', '')
        assignment_filter = request.GET.get('assigned', '')

        lecture_halls = LectureHall.objects.all()
        if query:
            lecture_halls = lecture_halls.filter(hall_name__icontains=query)
        if building_filter:
            lecture_halls = lecture_halls.filter(building=building_filter)
        if assignment_filter == 'assigned':
            lecture_halls = lecture_halls.exclude(assigned_teacher=None)
        elif assignment_filter == 'unassigned':
            lecture_halls = lecture_halls.filter(assigned_teacher=None)

        teachers = User.objects.filter(is_superuser=False)
        buildings = list(LectureHall.objects.values_list('building', flat=True).distinct())

        return success_response({
            'lecture_halls': LectureHallSerializer(lecture_halls, many=True).data,
            'teachers': UserSerializer(teachers, many=True).data,
            'buildings': buildings,
        })

    # POST
    data = request.data
    if 'add_hall' in data or ('hall_name' in data and 'building' in data):
        hall_name = data.get('hall_name')
        building = data.get('building')
        if not hall_name or not building:
            return error_response('hall_name and building required', status.HTTP_400_BAD_REQUEST)
        if LectureHall.objects.filter(hall_name=hall_name, building=building).exists():
            return error_response(f"Lecture Hall '{hall_name}' already exists in '{building}'", status.HTTP_400_BAD_REQUEST)
        LectureHall.objects.create(hall_name=hall_name, building=building)
        return success_response({'message': 'Lecture hall added'}, status.HTTP_201_CREATED)

    if 'map_teacher' in data or ('hall_id' in data and 'teacher_id' in data):
        hall_id = data.get('hall_id')
        teacher_id = data.get('teacher_id')
        try:
            hall = LectureHall.objects.get(id=hall_id)
            teacher = User.objects.get(id=teacher_id)
        except (LectureHall.DoesNotExist, User.DoesNotExist):
            return error_response('Hall or teacher not found', status.HTTP_400_BAD_REQUEST)
        LectureHall.objects.filter(assigned_teacher=teacher).update(assigned_teacher=None)
        hall.assigned_teacher = teacher
        hall.save()
        return success_response({'message': 'Teacher assigned'})

    return error_response('Invalid request body', status.HTTP_400_BAD_REQUEST)


# =============================================================================
# View Teachers (Admin)
# =============================================================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_view_teachers(request):
    """List teachers with filters."""
    if not request.user.is_superuser:
        return error_response('Admin only', status.HTTP_403_FORBIDDEN)

    assigned_filter = request.GET.get('assigned', '')
    building_filter = request.GET.get('building', '')

    teachers = User.objects.filter(is_superuser=False).select_related('lecturehall')
    if assigned_filter == 'assigned':
        teachers = teachers.filter(lecturehall__isnull=False)
    elif assigned_filter == 'unassigned':
        teachers = teachers.filter(lecturehall__isnull=True)
    if building_filter:
        teachers = teachers.filter(lecturehall__building=building_filter)

    def teacher_row(t):
        profile = getattr(t, 'teacherprofile', None)
        hall = getattr(t, 'lecturehall', None)
        return {
            'id': t.id,
            'username': t.username,
            'email': t.email,
            'first_name': t.first_name,
            'last_name': t.last_name,
            'full_name': t.get_full_name() or t.username,
            'phone': profile.phone if profile else None,
            'lecture_hall': f"{hall.building} - {hall.hall_name}" if hall else None,
        }

    return success_response({
        'teachers': [teacher_row(t) for t in teachers],
        'buildings': list(LectureHall.objects.values_list('building', flat=True).distinct()),
    })


# =============================================================================
# Run Cameras (Admin)
# =============================================================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_run_cameras_page(request):
    """Info for Run Cameras page (no auth enforcement for dev)."""
    if not request.user.is_superuser:
        return error_response('Admin only', status.HTTP_403_FORBIDDEN)
    return success_response({
        'message': 'Run Cameras - trigger scripts via POST to /api/cameras/trigger/',
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_trigger_camera_scripts(request):
    """Start camera scripts on configured clients."""
    if not request.user.is_superuser:
        return error_response('Admin only', status.HTTP_403_FORBIDDEN)

    client_configs = [
        {
            'name': 'Top Corner - Host(Allen 2)',
            'script_path': 'C:\\Users\\noelm\\Documents\\PROJECTS\\DetectSus\\ML\\front.py',
            'mode': 'local',
        },
    ]

    def run_on_client(config):
        if config.get('mode') == 'remote':
            use_venv = config.get('use_venv', True)
            venv_path = config.get('venv_path', None)
            success, output = ssh_run_script(
                config['ip'], config['username'], config['password'],
                config['script_path'], use_venv, venv_path,
            )
            print(f"[{config['name']}]: {output if success else 'Error: ' + output}")
        elif config.get('mode') == 'local':
            success, output = local_run_script(config['script_path'])
            print(f"[{config['name']}]: {output if success else 'Error: ' + output}")

    for config in client_configs:
        threading.Thread(target=run_on_client, args=(config,)).start()

    return success_response({'status': 'started'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_stop_camera_scripts(request):
    """Stop running camera scripts."""
    if not request.user.is_superuser:
        return error_response('Admin only', status.HTTP_403_FORBIDDEN)

    for key in list(RUNNING_SCRIPTS.keys()):
        handle = RUNNING_SCRIPTS[key]
        if handle.get('mode') == 'remote':
            try:
                channel = handle.get('channel')
                if channel:
                    channel.send('\x03')
                    time.sleep(2)
                    channel.close()
                ssh = handle.get('ssh')
                if ssh:
                    ssh.close()
                print(f"\n[{key}] Remote process terminated.")
            except Exception as e:
                print(f"\n[{key}] Error: {e}")
        elif handle.get('mode') == 'local':
            process = handle.get('process')
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"\n[{key}] Local process terminated.")
                except Exception as e:
                    print(f"\n[{key}] Error: {e}")
        RUNNING_SCRIPTS.pop(key, None)

    return success_response({'status': 'stopped'})
