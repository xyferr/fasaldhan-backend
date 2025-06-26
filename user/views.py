from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from .models import User, FarmerProfile, BuyerProfile
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    FarmerProfileSerializer, 
    BuyerProfileSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_overview(request):
    """
    API Overview - Lists available endpoints
    """
    api_urls = {
        'Authentication': {
            'Register': '/api/auth/register/',
            'Login': '/api/auth/login/',
            'Refresh Token': '/api/auth/token/refresh/',
            'User Profile': '/api/auth/profile/',
            'Dashboard': '/api/dashboard/',
        },
        'Profiles': {
            'Farmer Profile': '/api/farmer-profile/',
            'Buyer Profile': '/api/buyer-profile/',
        },
        'Contract System': {
            'Categories': '/api/contract/categories/',
            'Crops': '/api/contract/crops/',
            'Crop Listings': '/api/contract/listings/',
            'Contracts': '/api/contract/contracts/',
            'Reviews': '/api/contract/reviews/',
            'Dashboard': '/api/contract/dashboard/',
            'Market Trends': '/api/contract/market-trends/',
        },
        'Machine Learning (Simplified)': {
            'Price Prediction': '/api/contract/ml/predict-price/',
            'Quality Assessment': '/api/contract/ml/assess-quality/',
            'Yield Prediction': '/api/contract/ml/predict-yield/',
        },
        'Advanced Features': {
            'Crop Price History': '/api/contract/crops/{id}/price_history/',
            'Market Analysis': '/api/contract/crops/{id}/market_analysis/',
            'Upload Crop Images': '/api/contract/listings/{id}/upload_image/',
            'ML Insights': '/api/contract/listings/{id}/ml_insights/',
            'Contract Progress': '/api/contract/contracts/{id}/update_progress/',
            'Complete Contract': '/api/contract/contracts/{id}/complete_contract/',
            'Risk Analysis': '/api/contract/contracts/{id}/risk_analysis/',
        },
        'Core APIs': {
            'API Overview': '/api/overview/',
            'DRF Browsable API': '/api/',
            'Admin Panel': '/admin/',
        },
        'System Info': {
            'Version': '1.0.0',
            'ML Status': 'Simplified (Heavy ML disabled for better performance)',
            'Features': [
                'User Authentication & Profiles',
                'Crop Listings & Management', 
                'Contract Creation & Tracking',
                'Progress Updates with Images',
                'Reviews & Ratings System',
                'Market Trends & Analytics',
                'Simplified ML Predictions',
                'Dashboard & Insights'
            ]
        }
    }
    return Response(api_urls)


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user (farmer or buyer)
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    Login user and return JWT tokens
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class FarmerProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update farmer profile (create if doesn't exist)
    """
    serializer_class = FarmerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if not user.is_farmer:
            return Response(
                {'error': 'Only farmers can access this endpoint'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        profile, created = FarmerProfile.objects.get_or_create(user=user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if isinstance(instance, Response):  # Error response
                return instance
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class BuyerProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update buyer profile (create if doesn't exist)
    """
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if not user.is_buyer:
            return Response(
                {'error': 'Only buyers can access this endpoint'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        profile, created = BuyerProfile.objects.get_or_create(user=user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if isinstance(instance, Response):  # Error response
                return instance
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """
    Get user dashboard data based on user type
    """
    user = request.user
    
    dashboard_data = {
        'user': UserProfileSerializer(user).data,
        'profile_completion': 0,
        'profile_exists': user.has_profile,
    }
    
    if user.is_farmer and hasattr(user, 'farmer_profile'):
        dashboard_data['profile_completion'] = user.farmer_profile.completion_percentage
        dashboard_data['profile'] = FarmerProfileSerializer(user.farmer_profile).data
    elif user.is_buyer and hasattr(user, 'buyer_profile'):
        dashboard_data['profile_completion'] = user.buyer_profile.completion_percentage
        dashboard_data['profile'] = BuyerProfileSerializer(user.buyer_profile).data
    
    return Response(dashboard_data)