from django.urls import path
from . import views
urlpatterns = [
    path('buy/<int:pk>/', views.TabdealProject.Buy.as_view(), name="buy"),
    path('get-balance/<int:pk>/',
         views.TabdealProject.GetBalance.as_view(), name="get-balance"),
    path('charge/<int:pk>/', views.TabdealProject.ChargeWallet.as_view(), name="charge")
]
