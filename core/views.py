from rest_framework import generics
from django.shortcuts import get_object_or_404
from .models import Redirect
from .serializers import RedirectSerializer


class RedirectDetail(generics.RetrieveAPIView):
    """
    API endpoint to check if a path should redirect.
    Returns redirect information if found, 404 if not.
    """
    serializer_class = RedirectSerializer
    lookup_field = 'old_path'
    lookup_url_kwarg = 'path'
    
    def get_object(self):
        path = self.kwargs.get('path', '')
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        redirect = get_object_or_404(
            Redirect.objects.filter(is_active=True),
            old_path=path
        )
        return redirect


class RedirectList(generics.ListAPIView):
    """
    API endpoint to list all active redirects.
    """
    queryset = Redirect.objects.filter(is_active=True)
    serializer_class = RedirectSerializer

