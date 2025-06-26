from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

class Category(models.Model):
    """
    Crop categories (e.g., Cereals, Pulses, Vegetables, Fruits)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Crop(models.Model):
    """
    Master crop data with ML-enhanced information
    """
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='crops')
    variety = models.CharField(max_length=100, blank=True, null=True)
    
    # Basic crop information
    scientific_name = models.CharField(max_length=200, blank=True, null=True)
    growing_season = models.CharField(max_length=100, blank=True, null=True)
    harvest_time_days = models.PositiveIntegerField(blank=True, null=True, help_text="Days to harvest")
    
    # ML-related fields
    average_yield_per_acre = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_market_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predicted_price_next_month = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_volatility_score = models.FloatField(blank=True, null=True, help_text="0-1 score indicating price volatility")
    
    # Quality parameters for ML
    ideal_temperature_min = models.FloatField(blank=True, null=True)
    ideal_temperature_max = models.FloatField(blank=True, null=True)
    ideal_rainfall_mm = models.FloatField(blank=True, null=True)
    soil_ph_min = models.FloatField(blank=True, null=True)
    soil_ph_max = models.FloatField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'variety']

    def __str__(self):
        return f"{self.name} ({self.variety})" if self.variety else self.name


class CropListing(models.Model):
    """
    Farmer's crop listing with ML-enhanced features
    """
    LISTING_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('in_negotiation', 'In Negotiation'),
        ('contracted', 'Contracted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    QUALITY_GRADES = (
        ('A+', 'Premium Quality'),
        ('A', 'High Quality'),
        ('B+', 'Good Quality'),
        ('B', 'Standard Quality'),
        ('C', 'Basic Quality'),
    )

    # Basic information
    listing_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_listings')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='listings')
    
    # Quantity and pricing
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in quintals")
    expected_price_per_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quality and condition
    quality_grade = models.CharField(max_length=2, choices=QUALITY_GRADES, blank=True, null=True)
    organic_certified = models.BooleanField(default=False)
    
    # Harvest information
    expected_harvest_date = models.DateField()
    is_harvested = models.BooleanField(default=False)
    actual_harvest_date = models.DateField(blank=True, null=True)
    
    # Location
    farm_location = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=LISTING_STATUS_CHOICES, default='draft')
    
    # ML-enhanced fields
    ai_quality_score = models.FloatField(blank=True, null=True, help_text="AI-predicted quality score (0-1)")
    ai_price_recommendation = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    market_demand_score = models.FloatField(blank=True, null=True, help_text="Market demand prediction (0-1)")
    
    # Media
    description = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crop.name} - {self.farmer.username} ({self.quantity_available} quintals)"

    @property
    def total_value(self):
        return self.quantity_available * self.expected_price_per_quintal


class CropImage(models.Model):
    """
    Images for crop listings with ML analysis
    """
    IMAGE_TYPES = (
        ('field', 'Field/Farm View'),
        ('crop_close', 'Crop Close-up'),
        ('sample', 'Sample'),
        ('harvest', 'Harvested Crop'),
    )

    listing = models.ForeignKey(CropListing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='crop_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES)
    
    # ML analysis results
    ai_quality_assessment = models.JSONField(blank=True, null=True, help_text="AI analysis results")
    predicted_yield = models.FloatField(blank=True, null=True)
    health_score = models.FloatField(blank=True, null=True, help_text="Crop health score (0-1)")
    ripeness_score = models.FloatField(blank=True, null=True, help_text="Ripeness score (0-1)")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.crop.name} - {self.image_type}"


class Contract(models.Model):
    """
    Contract between farmer and buyer
    """
    CONTRACT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    )

    PAYMENT_TERMS = (
        ('advance_full', '100% Advance'),
        ('advance_50', '50% Advance, 50% on Delivery'),
        ('advance_30', '30% Advance, 70% on Delivery'),
        ('on_delivery', '100% on Delivery'),
        ('post_delivery', 'Payment after Delivery'),
    )

    contract_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    listing = models.ForeignKey(CropListing, on_delete=models.CASCADE, related_name='contracts')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_contracts')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_contracts')
    
    # Contract terms
    agreed_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    agreed_price_per_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    total_contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Dates
    contract_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(blank=True, null=True)
    
    # Terms
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS)
    quality_requirements = models.TextField(blank=True, null=True)
    delivery_location = models.CharField(max_length=255)
    
    # Status
    status = models.CharField(max_length=15, choices=CONTRACT_STATUS_CHOICES, default='pending')
    
    # Progress tracking with ML
    completion_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    ai_risk_score = models.FloatField(blank=True, null=True, help_text="AI-predicted contract risk (0-1)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Contract {self.contract_id} - {self.listing.crop.name}"

    @property
    def days_until_delivery(self):
        from django.utils import timezone
        if self.expected_delivery_date:
            return (self.expected_delivery_date - timezone.now().date()).days
        return None


class ContractProgress(models.Model):
    """
    Track contract progress with image updates
    """
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='progress_updates')
    
    # Progress information
    update_date = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    notes = models.TextField(blank=True, null=True)
    
    # Images for ML analysis
    progress_images = models.ManyToManyField('ProgressImage', blank=True)
    
    # ML predictions
    predicted_completion_date = models.DateField(blank=True, null=True)
    quality_trend = models.CharField(max_length=20, blank=True, null=True)  # improving/stable/declining
    
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-update_date']

    def __str__(self):
        return f"{self.contract.contract_id} - {self.progress_percentage}% complete"


class ProgressImage(models.Model):
    """
    Images showing crop/contract progress
    """
    image = models.ImageField(upload_to='progress_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    
    # ML analysis
    growth_stage = models.CharField(max_length=50, blank=True, null=True)
    health_assessment = models.JSONField(blank=True, null=True)
    estimated_yield = models.FloatField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    """
    Reviews and ratings for completed contracts
    """
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 stars

    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    
    # Ratings
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    quality_rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    communication_rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    timeliness_rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    
    # Review content
    review_text = models.TextField(blank=True, null=True)
    would_recommend = models.BooleanField(default=True)
    
    # ML sentiment analysis
    sentiment_score = models.FloatField(blank=True, null=True, help_text="Sentiment analysis score (-1 to 1)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"


class MarketPrice(models.Model):
    """
    Historical and current market prices for ML training
    """
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='market_prices')
    location = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    
    # Price data
    price_per_quintal = models.DecimalField(max_digits=10, decimal_places=2)
    market_name = models.CharField(max_length=255)
    
    # Context data for ML
    date = models.DateField()
    season = models.CharField(max_length=20, blank=True, null=True)
    weather_condition = models.CharField(max_length=100, blank=True, null=True)
    demand_level = models.CharField(max_length=20, blank=True, null=True)  # high/medium/low
    
    # External factors
    festival_season = models.BooleanField(default=False)
    export_demand = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['crop', 'location', 'date', 'market_name']

    def __str__(self):
        return f"{self.crop.name} - ₹{self.price_per_quintal}/quintal ({self.date})"


class MLModel(models.Model):
    """
    Track ML models and their performance
    """
    MODEL_TYPES = (
        ('price_prediction', 'Price Prediction'),
        ('quality_assessment', 'Quality Assessment'),
        ('yield_prediction', 'Yield Prediction'),
        ('demand_forecasting', 'Demand Forecasting'),
        ('risk_assessment', 'Risk Assessment'),
    )

    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    
    # Model metadata
    accuracy = models.FloatField(blank=True, null=True)
    training_date = models.DateTimeField()
    model_file_path = models.CharField(max_length=500)
    
    # Performance metrics
    mae = models.FloatField(blank=True, null=True, help_text="Mean Absolute Error")
    rmse = models.FloatField(blank=True, null=True, help_text="Root Mean Square Error")
    r2_score = models.FloatField(blank=True, null=True, help_text="R-squared Score")
    
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} v{self.version} ({self.model_type})"