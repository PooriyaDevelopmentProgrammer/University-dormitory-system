from django.urls import path
from .views import (
    CreateTransactionAPIView,
    TransactionListAPIView,
    TransactionRetrieveAPIView,
    TransactionDeleteAPIView,
    # StartZarinpalPaymentAPIView,
    # ZarinpalVerifyAPIView
    DormitoryFullFinanceReportAPIView
)

urlpatterns = [
    path('create/', CreateTransactionAPIView.as_view(), name='create-transaction'),
    path('', TransactionListAPIView.as_view(), name='list-transactions'),
    path('<str:pk>/', TransactionRetrieveAPIView.as_view(), name='detail-transaction'),
    path('<str:pk>/delete/', TransactionDeleteAPIView.as_view(), name='delete-transaction'),
]
"""urlpatterns += [
    path('<int:transaction_id>/pay/', StartZarinpalPaymentAPIView.as_view(), name='start-payment'),
    path('verify/', ZarinpalVerifyAPIView.as_view(), name='verify-payment'),
]"""

urlpatterns += [
    path('admin/full-report/', DormitoryFullFinanceReportAPIView.as_view(), name='dormitory-full-report'),
]
