import random
import string
import re
from django.contrib.auth import authenticate, logout
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from .models import User
from .serializers import (
    UserSerializer,
    ActivationCodeSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordVerifySerializer,
    LogoutSerializer,
    UserProfileSerializer
)
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def generate_activation_code():
    """Генерирует случайный код активации, состоящий только из цифр, длиной 6 символов."""
    return ''.join(random.choices(string.digits, k=6))

def validate_password(password):
    """Проверка пароля на минимум 8 символов, наличие заглавной буквы, цифры и строчной буквы."""
    if len(password) < 8:
        return False, _('Пароль должен быть не менее 8 символов.')
    if not re.search(r'[A-Z]', password):
        return False, _('Пароль должен содержать хотя бы одну заглавную букву.')
    if not re.search(r'[a-z]', password):
        return False, _('Пароль должен содержать хотя бы одну строчную букву.')
    if not re.search(r'[0-9]', password):
        return False, _('Пароль должен содержать хотя бы одну цифру.')
    return True, ''

class RegistrationAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.debug(f"Registration request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({
                'response': False,
                'message': _('Ошибка валидации')
            }, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        is_valid, message = validate_password(password)
        if not is_valid:
            return Response({
                'response': False,
                'message': message
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

            # Determine the language preference of the user
            language = user.language if hasattr(user, 'language') else 'ru'

            # Отправка письма с кодом активации на английском и русском
            message_en = (
                f"<h1>{_('Hello')}, {user.email}!</h1>"
                f"<p>{_('Congratulations on successfully registering at')} {settings.BASE_URL}</p>"
                f"<p>{_('Your activation code')}: {activation_code}</p>"
                f"<p>{_('Best regards')},<br>{_('Team')} {settings.BASE_URL}</p>"
            )
            message_ru = (
                f"<h1>{_('Здравствуйте')}, {user.email}!</h1>"
                f"<p>{_('Поздравляем Вас с успешной регистрацией на сайте')} {settings.BASE_URL}</p>"
                f"<p>{_('Ваш код активации')}: {activation_code}</p>"
                f"<p>{_('С наилучшими пожеланиями')},<br>{_('Команда')} {settings.BASE_URL}</p>"
            )

            send_mail(
                _('Активация вашего аккаунта'),
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message_en if language == 'en' else message_ru,
            )

            return Response({
                'response': True,
                'message': {
                    'en': _('User successfully registered. Check your email for the activation code.'),
                    'ru': _('Пользователь успешно зарегистрирован. Проверьте вашу электронную почту для получения кода активации.')
                }
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"IntegrityError: {str(e)}")
            if 'email' in str(e):
                return Response({
                    'response': False,
                    'message': _('Такой email уже зарегистрирован.')
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'response': False,
                'message': _('Не удалось зарегистрировать пользователя.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivateAccountView(generics.GenericAPIView):
    """Активация учетной записи по коду активации."""
    serializer_class = ActivationCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activation_code = serializer.validated_data['activation_code']

        try:
            user = User.objects.get(activation_code=activation_code)
            # Проверка на срок годности кода активации (если нужно)
            # if user.activation_code_created_at < timezone.now() - timedelta(hours=24):
            #     raise ValidationError(_('Срок действия кода активации истек.'))

            user.is_active = True
            user.activation_code = ''
            user.save()

            # Generate a new authentication token for automatic login after account activation
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'response': True,
                'token': token.key,  # Возвращаем токен
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

class ChangePasswordView(generics.GenericAPIView):
    """Изменение пароля пользователя."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"response": False, "message": _("Пользователь не аутентифицирован")}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.data["password"]
            confirm_password = serializer.data["confirm_password"]
            if password != confirm_password:
                return Response({"response": False, "message": _("Пароли не совпадают")}, status=status.HTTP_400_BAD_REQUEST)
            is_valid, message = validate_password(password)
            if not is_valid:
                return Response({"response": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return Response({"response": True, "message": _("Пароль успешно обновлен")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            activation_code = generate_activation_code()
            user.activation_code = activation_code
            user.save()
            message = (
                f"Здравствуйте, {user.email}!\n\n"
                f"<p>{_('Ваш код активации')}: {activation_code}</p>"
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
            user.reset_code = ''  # Очищаем код сброса пароля после его использования
            user.save()

            # Generate a new authentication token for automatic login after password reset
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'response': True,
                'token': token.key  # Возвращаем токен
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            logger.error(f"User with reset_code {reset_code} does not exist.")
            return Response({
                'response': False,
                'message': _('Неверный код для сброса пароля.')
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ResetPasswordVerifyView: {str(e)}")
            return Response({
                'response': False,
                'message': _('Произошла ошибка при сбросе пароля.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    """Выход пользователя."""
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        logout(request)
        return Response({
            'response': True,
            'message': _('Вы успешно вышли из системы.')
        }, status=status.HTTP_200_OK)
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer  # Замените на ваш сериализатор профиля пользователя
    permission_classes = [permissions.IsAuthenticated]  # Требуется аутентификация для доступа

    def get_object(self):
        return self.request.user  # Получаем текущего пользователя из запроса

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Получаем объект пользователя
        serializer = self.get_serializer(instance)  # Используем сериализатор для объекта пользователя
        return Response(serializer.data)  # Возвращаем данные сериализатора (включая email пользователя)
