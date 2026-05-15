from rest_framework import serializers
from .models import Skill, Resource, UserCourse




class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
        ]



class ResourceSerializer(serializers.ModelSerializer):

    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True
    )

    class Meta:
        model = Resource
        fields = [
            "id",
            "title",
            "description",
            "resource_type",
            "provider_name",
            "url",
            "language",
            "level",
            "is_free",
            "duration_minutes",
            "skill",
            "skill_name",
        ]



class UserCourseSerializer(serializers.ModelSerializer):

    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )

    course_url = serializers.CharField(
        source="course.url",
        read_only=True
    )

    skill_name = serializers.CharField(
        source="course.skill.name",
        read_only=True
    )

    class Meta:
        model = UserCourse
        fields = [
            "id",
            "course",
            "course_title",
            "course_url",
            "skill_name",
            "progress_percent",
            "status",
            "started_at",
        ]

        read_only_fields = [
            "status",
            "started_at"
        ]



class RecommendCourseSerializer(serializers.Serializer):

    skill = serializers.IntegerField()

    level = serializers.ChoiceField(
        choices=Resource.LevelChoices.choices
    )

    is_free = serializers.BooleanField()

    duration_minutes = serializers.IntegerField(
        required=False
    )
