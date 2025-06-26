from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Crop, CropListing, CropImage, Contract, 
    ContractProgress, ProgressImage, Review, MarketPrice, MLModel
)

# Try to import ML services, but handle failure gracefully
try:
    from .ml_services import price_service, quality_service, yield_service, risk_service
    ML_SERVICES_AVAILABLE = True
except ImportError:
    ML_SERVICES_AVAILABLE = False
    # Create dummy services that return default values
    class DummyMLService:
        def predict_price(self, *args, **kwargs):
            return {'predicted_price': 0, 'confidence': 0, 'method': 'unavailable'}
        def assess_quality(self, *args, **kwargs):
            return {'quality_score': 0.7, 'method': 'unavailable'}
        def predict_yield(self, *args, **kwargs):
            return {'predicted_yield': 0, 'confidence': 0, 'method': 'unavailable'}
        def assess_contract_risk(self, *args, **kwargs):
            return {'overall_risk_score': 0.5, 'risk_level': 'unknown', 'method': 'unavailable'}
    
    price_service = DummyMLService()
    quality_service = DummyMLService()
    yield_service = DummyMLService()
    risk_service = DummyMLService()

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for crop categories
    """
    crops_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_crops_count(self, obj):
        return obj.crops.count()


class CropSerializer(serializers.ModelSerializer):
    """
    Serializer for crops with ML predictions
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    active_listings_count = serializers.SerializerMethodField()
    price_prediction = serializers.SerializerMethodField()

    class Meta:
        model = Crop
        fields = '__all__'

    def get_active_listings_count(self, obj):
        return obj.listings.filter(status='active').count()

    def get_price_prediction(self, obj):
        """Get ML price prediction for the crop"""
        if not ML_SERVICES_AVAILABLE:
            return {'error': 'ML services unavailable', 'predicted_price': obj.current_market_price or 0}
        
        try:
            prediction = price_service.predict_price(
                crop_id=obj.id,
                location="Default",
                quantity=100,
                season="current"
            )
            return prediction
        except Exception as e:
            return {'error': str(e), 'predicted_price': obj.current_market_price or 0}


class CropImageSerializer(serializers.ModelSerializer):
    """
    Serializer for crop images with ML analysis
    """
    class Meta:
        model = CropImage
        fields = '__all__'
        read_only_fields = ('ai_quality_assessment', 'predicted_yield', 'health_score', 'ripeness_score')

    def create(self, validated_data):
        image = super().create(validated_data)
        
        # Trigger ML analysis for the uploaded image only if ML is available
        if ML_SERVICES_AVAILABLE:
            try:
                quality_assessment = quality_service.assess_quality(image.image.path)
                image.ai_quality_assessment = quality_assessment
                image.health_score = quality_assessment.get('quality_score')
                image.ripeness_score = quality_assessment.get('ripeness_score')
                image.save()
            except Exception as e:
                print(f"Error in ML analysis: {e}")
        else:
            # Set default values when ML is not available
            image.ai_quality_assessment = {'note': 'ML analysis unavailable'}
            image.health_score = 0.7  # Default score
            image.ripeness_score = 0.7  # Default score
            image.save()
        
        return image


class CropListingSerializer(serializers.ModelSerializer):
    """
    Serializer for crop listings with ML enhancements
    """
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    crop_category = serializers.CharField(source='crop.category.name', read_only=True)
    images = CropImageSerializer(many=True, read_only=True)
    total_value = serializers.ReadOnlyField()
    ml_predictions = serializers.SerializerMethodField()
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = CropListing
        fields = '__all__'
        read_only_fields = ('listing_id', 'farmer', 'ai_quality_score', 'ai_price_recommendation', 'market_demand_score')

    def get_ml_predictions(self, obj):
        """Get ML predictions for the listing"""
        if not ML_SERVICES_AVAILABLE:
            return {'note': 'ML predictions unavailable'}
        
        try:
            # Price prediction
            price_pred = price_service.predict_price(
                crop_id=obj.crop.id,
                location=obj.farm_location,
                quantity=float(obj.quantity_available),
                season="current"
            )
            
            # Yield prediction if farmer profile exists
            yield_pred = None
            if hasattr(obj.farmer, 'farmer_profile'):
                farmer_profile = obj.farmer.farmer_profile
                yield_pred = yield_service.predict_yield(
                    crop_id=obj.crop.id,
                    land_size=float(farmer_profile.land_size or 1),
                    farming_type=farmer_profile.farming_type or 'traditional',
                    location=obj.farm_location,
                    images=obj.images.all()
                )
            
            return {
                'price_prediction': price_pred,
                'yield_prediction': yield_pred,
                'ml_available': True
            }
        except Exception as e:
            return {'error': str(e), 'ml_available': False}

    def get_contracts_count(self, obj):
        return obj.contracts.count()

    def create(self, validated_data):
        # Set farmer from request user
        validated_data['farmer'] = self.context['request'].user
        listing = super().create(validated_data)
        
        # Generate ML recommendations only if available
        if ML_SERVICES_AVAILABLE:
            try:
                price_pred = price_service.predict_price(
                    crop_id=listing.crop.id,
                    location=listing.farm_location,
                    quantity=float(listing.quantity_available)
                )
                listing.ai_price_recommendation = price_pred.get('predicted_price')
                listing.save()
            except Exception as e:
                print(f"Error generating ML recommendations: {e}")
        
        return listing


class ContractSerializer(serializers.ModelSerializer):
    """
    Serializer for contracts with ML risk assessment
    """
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    crop_name = serializers.CharField(source='listing.crop.name', read_only=True)
    listing_details = CropListingSerializer(source='listing', read_only=True)
    days_until_delivery = serializers.ReadOnlyField()
    risk_assessment = serializers.SerializerMethodField()
    progress_updates = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ('contract_id', 'farmer', 'ai_risk_score', 'contract_date')

    def get_risk_assessment(self, obj):
        """Get ML risk assessment for the contract"""
        if not ML_SERVICES_AVAILABLE:
            return {'note': 'Risk assessment unavailable', 'risk_level': 'unknown'}
        
        try:
            return risk_service.assess_contract_risk(obj)
        except Exception as e:
            return {'error': str(e), 'risk_level': 'unknown'}

    def get_progress_updates(self, obj):
        """Get recent progress updates"""
        recent_updates = obj.progress_updates.all()[:3]
        return ContractProgressSerializer(recent_updates, many=True).data

    def create(self, validated_data):
        # Set buyer from request user
        validated_data['buyer'] = self.context['request'].user
        
        # Calculate total contract value
        validated_data['total_contract_value'] = (
            validated_data['agreed_quantity'] * validated_data['agreed_price_per_quintal']
        )
        
        contract = super().create(validated_data)
        
        # Generate ML risk assessment only if available
        if ML_SERVICES_AVAILABLE:
            try:
                risk_assessment = risk_service.assess_contract_risk(contract)
                contract.ai_risk_score = risk_assessment.get('overall_risk_score')
                contract.save()
            except Exception as e:
                print(f"Error generating risk assessment: {e}")
        
        return contract


class ProgressImageSerializer(serializers.ModelSerializer):
    """
    Serializer for progress images
    """
    class Meta:
        model = ProgressImage
        fields = '__all__'
        read_only_fields = ('growth_stage', 'health_assessment', 'estimated_yield')

    def create(self, validated_data):
        image = super().create(validated_data)
        
        # Trigger ML analysis only if available
        if ML_SERVICES_AVAILABLE:
            try:
                quality_assessment = quality_service.assess_quality(image.image.path)
                image.health_assessment = quality_assessment
                image.growth_stage = quality_assessment.get('quality_grade', 'Unknown')
                image.save()
            except Exception as e:
                print(f"Error in progress image ML analysis: {e}")
        else:
            # Set default values
            image.health_assessment = {'note': 'ML analysis unavailable'}
            image.growth_stage = 'Unknown'
            image.save()
        
        return image


class ContractProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for contract progress tracking
    """
    progress_images = ProgressImageSerializer(many=True, read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)

    class Meta:
        model = ContractProgress
        fields = '__all__'
        read_only_fields = ('predicted_completion_date', 'quality_trend')

    def create(self, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        progress = super().create(validated_data)
        
        # Update contract completion percentage
        contract = progress.contract
        contract.completion_percentage = progress.progress_percentage
        contract.save()
        
        return progress


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviews and ratings
    """
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.get_full_name', read_only=True)
    contract_details = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('reviewer', 'sentiment_score')

    def get_contract_details(self, obj):
        return {
            'contract_id': str(obj.contract.contract_id),
            'crop_name': obj.contract.listing.crop.name,
            'contract_value': obj.contract.total_contract_value
        }

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        
        # Determine reviewee based on reviewer
        contract = validated_data['contract']
        if self.context['request'].user == contract.farmer:
            validated_data['reviewee'] = contract.buyer
        else:
            validated_data['reviewee'] = contract.farmer
        
        review = super().create(validated_data)
        
        # Sentiment analysis would go here if ML was available
        # For now, set a neutral score
        review.sentiment_score = 0.0
        review.save()
        
        return review


class MarketPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for market price data
    """
    crop_name = serializers.CharField(source='crop.name', read_only=True)

    class Meta:
        model = MarketPrice
        fields = '__all__'


class MLModelSerializer(serializers.ModelSerializer):
    """
    Serializer for ML model tracking
    """
    class Meta:
        model = MLModel
        fields = '__all__'


class DashboardSerializer(serializers.Serializer):
    """
    Serializer for dashboard data
    """
    user_type = serializers.CharField()
    total_listings = serializers.IntegerField()
    active_contracts = serializers.IntegerField()
    completed_contracts = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=15, decimal_places=2)
    recent_activities = serializers.ListField()
    ml_insights = serializers.DictField()
    ml_available = serializers.BooleanField()


class PricePredictionSerializer(serializers.Serializer):
    """
    Serializer for price prediction requests
    """
    crop_id = serializers.IntegerField()
    location = serializers.CharField(max_length=255)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    season = serializers.CharField(max_length=20, default='current')


class QualityAssessmentSerializer(serializers.Serializer):
    """
    Serializer for quality assessment requests
    """
    image = serializers.ImageField()
    crop_type = serializers.CharField(max_length=100, required=False)


class YieldPredictionSerializer(serializers.Serializer):
    """
    Serializer for yield prediction requests
    """
    crop_id = serializers.IntegerField()
    land_size = serializers.DecimalField(max_digits=10, decimal_places=2)
    farming_type = serializers.CharField(max_length=20)
    location = serializers.CharField(max_length=255)
    images = serializers.ListField(child=serializers.ImageField(), required=False)