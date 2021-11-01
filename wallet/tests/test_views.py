from rest_framework import status
from .test_setup import TestAPI
from wallet.models import Charge, Purchase, Wallet
import random


class TestView(TestAPI):
    def test_regular_buy_charge_getBalance(self):
        this_url = self.get_buy_url(self.wallets[0])
        data = {"balance": "100"}

        # buying with 0 balance (cash = 100)
        res = self.client.post(this_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.wallets[0].balance, 0)

        # charging wallet (amount = 100)
        this_url = self.get_charge_url(self.wallets[0])
        res = self.client.post(this_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        this_wallet = Wallet.objects.get(id=self.wallets[0].id)
        self.assertEqual(this_wallet.balance, 100)
        this_wallet_charge_instances = Charge.objects.filter(
            wallet=this_wallet)
        self.assertEqual(this_wallet_charge_instances.count(), 1)
        self.assertEqual(this_wallet_charge_instances[0].amount, 100)

        # buying after charging
        res = self.client.post(self.get_buy_url(
            this_wallet), data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.wallets[0].balance, 0)

        # simple get balance api check
        res = self.client.get(self.get_balance_check_url(this_wallet))
        self.assertEqual(res.data.get('balance'), 0)

    def test_many_user_charge(self):
        # charging all wallets
        data = {"balance": "100"}
        for user in self.users:
            res = self.client.post(
                self.get_charge_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(user.wallet_set.get().balance, 100)

    def test_many_user_buy(self):
        # first we must charge all wallets
        data = {"balance": "100"}
        for user in self.users:
            res = self.client.post(
                self.get_charge_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(user.wallet_set.get().balance, 100)
            self.assertEqual(res.data, {'balance': 100.0})

        charge_instances = Charge.objects.all()
        self.assertEqual(charge_instances.count(), self.user_counts)

        # buying with all users
        for user in self.users:
            res = self.client.post(
                self.get_buy_url(user.wallet_set.get()), data, format="json")
            this_wallet = user.wallet_set.get()
            self.assertEqual(this_wallet.balance, 0)
            self.assertEqual(this_wallet.purchase_set.all().count(), 1)
            self.assertEqual(res.data, {"balance": 0})

        charge_instances = Purchase.objects.all()
        self.assertEqual(charge_instances.count(), self.user_counts)

    def test_response_data(self):
        # checking charge response data
        this_user = self.users[0]
        data = {"balance": "100.01"}
        res = self.client.post(
            self.get_charge_url(this_user.wallet_set.get()), data, format="json")
        self.assertEqual(res.data, {"balance": 100.01})

        # checking buy response data
        res = self.client.post(
            self.get_buy_url(this_user.wallet_set.get()), data, format="json")
        self.assertEqual(res.data, {"balance": 0})

    def test_empty_wallet_buy(self):
        for user in self.users:
            data = {
                'balance': 100
            }
            res = self.client.post(
                self.get_buy_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})

        self.assertEqual(Purchase.objects.all().count(), 0)
        self.assertEqual(Charge.objects.all().count(), 0)
        self.assertEqual(Wallet.objects.all().count(), self.user_counts)

    def test_random_shop_scenario_one(self):
        """
            1 - charging
            2 - buying 
            3 - checking balance
        """
        # charging first
        for user in self.users:
            data = {
                'balance': random.randint(0, 120000)
            }
            res = self.client.post(
                self.get_charge_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(res.data, data)
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, data)
        self.assertEqual(Charge.objects.all().count(), self.user_counts)

        # buying
        for user in self.users:
            data = {
                'balance': user.wallet_set.get().balance
            }
            res = self.client.post(
                self.get_buy_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(res.data, {'balance': 0})
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})
        self.assertEqual(Purchase.objects.all().count(), self.user_counts)

        # checking balance
        for user in self.users:
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})

    def test_random_shop_scenario_two(self):
        """
            1 - buying with empty wallet
            2 - checking balance
            3 - charging
            4 - buying 
            5 - checking balance
        """
        # buying with empty wallet
        for user in self.users:
            data = {
                'balance': random.randint(1, 120000)
            }
            res = self.client.post(
                self.get_buy_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})

        self.assertEqual(Purchase.objects.all().count(), 0)
        self.assertEqual(Charge.objects.all().count(), 0)
        self.assertEqual(Wallet.objects.all().count(), self.user_counts)

        # checking balance
        for user in self.users:
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})

        # charging
        for user in self.users:
            data = {
                'balance': random.randint(0, 120000)
            }
            res = self.client.post(
                self.get_charge_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(res.data, data)
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, data)
        self.assertEqual(Charge.objects.all().count(), self.user_counts)

        # buying
        for user in self.users:
            data = {
                'balance': user.wallet_set.get().balance
            }
            res = self.client.post(
                self.get_buy_url(user.wallet_set.get()), data, format="json")
            self.assertEqual(res.data, {'balance': 0})
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})
        self.assertEqual(Purchase.objects.all().count(), self.user_counts)

        # checking balance
        for user in self.users:
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})
