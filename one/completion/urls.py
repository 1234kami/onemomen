# completion/urls.py

from django.urls import path
from .views import PaymentDetailsAPIView

urlpatterns = [
    path('payment-details/', PaymentDetailsAPIView.as_view(), name='payment-details'),
]
