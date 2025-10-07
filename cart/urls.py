from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartDetail.as_view(), name='cart-detail'),
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('items/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('items/<int:item_id>/delete/', views.remove_from_cart, name='remove-from-cart'),
]