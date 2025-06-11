from django.urls import path
from dorms.views import DormAPIView, RoomAPIView, BedAPIView, DormDetailsAPIView

urlpatterns = [
    path('', DormAPIView.as_view(), name='dorm-list'),
    path('details/<int:pk>/', DormDetailsAPIView.as_view(), name='dorm-list'),
    path('rooms/', RoomAPIView.as_view(), name='room-list'),
    path('beds/', BedAPIView.as_view(), name='bed-list'),
]