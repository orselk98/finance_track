from django.shortcuts import get_object_or_404
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
    

@api_view(['GET', 'PATCH', 'DELETE'])
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'GET':
        
        serializer = TransactionSerializer(transaction, many=False)
        return Response(serializer.data)
    
        
    if request.method == 'PATCH':
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        transaction.delete()
        return Response({"message": "Transaction deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

