from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter
from django.utils import timezone
from .models import BlogPost, BlogTag
from .serializers import BlogPostListSerializer, BlogPostDetailSerializer, BlogTagSerializer
from core.permissions import IsAdminOrReadOnly


class BlogPostFilterSet(FilterSet):
    """Custom filter set for blog posts"""
    tags = CharFilter(method='filter_tags_by_slug')
    featured = CharFilter(field_name='is_featured', lookup_expr='exact')
    status = CharFilter(field_name='status', lookup_expr='exact')
    
    class Meta:
        model = BlogPost
        fields = ['tags', 'featured', 'status']
    
    def filter_tags_by_slug(self, queryset, name, value):
        """Filter posts by tag slugs"""
        if value:
            tag_slugs = [slug.strip() for slug in value.split(',') if slug.strip()]
            if tag_slugs:
                tags = BlogTag.objects.filter(slug__in=tag_slugs)
                if tags.exists():
                    return queryset.filter(tags__in=tags).distinct()
        return queryset


class BlogPostList(generics.ListAPIView):
    """Get all published blog posts"""
    serializer_class = BlogPostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BlogPostFilterSet
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at']
    
    def get_queryset(self):
        queryset = BlogPost.objects.select_related('author').prefetch_related('tags')
        
        # Only show published posts to non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                status='published',
                published_at__lte=timezone.now()
            )
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BlogPostDetail(generics.RetrieveAPIView):
    """Get a single blog post by slug"""
    serializer_class = BlogPostDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = BlogPost.objects.select_related('author').prefetch_related('tags')
        
        # Only show published posts to non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                status='published',
                published_at__lte=timezone.now()
            )
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BlogTagList(generics.ListAPIView):
    """Get all blog tags"""
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
