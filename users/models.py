from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    # Additional fields for registration
    full_name = models.CharField(blank=False, null=False)
    phone_number = models.CharField(blank=False, null=False )
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
      # Ensure email is unique
    USERNAME_FIELD = 'email' 
    
    REQUIRED_FIELDS = ['full_name', 'phone_number']