from django.test.client import Client
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from wallet.models import Wallet
from faker import Faker


class TestAPI(APITestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.users = []
        self.wallets = []
        self.faker = Faker()
        self.user_counts = 100
        for i in range(self.user_counts):
            new_user = User.objects.create(
                username=self.faker.email() + str(i), password="1234")
            self.users.append(new_user)
            new_wallet = Wallet.objects.create(owner=new_user, balance=0)
            self.wallets.append(new_wallet)
        return super().setUp()

    '''
        url for endpoints
    '''

    def get_buy_url(self, wallet):
        return reverse('buy', kwargs={'pk': wallet.id})

    def get_balance_check_url(self, wallet):
        return reverse('get-balance', kwargs={'pk': wallet.id})

    def get_charge_url(self, wallet):
        return reverse('charge', kwargs={'pk': wallet.id})

    def _buy_for_specific_user(self, user, data):
        res = self.client.post(
            self.get_buy_url(user.wallet_set.get()), data, format="json")
        assert (res.status_code == status.HTTP_200_OK or
                res.status_code == status.HTTP_400_BAD_REQUEST)

    def _charge_for_specific_user(self, user, data):
        res = self.client.post(
            self.get_charge_url(user.wallet_set.get()), data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def _get_balance_for_specific_user(self, user):
        res = self.client.get(
            self.get_balance_check_url(user.wallet_set.get()), format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def tearDown(self) -> None:
        return super().tearDown()
