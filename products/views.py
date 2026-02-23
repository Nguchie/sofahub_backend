from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from decimal import Decimal
from xml.sax.saxutils import escape
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
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    def get_queryset(self):
        """Get product types, optionally filtered by room category"""
        queryset = ProductType.objects.filter(is_active=True)
        
        # Filter by room category if provided
        room_category = self.request.query_params.get('room_category', None)
        if room_category:
            # Get product types that have products in this room category
            queryset = queryset.filter(
                products__room_categories__slug=room_category,
                products__is_active=True
            ).distinct()
        
        return queryset
    
    def get_serializer_context(self):
        """Ensure request context is passed to serializers"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductTypesByRoomView(generics.ListAPIView):
    """Get all product types for a specific room category"""
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        room_slug = self.kwargs['room_slug']
        # Get product types through products (not direct relationship)
        # Get all products in this room category, then get their types
        return ProductType.objects.filter(
            products__room_categories__slug=room_slug,
            is_active=True
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
    ordering_fields = ['name', 'base_price', 'created_at']
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

        # Price range filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)

        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)

        # Sort by price
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
    queryset = Product.objects.filter(is_active=True).prefetch_related('faqs', 'images', 'variations', 'room_categories', 'product_types')
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


@api_view(['GET'])
def merchant_feed(request):
    """
    Google Merchant Center feed in RSS 2.0 format.
    Exposes active products and variants with stable ids and KES prices.
    """
    site_url = getattr(settings, 'SITE_URL', 'https://sofahub.co.ke').rstrip('/')
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'variations')
    now = timezone.now()

    def amount(value: Decimal) -> str:
        return f"{Decimal(value):.2f} KES"

    def to_iso(dt):
        if not dt:
            return None
        return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def first_image_url(product):
        from core.utils import get_image_url
        images = list(product.images.all())
        selected = None
        for image in images:
            if image.is_primary:
                selected = image
                break
        if not selected and images:
            selected = images[0]
        if not selected or not selected.image:
            return None
        return get_image_url(selected.id, request)

    def stock_to_availability(in_stock: bool):
        return 'in stock' if in_stock else 'out of stock'

    items = []
    for product in products:
        product_link = f"{site_url}/product/{product.slug}"
        image_link = first_image_url(product)
        variations = [v for v in product.variations.all() if v.is_active]
        on_sale = product.is_on_sale and product.sale_price is not None
        sale_effective = None
        if on_sale:
            start = product.sale_start if product.sale_start and product.sale_start <= now else now
            end = product.sale_end
            if end:
                sale_effective = f"{to_iso(start)}/{to_iso(end)}"

        if variations:
            for variation in variations:
                base_variant_price = product.base_price + variation.price_modifier
                current_variant_price = product.current_price + variation.price_modifier
                title = f"{product.name} ({variation.sku})"
                items.append({
                    'id': variation.sku,
                    'item_group_id': str(product.id),
                    'title': title,
                    'description': product.description,
                    'link': product_link,
                    'image_link': image_link,
                    'availability': stock_to_availability(variation.stock_quantity > 0),
                    'price': amount(base_variant_price if on_sale else current_variant_price),
                    'sale_price': amount(current_variant_price) if on_sale else None,
                    'sale_effective_date': sale_effective,
                    'condition': 'new',
                    'brand': 'SofaHub',
                })
        else:
            items.append({
                'id': f"product-{product.id}",
                'item_group_id': str(product.id),
                'title': product.name,
                'description': product.description,
                'link': product_link,
                'image_link': image_link,
                'availability': stock_to_availability(True),
                'price': amount(product.base_price if on_sale else product.current_price),
                'sale_price': amount(product.current_price) if on_sale else None,
                'sale_effective_date': sale_effective,
                'condition': 'new',
                'brand': 'SofaHub',
            })

    xml_items = []
    for item in items:
        lines = [
            "    <item>",
            f"      <g:id>{escape(item['id'])}</g:id>",
            f"      <g:item_group_id>{escape(item['item_group_id'])}</g:item_group_id>",
            f"      <title>{escape(item['title'])}</title>",
            f"      <description>{escape(item['description'] or '')}</description>",
            f"      <link>{escape(item['link'])}</link>",
            f"      <g:availability>{escape(item['availability'])}</g:availability>",
            f"      <g:price>{escape(item['price'])}</g:price>",
            f"      <g:condition>{escape(item['condition'])}</g:condition>",
            f"      <g:brand>{escape(item['brand'])}</g:brand>",
        ]
        if item.get('image_link'):
            lines.append(f"      <g:image_link>{escape(item['image_link'])}</g:image_link>")
        if item.get('sale_price'):
            lines.append(f"      <g:sale_price>{escape(item['sale_price'])}</g:sale_price>")
        if item.get('sale_effective_date'):
            lines.append(f"      <g:sale_price_effective_date>{escape(item['sale_effective_date'])}</g:sale_price_effective_date>")
        lines.append("    </item>")
        xml_items.append("\n".join(lines))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n'
        '  <channel>\n'
        '    <title>SofaHub Product Feed</title>\n'
        f'    <link>{escape(site_url)}</link>\n'
        '    <description>Product feed for Google Merchant Center</description>\n'
        f"{chr(10).join(xml_items)}\n"
        '  </channel>\n'
        '</rss>\n'
    )
    return HttpResponse(xml, content_type='application/xml; charset=utf-8')
