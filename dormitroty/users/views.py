from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserRegisterSerializer
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from . import models


class UserRegisterView(APIView):
    """
    documentation for UserRegisterView with spectacular
    """
    permission_classes = [permissions.IsAdminUser]


    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return super().get_permissions()

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
    @extend_schema(
        summary="Get all users",
        responses={
            200: {'data':UserRegisterSerializer(many=True), 'description': 'List of all users'},
            401: {'description': 'not authenticated'},
        }
    )
    def get(self, request):
        """
        get all users from database
        """
        users = models.User.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Retrieve user details by ID",
        responses={
            200: UserRegisterSerializer,
            404: {'description': 'User not found'}
        }
    )
    def get(self, request, user_id):
        user = models.User.objects.filter(id=user_id).first()
        if user:
            serializer = UserRegisterSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update user details by ID",
        request=UserRegisterSerializer,
        responses={
            200: UserRegisterSerializer,
            400: {'description': 'Invalid data'},
            404: {'description': 'User not found'}
        }
    )
    def put(self, request, user_id):
        user = models.User.objects.filter(id=user_id).first()
        if user:
            serializer = UserRegisterSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Delete user by ID",
        responses={
            204: {'description': 'User deleted successfully'},
            404: {'description': 'User not found'}
        }
    )
    def delete(self, request, user_id):
        user = models.User.objects.filter(id=user_id).first()
        if user:
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


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


