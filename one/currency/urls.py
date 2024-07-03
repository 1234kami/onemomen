# urls.py
from django.urls import path
from .views import CoinDataAPIView, FiatCurrencyListView, All

urlpatterns = [
    path('api/coins/', CoinDataAPIView.as_view(), name='coin_data_api'),
    path('api/fiat-currencies/', FiatCurrencyListView.as_view(), name='fiat_currency_list_api'),
    path('api/all', All.as_view(), name='all_bank_cripta'),
]
