from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductVariationSerializer


class CartProductVariationSerializer(serializers.ModelSerializer):
    """Custom serializer for cart that excludes SKU and modifier from attributes"""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    attributes = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariationSerializer.Meta.model
        fields = ['id', 'sku', 'attributes', 'stock_quantity', 'price_modifier', 'price', 'is_active', 'product_name', 'product_image']

    def get_attributes(self, obj):
        """Safely parse attributes from JSON string or return as dict, excluding SKU and modifier"""
        if isinstance(obj.attributes, dict):
            attrs = obj.attributes
        else:
            try:
                import json
                attrs = json.loads(obj.attributes) if obj.attributes else {}
            except (json.JSONDecodeError, TypeError):
                attrs = {}
        
        # Filter out SKU and modifier for cart display
        return {k: v for k, v in attrs.items() if k.lower() not in ['sku', 'modifier']}

    def get_product_image(self, obj):
        """Get the primary image of the product"""
        product = obj.product
        primary_image = product.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            else:
                # Fallback for when no request context is available
                return f"http://localhost:8000{primary_image.image.url}"
        
        first_image = product.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            else:
                # Fallback for when no request context is available
                return f"http://localhost:8000{first_image.image.url}"
        return None


class CartItemSerializer(serializers.ModelSerializer):
    variation = CartProductVariationSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'variation', 'quantity', 'unit_price', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['session_id', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    variation_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    session_id = serializers.CharField(required=False, allow_blank=True)

    def validate_variation_id(self, value):
        from products.models import ProductVariation
        try:
            variation = ProductVariation.objects.get(id=value, is_active=True)
            if variation.stock_quantity <= 0:
                raise serializers.ValidationError("This variation is out of stock")
            return value
        except ProductVariation.DoesNotExist:
            raise serializers.ValidationError("Invalid variation ID")


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)