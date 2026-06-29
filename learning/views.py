from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import (
    Skill,
    Resource,
    UserCourse,
    ResourceStep,
    UserCourseStepProgress,
)
from .serializers import (
    SkillSerializer,
    ResourceSerializer,
    UserCourseSerializer,
    RecommendCourseSerializer,
    UpdateCourseStepProgressSerializer,
)
from .services import recommend_course


class SkillListAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all().prefetch_related("subskills")
        serializer = SkillSerializer(
            skills,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class CourseListAPIView(APIView):

    def get(self, request):
        courses = (
            Resource.objects
            .select_related("skill", "subskill")
            .prefetch_related("steps")
            .order_by("-created_at")
        )

        skill = request.query_params.get("skill")
        subskill = request.query_params.get("subskill")
        level = request.query_params.get("level")
        resource_type = request.query_params.get("resource_type")
        is_free = request.query_params.get("is_free")
        duration_minutes = request.query_params.get("duration_minutes")
        language = request.query_params.get("language")

        if skill:
            courses = courses.filter(skill_id=skill)

        if subskill:
            courses = courses.filter(subskill_id=subskill)

        if level:
            courses = courses.filter(level=level)

        if resource_type:
            courses = courses.filter(resource_type=resource_type)

        if duration_minutes:
            courses = courses.filter(duration_minutes=duration_minutes)

        if language:
            courses = courses.filter(language=language)

        if is_free is not None:
            if is_free.lower() == "true":
                courses = courses.filter(is_free=True)
            elif is_free.lower() == "false":
                courses = courses.filter(is_free=False)

        serializer = ResourceSerializer(
            courses,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

class MyCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_courses = (
            UserCourse.objects
            .filter(user=request.user)
            .select_related(
                "course",
                "course__skill",
                "course__subskill",
                "current_step",
            )
            .prefetch_related(
                "course__steps",
                "step_progresses",
            )
        )

        serializer = UserCourseSerializer(
            user_courses,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class UpdateUserCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        input_serializer = UpdateCourseStepProgressSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(
                input_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        step_id = input_serializer.validated_data["step_id"]
        is_done = input_serializer.validated_data["is_done"]

        user_course = get_object_or_404(
            UserCourse.objects.select_related(
                "course",
                "course__skill",
                "course__subskill",
                "current_step",
            ),
            pk=pk,
            user=request.user,
        )

        step = get_object_or_404(
            ResourceStep,
            id=step_id,
            resource=user_course.course,
        )

        with transaction.atomic():
            progress, created = UserCourseStepProgress.objects.select_for_update().get_or_create(
                user_course=user_course,
                step=step,
                defaults={
                    "is_done": is_done,
                }
            )

            if not created:
                progress.is_done = is_done
                progress.save(update_fields=[
                    "is_done",
                    "completed_at",
                    "updated_at",
                ])

            user_course.update_progress_state()

        user_course = get_object_or_404(
            UserCourse.objects
            .filter(user=request.user)
            .select_related(
                "course",
                "course__skill",
                "course__subskill",
                "current_step",
            )
            .prefetch_related(
                "course__steps",
                "step_progresses",
            ),
            pk=pk,
        )

        serializer = UserCourseSerializer(
            user_course,
            context={"request": request}
        )
        return Response(serializer.data)

    def delete(self, request, pk):
        user_course = get_object_or_404(
            UserCourse,
            pk=pk,
            user=request.user,
        )
        user_course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommendCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecommendCourseSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = recommend_course(
            skill=serializer.validated_data["skill"],
            subskill=serializer.validated_data["subskill"],
            level=serializer.validated_data["level"],
            is_free=serializer.validated_data["is_free"],
            duration_minutes=serializer.validated_data["duration_minutes"],
            resource_type=serializer.validated_data["resource_type"],
        )

        if not course:
            return Response(
                {"detail": "No course found with these specifications."},
                status=status.HTTP_404_NOT_FOUND,
            )

        output_serializer = ResourceSerializer(
            course,
            context={"request": request}
        )
        return Response(output_serializer.data)


class AddCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"detail": "course_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(
            Resource.objects.prefetch_related("steps"),
            id=course_id,
        )

        with transaction.atomic():
            user_course, created = UserCourse.objects.get_or_create(
                user=request.user,
                course=course,
            )

            UserCourseStepProgress.objects.bulk_create(
                [
                    UserCourseStepProgress(
                        user_course=user_course,
                        step=step,
                        is_done=False,
                    )
                    for step in course.steps.all()
                ],
                ignore_conflicts=True,
            )

            user_course.update_progress_state()

        user_course = get_object_or_404(
            UserCourse.objects
            .filter(user=request.user)
            .select_related(
                "course",
                "course__skill",
                "course__subskill",
                "current_step",
            )
            .prefetch_related(
                "course__steps",
                "step_progresses",
            ),
            pk=user_course.pk,
        )

        serializer = UserCourseSerializer(
            user_course,
            context={"request": request}
        )
        return Response(serializer.data)