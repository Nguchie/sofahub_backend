from django import forms
from django.utils.html import format_html
from django.contrib import admin
import json
from .models import RoomCategory, ProductType, Tag, Product, ProductImage, ProductVariation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview', 'image_status']
    fields = ['image', 'image_preview', 'image_status', 'alt_text', 'is_primary', 'order']

    def image_preview(self, obj):
        """Show image preview using ID-based URL"""
        if obj.image and obj.id:
            from core.utils import get_image_url
            image_url = get_image_url(obj.id)
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border: 1px solid #ddd;" />',
                image_url
            )
        return format_html('<span style="color: #999;">No image yet</span>')

    image_preview.short_description = 'Preview'

    def image_status(self, obj):
        """Show if the image file exists on filesystem"""
        if not obj.image or not obj.image.name:
            return format_html('<span style="color: #999;">-</span>')
        
        import os
        from django.conf import settings
        
        try:
            # Use the image name directly instead of obj.image.path
            full_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
            
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                size_kb = file_size / 1024
                return format_html(
                    '<span style="color: green;">✓ {:.1f} KB</span>',
                    size_kb
                )
            else:
                return format_html('<span style="color: red;">✗ File missing</span>')
                
        except Exception as e:
            # More detailed error for debugging
            return format_html(
                '<span style="color: orange;">? Error: {}</span>',
                str(e)[:20]  # Show first 20 chars of error
            )

    image_status.short_description = 'Status'


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


class TagAdminForm(forms.ModelForm):
    """Custom form for Tag with color picker"""
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'color_code': forms.TextInput(attrs={
                'type': 'color',
                'style': 'width: 100px; height: 40px; cursor: pointer;',
                'title': 'Click to choose a color'
            }),
        }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm
    list_display = ['name', 'slug', 'color_display', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    fieldsets = (
        ('Tag Information', {
            'fields': ('name', 'slug'),
        }),
        ('Display Settings', {
            'fields': ('color_code',),
            'description': 'Click the color box below to choose a color visually'
        }),
    )

    def color_display(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border: 2px solid #ddd; border-radius: 4px;"></div>',
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
    list_display = ['name', 'base_price', 'current_price', 'is_on_sale', 'is_active', 'created_at']
    list_filter = ['room_categories', 'product_types', 'tags', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariationInline]
    filter_horizontal = ['room_categories', 'product_types', 'tags']
    readonly_fields = ['current_price', 'is_on_sale', 'created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ['name', 'slug', 'description', 'is_active']
        }),
        ('Pricing', {
            'fields': ['base_price', 'sale_price', 'sale_start', 'sale_end', 'current_price', 'is_on_sale']
        }),
        ('Categorization', {
            'fields': ['room_categories', 'product_types', 'tags']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

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
    list_display = ['product', 'image_preview', 'is_primary', 'order']
    list_filter = ['is_primary', 'product']
    list_editable = ['is_primary', 'order']

    def image_preview(self, obj):
        if obj.image and obj.id:
            from core.utils import get_image_url
            image_url = get_image_url(obj.id)
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', image_url)
        return "No Image"

    image_preview.short_description = 'Preview'