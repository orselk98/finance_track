from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditCardViewset, all_transactions, transaction_analytics, transaction_detail, transaction_stats_by_category, transactions_list, budget_50_30_20, net_worth, top_spending

router =DefaultRouter()
router.register(r'credit_cards', CreditCardViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('transactions/', all_transactions, name='all-transactions'),
    path('transaction-detail/<int:pk>/', transaction_detail, name='transaction-detail'),
    path('transactions-list/', transactions_list, name='transactions-list'),
    path('transaction-stats-by-category/', transaction_stats_by_category, name='transaction-stats-by-category'),
    path('transaction-analytics/', transaction_analytics, name='transaction-analytics'),
    path('budget/50-30-20/', budget_50_30_20, name='budget-50-30-20'),
    path('net-worth/', net_worth, name='net-worth'),
    path('top-spending/', top_spending, name='top-spending'),
]