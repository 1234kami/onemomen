# exchange/serializers.py

from rest_framework import serializers

class CryptoCurrencyConversionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=8)
    from_currency = serializers.CharField(max_length=10)
    to_currency = serializers.CharField(max_length=10)
    converted_amount = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)

class FiatCurrencyConversionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    from_currency = serializers.CharField(max_length=10)
    to_currency = serializers.CharField(max_length=10)
    converted_amount = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
