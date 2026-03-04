from django.urls import reverse
from .models import CreditCard
from rest_framework import status
from rest_framework.test import APITestCase

# TODO: Rebuild views

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

    def test_create_credit_card(self):
        payload={
            "card_name": "Test Card 3",
            "credit_limit": 3000,
            "current_balance": 2000
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
            "current_balance": 2000
        }
        url=reverse('creditcard-list')
        response=self.client.post(url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CreditCard.objects.filter(card_name="Test Card 4").exists())
        self.assertEqual(response.data["error"], "Cannot create credit card: Current balance cannot exceed credit limit.")

