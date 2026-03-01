from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from expenses.serializers import CreditCardSerializer , TransactionSerializer
from .models import CreditCard, Transaction
from rest_framework.response import Response
from django.db.models import Avg
import pandas as pd


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

@api_view(['GET'])
def transactions_list(request):
    qs=Transaction.objects.all()
    #Get all filter parameters
    credit_card_id=request.GET.get('credit_card_id')
    category=request.GET.get('category')
    payment_method=request.GET.get('payment_method')
    transaction_date=request.GET.get('date')

    #Apply Filters
    if credit_card_id:
        qs=qs.filter(credit_card_id=credit_card_id)

    if category:
        qs=qs.filter(category=category)

    if payment_method:
        qs=qs.filter(payment_method=payment_method)
    
    if transaction_date:
        qs=qs.filter(date=transaction_date)

    serializer=TransactionSerializer(qs,many=True)
    return Response(serializer.data)


@api_view(['GET'])
def transaction_stats_by_category(request):
    qs=Transaction.objects.values('category').annotate(average_amount=Avg('amount'))
    if not qs.exists():
        return Response({'message': 'You havent added any transactions yet'}, status=status.HTTP_200_OK)
    return Response(list(qs))


@api_view(['GET'])
def transaction_analytics(request):
    if request.method == 'GET':
        # Example analytics: Total spending by category
        qs=Transaction.objects.all().values(
            'category',
            'payment_method',
            'date',
            'amount'
        )
        if not qs.exists():
            return Response({'message': 'You havent added any transactions yet'}, status=status.HTTP_200_OK)
        df=pd.DataFrame(qs)
        total_transactions=len(df)
        average_spending_by_category=df.groupby('category')['amount'].mean().to_dict()
        total_spending_by_payment_method=df.groupby('payment_method')['amount'].sum().to_dict()
        df['date']=pd.to_datetime(df['date'])
        monthly_trends={str(k): v for k, v in df.groupby(df['date'].dt.to_period('M'))['amount'].sum().to_dict().items()}
        return Response({
            'total_transactions': total_transactions,
            'average_spending_by_category': average_spending_by_category,
            'total_spending_by_payment_method': total_spending_by_payment_method,
            'monthly_trends': monthly_trends
        })