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
        
        print(f"DEBUG: Serving image ID {image_id}")
        print(f"DEBUG: Image name: {product_image.image.name}")
        print(f"DEBUG: File path: {file_path}")
        print(f"DEBUG: File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"DEBUG: File not found, trying to find alternative")
            # Try to find the file without the suffix
            base_name = product_image.image.name.split('_')[-1]
            if '.' in base_name:
                parts = product_image.image.name.split('_')
                if len(parts) > 1:
                    filename_without_suffix = '_'.join(parts[:-1]) + '.' + base_name.split('.')[-1]
                    alt_path = os.path.join(settings.MEDIA_ROOT, filename_without_suffix)
                    print(f"DEBUG: Trying alternative path: {alt_path}")
                    if os.path.exists(alt_path):
                        file_path = alt_path
                        print(f"DEBUG: Found alternative file: {alt_path}")
                    else:
                        raise Http404("Image file not found")
                else:
                    raise Http404("Image file not found")
            else:
                raise Http404("Image file not found")
        
        # Get file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Get content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'image/jpeg'  # Default to JPEG
        
        print(f"DEBUG: Serving file: {file_path}, size: {len(content)} bytes")
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Length'] = len(content)
        
        return response
        
    except ProductImage.DoesNotExist:
        print(f"DEBUG: ProductImage with ID {image_id} not found")
        raise Http404("Product image not found")
    except Exception as e:
        print(f"DEBUG: Error serving image: {e}")
        raise Http404("Error serving image")