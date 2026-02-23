from rest_framework import serializers
from .models import BlogPost, BlogTag
from django.contrib.auth.models import User


class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'name', 'slug', 'color']


class BlogAuthorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Use first_name + last_name if available, otherwise username
        if instance.first_name or instance.last_name:
            data['name'] = f"{instance.first_name} {instance.last_name}".strip()
        else:
            data['name'] = instance.username
        return data


class BlogPostListSerializer(serializers.ModelSerializer):
    author = BlogAuthorSerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    related_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'published_at', 'created_at', 'updated_at',
            'tags', 'is_featured', 'related_products', 'related_categories'
        ]
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(obj.featured_image.url)
            else:
                # Fallback for when no request context is available
                from django.conf import settings
                image_url = f"{settings.SITE_URL}{obj.featured_image.url}"
            return {
                'image': image_url,
                'alt_text': obj.featured_image_alt or obj.title
            }
        return None

    def get_related_products(self, obj):
        return [
            {
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'current_price': str(product.current_price),
            }
            for product in obj.related_products.filter(is_active=True)[:6]
        ]

    def get_related_categories(self, obj):
        return [
            {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
            }
            for category in obj.related_categories.filter(is_active=True)
        ]


class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = BlogAuthorSerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    related_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'content_type', 'featured_image',
            'author', 'published_at', 'created_at', 'updated_at',
            'tags', 'is_featured', 'related_products', 'related_categories'
        ]
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(obj.featured_image.url)
            else:
                # Fallback for when no request context is available
                from django.conf import settings
                image_url = f"{settings.SITE_URL}{obj.featured_image.url}"
            return {
                'image': image_url,
                'alt_text': obj.featured_image_alt or obj.title
            }
        return None
    
    def get_content_type(self, obj):
        return obj.get_content_type()

    def get_related_products(self, obj):
        related = obj.related_products.filter(is_active=True).prefetch_related('images')
        products = []
        for product in related[:6]:
            primary_image = None
            images = list(product.images.all())
            selected = None
            for image in images:
                if image.is_primary:
                    selected = image
                    break
            if not selected and images:
                selected = images[0]

            if selected and selected.image:
                from core.utils import get_image_url
                request = self.context.get('request')
                image_url = get_image_url(selected.id, request)
                primary_image = {
                    'image': image_url,
                    'alt_text': selected.alt_text or product.name
                }

            products.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'current_price': str(product.current_price),
                'primary_image': primary_image,
            })
        return products

    def get_related_categories(self, obj):
        return [
            {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
            }
            for category in obj.related_categories.filter(is_active=True)
        ]
