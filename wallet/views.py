from django.shortcuts import get_object_or_404
from .models import Wallet
from .serializers import WalletSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import mixins
from django.db import transaction

class TabdealProject:

    class GetBalance(generics.GenericAPIView, mixins.RetrieveModelMixin):
        serializer_class = WalletSerializer
        queryset = Wallet.objects.all()

        def get(self, request, pk):
            return self.retrieve(request, pk)

    class ChargeWallet(generics.GenericAPIView, mixins.UpdateModelMixin):
        serializer_class = WalletSerializer
        queryset = Wallet.objects.all()

        def post(self, request, pk):
            charge_amount = float(request.POST['balance'])
            with transaction.atomic():
                # this_wallet = get_object_or_404(Wallet.objects.select_for_update(), id=pk)
                this_wallet = Wallet.objects.filter(id=pk).select_for_update()[0]
                this_wallet.new_charge(charge_amount)
                return Response({'balance': this_wallet.balance}, status=status.HTTP_200_OK)

    class Buy(generics.GenericAPIView, mixins.UpdateModelMixin):
        serializer_class = WalletSerializer
        queryset = Wallet.objects.all()

        def post(self, request, pk):
            purchase_cash = float(request.POST['balance'])
            with transaction.atomic():
                this_wallet = Wallet.objects.filter(id=pk).select_for_update()[0]
                this_wallet.new_buy(purchase_cash)
                if this_wallet.balance < purchase_cash:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response({'balance': this_wallet.balance}, status=status.HTTP_200_OK)
