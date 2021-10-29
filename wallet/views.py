from django.shortcuts import get_object_or_404
from .models import Wallet
from .serializers import WalletSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import mixins


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
            charge_amount = int(request.POST['balance'])
            this_wallet = get_object_or_404(Wallet, id=pk)
            this_wallet.balance = this_wallet.balance + charge_amount
            this_wallet.save()
            return Response({'balance': this_wallet.balance}, status=status.HTTP_200_OK)

    class Buy(generics.GenericAPIView, mixins.UpdateModelMixin):
        serializer_class = WalletSerializer
        queryset = Wallet.objects.all()

        def post(self, request, pk):
            purchase_cash = int(request.POST['balance'])
            this_wallet = get_object_or_404(Wallet, id=pk)

            if this_wallet.balance < purchase_cash:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            this_wallet.balance = this_wallet.balance - purchase_cash
            this_wallet.save()
            return Response({'balance': this_wallet.balance}, status=status.HTTP_200_OK)
