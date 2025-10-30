from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    full_name = models.CharField(blank=False, null=False)
    phone_number = models.CharField(blank=False, null=False)
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    # Add these new fields for email verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']
    
    def generate_verification_token(self):
        """Generate a 4-digit verification code"""
        self.email_verification_token = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        self.save()
        return self.email_verification_token