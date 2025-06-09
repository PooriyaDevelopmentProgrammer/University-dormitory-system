from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserRegisterSerializer
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from . import models

class UserRegisterView(APIView):
    """
    documentation for UserRegisterView with spectacular
    """
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        summary="Register a new user",
        request=UserRegisterSerializer,
        responses={
            201: {'description': 'User created successfully'},
            400: {'description': 'Invalid data'}
        }
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        get all users from database
        """
        users = models.User.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    swagger docs with spectacular
    """
    @extend_schema(
        summary="Logout user",
        request=None,
        responses={
            200: {'description': 'Successfully logged out'},
            400: {'description': 'Invalid request'}
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)