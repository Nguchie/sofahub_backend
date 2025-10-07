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
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'published_at', 'created_at', 'updated_at',
            'tags', 'is_featured'
        ]
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(obj.featured_image.url)
            else:
                image_url = obj.featured_image.url
            return {
                'image': image_url,
                'alt_text': obj.featured_image_alt or obj.title
            }
        return None


class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = BlogAuthorSerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'content_type', 'featured_image',
            'author', 'published_at', 'created_at', 'updated_at',
            'tags', 'is_featured'
        ]
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(obj.featured_image.url)
            else:
                image_url = obj.featured_image.url
            return {
                'image': image_url,
                'alt_text': obj.featured_image_alt or obj.title
            }
        return None
    
    def get_content_type(self, obj):
        return obj.get_content_type()