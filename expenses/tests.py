from django.urls import reverse
from .models import CreditCard, Transaction
from rest_framework import status
from rest_framework.test import APITestCase


class CreditCardTest(APITestCase):
    def setUp(self):
        self.card1=CreditCard.objects.create(
            card_name="Test Card 1",
            credit_limit=1000,
            current_balance=500
        )
        self.card2=CreditCard.objects.create(
            card_name="Test Card 2",
            credit_limit=2000,
            current_balance=1500
        )

    def test_list_credit_cards(self):
        url=reverse('creditcard-list')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_credit_card(self):
        url=reverse('creditcard-detail', args=[self.card1.pk])
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['card_name'], self.card1.card_name)

    def test_update_credit_card(self):
        url=reverse('creditcard-detail', args=[self.card1.pk])
        response=self.client.patch(url, data={"current_balance": 600}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card1.refresh_from_db()
        self.assertEqual(self.card1.current_balance, 600)

    def test_delete_credit_card(self):
        url=reverse('creditcard-detail', args=[self.card2.pk])
        response=self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CreditCard.objects.filter(pk=self.card2.pk).exists())

    def test_create_credit_card(self):
        payload={
            "card_name": "Test Card 3",
            "credit_limit": 3000,
            "current_balance": 2500
        }
        url=reverse('creditcard-list')
        response=self.client.post(url, data=payload, format='json')
        new_creditcard=CreditCard.objects.get(card_name="Test Card 3")

        self.assertIsNotNone(new_creditcard)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(new_creditcard.card_name, payload['card_name'])
        self.assertEqual(response.data['card_name'], payload['card_name'])
        self.assertEqual(new_creditcard.credit_limit, payload['credit_limit'])
        self.assertEqual(new_creditcard.current_balance, payload['current_balance'])

    def test_create_credit_card_post_invalid(self):
        payload={
            "card_name": "Test Card 4",
            "credit_limit": 1000,
            "current_balance": 2500
        }
        url=reverse('creditcard-list')
        response=self.client.post(url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CreditCard.objects.filter(card_name="Test Card 4").exists())
        self.assertEqual(response.data["error"], "Cannot create credit card: Current balance cannot exceed credit limit.")


class TransactionTest(APITestCase):
    def setUp(self):
        self.card=CreditCard.objects.create(
            card_name="My Card",
            credit_limit=5000,
            current_balance=1000
        )
        self.t1=Transaction.objects.create(
            title="Salary",
            amount=3000,
            date="2026-01-15",
            category=Transaction.Category.INCOME,
            payment_method=Transaction.PaymentMethod.CASH,
        )
        self.t2=Transaction.objects.create(
            title="Groceries",
            amount=200,
            date="2026-01-20",
            category=Transaction.Category.NEED,
            payment_method=Transaction.PaymentMethod.CREDIT_CARD,
            credit_card=self.card,
        )
        self.t3=Transaction.objects.create(
            title="Netflix",
            amount=15,
            date="2026-01-25",
            category=Transaction.Category.WANT,
            payment_method=Transaction.PaymentMethod.CASH,
        )

    def test_list_transactions(self):
        url=reverse('all-transactions')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_transactions_order_by_amount(self):
        url=reverse('all-transactions')
        response=self.client.get(url, {'ordering': 'amount'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        amounts=[float(t['amount']) for t in response.data]
        self.assertEqual(amounts, sorted(amounts))

    def test_list_transactions_order_by_invalid_field(self):
        url=reverse('all-transactions')
        response=self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_transaction(self):
        payload={
            "title": "Bus ticket",
            "amount": "5.00",
            "date": "2026-02-01",
            "category": "need",
            "payment_method": "cash",
        }
        url=reverse('all-transactions')
        response=self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Transaction.objects.filter(title="Bus ticket").exists())

    def test_create_transaction_with_credit_card(self):
        payload={
            "title": "Dinner",
            "amount": "80.00",
            "date": "2026-02-05",
            "category": "want",
            "payment_method": "credit_card",
            "credit_card_id": self.card.pk,
        }
        url=reverse('all-transactions')
        response=self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        txn=Transaction.objects.get(title="Dinner")
        self.assertEqual(txn.credit_card, self.card)

    def test_create_transaction_invalid(self):
        payload={
            "title": "Missing category",
            "amount": "50.00",
        }
        url=reverse('all-transactions')
        response=self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_transaction(self):
        url=reverse('transaction-detail', args=[self.t1.pk])
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.t1.title)

    def test_retrieve_transaction_not_found(self):
        url=reverse('transaction-detail', args=[99999])
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_transaction(self):
        url=reverse('transaction-detail', args=[self.t2.pk])
        response=self.client.patch(url, data={"amount": "250.00"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.t2.refresh_from_db()
        self.assertEqual(self.t2.amount, 250)

    def test_delete_transaction(self):
        url=reverse('transaction-detail', args=[self.t3.pk])
        response=self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(pk=self.t3.pk).exists())

    def test_transactions_list_filter_by_category(self):
        url=reverse('transactions-list')
        response=self.client.get(url, {'category': 'income'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.t1.title)

    def test_transactions_list_filter_by_payment_method(self):
        url=reverse('transactions-list')
        response=self.client.get(url, {'payment_method': 'cash'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_transactions_list_filter_by_date(self):
        url=reverse('transactions-list')
        response=self.client.get(url, {'date': '2026-01-20'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.t2.title)

    def test_transactions_list_filter_by_credit_card_id(self):
        url=reverse('transactions-list')
        response=self.client.get(url, {'credit_card_id': self.card.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.t2.title)


class TransactionStatsTest(APITestCase):
    def test_stats_by_category_empty(self):
        url=reverse('transaction-stats-by-category')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You havent added any transactions yet')

    def test_stats_by_category(self):
        Transaction.objects.create(
            title="Salary", 
            amount=3000, 
            category=Transaction.Category.INCOME, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Rent", 
            amount=1000, 
            category=Transaction.Category.NEED, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Food", 
            amount=200, 
            category=Transaction.Category.NEED, 
            payment_method=Transaction.PaymentMethod.CASH)
        url=reverse('transaction-stats-by-category')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        need_stat=next(item for item in response.data if item['category'] == 'need')
        self.assertEqual(float(need_stat['average_amount']), 600.0)


class TransactionAnalyticsTest(APITestCase):
    def test_analytics_empty(self):
        url=reverse('transaction-analytics')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You havent added any transactions yet')

    def test_analytics(self):
        Transaction.objects.create(
            title="Salary", 
            amount=3000, 
            date="2026-01-15", 
            category=Transaction.Category.INCOME, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Groceries", 
            amount=200, 
            date="2026-01-20", 
            category=Transaction.Category.NEED, 
            payment_method=Transaction.PaymentMethod.CREDIT_CARD)
        url=reverse('transaction-analytics')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_transactions'], 2)
        self.assertIn('average_spending_by_category', response.data)
        self.assertIn('total_spending_by_payment_method', response.data)
        self.assertIn('monthly_trends', response.data)


class NetWorthTest(APITestCase):
    def setUp(self):
        Transaction.objects.create(
            title="Salary", 
            amount=5000, 
            date="2026-01-10", 
            category=Transaction.Category.INCOME, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Rent", 
            amount=1500, 
            date="2026-01-15", 
            category=Transaction.Category.NEED, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Games", 
            amount=100, 
            date="2026-01-20", 
            category=Transaction.Category.WANT, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Investment", 
            amount=500, 
            date="2026-01-25", 
            category=Transaction.Category.SAVING, 
            payment_method=Transaction.PaymentMethod.CASH)

    def test_net_worth(self):
        url=reverse('net-worth')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['income'], 5000.0)
        self.assertEqual(response.data['total_expenses'], 1600.0)
        self.assertEqual(response.data['savings_allocated'], 500.0)
        self.assertEqual(response.data['net_balance'], 2900.0)

    def test_net_worth_with_date_filter(self):
        url=reverse('net-worth')
        response=self.client.get(url, {'start_date': '2026-01-20', 'end_date': '2026-01-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_expenses'], 100.0)
        self.assertEqual(response.data['income'], 0.0)


class TopSpendingTest(APITestCase):
    def setUp(self):
        Transaction.objects.create(
            title="Salary", 
            amount=5000, 
            category=Transaction.Category.INCOME, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Rent", 
            amount=1500, 
            category=Transaction.Category.NEED, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Groceries", 
            amount=300, 
            category=Transaction.Category.NEED, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Netflix", 
            amount=15, 
            category=Transaction.Category.WANT, 
            payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Gym", 
            amount=50, 
            category=Transaction.Category.WANT, 
            payment_method=Transaction.PaymentMethod.CASH)

    def test_top_spending_default(self):
        url=reverse('top-spending')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # income is excluded; 4 expense transactions remain, default limit=5
        self.assertEqual(response.data['count'], 4)
        amounts=[float(t['amount']) for t in response.data['results']]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    def test_top_spending_with_limit(self):
        url=reverse('top-spending')
        response=self.client.get(url, {'limit': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_top_spending_filter_by_category(self):
        url=reverse('top-spending')
        response=self.client.get(url, {'category': 'want'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        for txn in response.data['results']:
            self.assertEqual(txn['category'], 'want')


class Budget503020Test(APITestCase):
    def test_budget_no_income(self):
        url=reverse('budget-50-30-20')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'No income transactions found.')

    def test_budget_breakdown(self):
        Transaction.objects.create(
            title="Salary", amount=4000, category=Transaction.Category.INCOME, payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Rent", amount=2000, category=Transaction.Category.NEED, payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Fun", amount=1200, category=Transaction.Category.WANT, payment_method=Transaction.PaymentMethod.CASH)
        Transaction.objects.create(
            title="Savings", amount=800, category=Transaction.Category.SAVING, payment_method=Transaction.PaymentMethod.CASH)
        url=reverse('budget-50-30-20')
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['income'], 4000.0)
        self.assertEqual(response.data['needs']['actual'], 2000.0)
        self.assertEqual(response.data['needs']['target'], 2000.0)
        self.assertEqual(response.data['needs']['status'], 'on_track')
        self.assertEqual(response.data['wants']['actual'], 1200.0)
        self.assertEqual(response.data['wants']['status'], 'on_track')
        self.assertEqual(response.data['savings']['actual'], 800.0)
        self.assertEqual(response.data['savings']['status'], 'on_track')

    

