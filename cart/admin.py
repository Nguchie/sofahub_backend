from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['variation', 'quantity', 'unit_price', 'total_price', 'added_at']

    def unit_price(self, obj):
        return obj.unit_price

    unit_price.short_description = 'Unit Price'

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = 'Total Price'

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow superusers to delete cart items"""
        return request.user.is_superuser


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'total_items', 'subtotal_display', 'created_at']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'total_items', 'subtotal']
    inlines = [CartItemInline]
    search_fields = ['session_id']

    def subtotal_display(self, obj):
        return f"KSh {obj.subtotal}"

    subtotal_display.short_description = 'Subtotal'

    def total_items(self, obj):
        return obj.total_items

    total_items.short_description = 'Items'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete carts"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Carts are read-only for everyone"""
        return False

    def has_module_permission(self, request):
        """Staff and superusers can see carts"""
        return request.user.is_staff


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'variation', 'quantity', 'unit_price_display', 'total_price_display', 'added_at']
    list_filter = ['cart']
    search_fields = ['cart__session_id', 'variation__product__name']
    readonly_fields = ['cart', 'variation', 'quantity', 'added_at']

    def unit_price_display(self, obj):
        return f"KSh {obj.unit_price}"

    unit_price_display.short_description = 'Unit Price'

    def total_price_display(self, obj):
        return f"KSh {obj.total_price}"

    total_price_display.short_description = 'Total Price'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete cart items"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Cart items are read-only for everyone"""
        return False

    def has_module_permission(self, request):
        """Staff and superusers can see cart items"""
        return request.user.is_staff