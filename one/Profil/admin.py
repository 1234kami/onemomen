from django.contrib import admin
from .models import *
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'direction', 'direct')
    search_fields = ('number', 'direction', 'direct')
    list_filter = ('language', 'date')
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('start_amount', 'end_amount', 'percentage',)
    search_fields = ('start_amount', 'end_amount', 'percentage')