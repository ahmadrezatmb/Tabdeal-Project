from django.urls import path
from .views import TabdealProject, WalletApiView, WalletDetailAPIView, WalletMixinAPIView, buy, charge_wallet, get_balance, get_wallet, home
urlpatterns = [
    # path('', WalletApiView.as_view()),
    path('<int:id>/', WalletMixinAPIView.as_view()),
    # path('<int:pk>/', get_wallet),
    # path('<int:id>/', WalletDetailAPIView.as_view()),
    path('charge/<int:pk>/', charge_wallet),
    path('get-balance/<int:pk>/', get_balance),
    path('buy/<int:pk>/', buy),

    # final

    path('v2/buy/<int:pk>/', TabdealProject.Buy.as_view()),
    path('v2/get-balance/<int:pk>/', TabdealProject.GetBalance.as_view()),
    path('v2/charge/<int:pk>/', TabdealProject.ChargeWallet.as_view())
]
