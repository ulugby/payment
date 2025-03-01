from django.contrib import admin
from .models import Order



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_cost', 'payment_method', 'is_paid', 'created_at', 'updated_at', 'status')
    search_fields = ('customer_name', 'payment_method')
    list_filter = ('is_paid', 'created_at', 'updated_at', 'status')
    readonly_fields = ('items',)