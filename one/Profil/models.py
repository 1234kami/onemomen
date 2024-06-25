from django.db import models
from django.utils.translation import gettext_lazy as _
from transliterate import translit

LANG_CHOICES = (
    ("en", "English"),
    ("ru", "Русский язык")
)
class Application(models.Model):
    language = models.CharField('Язык', choices=LANG_CHOICES, default='en', max_length=255, null=True,blank=True)
    number = models.CharField(max_length=100, verbose_name="Номер")
    date = models.DateField(verbose_name="Дата")
    direction = models.CharField(max_length=100, verbose_name="Направление")
    direct = models.CharField(max_length=100, verbose_name="Направление")
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
class Discount(models.Model):
    start_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="От")
    end_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="До")
    percentage = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Процент")
    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def str(self):
        if self.end_amount:
            return f"{self.start_amount}$ - {self.end_amount}$: {self.percentage}%"
        else:
            return f"Больше {self.start_amount}$: {self.percentage}%"
@classmethod
def update_discount(cls, user, amount):
    user_discount, created = cls.objects.get_or_create(user=user)
    user_discount.total_transactions += amount

    if user_discount.total_transactions < 500:
        user_discount.discount_percentage = 0.08
    elif 500 <= user_discount.total_transactions < 1000:
        user_discount.discount_percentage = 0.1
    elif 1000 <= user_discount.total_transactions < 2000:
        user_discount.discount_percentage = 0.12
    elif 2000 <= user_discount.total_transactions < 4000:
        user_discount.discount_percentage = 0.14
    elif 4000 <= user_discount.total_transactions < 6000:
        user_discount.discount_percentage = 0.16
    elif 6000 <= user_discount.total_transactions < 10000:
        user_discount.discount_percentage = 0.18
    else:
        user_discount.discount_percentage = 0.2

    user_discount.save()
    return user_discount
