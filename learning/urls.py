from django.urls import path
from .views import (
    SkillListAPIView,
    MyCoursesAPIView,
    UpdateUserCourseAPIView,
    RecommendCourseAPIView,
    AddCourseAPIView,
)

urlpatterns = [

    path("skills/", SkillListAPIView.as_view()),
    path("my-courses/", MyCoursesAPIView.as_view()),
    path("my-courses/<int:pk>/", UpdateUserCourseAPIView.as_view()),
    path("recommend-course/", RecommendCourseAPIView.as_view()),
    path("add-course/", AddCourseAPIView.as_view()),
]
