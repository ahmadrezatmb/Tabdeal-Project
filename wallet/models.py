from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Wallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return f'{self.owner} balance is {self.balance}'
