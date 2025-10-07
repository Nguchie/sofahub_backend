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