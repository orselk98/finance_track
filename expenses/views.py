from rest_framework import viewsets

from expenses.serializers import CreditCardSerializer
from .models import CreditCard, Transaction

# TODO: Rebuild views

class CreditCardViewset(viewsets.ModelViewSet):
    queryset=CreditCard.objects.all()
    serializer_class = CreditCardSerializer