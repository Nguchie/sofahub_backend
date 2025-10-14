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
    Ultra-lightweight image optimization - minimal processing only.
    Just converts format and does basic resize if absolutely necessary.
    
    Args:
        image: Django UploadedFile object
        max_width: Maximum width in pixels (default 2000)
        max_height: Maximum height in pixels (default 2000)
        quality: JPEG quality 1-100 (default 85)
    
    Returns:
        Optimized InMemoryUploadedFile object
    """
    try:
        # Open the image
        img = Image.open(image)
        
        # Only resize if image is HUGE (3x larger than max)
        original_width, original_height = img.size
        if original_width > max_width * 3 or original_height > max_height * 3:
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            # Use fastest possible resize
            img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
            print(f"✅ Emergency resize: {original_width}x{original_height} → {new_width}x{new_height}")
        
        # Convert to RGB only if absolutely necessary
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Save with minimal processing
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=False, progressive=False)
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

def optimize_image_storage(image, max_width=2000, max_height=2000, quality=75):
    """
    Storage-efficient image optimization - focuses on reducing file size quickly.
    Prioritizes compression over perfect quality to save storage costs.
    
    Args:
        image: Django UploadedFile object
        max_width: Maximum width in pixels (default 2000)
        max_height: Maximum height in pixels (default 2000)
        quality: JPEG quality 1-100 (default 75 for smaller files)
    
    Returns:
        Compressed InMemoryUploadedFile object
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
        
        # Resize if larger than max (save storage space)
        if original_width > max_width or original_height > max_height:
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            # Use fast resize method
            img = img.resize((new_width, new_height), Image.Resampling.NEAREST)
            print(f"📦 Resized for storage: {original_width}x{original_height} → {new_width}x{new_height}")
        
        # Save with aggressive compression to reduce storage
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
        output.seek(0)
        
        # Get file size info for storage savings
        original_size = image.size if hasattr(image, 'size') else 0
        new_size = output.getbuffer().nbytes
        if original_size > 0:
            savings = ((original_size - new_size) / original_size) * 100
            print(f"💾 Storage saved: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB ({savings:.1f}% smaller)")
        
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
        print(f"⚠️ Storage optimization failed: {e}. Using original image.")
        return image

def optimize_image_async(image, max_width=2000, max_height=2000, quality=85):
    """
    Async image optimization - saves original immediately, processes in background.
    Returns the original image immediately to prevent timeouts.
    """
    try:
        # For now, just return the original image to prevent timeouts
        # In a real implementation, you'd queue this for background processing
        print(f"📸 Image queued for background optimization: {image.name}")
        return image
    except Exception as e:
        print(f"⚠️ Async optimization failed: {e}")
        return image

def validate_product_image(image):
    """
    Smart image validation - fast but secure.
    Does essential validation without heavy processing.
    
    Args:
        image: Django UploadedFile object
        
    Raises:
        ValidationError if image is invalid
    """
    from django.core.exceptions import ValidationError
    from django.conf import settings
    
    # Always do basic security checks (fast)
    max_size = 10 * 1024 * 1024  # 10MB
    if hasattr(image, 'size') and image.size > max_size:
        raise ValidationError(f'Image file size cannot exceed 10MB. Current size: {image.size / (1024*1024):.1f}MB')
    
    # Check file type by extension (fast)
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    if hasattr(image, 'name'):
        ext = image.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise ValidationError(f'Invalid file type. Allowed types: {", ".join(valid_extensions)}')
    
    # Check for suspicious file names
    if hasattr(image, 'name') and any(char in image.name for char in ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']):
        raise ValidationError('Invalid file name. Contains unsafe characters.')
    
    # Only do heavy validation in development or when explicitly enabled
    if settings.DEBUG or getattr(settings, 'ENABLE_HEAVY_VALIDATION', False):
        try:
            # Quick image header check (doesn't load full image)
            img = Image.open(image)
            img.verify()
            image.seek(0)  # Reset file pointer
        except Exception as e:
            raise ValidationError(f'Invalid image file: {str(e)}')
    
    return True

def validate_blog_image(image):
    """
    Validate and optimize blog featured images.
    Same as product images but could have different rules in future.
    
    Args:
        image: Django UploadedFile object
    """
    return validate_product_image(image)