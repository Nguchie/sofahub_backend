from rest_framework import serializers
from .models import Redirect


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ['id', 'old_path', 'new_path', 'redirect_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

