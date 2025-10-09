from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import RoomCategory, ProductType, Tag, Product
from .serializers import (
    RoomCategorySerializer, ProductTypeSerializer, TagSerializer,
    ProductSerializer, ProductListSerializer
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
                tags = Tag.objects.filter(slug__in=tag_slugs)
                if tags.exists():
                    return queryset.filter(tags__in=tags).distinct()
        return queryset


class RoomCategoryList(generics.ListAPIView):
    """Get all room categories"""
    queryset = RoomCategory.objects.filter(is_active=True)
    serializer_class = RoomCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductTypeList(generics.ListAPIView):
    """Get all product types"""
    queryset = ProductType.objects.filter(is_active=True)
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductTypesByRoomView(generics.ListAPIView):
    """Get product types available in a specific room category"""
    serializer_class = ProductTypeSerializer

    def get_queryset(self):
        room_slug = self.kwargs.get('room_slug')
        try:
            room = RoomCategory.objects.get(slug=room_slug, is_active=True)
            # Get distinct product types that have products in this room
            return ProductType.objects.filter(
                products__room_categories=room,
                products__is_active=True,
                is_active=True
            ).distinct()
        except RoomCategory.DoesNotExist:
            return ProductType.objects.none()


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductList(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilterSet
    search_fields = ['name', 'description']
    ordering_fields = ['base_price', 'current_price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Add cache control headers to prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Filter by room category
        room_slug = self.request.query_params.get('room')
        if room_slug:
            try:
                room = RoomCategory.objects.get(slug=room_slug, is_active=True)
                queryset = queryset.filter(room_categories=room)
            except RoomCategory.DoesNotExist:
                pass

        # Filter by product type
        product_type_slug = self.request.query_params.get('product_type')
        if product_type_slug:
            try:
                product_type = ProductType.objects.get(slug=product_type_slug, is_active=True)
                queryset = queryset.filter(product_types=product_type)
            except ProductType.DoesNotExist:
                pass

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)

        # Filter by sale status - FIXED to use proper date checking
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                sale_price__isnull=False
            ).filter(
                Q(sale_start__isnull=True) | Q(sale_start__lte=now)
            ).filter(
                Q(sale_end__isnull=True) | Q(sale_end__gte=now)
            )

        return queryset


@method_decorator(never_cache, name='dispatch')
class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Add cache control headers to prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response