from django.test.client import Client
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

        for i in range(100):
            new_user = User.objects.create(
                username=self.faker.email(), password="1234")
            self.users.append(new_user)
            new_wallet = Wallet.objects.create(owner=new_user, balance=0)
            self.wallets.append(new_wallet)
        return super().setUp()
    # url for endpoints

    def get_buy_url(self, wallet):
        return reverse('buy', kwargs={'pk': wallet.id})

    def get_balance_check_url(self, wallet):
        return reverse('get-balance', kwargs={'pk': wallet.id})

    def get_charge_url(self, wallet):
        return reverse('charge', kwargs={'pk': wallet.id})

    def tearDown(self) -> None:
        return super().tearDown()
