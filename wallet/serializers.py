from django.db import models
from rest_framework import fields, serializers
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']
