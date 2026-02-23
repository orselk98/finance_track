from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditCardViewset, all_transactions

router =DefaultRouter()
router.register(r'credit_cards', CreditCardViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('transactions/', all_transactions, name='all-transactions'),
]