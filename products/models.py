from django.db import models
from django.utils.text import slugify
from core.utils import is_sale_active
from django.utils import timezone
from decimal import Decimal
import json

class RoomCategory(models.Model):
    """Living Room, Bedroom, Dining, Office, Outdoor, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='room_categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Room Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductType(models.Model):
    """Sofas, Chairs, Tables, Beds, Storage, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Product Types"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    color_code = models.CharField(max_length=7, default='#000000')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)

    # New many-to-many relationships
    room_categories = models.ManyToManyField(RoomCategory, related_name='products', blank=True)
    product_types = models.ManyToManyField(ProductType, related_name='products', blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        """Check if product is currently on sale"""
        if not self.sale_price:
            return False

        now = timezone.now()
        if self.sale_start and self.sale_end:
            return self.sale_start <= now <= self.sale_end
        elif self.sale_start and not self.sale_end:
            return self.sale_start <= now
        elif not self.sale_start and self.sale_end:
            return now <= self.sale_end
        else:
            # If no dates set, consider it always on sale if sale_price exists
            return True

    @property
    def current_price(self):
        if self.is_on_sale and self.sale_price is not None:
            return self.sale_price
        return self.base_price or Decimal('0')

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale and self.sale_price and self.base_price > 0:
            discount = ((self.base_price - self.sale_price) / self.base_price) * 100
            return round(discount, 1)
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Save the product first
        super().save(*args, **kwargs)

        # Then update the On Sale tag
        self._update_on_sale_tag()

    def _update_on_sale_tag(self):
        """PROPERLY update the On Sale tag based on current sale status"""
        try:
            # Get the On Sale tag - use get_or_create but handle duplicates
            on_sale_tag, created = Tag.objects.get_or_create(
                slug='on-sale',  # Use slug for uniqueness
                defaults={
                    'name': 'On Sale',
                    'color_code': '#FF0000'
                }
            )

            # If tag was found but name is different, update it
            if not created and on_sale_tag.name != 'On Sale':
                on_sale_tag.name = 'On Sale'
                on_sale_tag.save()

            # Check if product should have the On Sale tag
            should_have_tag = self.is_on_sale

            # Get current tags
            current_tags = list(self.tags.all())
            has_on_sale_tag = any(tag.slug == 'on-sale' for tag in current_tags)

            if should_have_tag and not has_on_sale_tag:
                # Add the On Sale tag
                self.tags.add(on_sale_tag)
                print(f"✅ Added 'On Sale' tag to {self.name}")

            elif not should_have_tag and has_on_sale_tag:
                # Remove the On Sale tag
                self.tags.remove(on_sale_tag)
                print(f"✅ Removed 'On Sale' tag from {self.name}")

        except Exception as e:
            print(f"❌ Error updating On Sale tag for {self.name}: {e}")


def product_image_upload_path(instance, filename):
    """Custom upload path for product images to prevent filename conflicts"""
    import uuid
    import os
    
    # Get file extension
    ext = filename.split('.')[-1]
    # Create unique filename using UUID to prevent conflicts
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return f'products/{unique_filename}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_path)
    alt_text = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.product.name}"
    
    def clean(self):
        """Validate image before saving"""
        if self.image:
            from core.utils import validate_product_image
            try:
                validate_product_image(self.image)
            except Exception as e:
                from django.core.exceptions import ValidationError
                raise ValidationError({'image': str(e)})
    
    def save(self, *args, **kwargs):
        """Override save to call full_clean() for validation"""
        self.full_clean()
        super().save(*args, **kwargs)


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    sku = models.CharField(max_length=50, unique=True)
    attributes = models.JSONField(default=dict)  # Default to empty dict
    stock_quantity = models.PositiveIntegerField(default=0)
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        # More user-friendly display
        attrs = self.get_attributes_display()
        if attrs:
            return f"{self.product.name} - {attrs}"
        return f"{self.product.name} - {self.sku}"

    @property
    def price(self):
        base_price = self.product.current_price or Decimal('0')
        return base_price + self.price_modifier

    def get_attributes_dict(self):
        """Safely get attributes as dictionary"""
        if isinstance(self.attributes, dict):
            return self.attributes
        try:
            return json.loads(self.attributes) if self.attributes else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_attributes_display(self):
        """Get attributes as human-readable string"""
        attrs = self.get_attributes_dict()
        if not attrs:
            return "Standard"

        display_parts = []
        if attrs.get('color'):
            display_parts.append(attrs['color'].title())
        if attrs.get('material'):
            display_parts.append(attrs['material'].title())
        if attrs.get('size'):
            display_parts.append(attrs['size'].title())

        return " ".join(display_parts)

    def get_color(self):
        return self.get_attributes_dict().get('color', '')

    def get_material(self):
        return self.get_attributes_dict().get('material', '')

    def get_size(self):
        return self.get_attributes_dict().get('size', '')

    def set_attribute(self, key, value):
        """Helper method to set individual attributes"""
        attrs = self.get_attributes_dict()
        if value:
            attrs[key] = value
        elif key in attrs:
            del attrs[key]
        self.attributes = attrs