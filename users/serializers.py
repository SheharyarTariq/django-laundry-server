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
    address = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'full_name', 'phone_number', 'role', 'is_email_verified', 'address')

    def get_address(self, obj):
        """Return address as a nested object"""
        return {
            'address_line_1': obj.address_line_1 or '',
            'address_line_2': obj.address_line_2 or '',
            'city': obj.city or '',
            'country': obj.country or '',
            'postcode': obj.postcode or ''
        }

class AddressSerializer(serializers.Serializer):
    """Serializer for address fields"""
    address_line_1 = serializers.CharField(max_length=255, required=True, allow_blank=False)
    address_line_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=True, allow_blank=False)
    country = serializers.CharField(max_length=100, required=True, allow_blank=False)
    postcode = serializers.CharField(max_length=20, required=True, allow_blank=False)

class UpdateProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False, allow_null=True)
    
    class Meta:
        model = get_user_model()
        fields = ['full_name', 'phone_number', 'address']

    def validate_full_name(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Full name must be at least 4 characters long.")
        return value

    def validate_phone_number(self, value):
        if value.startswith('+44'):
            value_without_plus_44 = value[3:]
            if not value_without_plus_44.isdigit():
                raise serializers.ValidationError("Phone number must only contain digits after the '+44' country code.")
            if len(value_without_plus_44) != 10:
                raise serializers.ValidationError("UK phone number must be exactly 10 digits long after '+44'.")
        else:
            raise serializers.ValidationError("Phone number must start with '+44' for UK numbers.")
        return value

    def validate_address(self, value):
        """Validate address fields if provided"""
        if value:
            allowed_keys = ['address_line_1', 'address_line_2', 'city', 'country', 'postcode']
            for key in value.keys():
                if key not in allowed_keys:
                    raise serializers.ValidationError(f"Invalid address field: {key}")
        return value

    def update(self, instance, validated_data):
        # Update basic fields
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        
        # Update address fields if provided
        address_data = validated_data.get('address')
        if address_data is not None:
            instance.address_line_1 = address_data.get('address_line_1', instance.address_line_1)
            instance.address_line_2 = address_data.get('address_line_2', instance.address_line_2)
            instance.city = address_data.get('city', instance.city)
            instance.country = address_data.get('country', instance.country)
            instance.postcode = address_data.get('postcode', instance.postcode)
        
        instance.save()
        return instance

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4, min_length=4)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
    def validate(self, data):
        """Check that password and confirm_password match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return data