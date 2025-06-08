from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer
from drf_spectacular.utils import extend_schema


class UserRegisterView(APIView):
    """
    documentation for UserRegisterView with spectacular
    """

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
