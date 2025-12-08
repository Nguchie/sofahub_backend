from django.db import models

# Create your models here.

class Redirect(models.Model):
    """
    Model to store URL redirects for SEO purposes.
    Automatically created when product, category, or blog post slugs change.
    """
    old_path = models.CharField(
        max_length=500,
        unique=True,
        help_text="Old URL path (e.g., /product/old-slug or /category/old-slug)"
    )
    new_path = models.CharField(
        max_length=500,
        help_text="New URL path (e.g., /product/new-slug or /category/new-slug)"
    )
    redirect_type = models.CharField(
        max_length=20,
        choices=[('product', 'Product'), ('category', 'Category'), ('blog', 'Blog'), ('manual', 'Manual')],
        default='manual',
        help_text="Type of redirect"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['old_path']),
            models.Index(fields=['is_active', 'old_path']),
        ]
    
    def __str__(self):
        return f"{self.old_path} → {self.new_path}"