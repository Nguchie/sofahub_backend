from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('<int:id>/', views.OrderDetail.as_view(), name='order-detail'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa-callback'),
    path('test-mpesa/', views.test_mpesa, name='test-mpesa'),
]