from django.urls import path
from .views import UserRegisterView, LogoutView, UserDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('', UserRegisterView.as_view(), name='user-register'),
    path('details/<str:user_id>/', UserDetailView.as_view(), name='user-details'),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
