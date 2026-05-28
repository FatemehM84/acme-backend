from django.urls import path
from .views import RegisterView, LoginView, MeView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signin/', RegisterView.as_view(), name='signin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('token/refresh/',TokenRefreshView.as_view(),
        name='token_refresh'),
]
