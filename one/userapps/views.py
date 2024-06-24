import random
import string
from django.contrib.auth import authenticate, logout
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from transliterate.utils import _
from .permissions import IsOwnerOrReadOnly  # Импортируем наше новое разрешение
from .models import User
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    ResetPasswordSerializer,
    ResetPasswordVerifySerializer,
    LogoutSerializer,
    UserProfileSerializer,
    ActivationCodeSerializer
)

def generate_activation_code():
    """Генерирует случайный код активации, состоящий только из цифр."""
    return ''.join(random.choices(string.digits, k=6))

class RegistrationAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = request.data.get('password')
        if len(password) < 8:
            return Response({
                'response': False,
                'message': _('Пароль должен быть не менее 8 символов.')
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            user.set_password(password)
            user.is_active = True  # Установить пользователя как активного
            user.save()

            return Response({
                'response': True,
                'message': _('Пользователь успешно зарегистрирован.')
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({
                'response': False,
                'message': _('Не удалось зарегистрировать пользователя')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(generics.CreateAPIView):
    """Аутентификация пользователя."""
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'response': True,
            'token': token.key
        }, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    """Запрос на сброс пароля."""
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            reset_code = generate_activation_code()
            user.reset_code = reset_code
            user.save()

            message = (
                f"Здравствуйте, {user.email}!\n\n"
                f"Ваш код для восстановления пароля: {reset_code}\n\n"
                f"С наилучшими пожеланиями,\nКоманда {settings.BASE_URL}"
            )

            send_mail(
                _('Восстановление пароля'),
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message,
            )

            return Response({
                'response': True,
                'message': _('Письмо с инструкциями по восстановлению пароля было отправлено на ваш email.')
            })

        except User.DoesNotExist:
            return Response({
                'response': False,
                'message': _('Пользователь с этим адресом электронной почты не найден.')
            }, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordVerifyView(generics.GenericAPIView):
    """Подтверждение сброса пароля."""
    serializer_class = ResetPasswordVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_code = serializer.validated_data['reset_code']

        try:
            user = User.objects.get(reset_code=reset_code)

            user.set_password(reset_code)
            user.reset_code = ''
            user.save()

            return Response({
                'response': True,
                'message': _('Password has been successfully changed.')
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'response': False,
                'message': _('Invalid password reset code.')
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(generics.GenericAPIView):
    """Выход пользователя из системы."""
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({
            'response': True,
            'message': _('Вы успешно вышли из системы.')
        })

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]  # Добавляем наше новое разрешение

    def get_object(self):
        return self.request.user
