from rest_framework import serializers
from .models import Skill, Resource, UserCourse



class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = "__all__"



class ResourceSerializer(serializers.ModelSerializer):

    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True
    )

    class Meta:
        model = Resource

        fields = [
            "id",
            "skill",
            "skill_name",
            "title",
            "description",
            "provider_name",
            "url",
            "language",
            "level",
            "is_free",
            "duration_minutes",
            "created_at",
            "updated_at",
        ]


class UserCourseSerializer(serializers.ModelSerializer):

    course_detail = ResourceSerializer(
        source="course",
        read_only=True
    )

    class Meta:
        model = UserCourse

        fields = [
            "id",
            "user",
            "course",
            "course_detail",
            "progress_percent",
            "status",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "status",
            "completed_at",
            "created_at",
            "updated_at",
        ]



