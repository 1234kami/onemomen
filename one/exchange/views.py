# exchange/views.py

import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CryptoCurrencyConversionSerializer, FiatCurrencyConversionSerializer

class ConvertCryptoCurrency(APIView):
    async def get_exchange_rate(self, from_currency, to_currency):
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': from_currency.lower(),
            'vs_currencies': to_currency.lower()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Проверка на наличие ошибок
            data = response.json()
            return data[from_currency.lower()][to_currency.lower()]

    async def post(self, request):
        serializer = CryptoCurrencyConversionSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            from_currency = serializer.validated_data['from_currency']
            to_currency = serializer.validated_data['to_currency']

            try:
                exchange_rate = await self.get_exchange_rate(from_currency, to_currency)
                converted_amount = amount * exchange_rate

                response_data = {
                    'amount': amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'converted_amount': converted_amount,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            except httpx.HTTPStatusError as e:
                return Response({'error': f'HTTP ошибка: {e.response.status_code}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except httpx.RequestError as e:
                return Response({'error': f'Ошибка запроса: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': f'Произошла ошибка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConvertFiatCurrency(APIView):
    async def get_exchange_rate(self, from_currency, to_currency):
        url = "https://data.fx.kg/api/v1/currencies"
        headers = {
            'Authorization': 'Bearer xrQq7XzYLGGXvK2ci0X9jhUKRJMvxnFBS9GiLnMAffb77394'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Проверка на наличие ошибок
            data = response.json()

            # Ваша бизнес-логика для получения курса фиатной валюты

            return 1.0  # В данном примере возвращаем фиксированный курс

    async def post(self, request):
        serializer = FiatCurrencyConversionSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            from_currency = serializer.validated_data['from_currency']
            to_currency = serializer.validated_data['to_currency']

            try:
                exchange_rate = await self.get_exchange_rate(from_currency, to_currency)
                converted_amount = amount * exchange_rate

                response_data = {
                    'amount': amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'converted_amount': converted_amount,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            except httpx.HTTPStatusError as e:
                return Response({'error': f'HTTP ошибка: {e.response.status_code}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except httpx.RequestError as e:
                return Response({'error': f'Ошибка запроса: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': f'Произошла ошибка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render

# Create your views here.
