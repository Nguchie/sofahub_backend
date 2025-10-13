import uuid
from django.utils import timezone

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

def validate_product_image(image):
    """
    Placeholder validator for product images.
    Currently allows all images. Add validation logic here if needed.
    
    Args:
        image: Django UploadedFile object
    """
    # Placeholder - no validation currently
    # You can add validation here if needed in the future
    pass