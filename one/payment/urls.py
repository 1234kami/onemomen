from django.urls import path
from .views import PaymentCreateView, PayPalExecuteView, PayPalCancelView, PaymentHistoryView

urlpatterns = [
    path('create-payment/', PaymentCreateView.as_view(), name='create-payment'),
    path('execute/', PayPalExecuteView.as_view(), name='paypal-execute'),
    path('cancel/', PayPalCancelView.as_view(), name='paypal-cancel'),
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
]
