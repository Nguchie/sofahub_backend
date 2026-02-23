from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import re


class BlogTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, unique=True)
    color = models.CharField(
        default='#6B7280', 
        help_text='Hex color code', 
        max_length=7
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, max_length=200, unique=True)
    excerpt = models.TextField(
        help_text='Short description of the blog post', 
        max_length=500
    )
    content = models.TextField(
        help_text='Blog post content. Can be plain text or HTML.'
    )
    featured_image = models.ImageField(
        blank=True, 
        null=True, 
        upload_to='blog/images/'
    )
    featured_image_alt = models.CharField(
        blank=True, 
        help_text='Alt text for the featured image', 
        max_length=200
    )
    status = models.CharField(
        choices=STATUS_CHOICES, 
        default='draft', 
        max_length=20
    )
    is_featured = models.BooleanField(
        default=False, 
        help_text='Featured posts appear prominently'
    )
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='blog_posts'
    )
    tags = models.ManyToManyField(
        BlogTag, 
        blank=True, 
        related_name='posts'
    )
    related_products = models.ManyToManyField(
        'products.Product',
        blank=True,
        related_name='blog_posts',
        help_text='Products referenced by this post for SEO interlinking.'
    )
    related_categories = models.ManyToManyField(
        'products.RoomCategory',
        blank=True,
        related_name='blog_posts',
        help_text='Furniture categories this post supports.'
    )
    
    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Only optimize when a new featured image is uploaded or changed.
        # Re-optimizing the same image on every edit can make admin saves slow.
        should_optimize_image = False
        if self.featured_image:
            if not self.pk:
                should_optimize_image = True
            else:
                old_image_name = (
                    BlogPost.objects.filter(pk=self.pk)
                    .values_list('featured_image', flat=True)
                    .first()
                )
                current_image_name = getattr(self.featured_image, 'name', None)
                should_optimize_image = str(old_image_name or '') != str(current_image_name or '')

        # Handle featured image optimization based on mode
        if self.featured_image and should_optimize_image:
            from core.utils import optimize_image, optimize_image_async, optimize_image_storage
            optimization_mode = getattr(
                settings,
                'BLOG_IMAGE_OPTIMIZATION_MODE',
                getattr(settings, 'IMAGE_OPTIMIZATION_MODE', 'async')
            ).lower()
            
            try:
                if optimization_mode == 'storage':
                    # Storage-efficient optimization (saves space, fast)
                    self.featured_image = optimize_image_storage(self.featured_image, max_width=1920, max_height=1920, quality=75)
                elif optimization_mode == 'sync':
                    # Immediate optimization (may be slow)
                    self.featured_image = optimize_image(self.featured_image, max_width=1920, max_height=1920, quality=85)
                elif optimization_mode == 'async':
                    # Background optimization (fast upload)
                    self.featured_image = optimize_image_async(self.featured_image, max_width=1920, max_height=1920, quality=85)
                # If 'false' or any other value, no optimization
            except Exception as e:
                print(f"⚠️ Blog image optimization failed: {e}")
        
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_at is not None
    
    def is_html_content(self):
        """Check if content contains HTML tags"""
        html_pattern = re.compile(r'<[^>]+>')
        return bool(html_pattern.search(self.content))
    
    def get_content_type(self):
        """Return 'html' or 'text' based on content"""
        return 'html' if self.is_html_content() else 'text'
