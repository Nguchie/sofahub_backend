from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
import json
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
from .services import send_whatsapp_message, initiate_mpesa_payment
from cart.views import get_or_create_cart


class OrderDetail(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = 'id'


@api_view(['POST'])
def checkout(request):
    print("=" * 50)
    print("CHECKOUT PROCESS STARTED")
    print("=" * 50)
    
    # Get session ID from request data (frontend sends it in the body)
    session_id = request.data.get('session_id')
    print(f"Session ID from request: {session_id}")
    
    if session_id:
        # Use the session ID from request data
        try:
            cart = Cart.objects.get(session_id=session_id)
            print(f"Cart found by session ID: {cart.id}, Items: {cart.items.count()}")
        except Cart.DoesNotExist:
            print(f"❌ No cart found for session ID: {session_id}")
            return Response(
                {"error": "Cart not found. Please add items to cart first."},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        # Fall back to Django session
        cart = get_or_create_cart(request)
        print(f"Cart retrieved from Django session: {cart.id}, Items: {cart.items.count()}")

    if not cart.items.exists():
        print("❌ Cart is empty - checkout failed")
        return Response(
            {"error": "Cart is empty"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Debug: Print the incoming data
    print(f"Checkout request data: {request.data}")
    
    serializer = CheckoutSerializer(data=request.data)
    
    # Debug: Print validation errors if any
    if not serializer.is_valid():
        print(f"❌ Serializer validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    print("✅ Serializer validation passed")
    
    if serializer.is_valid():
        # Create order
        print("Creating order...")
        order = Order.objects.create(
            customer_name=serializer.validated_data['customer_name'],
            customer_email=serializer.validated_data['customer_email'],
            customer_phone=serializer.validated_data['customer_phone'],
            shipping_address=serializer.validated_data['shipping_address'],
            shipping_city=serializer.validated_data['shipping_city'],
            shipping_zip_code=serializer.validated_data['shipping_zip_code'],
            cart_session=cart.session_id,
            subtotal=cart.subtotal
        )
        print(f"✅ Order created with ID: {order.id}")

        # Calculate downpayment amounts
        deposit_amount, remaining_amount = order.calculate_downpayment()
        order.save()
        print(f"Deposit amount: {deposit_amount}, Remaining: {remaining_amount}")

        # Create order items
        print("Creating order items...")
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variation=cart_item.variation,
                product_name=cart_item.variation.product.name,
                variation_attributes=cart_item.variation.attributes,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price
            )
        print(f"✅ Created {cart.items.count()} order items")

        # Use M-Pesa phone number if provided, otherwise use customer phone
        mpesa_phone = serializer.validated_data.get('mpesa_phone') or serializer.validated_data['customer_phone']
        print(f"Using M-Pesa phone: {mpesa_phone}")
        
        # Initiate M-Pesa payment for deposit amount
        print("Initiating M-Pesa payment...")
        payment_response = initiate_mpesa_payment(
            mpesa_phone,
            float(deposit_amount),  # Pay only the deposit amount
            order.id
        )
        print(f"M-Pesa payment response: {payment_response}")

        if payment_response.get('ResponseCode') == '0':
            print("✅ M-Pesa payment initiated successfully")
            # Send WhatsApp confirmation
            message = f"Thank you for your order #{order.id} at SOFAHUB. Your deposit payment request ({deposit_amount} KSh) has been sent to M-Pesa. Please complete the payment to confirm your order. Balance of {remaining_amount} KSh will be paid upon delivery."
            send_whatsapp_message(serializer.validated_data['customer_phone'], message)

            # Clear the cart
            cart.items.all().delete()
            print("✅ Cart cleared")

            order_serializer = OrderSerializer(order)
            print("✅ Checkout completed successfully")
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"❌ M-Pesa payment initiation failed: {payment_response}")
            # Payment initiation failed
            order.status = 'cancelled'
            order.save()
            return Response(
                {"error": "Payment initiation failed", "details": payment_response.get('error', 'Unknown error')},
                status=status.HTTP_400_BAD_REQUEST
            )

    print("❌ Serializer validation failed")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def mpesa_callback(request):
    """
    Handle M-Pesa payment callback
    """
    print(f"M-Pesa Callback received: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.body}")
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed'}, status=405)
    
    try:
        # Parse the callback data
        callback_data = json.loads(request.body)
        print(f"Parsed callback data: {callback_data}")
        
        # Extract relevant information
        result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode', -1)
        checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID', '')
        
        print(f"Result Code: {result_code}")
        print(f"Checkout Request ID: {checkout_request_id}")
        
        # Find the order by checkout request ID (we'll need to store this in the order)
        # For now, we'll use the account reference to find the order
        account_reference = callback_data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [{}])[0].get('Value', '')
        
        print(f"Account Reference: {account_reference}")
        
        if account_reference and account_reference.startswith('SOFAHUB'):
            order_id = account_reference.replace('SOFAHUB', '')
            print(f"Looking for order ID: {order_id}")
            
            try:
                order = Order.objects.get(id=order_id)
                print(f"Found order: {order.id}")
                
                if result_code == 0:
                    # Payment successful
                    order.payment_confirmed = True
                    order.status = 'confirmed'
                    order.save()
                    
                    # Send confirmation WhatsApp message
                    message = f"Payment confirmed for Order #{order.id} at SOFAHUB. Your deposit of {order.deposit_amount} KSh has been received. We'll contact you soon to arrange delivery. Balance of {order.remaining_amount} KSh will be paid upon delivery."
                    send_whatsapp_message(order.customer_phone, message)
                    
                    print(f"Payment successful for order {order.id}")
                else:
                    # Payment failed
                    order.status = 'payment_failed'
                    order.save()
                    
                    # Send failure notification
                    message = f"Payment failed for Order #{order.id} at SOFAHUB. Please try again or contact our support team."
                    send_whatsapp_message(order.customer_phone, message)
                    
                    print(f"Payment failed for order {order.id}, result code: {result_code}")
                
                return JsonResponse({'status': 'success'})
                
            except Order.DoesNotExist:
                print(f"Order {order_id} not found")
                return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"M-Pesa callback error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@api_view(['POST'])
def test_mpesa(request):
    """
    Test endpoint for M-Pesa integration
    """
    try:
        # Test data
        test_phone = request.data.get('phone', '254708374149')  # Safaricom test number
        test_amount = request.data.get('amount', 1)
        test_order_id = request.data.get('order_id', 999)
        
        print(f"Testing M-Pesa with phone: {test_phone}, amount: {test_amount}, order: {test_order_id}")
        
        # Test access token
        access_token = get_mpesa_access_token()
        if not access_token:
            return Response({
                'error': 'Failed to get access token',
                'details': 'Check your M-Pesa credentials'
            }, status=400)
        
        # Test STK push
        result = initiate_mpesa_payment(test_phone, test_amount, test_order_id)
        
        return Response({
            'message': 'M-Pesa test initiated',
            'access_token': access_token[:20] + '...',
            'stk_push_result': result,
            'callback_url': settings.MPESA_CALLBACK_URL
        })
        
    except Exception as e:
        return Response({
            'error': 'M-Pesa test failed',
            'details': str(e)
        }, status=500)