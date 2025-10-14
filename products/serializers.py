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
        """Get product count, filtered by room category if provided in context"""
        queryset = obj.products.filter(is_active=True)
        
        # Check if room_category filter is in request context
        request = self.context.get('request')
        if request:
            # Handle both DRF request objects and Django WSGIRequest objects
            if hasattr(request, 'query_params'):
                # DRF request object
                room_category = request.query_params.get('room_category')
            elif hasattr(request, 'GET'):
                # Django WSGIRequest object
                room_category = request.GET.get('room_category')
            else:
                room_category = None
                
            if room_category:
                queryset = queryset.filter(room_categories__slug=room_category)
        
        return queryset.count()


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
            from core.utils import get_image_url
            request = self.context.get('request')
            return get_image_url(obj.id, request)
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
    images = serializers.SerializerMethodField()
    variations = ProductVariationSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.SerializerMethodField()

    def get_images(self, obj):
        """Return all images ordered by order field, then by id"""
        images = obj.images.all().order_by('order', 'id')
        serializer = ProductImageSerializer(images, many=True, context=self.context)
        
        # Add metadata to help frontend with gallery display
        image_data = serializer.data
        total_images = len(image_data)
        
        # Add index to each image for frontend navigation
        for i, img in enumerate(image_data):
            img['index'] = i
            img['is_first'] = (i == 0)
            img['is_last'] = (i == total_images - 1)
            img['total_count'] = total_images
        
        return image_data


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
        # Use prefetched images to avoid N+1 queries
        images = obj.images.all()  # Uses prefetch_related from view
        
        # Find primary image in Python (no new query)
        for img in images:
            if img.is_primary:
                serializer = ProductImageSerializer(img, context=self.context)
                return serializer.data
        
        # Fallback to first image
        if images:
            serializer = ProductImageSerializer(images[0], context=self.context)
            return serializer.data
        
        return None