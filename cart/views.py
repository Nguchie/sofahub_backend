from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from products.models import ProductVariation


def get_or_create_cart(request):
    """Helper function to get or create a cart based on session ID"""
    # Check if a custom session_id is provided in query parameters
    custom_session_id = request.GET.get('session_id')
    if custom_session_id:
        cart, created = Cart.objects.get_or_create(session_id=custom_session_id)
        return cart
    
    # Fall back to Django's built-in session system
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart


class CartDetail(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        return get_or_create_cart(self.request)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
def add_to_cart(request):
    # Check if session_id is provided in request data
    if 'session_id' in request.data:
        custom_session_id = request.data['session_id']
        cart, created = Cart.objects.get_or_create(session_id=custom_session_id)
    else:
        cart = get_or_create_cart(request)
    
    serializer = AddToCartSerializer(data=request.data)

    if serializer.is_valid():
        variation_id = serializer.validated_data['variation_id']
        quantity = serializer.validated_data['quantity']

        variation = get_object_or_404(ProductVariation, id=variation_id, is_active=True)

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variation=variation,
            defaults={'quantity': quantity}
        )

        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_cart_item(request, item_id):
    # Check if session_id is provided in query parameters
    custom_session_id = request.GET.get('session_id')
    if custom_session_id:
        cart = get_object_or_404(Cart, session_id=custom_session_id)
    else:
        cart = get_or_create_cart(request)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    serializer = UpdateCartItemSerializer(data=request.data)

    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']

        if quantity == 0:
            # Remove item if quantity is 0
            cart_item.delete()
        else:
            # Check stock availability
            if quantity > cart_item.variation.stock_quantity:
                return Response(
                    {"error": "Requested quantity exceeds available stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity = quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def remove_from_cart(request, item_id):
    # Check if a custom session_id is provided in query parameters
    custom_session_id = request.GET.get('session_id')
    if custom_session_id:
        cart = get_object_or_404(Cart, session_id=custom_session_id)
    else:
        cart = get_or_create_cart(request)
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()

    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response(cart_serializer.data, status=status.HTTP_200_OK)