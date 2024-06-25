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

from .models import *
from .serializers import *
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
            user.is_active = False
            user.set_password(password)
            user.save()

            # Генерация и установка кода активации
            activation_code = generate_activation_code()
            user.activation_code = activation_code
            user.save()

            # Отправка письма с кодом активации
            message = (
                f"<h1>Здравствуйте, {user.email}!</h1>"
                f"<p>Поздравляем Вас с успешной регистрацией на сайте {settings.BASE_URL}</p>"
                f"<p>Ваш код активации: {activation_code}</p>"
                f"<p>С наилучшими пожеланиями,<br>Команда {settings.BASE_URL}</p>"
            )

            send_mail(
                _('Активация вашего аккаунта'),
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message,
            )

            return Response({
                'response': True,
                'message': _(
                    'Пользователь успешно зарегистрирован. Проверьте вашу электронную почту для получения кода активации.')
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({
                'response': False,
                'message': _('Не удалось зарегистрировать пользователя')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivateAccountView(generics.GenericAPIView):
    """Активация учетной записи по коду активации."""
    serializer_class = ActivationCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # email = serializer.validated_data['email']
        activation_code = serializer.validated_data['activation_code']

        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save()
            return Response({
                'response': True,
                'message': _('Ваш аккаунт был успешно активирован.')
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'response': False,
                'message': _('Неверный код активации или email.')
            }, status=status.HTTP_400_BAD_REQUEST)

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
    """Просмотр профиля пользователя."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
