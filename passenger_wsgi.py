import os
import sys

# Add your project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sofahub_backend.settings')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
