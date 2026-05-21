from django.urls import path

from .views import (
    SkillListAPIView,
    MyCoursesAPIView,
    UpdateUserCourseAPIView,
    RecommendCourseAPIView,
    AddCourseAPIView,
)

urlpatterns = [

    path(
        "skills/",
        SkillListAPIView.as_view(),
        name="skills-list"
    ),

    path(
        "my-courses/",
        MyCoursesAPIView.as_view(),
        name="my-courses"
    ),

    path(
        "my-courses/<int:pk>/",
        UpdateUserCourseAPIView.as_view(),
        name="update-user-course"
    ),

    path(
        "recommend-course/",
        RecommendCourseAPIView.as_view(),
        name="recommend-course"
    ),

    path(
        "add-course/",
        AddCourseAPIView.as_view(),
        name="add-course"
    ),
]
