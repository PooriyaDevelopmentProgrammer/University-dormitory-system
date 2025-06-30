from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserRegisterSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
        summary="Get all users or search users",
        responses={
            200: UserRegisterSerializer(many=True),
            400: {'description': 'Invalid query parameters'}
        },
        parameters=[
            OpenApiParameter(name='email', type=str, description='Filter by email'),
            OpenApiParameter(name='student_code', type=str, description='Filter by student code'),
            OpenApiParameter(name='national_code', type=str, description='Filter by national code'),
            OpenApiParameter(name='phone_number', type=str, description='Filter by phone number'),
            OpenApiParameter(name='gender', type=str, description='Filter by gender'),
            OpenApiParameter(name='first_name', type=str, description='Filter by first name'),
            OpenApiParameter(name='last_name', type=str, description='Filter by last name'),
        ]
    )
    def get(self, request):
        """
        Get all users or search users based on query parameters
        """
        query_params = request.query_params
        filters = {}
        if 'email' in query_params:
            filters['email__icontains'] = query_params['email']
        if 'student_code' in query_params:
            filters['student_code__icontains'] = query_params['student_code']
        if 'national_code' in query_params:
            filters['national_code__icontains'] = query_params['national_code']
        if 'phone_number' in query_params:
            filters['phone_number__icontains'] = query_params['phone_number']
        if 'gender' in query_params:
            filters['gender'] = query_params['gender']
        if 'first_name' in query_params:
            filters['first_name__icontains'] = query_params['first_name']
        if 'last_name' in query_params:
            filters['last_name__icontains'] = query_params['last_name']

        users = models.User.objects.filter(**filters)
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
