from django.urls import path
from .views import (
    ComplaintListCreateAPIView,
    ComplaintMessageCreateAPIView,
    ComplaintMessageListAPIView,
    ComplaintDeleteAPIView,
    ComplaintMessageDeleteAPIView,
    ComplaintMessageUpdateAPIView
)

urlpatterns = [
    path('', ComplaintListCreateAPIView.as_view(), name='complaint-list-create'),
    path('<str:complaint_id>/messages/', ComplaintMessageCreateAPIView.as_view(), name='complaint-messages'),
    path('<str:complaint_id>/messages/send/', ComplaintMessageListAPIView.as_view(), name='complaint-send-message'),
]

urlpatterns += [
    path('<int:pk>/delete/', ComplaintDeleteAPIView.as_view(), name='complaint-delete'),
    path('messages/<int:pk>/delete/', ComplaintMessageDeleteAPIView.as_view(), name='message-delete'),
    path('messages/<int:pk>/update/', ComplaintMessageUpdateAPIView.as_view(), name='message-update'),
]
