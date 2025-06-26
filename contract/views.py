from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    Category, Crop, CropListing, CropImage, Contract, 
    ContractProgress, ProgressImage, Review, MarketPrice, MLModel
)
from .serializers import (
    CategorySerializer, CropSerializer, CropListingSerializer, CropImageSerializer,
    ContractSerializer, ContractProgressSerializer, ProgressImageSerializer,
    ReviewSerializer, MarketPriceSerializer, MLModelSerializer,
    DashboardSerializer, PricePredictionSerializer, QualityAssessmentSerializer,
    YieldPredictionSerializer
)

# Import ML services (now simplified without heavy dependencies)
try:
    from .ml_services import price_service, quality_service, yield_service, risk_service
    ML_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"ML services not available: {e}")
    ML_SERVICES_AVAILABLE = False
    # Create dummy services
    class DummyService:
        def predict_price(self, *args, **kwargs):
            return {'predicted_price': 100, 'confidence': 0.1, 'method': 'unavailable'}
        def assess_quality(self, *args, **kwargs):
            return {'quality_score': 0.5, 'method': 'unavailable'}
        def predict_yield(self, *args, **kwargs):
            return {'predicted_yield': 10, 'confidence': 0.1, 'method': 'unavailable'}
        def assess_contract_risk(self, *args, **kwargs):
            return {'overall_risk_score': 0.5, 'risk_level': 'unknown', 'method': 'unavailable'}
    
    price_service = DummyService()
    quality_service = DummyService()
    yield_service = DummyService()
    risk_service = DummyService()


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for crop categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Allow read-only access for list and retrieve"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class CropViewSet(viewsets.ModelViewSet):
    """
    ViewSet for crops with ML predictions
    """
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Allow read-only access for list and retrieve"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Crop.objects.all()
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(scientific_name__icontains=search) |
                Q(variety__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        """Get price history for a crop"""
        crop = self.get_object()
        prices = crop.market_prices.order_by('-date')[:30]
        return Response(MarketPriceSerializer(prices, many=True).data)

    @action(detail=True, methods=['get'])
    def market_analysis(self, request, pk=None):
        """Get market analysis for a crop"""
        crop = self.get_object()
        
        # Get recent price trends
        recent_prices = crop.market_prices.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        ).order_by('date')
        
        analysis = {
            'current_price': crop.current_market_price,
            'predicted_price': crop.predicted_price_next_month,
            'volatility_score': crop.price_volatility_score,
            'recent_trend': list(recent_prices.values('date', 'price_per_quintal', 'location')),
            'demand_level': 'medium',
            'ml_available': ML_SERVICES_AVAILABLE
        }
        
        return Response(analysis)


class CropListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for crop listings with ML features
    """
    queryset = CropListing.objects.all()
    serializer_class = CropListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CropListing.objects.all()
        user = self.request.user
        
        # Filter based on user type and query parameters
        status_filter = self.request.query_params.get('status', None)
        crop_filter = self.request.query_params.get('crop', None)
        location_filter = self.request.query_params.get('location', None)
        my_listings = self.request.query_params.get('my_listings', None)
        
        if my_listings and user.is_farmer:
            queryset = queryset.filter(farmer=user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if crop_filter:
            queryset = queryset.filter(crop__name__icontains=crop_filter)
        if location_filter:
            queryset = queryset.filter(farm_location__icontains=location_filter)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Ensure only farmers can create listings"""
        if not self.request.user.is_farmer:
            raise PermissionError("Only farmers can create crop listings")
        serializer.save(farmer=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload image for crop listing"""
        listing = self.get_object()
        
        # Check if user owns the listing
        if listing.farmer != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        image_data = {
            'listing': listing.id,
            'image': request.FILES.get('image'),
            'image_type': request.data.get('image_type', 'crop_close')
        }
        
        serializer = CropImageSerializer(data=image_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def ml_insights(self, request, pk=None):
        """Get ML insights for a listing"""
        listing = self.get_object()
        
        insights = {
            'price_recommendation': listing.ai_price_recommendation,
            'quality_score': listing.ai_quality_score,
            'market_demand': listing.market_demand_score,
            'ml_available': ML_SERVICES_AVAILABLE
        }
        
        # Add image analysis if images exist
        if listing.images.exists():
            latest_image = listing.images.latest('uploaded_at')
            insights['image_analysis'] = {
                'health_score': latest_image.health_score,
                'ripeness_score': latest_image.ripeness_score,
                'quality_assessment': latest_image.ai_quality_assessment
            }
        
        return Response(insights)


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for contracts with ML risk assessment
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Contract.objects.all()
        
        # Filter contracts based on user role
        if user.is_farmer:
            queryset = queryset.filter(farmer=user)
        elif user.is_buyer:
            queryset = queryset.filter(buyer=user)
        
        # Additional filters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Ensure only buyers can create contracts"""
        if not self.request.user.is_buyer:
            raise PermissionError("Only buyers can create contracts")
        
        # Set farmer from listing
        listing = serializer.validated_data['listing']
        serializer.save(buyer=self.request.user, farmer=listing.farmer)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update contract progress"""
        contract = self.get_object()
        
        # Check permissions
        if request.user not in [contract.farmer, contract.buyer]:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        progress_data = {
            'contract': contract.id,
            'progress_percentage': request.data.get('progress_percentage'),
            'notes': request.data.get('notes', ''),
        }
        
        serializer = ContractProgressSerializer(data=progress_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete_contract(self, request, pk=None):
        """Mark contract as completed"""
        contract = self.get_object()
        
        # Check permissions (usually farmer completes delivery)
        if request.user != contract.farmer:
            return Response({'error': 'Only farmer can mark contract as completed'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        contract.status = 'completed'
        contract.completion_percentage = 100.0
        contract.actual_delivery_date = timezone.now().date()
        contract.save()
        
        return Response({'message': 'Contract marked as completed'})

    @action(detail=True, methods=['get'])
    def risk_analysis(self, request, pk=None):
        """Get detailed risk analysis for contract"""
        contract = self.get_object()
        
        if ML_SERVICES_AVAILABLE:
            risk_assessment = risk_service.assess_contract_risk(contract)
        else:
            risk_assessment = {
                'overall_risk_score': 0.5,
                'risk_level': 'medium',
                'message': 'ML services unavailable - using default assessment'
            }
        
        return Response(risk_assessment)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for reviews and ratings
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Review.objects.all()
        
        # Filter based on query parameters
        for_user = self.request.query_params.get('for_user', None)
        by_user = self.request.query_params.get('by_user', None)
        
        if for_user:
            queryset = queryset.filter(reviewee__username=for_user)
        if by_user:
            queryset = queryset.filter(reviewer__username=by_user)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """
    Get dashboard data based on user type
    """
    user = request.user
    
    if user.is_farmer:
        # Farmer dashboard data
        listings = CropListing.objects.filter(farmer=user)
        contracts = Contract.objects.filter(farmer=user)
        
        dashboard_data = {
            'user_type': 'farmer',
            'total_listings': listings.count(),
            'active_listings': listings.filter(status='active').count(),
            'active_contracts': contracts.filter(status__in=['active', 'in_progress']).count(),
            'completed_contracts': contracts.filter(status='completed').count(),
            'total_earnings': contracts.filter(status='completed').aggregate(
                total=Sum('total_contract_value'))['total'] or 0,
            'recent_activities': get_recent_activities(user, 'farmer'),
            'ml_insights': get_farmer_ml_insights(user) if ML_SERVICES_AVAILABLE else {},
            'ml_available': ML_SERVICES_AVAILABLE
        }
    
    elif user.is_buyer:
        # Buyer dashboard data
        contracts = Contract.objects.filter(buyer=user)
        
        dashboard_data = {
            'user_type': 'buyer',
            'total_contracts': contracts.count(),
            'active_contracts': contracts.filter(status__in=['active', 'in_progress']).count(),
            'completed_contracts': contracts.filter(status='completed').count(),
            'total_spent': contracts.filter(status='completed').aggregate(
                total=Sum('total_contract_value'))['total'] or 0,
            'recent_activities': get_recent_activities(user, 'buyer'),
            'ml_insights': get_buyer_ml_insights(user) if ML_SERVICES_AVAILABLE else {},
            'ml_available': ML_SERVICES_AVAILABLE
        }
    
    else:
        dashboard_data = {
            'user_type': 'unknown',
            'message': 'Please set your user type in profile',
            'ml_available': ML_SERVICES_AVAILABLE
        }
    
    return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_price(request):
    """
    ML endpoint for price prediction
    """
    if not ML_SERVICES_AVAILABLE:
        return Response({
            'error': 'ML services not available', 
            'predicted_price': 100,
            'method': 'unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    serializer = PricePredictionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            prediction = price_service.predict_price(
                crop_id=serializer.validated_data['crop_id'],
                location=serializer.validated_data['location'],
                quantity=float(serializer.validated_data['quantity']),
                season=serializer.validated_data['season']
            )
            return Response(prediction)
        except Exception as e:
            return Response({
                'error': str(e),
                'predicted_price': 100,
                'method': 'error_fallback'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assess_quality(request):
    """
    ML endpoint for quality assessment
    """
    if not ML_SERVICES_AVAILABLE:
        return Response({
            'error': 'ML services not available',
            'quality_score': 0.7,
            'method': 'unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    if 'image' not in request.FILES:
        return Response({'error': 'Image file required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # For now, return simplified assessment without heavy image processing
        assessment = quality_service.assess_quality(None)  # Pass None since we're not processing
        return Response(assessment)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_yield(request):
    """
    ML endpoint for yield prediction
    """
    if not ML_SERVICES_AVAILABLE:
        return Response({
            'error': 'ML services not available',
            'predicted_yield': 10,
            'method': 'unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    serializer = YieldPredictionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            prediction = yield_service.predict_yield(
                crop_id=serializer.validated_data['crop_id'],
                land_size=float(serializer.validated_data['land_size']),
                farming_type=serializer.validated_data['farming_type'],
                location=serializer.validated_data['location'],
                images=serializer.validated_data.get('images', [])
            )
            return Response(prediction)
        except Exception as e:
            return Response({
                'error': str(e),
                'predicted_yield': 10,
                'method': 'error_fallback'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def market_trends(request):
    """
    Get market trends and insights
    """
    # Get trending crops
    trending_crops = Crop.objects.annotate(
        listings_count=Count('listings'),
        avg_price=Avg('market_prices__price_per_quintal')
    ).filter(listings_count__gt=0).order_by('-listings_count')[:10]
    
    # Get recent price changes
    recent_prices = MarketPrice.objects.filter(
        date__gte=timezone.now().date() - timedelta(days=7)
    ).order_by('-date')[:20]
    
    trends_data = {
        'trending_crops': CropSerializer(trending_crops, many=True).data,
        'recent_price_updates': MarketPriceSerializer(recent_prices, many=True).data,
        'market_summary': {
            'total_active_listings': CropListing.objects.filter(status='active').count(),
            'total_active_contracts': Contract.objects.filter(status__in=['active', 'in_progress']).count(),
            'avg_contract_value': Contract.objects.aggregate(avg=Avg('total_contract_value'))['avg'] or 0
        },
        'ml_available': ML_SERVICES_AVAILABLE
    }
    
    return Response(trends_data)


def get_recent_activities(user, user_type):
    """Helper function to get recent activities"""
    activities = []
    
    try:
        if user_type == 'farmer':
            # Recent listings
            recent_listings = CropListing.objects.filter(farmer=user).order_by('-created_at')[:5]
            for listing in recent_listings:
                activities.append({
                    'type': 'listing_created',
                    'description': f"Created listing for {listing.crop.name}",
                    'date': listing.created_at,
                    'data': {'listing_id': str(listing.listing_id)}
                })
            
            # Recent contract updates
            recent_contracts = Contract.objects.filter(farmer=user).order_by('-updated_at')[:3]
            for contract in recent_contracts:
                activities.append({
                    'type': 'contract_update',
                    'description': f"Contract status: {contract.status}",
                    'date': contract.updated_at,
                    'data': {'contract_id': str(contract.contract_id)}
                })
        
        elif user_type == 'buyer':
            # Recent contracts
            recent_contracts = Contract.objects.filter(buyer=user).order_by('-created_at')[:5]
            for contract in recent_contracts:
                activities.append({
                    'type': 'contract_created',
                    'description': f"Created contract for {contract.listing.crop.name}",
                    'date': contract.created_at,
                    'data': {'contract_id': str(contract.contract_id)}
                })
    except Exception as e:
        print(f"Error getting recent activities: {e}")
    
    return sorted(activities, key=lambda x: x['date'], reverse=True)[:10]


def get_farmer_ml_insights(user):
    """Get ML insights for farmers - SIMPLIFIED"""
    insights = {
        'recommended_crops': [],
        'price_alerts': [],
        'optimization_tips': [
            "Complete your farmer profile for better recommendations",
            "Upload crop images to track quality",
            "Monitor market trends for optimal pricing",
            "ML features coming soon!"
        ]
    }
    
    if not ML_SERVICES_AVAILABLE:
        insights['note'] = "Advanced ML insights will be available in future updates"
    
    return insights


def get_buyer_ml_insights(user):
    """Get ML insights for buyers - SIMPLIFIED"""
    insights = {
        'recommended_listings': [],
        'market_opportunities': [],
        'risk_alerts': [],
        'tips': [
            "Review farmer profiles and ratings",
            "Compare prices across different regions",
            "Consider contract terms carefully",
            "ML recommendations coming soon!"
        ]
    }
    
    if not ML_SERVICES_AVAILABLE:
        insights['note'] = "Advanced ML insights will be available in future updates"
    
    return insights