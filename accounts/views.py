from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer,MeSerializer


# Create your views here.

#--register mode-----------------------------------

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "User created successfully"
            },
            status=status.HTTP_201_CREATED
        )

#--login mode--------------------------------------
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )
    
#--logout------------------------------------------
class LogoutView(GenericAPIView):

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Logged out successfully"},
            status=200
        )
    
#--meview------------------------------------------
class MeView(GenericAPIView):

    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

