from django.contrib import admin
from rest_framework import fields

from wallet.models import Charge, Purchase, Wallet

# Register your models here.


admin.site.register(Wallet)
admin.site.register(Charge)
admin.site.register(Purchase)
