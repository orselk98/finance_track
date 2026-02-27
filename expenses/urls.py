from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditCardViewset, all_transactions, transaction_detail, transaction_stats_by_category, transactions_list

router =DefaultRouter()
router.register(r'credit_cards', CreditCardViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('transactions/', all_transactions, name='all-transactions'),
    path('transaction-detail/<int:pk>/', transaction_detail, name='transaction-detail'),
    path('transactions-list/', transactions_list, name='transactions-list'),
    path('transaction-stats-by-category/', transaction_stats_by_category, name='transaction-stats-by-category'),
]