from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ContactSubmission
from .serializers import ContactSubmissionSerializer

@api_view(['GET', 'POST'])
def contact_submission(request):
    """
    Handle contact form submissions
    GET: Returns API information
    POST: Processes contact form data and sends emails
    """
    
    if request.method == 'GET':
        # Return API information for testing
        return Response({
            'message': '✅ Contact API is working!',
            'instruction': 'Send POST request with: name, email, message',
            'required_fields': ['name', 'email', 'message'],
            'example': {
                'name': 'John Doe',
                'email': 'john@example.com',
                'message': 'Hello, I would like to connect with you!'
            }
        })
    
    elif request.method == 'POST':
        # Validate and process the contact form data
        serializer = ContactSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save to database
            contact = serializer.save()
            
            try:
                # Email to you (portfolio owner)
                send_mail(
                    subject=f'📧 New Contact from {contact.name}',
                    message=f"""
Name: {contact.name}
Email: {contact.email}
Message: 
{contact.message}

Submitted at: {contact.submitted_at}
                    """.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                
                # Auto-reply to user
                send_mail(
                    subject='Thank you for reaching out! - Abhiram',
                    message=f"""
Hi {contact.name},

Thank you for reaching out through my portfolio website! 
I've received your message and will get back to you within 24 hours.

Best regards,
Abhiram
Email: chabhiram2001@gmail.com
Phone: +91 7095885614
                    """.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact.email],
                    fail_silently=False,
                )
                
                # Mark as processed successfully
                contact.is_processed = True
                contact.save()
                
                return Response(
                    {
                        'message': 'Message sent successfully! Thank you for reaching out.',
                        'status': 'success'
                    },
                    status=status.HTTP_201_CREATED
                )
                
            except Exception as e:
                # Save the submission but mark as not processed due to email failure
                contact.is_processed = False
                contact.save()
                
                # Log the error for debugging
                print(f"Email sending failed: {str(e)}")
                
                return Response(
                    {
                        'error': 'Message was received but email delivery failed. I\'ll still get your message!',
                        'status': 'warning'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Return validation errors
            return Response(
                {
                    'error': 'Invalid form data. Please check your inputs.',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )