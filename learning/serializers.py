from rest_framework import serializers
from .models import Skill, Resource, UserCourse, ResourceStep




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


class ResourceStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceStep
        fields = [
            "id",
            "title",
            "order",
            "duration_minutes",
        ]



class ResourceSerializer(serializers.ModelSerializer):

    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True
    )

    steps = ResourceStepSerializer(
        many=True,
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
            "steps",
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

    current_step = ResourceStepSerializer(read_only=True)

    next_step = serializers.SerializerMethodField()


    class Meta:
        model = UserCourse
        fields = [
            "id",
            "course",
            "course_title",
            "course_url",
            "skill_name",
            "current_step",
            "next_step",
            "status",
            "started_at",
        ]

        read_only_fields = [
            "status",
            "started_at"
        ]

    def get_next_step(self, obj):

        if not obj.current_step:
            step = obj.course.steps.first()
        else:
            step = obj.course.steps.filter(
                order__gt=obj.current_step.order
            ).first()

        if step:
            return ResourceStepSerializer(step).data

        return None


class RecommendCourseSerializer(serializers.Serializer):

    skill = serializers.IntegerField()

    level = serializers.ChoiceField(
        choices=Resource.LevelChoices.choices
    )

    is_free = serializers.BooleanField()

    duration_minutes = serializers.ChoiceField(
        choices=Resource.Time_It_Takes
    )

    resource_type = serializers.ChoiceField(
        choices=Resource.Resource_types
    )
