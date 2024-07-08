# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.urls import reverse
# from .serializers import PaymentInputSerializer
# from .services import create_paypal_payment, execute_paypal_payment, save_payment_data, save_payment_transaction

# class CreatePaymentView(APIView):
#     """
#     Вью для создания платежа через PayPal.
#     """
#     def post(self, request, *args, **kwargs):
#         # Десериализация входных данных
#         serializer = PaymentInputSerializer(data=request.data)
#         if serializer.is_valid():
#             # Сохранение данных платежа в базу данных
#             payment_data = serializer.validated_data
#             payment = save_payment_data(payment_data)
            
#             # Создание PayPal платежа
#             return_url = request.build_absolute_uri(reverse('execute-payment'))
#             cancel_url = request.build_absolute_uri(reverse('cancel-payment'))
#             paypal_payment = create_paypal_payment(payment.amount, payment.currency, return_url, cancel_url)
            
#             if paypal_payment:
#                 # Сохранение транзакции платежа в базу данных
#                 save_payment_transaction(payment, paypal_payment.to_dict())
                
#                 # Возврат ссылки для оплаты
#                 approval_url = next(link.href for link in paypal_payment.links if link.rel == "approval_url")
#                 return Response({'approval_url': approval_url}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'error': 'Ошибка создания платежа PayPal.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ExecutePaymentView(APIView):
#     """
#     Вью для выполнения платежа через PayPal.
#     """
#     def get(self, request, *args, **kwargs):
#         payment_id = request.query_params.get('paymentId')
#         payer_id = request.query_params.get('PayerID')
        
#         if payment_id and payer_id:
#             # Выполнение платежа PayPal
#             payment = execute_paypal_payment(payment_id, payer_id)
#             if payment:
#                 return Response({'status': 'Платеж выполнен успешно.'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Ошибка выполнения платежа PayPal.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response({'error': 'Отсутствуют необходимые параметры.'}, status=status.HTTP_400_BAD_REQUEST)

# class CancelPaymentView(APIView):
#     """
#     Вью для отмены платежа через PayPal.
#     """
#     def get(self, request, *args, **kwargs):
#         return Response({'status': 'Платеж отменен.'}, status=status.HTTP_200_OK)








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from .serializers import PaymentDetailsSerializer
from .serializers import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PaymentCreateView(APIView):
    """
    Create a new payment.

    Parameters:
    - email (string): Email address of the payer.
    - sender_name (string): Full name of the sender.
    - sberbank_card (string): Sberbank card number (16-18 digits).
    - tether_wallet (string): Tether (TRC20) wallet address.
    - amount (decimal): Amount of the payment.
    - currency (string): Currency of the payment (3-character code).
    - description (string): Description of the payment.
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'sender_name', 'sberbank_card', 'tether_wallet', 'amount', 'currency', 'description'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the payer'),
                'sender_name': openapi.Schema(type=openapi.TYPE_STRING, description='Full name of the sender'),
                'sberbank_card': openapi.Schema(type=openapi.TYPE_STRING, description='Sberbank card number (16-18 digits)'),
                'tether_wallet': openapi.Schema(type=openapi.TYPE_STRING, description='Tether (TRC20) wallet address'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount of the payment'),
                'currency': openapi.Schema(type=openapi.TYPE_STRING, description='Currency of the payment (3-character code)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the payment'),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = PaymentDetailsSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        payments = Payment.objects.all()
        serializer = PaymentHistorySerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class PayPalExecuteView(APIView):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')

        if not payment_id or not payer_id:
            return Response({'error': 'Payment ID and Payer ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({'payer_id': payer_id}):
            payment_record = Payment.objects.get(paypal_payment_id=payment_id)
            payment_record.status = 'completed'
            payment_record.save()
            return Response({'status': 'Payment executed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)



class PayPalCancelView(APIView):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('paymentId')

        if not payment_id:
            return Response({'error': 'Payment ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_record = Payment.objects.get(paypal_payment_id=payment_id)
            payment_record.status = 'cancelled'
            payment_record.save()
            return Response({'status': 'Payment cancelled successfully'}, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)


