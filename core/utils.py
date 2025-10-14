import uuid
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def generate_session_id():
    """Generate a unique session ID for anonymous users"""
    return str(uuid.uuid4())

def is_sale_active(sale_start, sale_end):
    """Check if a sale is currently active"""
    now = timezone.now()
    if sale_start and sale_end:
        return sale_start <= now <= sale_end
    return False

def get_image_url(image_id, request=None):
    """
    Generate absolute URL for a product image by ID.
    
    Args:
        image_id: The ProductImage ID
        request: Optional HTTP request object for building absolute URI
        
    Returns:
        Absolute URL string for the image endpoint
    """
    if request:
        return request.build_absolute_uri(f'/api/images/{image_id}/')
    
    # Fallback when request context is not available
    from django.conf import settings
    if hasattr(settings, 'SITE_URL'):
        return f"{settings.SITE_URL}/api/images/{image_id}/"
    
    # Final fallback - use DEBUG setting
    if settings.DEBUG:
        return f"http://localhost:8000/api/images/{image_id}/"
    else:
        return f"https://sofahubbackend-production.up.railway.app/api/images/{image_id}/"

def optimize_image(image, max_width=2000, max_height=2000, quality=85):
    """
    Lightweight image optimization to prevent timeouts.
    Only does basic resizing without heavy processing.
    
    Args:
        image: Django UploadedFile object
        max_width: Maximum width in pixels (default 2000)
        max_height: Maximum height in pixels (default 2000)
        quality: JPEG quality 1-100 (default 85, good balance)
    
    Returns:
        Optimized InMemoryUploadedFile object
    """
    try:
        # Open the image
        img = Image.open(image)
        
        # Quick mode conversion (no heavy processing)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get original dimensions
        original_width, original_height = img.size
        
        # Only resize if significantly larger (prevent unnecessary processing)
        if original_width > max_width * 1.2 or original_height > max_height * 1.2:
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            # Use faster resampling method
            img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
            print(f"✅ Quick resize: {original_width}x{original_height} → {new_width}x{new_height}")
        
        # Save with basic optimization
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=False)  # Disable heavy optimization
        output.seek(0)
        
        # Create new InMemoryUploadedFile
        optimized_image = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return optimized_image
        
    except Exception as e:
        print(f"⚠️ Image optimization failed: {e}. Using original image.")
        return image

def validate_product_image(image):
    """
    Validate and optimize product images.
    
    Args:
        image: Django UploadedFile object
        
    Raises:
        ValidationError if image is invalid
    """
    from django.core.exceptions import ValidationError
    
    # Check file size (max 10MB before optimization)
    max_size = 10 * 1024 * 1024  # 10MB
    if hasattr(image, 'size') and image.size > max_size:
        raise ValidationError(f'Image file size cannot exceed 10MB. Current size: {image.size / (1024*1024):.1f}MB')
    
    # Check file type
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    if hasattr(image, 'name'):
        ext = image.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise ValidationError(f'Invalid file type. Allowed types: {", ".join(valid_extensions)}')
    
    # Try to open and validate as image
    try:
        img = Image.open(image)
        img.verify()
        image.seek(0)  # Reset file pointer after verify
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')

def validate_blog_image(image):
    """
    Validate and optimize blog featured images.
    Same as product images but could have different rules in future.
    
    Args:
        image: Django UploadedFile object
    """
    return validate_product_image(image)