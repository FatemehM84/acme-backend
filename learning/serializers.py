from rest_framework import serializers
from .models import (
    Skill,
    SubSkill,
    Resource,
    UserCourse,
    ResourceStep,
    UserCourseStepProgress,
    UserProfile,
)


class SubSkillSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SubSkill
        fields = ["id", "skill", "name", "image_url"]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        url = obj.image.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class SkillSerializer(serializers.ModelSerializer):
    subskills = SubSkillSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "image_url",
            "subskills",
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ResourceStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceStep
        fields = [
            "id",
            "title",
            "order",
            "duration_minutes",
        ]


class UserCourseStepStatusSerializer(serializers.ModelSerializer):
    is_done = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()

    class Meta:
        model = ResourceStep
        fields = [
            "id",
            "title",
            "order",
            "duration_minutes",
            "is_done",
            "completed_at",
        ]

    def _get_progress(self, obj):
        progress_map = self.context.get("progress_map", {})
        return progress_map.get(obj.id)

    def get_is_done(self, obj):
        progress = self._get_progress(obj)
        return bool(progress and progress.is_done)

    def get_completed_at(self, obj):
        progress = self._get_progress(obj)

        if not progress or not progress.completed_at:
            return None

        return progress.completed_at


class ResourceSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True
    )
    subskill_name = serializers.CharField(
        source="subskill.name",
        read_only=True
    )
    steps = ResourceStepSerializer(
        many=True,
        read_only=True
    )

    image_url = serializers.SerializerMethodField()


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
            "subskill",
            "subskill_name",
            "steps",
            "image_url",
        ]
        
    def get_image_url(self, obj):
        if not obj.image:
            return None

        url = obj.image.url
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(url)

        return url


class UserCourseSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source="course.title",
        read_only=True
    )
    course_url = serializers.CharField(
        source="course.url",
        read_only=True
    )
    course_image_url = serializers.SerializerMethodField()

    skill_name = serializers.CharField(
        source="course.skill.name",
        read_only=True
    )
    subskill_name = serializers.CharField(
        source="course.subskill.name",
        read_only=True
    )

    current_step = ResourceStepSerializer(read_only=True)
    next_step = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()
    completed_steps_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserCourse
        fields = [
            "id",
            "course",
            "course_title",
            "course_url",
            "course_image_url",
            "skill_name",
            "subskill_name",
            "current_step",
            "next_step",
            "steps",
            "total_steps",
            "completed_steps_count",
            "progress_percentage",
            "status",
            "started_at",
        ]
        read_only_fields = [
            "status",
            "started_at",
        ]

    def get_course_image_url(self, obj):
        if not obj.course.image:
            return None

        url = obj.course.image.url
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(url)

        return url

    def _progress_map(self, obj):
        return {
            progress.step_id: progress
            for progress in obj.step_progresses.all()
        }

    def get_steps(self, obj):
        progress_map = self._progress_map(obj)

        return UserCourseStepStatusSerializer(
            obj.course.steps.all(),
            many=True,
            context={
                **self.context,
                "progress_map": progress_map,
            }
        ).data

    def get_next_step(self, obj):
        if not obj.current_step:
            return None

        progress_map = self._progress_map(obj)

        next_steps = obj.course.steps.filter(
            order__gt=obj.current_step.order
        ).order_by("order")

        for step in next_steps:
            progress = progress_map.get(step.id)

            if not progress or not progress.is_done:
                return ResourceStepSerializer(step).data

        return None

    def get_total_steps(self, obj):
        return obj.course.steps.count()

    def get_completed_steps_count(self, obj):
        return obj.step_progresses.filter(is_done=True).count()

    def get_progress_percentage(self, obj):
        total_steps = obj.course.steps.count()

        if total_steps == 0:
            return 0

        completed_steps = obj.step_progresses.filter(is_done=True).count()
        percentage = (completed_steps / total_steps) * 100

        return min(100, max(0, int(round(percentage))))


class RecommendCourseSerializer(serializers.Serializer):
    skill = serializers.IntegerField()
    subskill = serializers.IntegerField()

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


class UpdateCourseStepProgressSerializer(serializers.Serializer):
    step_id = serializers.IntegerField()
    is_done = serializers.BooleanField(required=False, default=True)



class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )
    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "avatar_url",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar_url",
        ]

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None

        url = obj.avatar.url
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(url)

        return url