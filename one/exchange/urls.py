# exchange/urls.py

from django.urls import path
from .views import ConvertCryptoCurrency, ConvertFiatCurrency

urlpatterns = [
    path('convert/crypto/', ConvertCryptoCurrency.as_view(), name='convert_crypto_currency'),
    path('convert/fiat/', ConvertFiatCurrency.as_view(), name='convert_fiat_currency'),
]
