from django.urls import path
from . import views

urlpatterns = [
    path('merchant-feed.xml', views.merchant_feed, name='merchant-feed'),
    # New endpoints for room categories and product types
    path('room-categories/', views.RoomCategoryList.as_view(), name='room-category-list'),
    path('product-types/', views.ProductTypeList.as_view(), name='product-type-list'),
    path('product-types/room/<slug:room_slug>/', views.ProductTypesByRoomView.as_view(), name='product-types-by-room'),

    # Existing endpoints
    path('tags/', views.TagList.as_view(), name='tag-list'),
    # Mount list/detail at base so final URLs are /api/products/ and /api/products/<slug>/
    path('', views.ProductList.as_view(), name='product-list'),
    path('<slug:slug>/', views.ProductDetail.as_view(), name='product-detail'),
    path('<slug:slug>/images/', views.product_images, name='product-images'),
]
