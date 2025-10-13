from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import RoomCategory, ProductType, Tag, Product, ProductImage
from .serializers import (
    RoomCategorySerializer, ProductTypeSerializer, TagSerializer,
    ProductSerializer, ProductListSerializer, ProductImageSerializer
)
from core.permissions import IsAdminOrReadOnly


class ProductFilterSet(FilterSet):
    """Custom filter set to handle tag slugs instead of IDs"""
    tags = CharFilter(method='filter_tags_by_slug')

    class Meta:
        model = Product
        fields = ['room_categories', 'product_types', 'tags']

    def filter_tags_by_slug(self, queryset, name, value):
        """Filter products by tag slugs instead of IDs"""
        if value:
            tag_slugs = [slug.strip() for slug in value.split(',') if slug.strip()]
            if tag_slugs:
                return queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset


class RoomCategoryList(generics.ListCreateAPIView):
    queryset = RoomCategory.objects.all()
    serializer_class = RoomCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class ProductTypeList(generics.ListCreateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class ProductTypesByRoomView(generics.ListAPIView):
    """Get all product types for a specific room category"""
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        room_slug = self.kwargs['room_slug']
        return ProductType.objects.filter(
            room_categories__slug=room_slug
        ).distinct()


class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class ProductList(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilterSet
    search_fields = ['name', 'description', 'tags__name']
    ordering_fields = ['name', 'base_price', 'created_at']  # Using base_price since current_price is a property
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_context(self):
        """Ensure request context is passed to serializers"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'variations')

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        # Filter by room category
        room_category = self.request.query_params.get('room_category', None)
        if room_category:
            queryset = queryset.filter(room_categories__slug=room_category)

        # Filter by product type
        product_type = self.request.query_params.get('product_type', None)
        if product_type:
            queryset = queryset.filter(product_types__slug=product_type)

        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__slug__in=tag_list).distinct()

        # Price range filter - uses base_price since current_price is a property
        # Note: This doesn't account for sale prices in filtering
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)

        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)

        # Sort by price - uses base_price since current_price is a property
        sort_by = self.request.query_params.get('sort', None)
        if sort_by == 'price_low':
            queryset = queryset.order_by('base_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-base_price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        else:
            # Default sorting
            queryset = queryset.order_by('-created_at')

        return queryset


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['GET'])
def product_images(request, slug):
    """
    Get all images for a specific product
    Useful for frontend image galleries/carousels
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Get all images ordered by order field, then by id
    images = product.images.all().order_by('order', 'id')
    
    # Serialize images with context for proper URL generation
    serializer = ProductImageSerializer(images, many=True, context={'request': request})
    
    # Add metadata for frontend
    image_data = serializer.data
    total_images = len(image_data)
    
    for i, img in enumerate(image_data):
        img['index'] = i
        img['is_first'] = (i == 0)
        img['is_last'] = (i == total_images - 1)
        img['total_count'] = total_images
    
    return Response({
        'product_id': product.id,
        'product_name': product.name,
        'images': image_data,
        'total_images': total_images
    })