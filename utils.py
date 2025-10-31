from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user):
    """Send verification code to user's email"""
    subject = 'Verify Your Email Address'
    message = f'''
Hello {user.full_name},

Thank you for registering! Your verification code is:

{user.email_verification_token}

Please enter this code to verify your email address.

This code will expire in 15 minutes.

If you didn't register for an account, please ignore this email.

Best regards,
Laundry Server
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

def send_password_reset_email(user):
    """Send password reset code"""
    subject = 'Password Reset Code'
    message = f'Your password reset code is: {user.password_reset_token}\n\nIf you did not request this, please ignore this email.'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )