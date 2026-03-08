from django.shortcuts import get_object_or_404
from rest_framework import request, status, viewsets
from rest_framework.decorators import api_view
from expenses.serializers import CreditCardSerializer , TransactionSerializer
from .models import CreditCard, Transaction
from rest_framework.response import Response
from django.db.models import Avg, Sum, Count
import pandas as pd


# TODO: Rebuild views

class CreditCardViewset(viewsets.ModelViewSet):
        queryset=CreditCard.objects.all()
        serializer_class = CreditCardSerializer

        def create(self, request):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': "Cannot create credit card: Current balance cannot exceed credit limit."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def all_transactions(request):
    if request.method =="GET":
        qs=Transaction.objects.all()
        #Get all filter parameters
        allowed_ordering_fields=['amount', 'date']
        ordering=request.GET.get('ordering')
        if ordering:
            if ordering in allowed_ordering_fields:
                qs=qs.order_by(ordering)
            else:
                return Response({'message': f'Invalid ordering field. Allowed fields: {allowed_ordering_fields}'}, status=status.HTTP_400_BAD_REQUEST)
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


@api_view(['GET'])
def net_worth(request):
    """
    Returns a financial summary: total income, total expenses, and net balance.
    Supports optional ?start_date=YYYY-MM-DD and ?end_date=YYYY-MM-DD filters.
    """
    qs = Transaction.objects.all()

    # Optional date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    totals = qs.values('category').annotate(total=Sum('amount'))
    totals_map = {item['category']: float(item['total']) for item in totals}

    income = totals_map.get(Transaction.Category.INCOME, 0)
    needs = totals_map.get(Transaction.Category.NEED, 0)
    wants = totals_map.get(Transaction.Category.WANT, 0)
    savings = totals_map.get(Transaction.Category.SAVING, 0)
    total_expenses = needs + wants

    return Response({
        'income': round(income, 2),
        'total_expenses': round(total_expenses, 2),
        'savings_allocated': round(savings, 2),
        'net_balance': round(income - total_expenses - savings, 2),
    })


@api_view(['GET'])
def top_spending(request):
    """
    Returns the top N transactions by amount (descending).
    Supports optional ?limit=10 (default 5) and ?category= filters.
    Only considers expense categories: need, want.
    """
    limit = int(request.GET.get('limit', 5))
    category = request.GET.get('category')

    qs = Transaction.objects.exclude(category=Transaction.Category.INCOME)

    if category:
        qs = qs.filter(category=category)

    qs = qs.order_by('-amount')[:limit]
    serializer = TransactionSerializer(qs, many=True)
    return Response({
        'count': len(serializer.data),
        'results': serializer.data,
    })


@api_view(['GET'])
def budget_50_30_20(request):
    totals = Transaction.objects.values('category').annotate(total=Sum('amount'))
    totals_map = {item['category']: float(item['total']) for item in totals}

    income = totals_map.get(Transaction.Category.INCOME, 0)
    needs = totals_map.get(Transaction.Category.NEED, 0)
    wants = totals_map.get(Transaction.Category.WANT, 0)
    savings = totals_map.get(Transaction.Category.SAVING, 0)

    if income == 0:
        return Response({'message': 'No income transactions found.'}, status=status.HTTP_200_OK)

    def breakdown(actual, target_pct):
        target = round(income * target_pct / 100, 2)
        actual_pct = round((actual / income) * 100, 2)
        return {
            'actual': round(actual, 2),
            'actual_pct': actual_pct,
            'target': target,
            'target_pct': target_pct,
            'difference': round(actual - target, 2),
            'status': 'over' if actual > target else 'under' if actual < target else 'on_track',
        }

    return Response({
        'income': round(income, 2),
        'needs': breakdown(needs, 50),
        'wants': breakdown(wants, 30),
        'savings': breakdown(savings, 20),
    })