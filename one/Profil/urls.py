from django.urls import path
from .views import *
urlpatterns = [
    path('api/applications/<str:lang>/', ApplicationListCreateAPIView.as_view(), name='application-list-create'),
    path('api/discounts/<str:lang>/', DiscountListCreateAPIView.as_view(), name='discount-list-create'),

]