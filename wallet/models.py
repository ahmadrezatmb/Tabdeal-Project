from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Wallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.FloatField(validators=[MinValueValidator(0.0)])
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return f'{self.owner}\'s wallet'

    def add_balance(self, amount):
        self.balance = self.balance + amount
        return self.save()

    def new_charge(self, amount):
        self.add_balance(amount)
        new_charge = Charge.objects.create(wallet=self, amount=amount)
        return new_charge.save()

    def new_buy(self, cost):
        self.add_balance(-1 * cost)
        new_purchase = Purchase.objects.create(wallet=self, cost=cost)
        return new_purchase.save()


class Purchase(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    cost = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self) -> str:
        return f'wallet id={self.wallet.id} cost={self.cost}'


class Charge(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    amount = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self) -> str:
        return f'wallet id={self.wallet.id} amount={self.amount}'
