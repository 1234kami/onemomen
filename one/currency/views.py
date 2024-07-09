from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Coin, FiatCurrency
from .serializers import CoinSerializer, FiatCurrencySerializer
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse




class CoinDataAPIView(APIView):
    def get(self, request, *args, **kwargs):
        coins = Coin.objects.all()
        serializer = CoinSerializer(coins, many=True)
        data = {
            'success': 1,
            'data': serializer.data
        }
        return Response(data)



class FiatCurrencyListView(APIView):
    def get(self, request):
        fiat_currencies = FiatCurrency.objects.all()
        serializer = FiatCurrencySerializer(fiat_currencies, many=True)
        data = {
            "code": "000000",
            "message": None,
            "messageDetail": None,
            "data": {
                "fiatList": serializer.data
            }
        }
        return Response(data)




class All(APIView):
    def get(self, request, *args, **kwargs):
        banks = FiatCurrency.objects.all()
        cryptocurrencies = Coin.objects.all()

        banks_data = FiatCurrencySerializer(banks, many=True).data
        cryptocurrencies_data = CoinSerializer(cryptocurrencies, many=True).data

        data = {
            "vse": {
                "banks": banks_data,
                "cryptocurrencies": cryptocurrencies_data
            },
            "banki": banks_data,
            "kripta": cryptocurrencies_data
        }
        return Response(data)



# class Banks(APIView):
#     def get(self, request, *args, **kwargs):
#         banki = Bank.objects.all()

#         banki_data = BankSerializer(banki,many=True).data


#         data = {
#             "banki" : banki_data,

#         }
#         return Response(data)



class Allvalut(APIView):
    def get_queryset(self, model_class, name=None, code=None):
        queryset = model_class.objects.all()

        if name:
            queryset = queryset.filter(name=name)
        if code:
            queryset = queryset.filter(code=code)
        
        return queryset

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name', None)
        code = request.query_params.get('code', None)

        # Фильтрация фиатных валют
        fiat_queryset = self.get_queryset(FiatCurrency, name=name)
        fiat_serializer = FiatCurrencySerializer(fiat_queryset, many=True, context={'request': request})

        # Фильтрация криптовалют
        coin_queryset = self.get_queryset(Coin, name=name, code=code)
        coin_serializer = CoinSerializer(coin_queryset, many=True, context={'request': request})

        # Формирование ответа с объединёнными и отдельными данными
        data = {
            "all": {
                "banks": fiat_serializer.data,
                "cryptocurrencies": coin_serializer.data
            },
            "banks": fiat_serializer.data,
            "cryptocurrencies": coin_serializer.data
        }

        return Response(data)
