from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # API Overview
    path('overview/', views.api_overview, name='api-overview'),
    
    # Authentication
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Profiles
    path('farmer-profile/', views.FarmerProfileView.as_view(), name='farmer-profile'),
    path('buyer-profile/', views.BuyerProfileView.as_view(), name='buyer-profile'),
    
    # Dashboard
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
]