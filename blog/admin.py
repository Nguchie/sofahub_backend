from django.contrib import admin
from .models import BlogPost, BlogTag


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'status', 'is_featured', 
        'published_at', 'created_at'
    ]
    list_filter = [
        'status', 'is_featured', 'tags', 'author', 
        'published_at', 'created_at'
    ]
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags', 'related_products', 'related_categories']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        (None, {
            'fields': ['title', 'slug', 'excerpt', 'content', 'author']
        }),
        ('Media', {
            'fields': ['featured_image', 'featured_image_alt']
        }),
        ('Publishing', {
            'fields': ['status', 'is_featured', 'published_at']
        }),
        ('Categorization', {
            'fields': ['tags', 'related_products', 'related_categories']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
