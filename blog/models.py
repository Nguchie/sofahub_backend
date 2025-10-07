from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.utils.html import strip_tags
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
