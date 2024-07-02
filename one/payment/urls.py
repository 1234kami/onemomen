from django.urls import path
from .views import CreatePaymentView, ExecutePaymentView, CancelPaymentView

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('execute-payment/', ExecutePaymentView.as_view(), name='execute-payment'),
    path('cancel-payment/', CancelPaymentView.as_view(), name='cancel-payment'),
]
