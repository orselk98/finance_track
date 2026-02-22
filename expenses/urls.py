from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditCardViewset

router =DefaultRouter()
router.register(r'credit_cards', CreditCardViewset)

urlpatterns = [
    path('', include(router.urls)),
    

]