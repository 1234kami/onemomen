from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.urls import reverse
from .serializers import PaymentInputSerializer
from .services import create_paypal_payment, execute_paypal_payment, save_payment_data, save_payment_transaction

class CreatePaymentView(APIView):
    """
    Вью для создания платежа через PayPal.
    """
    def post(self, request, *args, **kwargs):
        # Десериализация входных данных
        serializer = PaymentInputSerializer(data=request.data)
        if serializer.is_valid():
            # Сохранение данных платежа в базу данных
            payment_data = serializer.validated_data
            payment = save_payment_data(payment_data)
            
            # Создание PayPal платежа
            return_url = request.build_absolute_uri(reverse('execute-payment'))
            cancel_url = request.build_absolute_uri(reverse('cancel-payment'))
            paypal_payment = create_paypal_payment(payment.amount, payment.currency, return_url, cancel_url)
            
            if paypal_payment:
                # Сохранение транзакции платежа в базу данных
                save_payment_transaction(payment, paypal_payment.to_dict())
                
                # Возврат ссылки для оплаты
                approval_url = next(link.href for link in paypal_payment.links if link.rel == "approval_url")
                return Response({'approval_url': approval_url}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Ошибка создания платежа PayPal.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExecutePaymentView(APIView):
    """
    Вью для выполнения платежа через PayPal.
    """
    def get(self, request, *args, **kwargs):
        payment_id = request.query_params.get('paymentId')
        payer_id = request.query_params.get('PayerID')
        
        if payment_id and payer_id:
            # Выполнение платежа PayPal
            payment = execute_paypal_payment(payment_id, payer_id)
            if payment:
                return Response({'status': 'Платеж выполнен успешно.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Ошибка выполнения платежа PayPal.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Отсутствуют необходимые параметры.'}, status=status.HTTP_400_BAD_REQUEST)

class CancelPaymentView(APIView):
    """
    Вью для отмены платежа через PayPal.
    """
    def get(self, request, *args, **kwargs):
        return Response({'status': 'Платеж отменен.'}, status=status.HTTP_200_OK)
