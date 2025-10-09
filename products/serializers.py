from rest_framework import serializers
from .models import RoomCategory, ProductType, Tag, Product, ProductImage, ProductVariation


class RoomCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = RoomCategory
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'order', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductTypeSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductType
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active', 'order', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color_code']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']

    def get_image(self, obj):
        """Return absolute URL for the image using ID-based serving"""
        if obj.image:
            request = self.context.get('request')
            
            # Always use ID-based URL - it's reliable and handles missing files gracefully
            if request:
                return request.build_absolute_uri(f'/api/images/{obj.id}/')
            else:
                from django.conf import settings
                if settings.DEBUG:
                    return f"http://localhost:8000/api/images/{obj.id}/"
                else:
                    return f"https://sofahubbackend-production.up.railway.app/api/images/{obj.id}/"
        return None


class ProductVariationSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariation
        fields = ['id', 'sku', 'attributes', 'stock_quantity', 'price_modifier', 'price', 'is_active']

    def get_attributes(self, obj):
        """Safely parse attributes from JSON string or return as dict"""
        if isinstance(obj.attributes, dict):
            return obj.attributes
        try:
            import json
            return json.loads(obj.attributes) if obj.attributes else {}
        except (json.JSONDecodeError, TypeError):
            return {}


class ProductSerializer(serializers.ModelSerializer):
    room_categories = RoomCategorySerializer(many=True, read_only=True)
    product_types = ProductTypeSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price', 'sale_price',
            'sale_start', 'sale_end', 'current_price', 'is_on_sale', 'discount_percentage',
            'room_categories', 'product_types', 'tags', 'images', 'variations',
            'is_active', 'created_at', 'updated_at'
        ]

    def get_discount_percentage(self, obj):
        return obj.discount_percentage


class ProductListSerializer(serializers.ModelSerializer):
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    room_categories = RoomCategorySerializer(many=True, read_only=True)
    product_types = ProductTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'current_price', 'is_on_sale', 'discount_percentage',
            'primary_image', 'room_categories', 'product_types'
        ]

    def get_discount_percentage(self, obj):
        return obj.discount_percentage

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            serializer = ProductImageSerializer(primary_image, context=self.context)
            return serializer.data
        first_image = obj.images.first()
        if first_image:
            serializer = ProductImageSerializer(first_image, context=self.context)
            return serializer.data
        return None