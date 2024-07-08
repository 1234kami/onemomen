# import paypalrestsdk
# from django.conf import settings
# from .models import Payment, PaymentTransaction

# from django.conf import settings
# import paypalrestsdk

# paypalrestsdk.configure({
#     "mode": "live",  # or "live"
#     "client_id": settings.PAYPAL_CLIENT_ID,
#     "client_secret": settings.PAYPAL_CLIENT_SECRET
# })


# def create_paypal_payment(amount, currency, return_url, cancel_url):
#     """
#     Функция для создания платежа PayPal.

#     :param amount: Сумма платежа
#     :param currency: Валюта платежа (например, "USD")
#     :param return_url: URL для перенаправления при успешной оплате
#     :param cancel_url: URL для перенаправления при отмене оплаты
#     :return: Объект платежа или None в случае ошибки
#     """
#     payment = paypalrestsdk.Payment({
#         "intent": "sale",
#         "payer": {
#             "payment_method": "paypal"
#         },
#         "transactions": [{
#             "amount": {
#                 "total": str(amount),
#                 "currency": currency
#             },
#             "description": "Оплата заказа"
#         }],
#         "redirect_urls": {
#             "return_url": return_url,
#             "cancel_url": cancel_url
#         }
#     })

#     if payment.create():
#         return payment
#     else:
#         print(payment.error)
#         return None

# def execute_paypal_payment(payment_id, payer_id):
#     """
#     Функция для выполнения платежа PayPal после подтверждения пользователем.

#     :param payment_id: ID платежа PayPal
#     :param payer_id: ID плательщика PayPal
#     :return: Объект платежа или None в случае ошибки
#     """
#     payment = paypalrestsdk.Payment.find(payment_id)

#     if payment.execute({"payer_id": payer_id}):
#         return payment
#     else:
#         print(payment.error)
#         return None

# def save_payment_data(payment_data):
#     """
#     Функция для сохранения данных платежа в базу данных.

#     :param payment_data: Данные платежа, которые нужно сохранить
#     :return: Объект Payment
#     """
#     payment = Payment(
#         email=payment_data['email'],
#         fio_sender=payment_data['fio_sender'],
#         sberbank_card=payment_data['sberbank_card'],
#         tether_wallet=payment_data['tether_wallet'],
#         amount=payment_data['amount'],
#         currency=payment_data['currency'],
#         status='created'
#     )
#     payment.save()
#     return payment

# def save_payment_transaction(payment, transaction_data):
#     """
#     Функция для сохранения данных транзакции платежа в базу данных.

#     :param payment: Объект Payment
#     :param transaction_data: Данные транзакции, которые нужно сохранить
#     :return: Объект PaymentTransaction
#     """
#     transaction = PaymentTransaction(
#         payment=payment,
#         transaction_id=transaction_data['id'],
#         status=transaction_data['state']
#     )
#     transaction.save()
#     return transaction






import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    # "mode": #settings.PAYPAL_MODE, 
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_paypal_payment(amount, currency, description):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": currency
            },
            "description": description
        }],
        "redirect_urls": {
            "return_url": "http://localhost:8000/api/payments/execute/",
            "cancel_url": "http://localhost:8000/api/payments/cancel/"
        }
    })

    if payment.create():
        return payment
    else:
        raise Exception(payment.error)

