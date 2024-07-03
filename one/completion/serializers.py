
import qrcode
from io import BytesIO
from rest_framework import serializers

class PaymentDetailsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    currency = serializers.CharField(max_length=3, default='RUB')
    requisites = serializers.CharField(max_length=16, default='2202206875265626')
    qr_code_url = serializers.SerializerMethodField()

    def get_qr_code_url(self, obj):
        # Генерация QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(obj['requisites'])  # Добавление данных для QR-кода (в данном случае реквизиты)
        qr.make(fit=True)

        # Сохранение QR-кода в памяти и получение URL
        buffer = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(buffer)
        
        # Использование контекста запроса для получения абсолютного URL
        request = self.context.get('request')
        if request is not None:
            qr_code_url = request.build_absolute_uri('/path/to/qr_code.png')  # замените на ваш путь сохранения или URL
            return qr_code_url
        
        return None
