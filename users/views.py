from rest_framework import generics
from .serializers import RegistrationSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
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

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user by email and password
        user = get_user_model().objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
       

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user': UserSerializer(user).data,
        })

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=LogoutSerializer)
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