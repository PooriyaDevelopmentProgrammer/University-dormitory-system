from django.urls import path
from .views import BookingListCreateAPIView, BookingDetailAPIView

urlpatterns = [
    path('', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('details/<str:booking_id>/', BookingDetailAPIView.as_view(), name='booking-list-create'),
]