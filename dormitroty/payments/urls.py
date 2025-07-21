from django.urls import path
from .views import (
    CreateTransactionAPIView,
    TransactionListAPIView,
    TransactionRetrieveAPIView,
    TransactionDeleteAPIView,
)

urlpatterns = [
    path('create/', CreateTransactionAPIView.as_view(), name='create-transaction'),
    path('', TransactionListAPIView.as_view(), name='list-transactions'),
    path('<str:pk>/', TransactionRetrieveAPIView.as_view(), name='detail-transaction'),
    path('<str:pk>/delete/', TransactionDeleteAPIView.as_view(), name='delete-transaction'),
]