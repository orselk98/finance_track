from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditCardViewset, all_transactions, transaction_detail

router =DefaultRouter()
router.register(r'credit_cards', CreditCardViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('transactions/', all_transactions, name='all-transactions'),
    path('transaction-detail/<int:pk>/', transaction_detail, name='transaction-detail'),
]