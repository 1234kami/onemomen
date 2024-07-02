# completion/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaymentDetailsSerializer

class PaymentDetailsAPIView(APIView):
    def get(self, request):
        serializer = PaymentDetailsSerializer(context={'request': request}, data={
            'amount': 1000.00,
            'currency': 'RUB',
            'requisites': '2202206875265626'
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

