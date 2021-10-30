from rest_framework import status
from .test_setup import TestAPI
from wallet.models import Charge, Wallet

# import pdb
# pdb.set_trace()


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
