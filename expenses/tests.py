from unittest.mock import patch, MagicMock
from urllib import response
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Transaction
from datetime import date

# Create your tests here.

class TransactionTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.transaction1 =Transaction.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.transaction2 =Transaction.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.transaction3 =Transaction.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )
    def test_summary_success(self):
        url='/api/transactions/summary/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expense', response.data)
        self.assertIn('balance', response.data)
        self.assertIn('by_category', response.data)

    def test_summary_calculations(self):
        url='/api/transactions/summary/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], 200.00)
        self.assertEqual(response.data['total_expense'], 160.00)
        self.assertEqual(response.data['balance'], 40.00)

    def test_summary_empty_database(self):

        Transaction.objects.all().delete()
        
        url='/api/transactions/summary/'
        
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'],0)
        self.assertEqual(response.data['total_expense'],0)
        self.assertEqual(response.data['balance'],0)

class CategoryStatsTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.transaction1 =Transaction.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.transaction2 =Transaction.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.transaction3 =Transaction.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )

    def test_category_stats_success(self):
        url='/api/transactions/category-stats/'
        response=self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)  # Should have 3 categories

    def test_category_stats_calculations(self):
        url='/api/transactions/category-stats/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        needs_item = None
        for item in response.data:
            if item['category__name'] == 'Needs':
                needs_item = item
                break
        self.assertEqual(needs_item['count'], 1)
        self.assertEqual(needs_item['total'], 60.00)
        self.assertEqual(needs_item['average'], 60.00)

    def test_category_stats_empty_database(self):
        Transaction.objects.all().delete()
        url='/api/transactions/category-stats/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class TransactionFilterTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.transaction1 =Transaction.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.transaction2 =Transaction.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.transaction3 =Transaction.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )

    def test_transaction_filter_category(self):
        url='/api/transactions/filter/?category=Needs'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['transactions']), 1)
        self.assertEqual(response.data['transactions'][0]['category']['name'], 'Needs')

    def test_filter_by_min_amount(self):
        url='/api/transactions/filter/?min_amount=80'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_max_amount(self):
        url='/api/transactions/filter/?max_amount=100'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        for t in response.data['transactions']:
            self.assertLessEqual(float(t['amount']), 100.00)

    def test_filter_by_amount_range(self):
        url='/api/transactions/filter/?min_amount=80&max_amount=150'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(float(response.data['transactions'][0]['amount']), 100.00)

    def test_filter_by_date_range(self):
        url='/api/transactions/filter/?start_date=2026-01-01&end_date=2026-01-02'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_ordering_by_amount_asc(self):
        url='/api/transactions/filter/?ordering=amount'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        amounts = [float(t['amount']) for t in response.data['transactions']]
        self.assertEqual(amounts, sorted(amounts))

    def test_filter_ordering_by_amount_desc(self):
        url='/api/transactions/filter/?ordering=-amount'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        amounts = [float(t['amount']) for t in response.data['transactions']]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    def test_filter_invalid_ordering(self):
        url='/api/transactions/filter/?ordering=description'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filter_invalid_min_amount(self):
        url='/api/transactions/filter/?min_amount=abc'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filter_invalid_max_amount(self):
        url='/api/transactions/filter/?max_amount=xyz'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filter_invalid_date_format(self):
        url='/api/transactions/filter/?start_date=not-a-date&end_date=2026-01-02'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filter_no_params_returns_all(self):
        url='/api/transactions/filter/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIn('total', response.data)
        self.assertIn('average', response.data)
        self.assertIn('transactions', response.data)

    def test_filter_nonexistent_category(self):
        url='/api/transactions/filter/?category=NonExistent'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['total'], 0)

    def test_filter_combined_category_and_amount(self):
        url='/api/transactions/filter/?category=Needs&min_amount=50'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['transactions'][0]['category']['name'], 'Needs')

    def test_filter_stats_accuracy(self):
        url='/api/transactions/filter/?category=Wants'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['total'], 100.00)
        self.assertEqual(response.data['average'], 100.00)


class AiCategorizeTest(APITestCase):
    def setUp(self):
        self.url = '/api/transactions/ai-categorize/'
        self.income_cat = Category.objects.create(name='Income')
        self.needs_cat = Category.objects.create(name='Needs')
        self.wants_cat = Category.objects.create(name='Wants')

    @patch('expenses.views.http_requests.post')
    def test_successful_categorization(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'labels': ['Needs', 'Wants', 'Income'],
            'scores': [0.85, 0.10, 0.05],
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        response = self.client.post(self.url, {'description': 'grocery shopping'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'grocery shopping')
        self.assertEqual(len(response.data['suggested_categories']), 3)
        self.assertEqual(response.data['suggested_categories'][0]['category'], 'Needs')
        self.assertEqual(response.data['suggested_categories'][0]['confidence'], 0.85)

    def test_missing_description(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('expenses.views.http_requests.post')
    def test_api_failure_returns_503(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError('Service unavailable')

        response = self.client.post(self.url, {'description': 'dinner at restaurant'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)

    def test_empty_categories_returns_400(self):
        Category.objects.all().delete()
        response = self.client.post(self.url, {'description': 'some expense'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
