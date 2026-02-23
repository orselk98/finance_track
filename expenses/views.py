from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from expenses.serializers import CreditCardSerializer , TransactionSerializer
from .models import CreditCard, Transaction
from rest_framework.response import Response

# TODO: Rebuild views

class CreditCardViewset(viewsets.ModelViewSet):
    queryset=CreditCard.objects.all()
    serializer_class = CreditCardSerializer

@api_view(['GET', 'POST'])
def all_transactions(request):
    if request.method =="GET":
        qs=Transaction.objects.all()
        serializer=TransactionSerializer(qs,many=True)
        return Response(serializer.data)
    
    if request.method =="POST":
        serializer=TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_transaction(request,pk):
    try:
        transaction=Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method =="GET":
        serializer=TransactionSerializer(transaction)
        return Response(serializer.data)