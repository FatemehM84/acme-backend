from django.urls import path
from .views import RegisterView, LoginView, MeView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/',RegisterView.as_view(),
        name='signup'),

    path('login/',LoginView.as_view(),
        name='login'),

    path('me/', MeView.as_view()),

    path('token/refresh/',TokenRefreshView.as_view(),
        name='token_refresh'),
]
