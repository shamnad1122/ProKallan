# api_views.py - JSON API endpoints for React frontend
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.middleware.csrf import get_token
from .models import TeacherProfile, LectureHall, MalpraticeDetection
from .utils import send_sms_notification, ssh_run_script, local_run_script, RUNNING_SCRIPTS
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
import threading
import time


def is_admin(user):
    return user.is_superuser


# ============ AUTH ENDPOINTS ============

@require_http_methods(["GET"])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Return CSRF token for frontend"""
    return JsonResponse({'csrfToken': get_token(request)})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """Login endpoint - returns JSON"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'success': False, 'error': 'Username and password required'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            
            # Get user profile data
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_superuser,
            }
            
            # Add teacher profile if exists
            try:
                profile = user.teacherprofile
                user_data['phone'] = profile.phone
                user_data['profile_picture'] = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
                
                # Add lecture hall info
                if profile.lecture_hall:
                    user_data['lecture_hall'] = {
                        'id': profile.lecture_hall.id,
                        'building': profile.lecture_hall.building,
                        'hall_name': profile.lecture_hall.hall_name,
                    }
            except TeacherProfile.DoesNotExist:
                pass

            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': user_data
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def api_logout(request):
    """Logout endpoint"""
    auth_logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """Register new teacher"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'error': f'{field} is required'}, status=400)

        # Check if username exists
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

        # Check if email exists
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'}, status=400)

        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        # Create teacher profile
        profile = TeacherProfile.objects.create(
            user=user,
            phone=data['phone']
        )

        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def api_current_user(request):
    """Get current logged-in user info"""
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': user.is_superuser,
    }
    
    try:
        profile = user.teacherprofile
        user_data['phone'] = profile.phone
        user_data['profile_picture'] = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
        
        if profile.lecture_hall:
            user_data['lecture_hall'] = {
                'id': profile.lecture_hall.id,
                'building': profile.lecture_hall.building,
                'hall_name': profile.lecture_hall.hall_name,
            }
    except TeacherProfile.DoesNotExist:
        pass

    return JsonResponse({'success': True, 'user': user_data})


# ============ PROFILE ENDPOINTS ============

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def api_update_profile(request):
    """Update user profile"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        user.save()
        
        # Update teacher profile
        profile, _ = TeacherProfile.objects.get_or_create(user=user)
        if 'phone' in data:
            profile.phone = data['phone']
        profile.save()
        
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_change_password(request):
    """Change user password"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return JsonResponse({'success': False, 'error': 'Both old and new passwords required'}, status=400)
        
        if not user.check_password(old_password):
            return JsonResponse({'success': False, 'error': 'Current password is incorrect'}, status=400)
        
        user.set_password(new_password)
        user.save()
        
        # Keep user logged in
        auth_login(request, user)
        
        return JsonResponse({'success': True, 'message': 'Password changed successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============ MALPRACTICE LOG ENDPOINTS ============

@require_http_methods(["GET"])
@login_required
def api_malpractice_logs(request):
    """Get malpractice logs with filters"""
    try:
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
                'date': log.date.isoformat() if log.date else None,
                'time': log.time.isoformat() if log.time else None,
                'malpractice': log.malpractice,
                'proof': request.build_absolute_uri(settings.MEDIA_URL + log.proof) if log.proof else None,
                'is_malpractice': log.is_malpractice,
                'verified': log.verified,
            }
            
            if log.lecture_hall:
                log_data['lecture_hall'] = {
                    'id': log.lecture_hall.id,
                    'building': log.lecture_hall.building,
                    'hall_name': log.lecture_hall.hall_name,
                }
                
                if log.lecture_hall.assigned_teacher:
                    teacher = log.lecture_hall.assigned_teacher
                    log_data['assigned_teacher'] = {
                        'id': teacher.id,
                        'username': teacher.username,
                        'full_name': teacher.get_full_name(),
                    }
            
            logs_data.append(log_data)

        return JsonResponse({
            'success': True,
            'logs': logs_data,
            'count': len(logs_data)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def api_review_malpractice(request):
    """Review malpractice log (admin only)"""
    try:
        data = json.loads(request.body)
        log_id = data.get('id')
        decision = data.get('decision')

        if not log_id or decision not in ['yes', 'no']:
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

        try:
            log = MalpraticeDetection.objects.get(id=log_id)
        except MalpraticeDetection.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Log not found'}, status=404)

        # Update log
        log.verified = True
        log.is_malpractice = (decision == 'yes')
        log.save()

        # Send notifications if approved
        if log.is_malpractice and log.lecture_hall and log.lecture_hall.assigned_teacher:
            teacher_user = log.lecture_hall.assigned_teacher

            try:
                teacher_profile = teacher_user.teacherprofile
            except TeacherProfile.DoesNotExist:
                teacher_profile = None

            # Email notification
            subject = 'Malpractice Alert: New Case Reviewed'
            message_body = (
                f"Dear {teacher_user.get_full_name() or teacher_user.username},\n\n"
                f"A malpractice has been detected and approved.\n\n"
                f"Details:\n"
                f"- Date: {log.date}\n"
                f"- Time: {log.time}\n"
                f"- Type: {log.malpractice}\n"
                f"- Hall: {log.lecture_hall.building} - {log.lecture_hall.hall_name}\n\n"
                f"View proof in DetectSus portal.\n\n"
                f"Best regards,\nDetectSus Team"
            )

            try:
                send_mail(subject, message_body, settings.EMAIL_HOST_USER, [teacher_user.email], fail_silently=False)
            except Exception as e:
                print(f"[ERROR] Email failed: {e}")

            # SMS notification
            if teacher_profile and teacher_profile.phone:
                sms_message = (
                    f"Malpractice Alert\n"
                    f"{log.date} | {log.time}\n"
                    f"{log.malpractice} in {log.lecture_hall.building}-{log.lecture_hall.hall_name}\n"
                    f"Check DetectSus portal."
                )
                try:
                    send_sms_notification(f"+91{teacher_profile.phone.strip()}", sms_message)
                except Exception as e:
                    print(f"[ERROR] SMS failed: {e}")

        return JsonResponse({'success': True, 'message': 'Review completed'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============ LECTURE HALL ENDPOINTS ============

@require_http_methods(["GET"])
@login_required
def api_lecture_halls(request):
    """Get all lecture halls with filters"""
    try:
        query = request.GET.get('q', '')
        building_filter = request.GET.get('building', '')
        assignment_filter = request.GET.get('assigned', '')

        halls = LectureHall.objects.all()

        if query:
            halls = halls.filter(hall_name__icontains=query)
        if building_filter:
            halls = halls.filter(building=building_filter)
        if assignment_filter == "assigned":
            halls = halls.exclude(assigned_teacher=None)
        elif assignment_filter == "unassigned":
            halls = halls.filter(assigned_teacher=None)

        halls_data = []
        for hall in halls:
            hall_data = {
                'id': hall.id,
                'building': hall.building,
                'hall_name': hall.hall_name,
            }
            
            if hall.assigned_teacher:
                teacher = hall.assigned_teacher
                hall_data['assigned_teacher'] = {
                    'id': teacher.id,
                    'username': teacher.username,
                    'full_name': teacher.get_full_name(),
                    'email': teacher.email,
                }
            
            halls_data.append(hall_data)

        # Get unique buildings
        buildings = list(LectureHall.objects.values_list('building', flat=True).distinct())

        return JsonResponse({
            'success': True,
            'halls': halls_data,
            'buildings': buildings
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def api_add_lecture_hall(request):
    """Add new lecture hall (admin only)"""
    try:
        data = json.loads(request.body)
        hall_name = data.get('hall_name')
        building = data.get('building')

        if not hall_name or not building:
            return JsonResponse({'success': False, 'error': 'Hall name and building required'}, status=400)

        if LectureHall.objects.filter(hall_name=hall_name, building=building).exists():
            return JsonResponse({'success': False, 'error': 'Hall already exists'}, status=400)

        hall = LectureHall.objects.create(hall_name=hall_name, building=building)

        return JsonResponse({
            'success': True,
            'message': 'Hall added successfully',
            'hall': {
                'id': hall.id,
                'building': hall.building,
                'hall_name': hall.hall_name,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def api_assign_teacher(request):
    """Assign teacher to lecture hall (admin only)"""
    try:
        data = json.loads(request.body)
        hall_id = data.get('hall_id')
        teacher_id = data.get('teacher_id')

        if not hall_id or not teacher_id:
            return JsonResponse({'success': False, 'error': 'Hall ID and teacher ID required'}, status=400)

        try:
            hall = LectureHall.objects.get(id=hall_id)
            teacher = User.objects.get(id=teacher_id)
        except (LectureHall.DoesNotExist, User.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Hall or teacher not found'}, status=404)

        # Unassign teacher from other halls
        LectureHall.objects.filter(assigned_teacher=teacher).update(assigned_teacher=None)
        
        # Assign to new hall
        hall.assigned_teacher = teacher
        hall.save()

        return JsonResponse({'success': True, 'message': 'Teacher assigned successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============ TEACHER ENDPOINTS ============

@require_http_methods(["GET"])
@login_required
@user_passes_test(is_admin)
def api_teachers(request):
    """Get all teachers (admin only)"""
    try:
        assigned_filter = request.GET.get('assigned', '')
        building_filter = request.GET.get('building', '')

        teachers = User.objects.filter(is_superuser=False)

        if assigned_filter == 'assigned':
            teachers = teachers.filter(lecturehall__isnull=False)
        elif assigned_filter == 'unassigned':
            teachers = teachers.filter(lecturehall__isnull=True)

        if building_filter:
            teachers = teachers.filter(lecturehall__building=building_filter)

        teachers_data = []
        for teacher in teachers:
            teacher_data = {
                'id': teacher.id,
                'username': teacher.username,
                'email': teacher.email,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'full_name': teacher.get_full_name(),
            }
            
            try:
                profile = teacher.teacherprofile
                teacher_data['phone'] = profile.phone
                teacher_data['profile_picture'] = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
            except TeacherProfile.DoesNotExist:
                pass
            
            try:
                hall = teacher.lecturehall
                teacher_data['lecture_hall'] = {
                    'id': hall.id,
                    'building': hall.building,
                    'hall_name': hall.hall_name,
                }
            except LectureHall.DoesNotExist:
                pass
            
            teachers_data.append(teacher_data)

        return JsonResponse({
            'success': True,
            'teachers': teachers_data
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============ CAMERA CONTROL ENDPOINTS ============

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def api_start_cameras(request):
    """Start camera scripts (admin only)"""
    try:
        # Camera configurations
        client_configs = [
            {
                "name": "Top Corner - Host(Allen 2)",
                "script_path": "C:\\Users\\noelm\\Documents\\PROJECTS\\DetectSus\\ML\\front.py",
                "mode": "local"
            },
        ]

        def run_on_client(config):
            if config.get("mode") == "remote":
                use_venv = config.get("use_venv", True)
                venv_path = config.get("venv_path", None)
                success, output = ssh_run_script(
                    config["ip"],
                    config["username"],
                    config["password"],
                    config["script_path"],
                    use_venv,
                    venv_path
                )
                print(f"[{config['name']}]: {output if success else 'Error: ' + output}")
            elif config.get("mode") == "local":
                success, output = local_run_script(config["script_path"])
                print(f"[{config['name']}]: {output if success else 'Error: ' + output}")

        # Launch scripts in threads
        for config in client_configs:
            threading.Thread(target=run_on_client, args=(config,)).start()

        return JsonResponse({'success': True, 'message': 'Cameras started'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def api_stop_cameras(request):
    """Stop camera scripts (admin only)"""
    try:
        for key in list(RUNNING_SCRIPTS.keys()):
            handle = RUNNING_SCRIPTS[key]
            if handle.get("mode") == "remote":
                try:
                    channel = handle.get("channel")
                    if channel:
                        channel.send("\x03")
                        time.sleep(2)
                        channel.close()
                    ssh = handle.get("ssh")
                    if ssh:
                        ssh.close()
                    print(f"[{key}] Remote process terminated")
                except Exception as e:
                    print(f"[{key}] Error: {e}")
            elif handle.get("mode") == "local":
                process = handle.get("process")
                if process:
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                        print(f"[{key}] Local process terminated")
                    except Exception as e:
                        print(f"[{key}] Error: {e}")
            RUNNING_SCRIPTS.pop(key, None)

        return JsonResponse({'success': True, 'message': 'Cameras stopped'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
