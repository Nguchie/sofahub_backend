from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactMessageSerializer
from .models import ContactMessage


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_form(request):
    """
    Handle contact form submission and send email notification
    """
    serializer = ContactMessageSerializer(data=request.data)
    
    if serializer.is_valid():
        # Save the contact message to database
        contact_message = serializer.save()
        
        # Send email notification
        try:
            subject = f"New Contact Form Submission: {contact_message.subject}"
            message = f"""
New contact form submission from SofaHub website:

Name: {contact_message.name}
Email: {contact_message.email}
Phone: {contact_message.phone or 'Not provided'}
Subject: {contact_message.subject}

Message:
{contact_message.message}

---
This message was sent from the SofaHub contact form.
            """
            
            # Send email to the client's email address
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_message.email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Thank you for your message! We will get back to you within 24 hours.',
                'success': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If email fails, still save the message but return a different response
            return Response({
                'message': 'Your message has been received. We will get back to you soon.',
                'success': True,
                'note': 'Email notification failed, but your message was saved.'
            }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)