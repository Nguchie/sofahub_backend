from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_name', 'variation_attributes', 'quantity', 'unit_price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    deposit_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'shipping_city', 'shipping_zip_code',
            'subtotal', 'status', 'mpesa_transaction_id', 'payment_confirmed',
            'total_items', 'items', 'created_at', 'is_downpayment',
            'deposit_amount', 'remaining_amount', 'deposit_paid', 'balance_paid',
            'payment_status'
        ]
        read_only_fields = ['status', 'mpesa_transaction_id', 'payment_confirmed', 'created_at']

    def get_payment_status(self, obj):
        return obj.get_payment_status()


class CheckoutSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=100)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)
    mpesa_phone = serializers.CharField(max_length=20, required=False)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_zip_code = serializers.CharField(max_length=20)

    def validate_customer_phone(self, value):
        # Basic phone validation for Kenya (adjust as needed)
        if not value.startswith('+254') and not value.startswith('07'):
            raise serializers.ValidationError("Please enter a valid Kenyan phone number")
        return value

    def validate_mpesa_phone(self, value):
        if value:
            # Basic phone validation for Kenya (adjust as needed)
            if not value.startswith('+254') and not value.startswith('07'):
                raise serializers.ValidationError("Please enter a valid Kenyan M-Pesa phone number")
        return value