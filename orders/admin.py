from django.contrib import admin
from .models import Order, OrderItem
from django.utils.html import format_html


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variation_attributes', 'quantity', 'unit_price', 'total_price']

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_phone', 'subtotal_display', 'status', 'payment_confirmed',
                    'created_at']
    list_filter = ['status', 'payment_confirmed', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'customer_email', 'id']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'cart_session']
    inlines = [OrderItemInline]
    list_editable = ['status']

    fieldsets = [
        ('Customer Information', {
            'fields': ['customer_name', 'customer_email', 'customer_phone']
        }),
        ('Shipping Information', {
            'fields': ['shipping_address', 'shipping_city', 'shipping_zip_code']
        }),
        ('Order Details', {
            'fields': ['cart_session', 'subtotal', 'status']
        }),
        ('Payment Information', {
            'fields': ['mpesa_transaction_id', 'payment_confirmed']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

    def subtotal_display(self, obj):
        return f"KSh {obj.subtotal}"

    subtotal_display.short_description = 'Subtotal'

    def has_add_permission(self, request):
        return False

    def has_module_permission(self, request):
        """Only superusers can see orders"""
        return request.user.is_superuser


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'variation_attributes', 'quantity', 'unit_price_display',
                    'total_price_display']
    list_filter = ['order']
    search_fields = ['product_name', 'order__id']
    readonly_fields = ['order', 'variation', 'product_name', 'variation_attributes', 'quantity', 'unit_price',
                       'total_price']

    def unit_price_display(self, obj):
        return f"KSh {obj.unit_price}"

    unit_price_display.short_description = 'Unit Price'

    def total_price_display(self, obj):
        return f"KSh {obj.total_price}"

    total_price_display.short_description = 'Total Price'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        """Only superusers can see order items"""
        return request.user.is_superuser