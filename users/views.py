from rest_framework import generics
from .serializers import ForgotPasswordSerializer, RegistrationSerializer, ResetPasswordSerializer, UpdateProfileSerializer, UserSerializer, VerifyEmailSerializer, ResendVerificationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from utils import send_password_reset_email, send_verification_email
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer

User = get_user_model()

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    
    @swagger_auto_schema(request_body=RegistrationSerializer, tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Registration successful! Please check your email for verification code.',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

class GetProfileView(APIView):
    """Get current user profile"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags=["Profile"])
    def get(self, request):
        user = request.user
        return Response({
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    """Update user profile including address"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=UpdateProfileSerializer,
        tags=["Profile"]
    )
    def patch(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    """Verify email with the code sent to user"""
    
    @swagger_auto_schema(request_body=VerifyEmailSerializer, tags=["Authentication"])
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({
                'error': 'Email and verification code are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_email_verified:
            return Response({
                'message': 'Email is already verified.'
            }, status=status.HTTP_200_OK)
        
        if user.email_verification_token == code:
            user.is_email_verified = True
            user.is_active = True
            user.email_verification_token = None
            user.save()
        
                # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'message': 'Email verified successfully! You can now login.',
                'refresh': str(refresh),
                'access': str(access_token),
                'user': UserSerializer(user).data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid verification code.'
            }, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationCodeView(APIView):
    """Resend verification code to user's email"""
    
    @swagger_auto_schema(request_body=ResendVerificationSerializer, tags=["Authentication"])
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_email_verified:
            return Response({
                'message': 'Email is already verified.'
            }, status=status.HTTP_200_OK)
        
        user.generate_verification_token()
        send_verification_email(user)
        
        return Response({
            'message': 'Verification code resent successfully.'
        }, status=status.HTTP_200_OK)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user by email and password
        user = get_user_model().objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_email_verified:
            return Response({'detail': 'Please verify your email before logging in.'}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
       

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user': UserSerializer(user).data,
        })

class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ForgotPasswordView(APIView):
    """Request password reset code"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=ForgotPasswordSerializer, tags=["Password Reset"])
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Only allow password reset for verified users
            if not user.is_email_verified:
                return Response({
                    'error': 'Please verify your email first before resetting password.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate and send password reset token
            user.generate_password_reset_token()
            send_password_reset_email(user)
            
            return Response({
                'message': 'Password reset code sent to your email.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # For security, don't reveal if email exists or not
            return Response({
                'message': 'If the email exists, a password reset code has been sent.'
            }, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    """Verify code and reset password"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=ResetPasswordSerializer, tags=["Password Reset"])
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if password reset token is set
        if not user.password_reset_token:
            return Response({
                'error': 'No password reset request found. Please request a new code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the code
        if user.password_reset_token == code:
            # Reset password
            user.set_password(new_password)
            user.password_reset_token = None  # Clear the token
            user.save()
            
            return Response({
                'message': 'Password reset successful! You can now login with your new password.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid verification code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=LogoutSerializer, tags=["Authentication"])
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logout successful.'}, status=200)
        except TokenError:
            return Response({'detail': 'Invalid token.'}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)