from django.contrib.auth import get_user_model
from rest_framework import serializers
from utils import send_verification_email

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()  # Custom User model
        fields = ['id', 'full_name', 'phone_number', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}, 'role': {'read_only': True}}

    # Field-level validation for 'full_name'
    def validate_full_name(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Full name must be at least 4 characters long.")
        return value

    def validate_phone_number(self, value):
        # Check if phone number starts with '+44' for UK
        if value.startswith('+44'):
            # Remove the '+44' for the length check and digit validation
            value_without_plus_44 = value[3:]

            # Ensure the remaining part contains only digits
            if not value_without_plus_44.isdigit():
                raise serializers.ValidationError("Phone number must only contain digits after the '+44' country code.")
            
            # Ensure the phone number is 10 digits long after '+44' (total of 13 characters)
            if len(value_without_plus_44) != 10:
                raise serializers.ValidationError("UK phone number must be exactly 10 digits long after '+44'.")
        else:
            raise serializers.ValidationError("Phone number must start with '+44' for UK numbers.")

        return value

    # Custom validation for password (optional)
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value


    def create(self, validated_data):
        # Create a new user with the provided data
        user = get_user_model().objects.create_user(
            username=validated_data.get('email'),
            full_name=validated_data['full_name'],
            phone_number=validated_data.get('phone_number'),
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # Add this - user inactive until verified
        )
        
        # Generate token and send email
        user.generate_verification_token()
        send_verification_email(user)
        
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'full_name', 'phone_number', 'role', 'is_email_verified')

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
