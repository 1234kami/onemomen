from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('activate/', ActivateAccountView.as_view(), name='activate'),
    path('api/applications/<str:lang>/', ApplicationListCreateAPIView.as_view(), name='application-list-create'),
    path('api/discounts/<str:lang>/', DiscountListCreateAPIView.as_view(), name='discount-list-create'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password-verify/', ResetPasswordVerifyView.as_view(), name='reset_password_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
]
