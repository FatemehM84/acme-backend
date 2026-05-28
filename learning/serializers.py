from rest_framework import serializers
from .models import Skill, SubSkill, Resource, UserCourse, ResourceStep


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
    subskill_name = serializers.CharField(
        source="course.subskill.name",
        read_only=True
    )
    current_step = ResourceStepSerializer(read_only=True)
    next_step = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserCourse
        fields = [
            "id",
            "course",
            "course_title",
            "course_url",
            "skill_name",
            "subskill_name",
            "current_step",
            "next_step",
            "progress_percentage",
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

    def get_progress_percentage(self, obj):
        total_steps = obj.course.steps.count()
        if total_steps == 0:
            return 0
        
        if not obj.current_step:
            return 0
            
        completed_steps = obj.current_step.order
        
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