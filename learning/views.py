from django.shortcuts import render

# Create your views here.
import json

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import Skill, Resource, UserCourse
from .serializers import (
    SkillSerializer,
    ResourceSerializer,
    UserCourseSerializer
)


class SkillListAPIView(APIView):

    def get(self, request):

        skills = Skill.objects.all()

        serializer = SkillSerializer(
            skills,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer =SkillSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    



