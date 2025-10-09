from django.http import HttpResponse, Http404
from django.conf import settings
from products.models import ProductImage
import os
import mimetypes


def serve_media(request, path):
    """Custom view to serve media files"""
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Get file content
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Get content type
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    response = HttpResponse(content, content_type=content_type)
    response['Content-Length'] = len(content)
    
    return response


def serve_product_image(request, image_id):
    """Serve product image by ID - more reliable than filename"""
    try:
        product_image = ProductImage.objects.get(id=image_id)
        file_path = product_image.image.path
        
        if not os.path.exists(file_path):
            raise Http404("Image file not found")
        
        # Get file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Get content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'image/jpeg'  # Default to JPEG
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Length'] = len(content)
        
        return response
        
    except ProductImage.DoesNotExist:
        raise Http404("Product image not found")