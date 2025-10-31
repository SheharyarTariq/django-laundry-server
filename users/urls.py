from django.urls import path
from .views import ForgotPasswordView, RegistrationView, LoginView, LogoutView, ResetPasswordView, VerifyEmailView,GetProfileView,UpdateProfileView, ResendVerificationCodeView, CustomTokenRefreshView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationCodeView.as_view(), name='resend_verification'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', GetProfileView.as_view(), name='get-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
