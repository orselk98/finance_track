from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, category_stats, transaction_filter, transaction_summary

router =DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('transactions/summary/',transaction_summary, name='transaction-summary'),
    path('transactions/category-stats/', category_stats, name='category-stats'),
    path('transactions/filter/',transaction_filter,name='transaction-filter'),
    path('', include(router.urls)),

]