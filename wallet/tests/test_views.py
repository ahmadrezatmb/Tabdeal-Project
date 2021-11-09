from rest_framework import status
from .test_setup import TestAPI
from wallet.models import Charge, Purchase, Wallet
import random
import threading
from multiprocessing import Process
from django.db import transaction
from django import db
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
        import pdb
        pdb.set_trace()
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

        self.assertEqual(Purchase.objects.count(), 0)
        self.assertEqual(Charge.objects.count(), 0)
        self.assertEqual(Wallet.objects.count(), self.user_counts)

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
        self.assertEqual(Charge.objects.count(), self.user_counts)

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
        self.assertEqual(Purchase.objects.count(), self.user_counts)

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

        self.assertEqual(Purchase.objects.count(), 0)
        self.assertEqual(Charge.objects.count(), 0)
        self.assertEqual(Wallet.objects.count(), self.user_counts)

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
        self.assertEqual(Charge.objects.count(), self.user_counts)

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
        self.assertEqual(Purchase.objects.count(), self.user_counts)

        # checking balance
        for user in self.users:
            res = self.client.get(
                self.get_balance_check_url(user.wallet_set.get()), format="json")
            self.assertEqual(res.data, {'balance': 0})
    
    def test_multithreading_charge_then_buy(self):
        # first we must charge all wallets
        threads = []
        data = {"balance": "100"}
        
        for user in self.users:
            threads.append(threading.Thread(target=self._charge_for_specific_user,args=(user, data)))
            
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

        # start buying
        threads.clear()
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._buy_for_specific_user, args=(user, data))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        purchase_instances = Purchase.objects.all()
        self.assertEqual(purchase_instances.count(), self.user_counts)

        for buy in purchase_instances:
            self.assertEqual(buy.cost, 100)

    def test_multithreading_shop_scenario_one(self):
        """
            1 - buying with empty wallet
            2 - checking balance
            3 - charging
            4 - buying 
            5 - checking balance
        """
        threads = []

        # buying with empty wallet
        for user in self.users:
            data = {
                'balance': random.randint(1, 13000)
            }
            threads.append(
                threading.Thread(
                    target=self._buy_for_specific_user, args=(user, data))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(Purchase.objects.count(), 0)
        self.assertEqual(Charge.objects.count(), 0)

        # checking balance
        threads.clear()
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._get_balance_for_specific_user, args=(user,))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        self.assertEqual(Purchase.objects.count(), 0)
        self.assertEqual(Charge.objects.count(), 0)

        # charging
        threads.clear()
        data = {"balance": "100"}
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._charge_for_specific_user, args=(user, data))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        wallets = Wallet.objects.all()
        for wallet in wallets:
            self.assertEqual(wallet.balance, 100)
        self.assertEqual(Charge.objects.count(), self.user_counts)

        # buying
        threads.clear()
        data = {"balance": "50"}
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._buy_for_specific_user, args=(user, data))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        wallets = Wallet.objects.all()
        for wallet in wallets:
            self.assertEqual(wallet.balance, 50)
        self.assertEqual(Purchase.objects.count(), self.user_counts)

        threads.clear()
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._get_balance_for_specific_user, args=(user,))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
        self.assertEqual(Purchase.objects.count(), self.user_counts)
        self.assertEqual(Charge.objects.count(), self.user_counts)

    def test_multithreading_for_one_user(self):
        """
            for 1 user :
                1 - charging twice at the same time
        """
        this_user = self.users[0]
        data = {
            'balance': 100
        }
        t1 = threading.Thread(
            target=self._charge_for_specific_user, args=(this_user, data))
        t2 = threading.Thread(
            target=self._charge_for_specific_user, args=(this_user, data))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(this_user.wallet_set.get().balance, 200)

    def test_multithreading_buy_and_charge_for_one_user(self):
        """
            for one user:
                1 - charging
                2 - buying and charging at the same time
        """
        this_user = self.users[0]
        data = {
            'balance': 100
        }
        # charging
        self._charge_for_specific_user(this_user, data)

        # buying and charging at the same time
        t1 = threading.Thread(
            target=self._charge_for_specific_user,args=(this_user, data))
        t2 = threading.Thread(
            target=self._buy_for_specific_user, args=(this_user, data))
        t3 = threading.Thread(
            target=self._get_balance_for_specific_user, args=(this_user,))
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

        self.assertEqual(this_user.wallet_set.get().balance, 100)
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(Charge.objects.count(), 2)

    def test_multithreading_buy_and_charge_for_many_user(self):
        """
            for all self.user_count users :
                1 - charging
                2 - charging and buying at the same time
        """
        # charging
        threads = []
        data = {"balance": "1000"}
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._charge_for_specific_user, args=(user, data))
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        wallets = Wallet.objects.all()
        for wallet in wallets:
            self.assertEqual(wallet.balance, 1000)
        self.assertEqual(Charge.objects.count(), self.user_counts)

        # buying and charging at the same time

        threads.clear()
        for user in self.users:
            threads.append(
                threading.Thread(
                    target=self._charge_for_specific_user, args=((user, data)))
            )
            threads.append(threading.Thread(
                target=self._buy_for_specific_user, args=(user, {'balance': "401.23"})))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
       
        purchase_instances = Purchase.objects.all()
        charge_instances = Charge.objects.all()
        wallet_instances = Wallet.objects.all()
        self.assertEqual(purchase_instances.count(), self.user_counts)
        self.assertEqual(charge_instances.count(), (self.user_counts)*2)
        for purchase in purchase_instances:
            self.assertEqual(purchase.cost, 401.23)
        for charge in charge_instances:
            self.assertEqual(charge.amount, 1000)
        for wallet in wallet_instances:
            self.assertEqual(wallet.balance, 2000 - 401.23)

    def test_charging_wallet_and_buy_100_times(self):
        """
            charging and buying for 1 user about 100 times
        """

        threads = []
        this_user = self.users[12]

        # charging
        for i in range(16):
            threads.append(threading.Thread(
                target=self._charge_for_specific_user, args=(this_user, {'balance': 240.5})))
            threads[i].start()
        for i in range(16):
            threads[i].join()
        this_wallet = this_user.wallet_set.get()

        self.assertEqual(this_wallet.balance, 16 * 240.5)
        self.assertEqual(Charge.objects.count(), 16)

        # buying
        threads.clear()
        for i in range(16):
            threads.append(threading.Thread(
                target=self._buy_for_specific_user, args=(this_user, {'balance': 240.5})))
            threads[i].start()
        for i in range(16):
            threads[i].join()

        self.assertEqual(Purchase.objects.count(), 16)
        self.assertEqual(this_user.wallet_set.get().balance, 0)
    
    def test_multiprocessing_one_user(self):
        db.connections.close_all()
        this_user = self.users[0]

        t1 = Process(target=self._charge_for_specific_user, args=(this_user, {'balance' : 1000}))
        t2 = Process(target=self._charge_for_specific_user, args=(this_user, {'balance' : 1000}))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        self.assertEqual(Charge.objects.count(), 2)        
        self.assertEqual(this_user.wallet_set.get().balance, 2000)

        t1 = Process(target=self._buy_for_specific_user(this_user, {'balance' : 1000}))
        t2 = Process(target=self._buy_for_specific_user(this_user, {'balance' : 1000}))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(Purchase.objects.count(), 2)        
        self.assertEqual(this_user.wallet_set.get().balance, 0)