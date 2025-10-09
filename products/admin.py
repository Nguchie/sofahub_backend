from django import forms
from django.utils.html import format_html
from django.contrib import admin
import json
from .models import RoomCategory, ProductType, Tag, Product, ProductImage, ProductVariation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Show 3 empty slots for easy image addition
    readonly_fields = ['image_preview', 'image_info']
    fields = ['image', 'image_preview', 'image_info', 'alt_text', 'is_primary', 'order']
    
    # Make it easier to see and manage images
    verbose_name = "Product Image"
    verbose_name_plural = "📸 Product Images (Drag & Drop to Upload)"

    def image_preview(self, obj):
        """Show large preview of the image"""
        try:
            if obj and obj.pk and obj.image:
                from django.conf import settings
                
                if settings.DEBUG:
                    base_url = "http://localhost:8000"
                else:
                    base_url = "https://sofahubbackend-production.up.railway.app"
                
                return format_html(
                    '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                    f"{base_url}/api/images/{obj.id}/"
                )
        except:
            pass
        return format_html('<span style="color: #999;">Upload to see preview</span>')

    image_preview.short_description = '🖼️ Preview'
    
    def image_info(self, obj):
        """Show helpful information about the image"""
        try:
            if obj and obj.pk and obj.image:
                size = obj.image.size / 1024  # KB
                return format_html(
                    '<span style="color: #666; font-size: 11px;">Size: {:.1f} KB<br/>{} {}</span>',
                    size,
                    '✓' if obj.is_primary else '○',
                    'Primary' if obj.is_primary else 'Additional'
                )
        except:
            pass
        return format_html('<span style="color: #999;">-</span>')
    
    image_info.short_description = 'ℹ️ Info'


class ProductVariationForm(forms.ModelForm):
    """User-friendly form for product variations"""
    COLOR_CHOICES = [
        ('', '---------'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('black', 'Black'),
        ('white', 'White'),
        ('brown', 'Brown'),
        ('gray', 'Gray'),
        ('beige', 'Beige'),
        ('navy', 'Navy Blue'),
        ('charcoal', 'Charcoal'),
    ]

    MATERIAL_CHOICES = [
        ('', '---------'),
        ('leather', 'Leather'),
        ('fabric', 'Fabric'),
        ('wood', 'Wood'),
        ('metal', 'Metal'),
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('marble', 'Marble'),
        ('rattan', 'Rattan'),
    ]

    SIZE_CHOICES = [
        ('', '---------'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('king', 'King Size'),
        ('queen', 'Queen Size'),
        ('single', 'Single'),
        ('double', 'Double'),
    ]

    # Form fields instead of JSON
    color = forms.ChoiceField(choices=COLOR_CHOICES, required=False, help_text="Select color variation")
    material = forms.ChoiceField(choices=MATERIAL_CHOICES, required=False, help_text="Select material type")
    size = forms.ChoiceField(choices=SIZE_CHOICES, required=False, help_text="Select size option")

    class Meta:
        model = ProductVariation
        exclude = ['attributes']  # We'll handle this manually

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill form fields from existing JSON attributes
        if self.instance and self.instance.attributes:
            try:
                attributes = json.loads(self.instance.attributes)
                self.fields['color'].initial = attributes.get('color', '')
                self.fields['material'].initial = attributes.get('material', '')
                self.fields['size'].initial = attributes.get('size', '')
            except json.JSONDecodeError:
                pass

    def save(self, commit=True):
        variation = super().save(commit=False)

        # Build attributes JSON from form fields
        attributes = {}
        if self.cleaned_data['color']:
            attributes['color'] = self.cleaned_data['color']
        if self.cleaned_data['material']:
            attributes['material'] = self.cleaned_data['material']
        if self.cleaned_data['size']:
            attributes['size'] = self.cleaned_data['size']

        variation.attributes = json.dumps(attributes)

        if commit:
            variation.save()
        return variation


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    form = ProductVariationForm
    extra = 1
    readonly_fields = ['price_display', 'attributes_display']
    fields = ['sku', 'color', 'material', 'size', 'stock_quantity', 'price_modifier', 'price_display', 'is_active']

    def price_display(self, obj):
        return f"KSh {obj.price}"

    price_display.short_description = 'Price'

    def attributes_display(self, obj):
        if obj.attributes:
            try:
                attrs = json.loads(obj.attributes)
                return ", ".join([f"{k}: {v}" for k, v in attrs.items() if v])
            except:
                return obj.attributes
        return "No attributes"

    attributes_display.short_description = 'Attributes'


@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Products'

    def has_add_permission(self, request):
        """Only superusers can add room categories"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can change room categories"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete room categories"""
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for staff users"""
        if not request.user.is_superuser:
            return ['name', 'slug', 'description', 'image', 'order', 'is_active']
        return []


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['icon', 'order', 'is_active']

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Products'

    def has_add_permission(self, request):
        """Only superusers can add product types"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can change product types"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete product types"""
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for staff users"""
        if not request.user.is_superuser:
            return ['name', 'slug', 'description', 'icon', 'order', 'is_active']
        return []


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_display', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #000;"></div>',
            obj.color_code
        )

    color_display.short_description = 'Color'

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Products'

    def has_add_permission(self, request):
        """Only superusers can add tags"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can change tags"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete tags"""
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for staff users"""
        if not request.user.is_superuser:
            return ['name', 'slug', 'color_code']
        return []


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_count', 'base_price', 'current_price', 'is_on_sale', 'is_active', 'created_at']
    list_filter = ['room_categories', 'product_types', 'tags', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariationInline]
    filter_horizontal = ['room_categories', 'product_types', 'tags']
    readonly_fields = ['current_price', 'is_on_sale', 'created_at', 'updated_at', 'quick_tips']
    fieldsets = [
        (None, {
            'fields': ['name', 'slug', 'description', 'is_active', 'quick_tips']
        }),
        ('💰 Pricing', {
            'fields': ['base_price', 'sale_price', 'sale_start', 'sale_end', 'current_price', 'is_on_sale'],
            'description': 'Set base price and optional sale pricing with start/end dates'
        }),
        ('🏷️ Categorization', {
            'fields': ['room_categories', 'product_types', 'tags'],
            'description': 'Select relevant categories, types, and tags for the product'
        }),
        ('📅 Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def quick_tips(self, obj):
        """Show helpful tips for managing the product"""
        if obj and obj.pk:
            return format_html('''
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #417690;">
                    <h3 style="margin-top: 0; color: #417690;">💡 Quick Tips</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li><strong>Images:</strong> Add at least 1 image below. Mark one as "Primary" for the main display.</li>
                        <li><strong>Variations:</strong> Add color, size, or material options if this product has variations.</li>
                        <li><strong>Pricing:</strong> Sale price only applies between sale start and end dates.</li>
                        <li><strong>Changes:</strong> All changes save automatically when you click "Save" at the bottom.</li>
                    </ul>
                </div>
            ''')
        return format_html('<p style="color: #666;">Save the product first to see tips and add images.</p>')
    
    quick_tips.short_description = ''
    
    def image_count(self, obj):
        """Show how many images this product has"""
        try:
            if obj and obj.pk:
                count = obj.images.count()
                if count == 0:
                    return format_html('<span style="color: #dc3545;">❌ No images</span>')
                elif count == 1:
                    return format_html('<span style="color: #ffc107;">⚠️ 1 image</span>')
                else:
                    return format_html('<span style="color: #28a745;">✓ {} images</span>', count)
        except:
            pass
        return format_html('<span style="color: #999;">-</span>')
    
    image_count.short_description = '📸 Images'

    def current_price(self, obj):
        return f"KSh {obj.current_price}"

    current_price.short_description = 'Current Price'

    def is_on_sale(self, obj):
        return obj.is_on_sale

    is_on_sale.boolean = True

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete products"""
        return request.user.is_superuser


@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    form = ProductVariationForm
    list_display = ['product', 'sku', 'attributes_display', 'stock_quantity', 'price_display', 'is_active']
    list_filter = ['is_active', 'product']
    search_fields = ['sku', 'product__name']
    list_editable = ['stock_quantity', 'is_active']
    fields = ['product', 'sku', 'color', 'material', 'size', 'stock_quantity', 'price_modifier', 'is_active']

    def attributes_display(self, obj):
        if obj.attributes:
            try:
                attrs = json.loads(obj.attributes)
                return ", ".join([f"{k}: {v}" for k, v in attrs.items() if v])
            except:
                return obj.attributes
        return "No attributes"

    attributes_display.short_description = 'Attributes'

    def price_display(self, obj):
        return f"KSh {obj.price}"

    price_display.short_description = 'Price'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'product', 'is_primary', 'order', 'alt_text', 'image_actions']
    list_filter = ['is_primary', 'product', 'product__room_categories']
    list_editable = ['is_primary', 'order']
    search_fields = ['product__name', 'alt_text']
    list_per_page = 50
    
    # Fields to show when editing
    fields = ['product', 'image', 'image_preview_large', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['image_preview_large']

    def image_preview(self, obj):
        """Small preview for list view"""
        try:
            if obj and obj.pk and obj.image:
                from django.conf import settings
                
                if settings.DEBUG:
                    base_url = "http://localhost:8000"
                else:
                    base_url = "https://sofahubbackend-production.up.railway.app"
                
                return format_html(
                    '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />',
                    f"{base_url}/api/images/{obj.id}/"
                )
        except:
            pass
        return format_html('<span style="color: #999;">-</span>')

    image_preview.short_description = '🖼️'
    
    def image_preview_large(self, obj):
        """Large preview for detail view"""
        try:
            if obj and obj.pk and obj.image:
                from django.conf import settings
                
                if settings.DEBUG:
                    base_url = "http://localhost:8000"
                else:
                    base_url = "https://sofahubbackend-production.up.railway.app"
                
                return format_html(
                    '<div style="margin: 20px 0;"><img src="{}" style="max-width: 500px; max-height: 500px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" /></div>',
                    f"{base_url}/api/images/{obj.id}/"
                )
        except:
            pass
        return format_html('<p style="color: #999;">No image uploaded yet</p>')
    
    image_preview_large.short_description = '🖼️ Image Preview'
    
    def image_actions(self, obj):
        """Quick action buttons"""
        try:
            if obj and obj.pk and obj.image:
                from django.conf import settings
                
                if settings.DEBUG:
                    base_url = "http://localhost:8000"
                else:
                    base_url = "https://sofahubbackend-production.up.railway.app"
                
                view_url = f"{base_url}/api/images/{obj.id}/"
                return format_html(
                    '<a href="{}" target="_blank" style="background: #417690; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">👁️ View</a>',
                    view_url
                )
        except:
            pass
        return ""
    
    image_actions.short_description = 'Actions'