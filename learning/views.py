from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Skill, Resource, UserCourse
from .serializers import (
    SkillSerializer,
    ResourceSerializer,
    UserCourseSerializer,
    RecommendCourseSerializer,
)

from .services import recommend_course




class SkillListAPIView(APIView):

    def get(self, request):

        skills = Skill.objects.all()

        serializer = SkillSerializer(
            skills,
            many=True
        )

        return Response(serializer.data)



class MyCoursesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_courses = UserCourse.objects.filter(
            user=request.user
        ).select_related("course", "course__skill")

        serializer = UserCourseSerializer(
            user_courses,
            many=True
        )

        return Response(serializer.data)




class UpdateUserCourseAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        user_course = get_object_or_404(
            UserCourse,
            pk=pk,
            user=request.user
        )

        serializer = UserCourseSerializer(
            user_course,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

    def delete(self, request, pk):

        user_course = get_object_or_404(
            UserCourse,
            pk=pk,
            user=request.user
        )

        user_course.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)




class RecommendCourseAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = RecommendCourseSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        skill = serializer.validated_data["skill"]
        level = serializer.validated_data["level"]
        is_free = serializer.validated_data["is_free"]

        course = recommend_course(
            skill=skill,
            level=level,
            is_free=is_free
        )

        if not course:

            return Response(
                {"detail": "No course found."},
                status=status.HTTP_404_NOT_FOUND
            )

        response_serializer = ResourceSerializer(course)

        return Response(response_serializer.data)



class AddCourseAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        course_id = request.data.get("course_id")

        if not course_id:

            return Response(
                {"detail": "course_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(
            Resource,
            id=course_id
        )

        user_course, created = UserCourse.objects.get_or_create(
            user=request.user,
            course=course
        )

        serializer = UserCourseSerializer(user_course)

        return Response(serializer.data)



