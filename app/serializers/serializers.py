"""
Serializers for DetectSus API.
Uses Django REST Framework for model serialization.
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from app.models import TeacherProfile, LectureHall, MalpraticeDetection


class UserSerializer(serializers.ModelSerializer):
    """Serialize Django User for API responses."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'date_joined', 'is_superuser']
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class LectureHallSerializer(serializers.ModelSerializer):
    """Serialize LectureHall with optional assigned teacher info."""
    assigned_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = LectureHall
        fields = ['id', 'building', 'hall_name', 'assigned_teacher', 'assigned_teacher_name']
        read_only_fields = fields

    def get_assigned_teacher_name(self, obj):
        if obj.assigned_teacher:
            return obj.assigned_teacher.get_full_name() or obj.assigned_teacher.username
        return None


class MalpraticeDetectionSerializer(serializers.ModelSerializer):
    """Serialize MalpraticeDetection with lecture hall info."""
    lecture_hall_display = serializers.SerializerMethodField()
    assigned_faculty = serializers.SerializerMethodField()

    class Meta:
        model = MalpraticeDetection
        fields = [
            'id', 'date', 'time', 'malpractice', 'proof', 'is_malpractice',
            'verified', 'lecture_hall', 'lecture_hall_display', 'assigned_faculty'
        ]
        read_only_fields = fields

    def get_lecture_hall_display(self, obj):
        if obj.lecture_hall:
            return f"{obj.lecture_hall.building} - {obj.lecture_hall.hall_name}"
        return None

    def get_assigned_faculty(self, obj):
        if obj.lecture_hall and obj.lecture_hall.assigned_teacher:
            return obj.lecture_hall.assigned_teacher.get_full_name() or obj.lecture_hall.assigned_teacher.username
        return None


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serialize TeacherProfile with user info."""
    user = UserSerializer(read_only=True)
    lecture_hall_display = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = ['user', 'phone', 'profile_picture', 'lecture_hall', 'lecture_hall_display']
        read_only_fields = fields

    def get_lecture_hall_display(self, obj):
        if obj.lecture_hall:
            return f"{obj.lecture_hall.building} - {obj.lecture_hall.hall_name}"
        return None


class TeacherRegisterSerializer(serializers.Serializer):
    """Input serializer for teacher registration."""
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=1)
    phone = serializers.CharField(max_length=20)
    profile_picture = serializers.ImageField(required=True)


class EditProfileSerializer(serializers.Serializer):
    """Input serializer for editing profile."""
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Input serializer for password change."""
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
