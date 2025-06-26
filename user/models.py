from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model for contract farming platform
    """
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    )
    
    # User type fields
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, blank=True, null=True)
    
    # Contact information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    # Location
    location = models.CharField(max_length=255, blank=True, null=True)
    
    # Status fields
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display() or 'No type'})"

    @property
    def is_farmer(self):
        return self.user_type == 'farmer'

    @property
    def is_buyer(self):
        return self.user_type == 'buyer'

    @property
    def has_profile(self):
        """Check if user has completed their profile"""
        if self.is_farmer:
            return hasattr(self, 'farmer_profile')
        elif self.is_buyer:
            return hasattr(self, 'buyer_profile')
        return False


class FarmerProfile(models.Model):
    """
    Optional profile for farmers - all fields are optional except user
    """
    FARMING_TYPE_CHOICES = (
        ('organic', 'Organic'),
        ('traditional', 'Traditional'),
        ('hydroponic', 'Hydroponic'),
        ('mixed', 'Mixed'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    
    # Farm details (all optional)
    land_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Land size in acres")
    farming_type = models.CharField(max_length=20, choices=FARMING_TYPE_CHOICES, blank=True, null=True)
    
    # Personal details (all optional)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    profile_picture = models.ImageField(upload_to='farmer_pictures/', blank=True, null=True)
    
    # Farm address (optional)
    farm_address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    
    # Additional details (optional)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    specializations = models.TextField(blank=True, null=True, help_text="Crops you specialize in")
    certifications = models.TextField(blank=True, null=True, help_text="Any farming certifications")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Farmer Profile - {self.user.username}"

    @property
    def completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = ['land_size', 'farming_type', 'aadhaar_number', 'farm_address', 'pincode', 'experience_years']
        filled_fields = sum(1 for field in fields if getattr(self, field))
        return (filled_fields / len(fields)) * 100


class BuyerProfile(models.Model):
    """
    Optional profile for buyers - all fields are optional except user
    """
    BUSINESS_TYPE_CHOICES = (
        ('wholesaler', 'Wholesaler'),
        ('exporter', 'Exporter'),
        ('retailer', 'Retailer'),
        ('processor', 'Food Processor'),
        ('restaurant', 'Restaurant/Hotel'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    
    # Business details (all optional)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, blank=True, null=True)
    
    # Business address (optional)
    business_address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    
    # Additional details (optional)
    company_logo = models.ImageField(upload_to='buyer_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    preferred_crops = models.TextField(blank=True, null=True, help_text="Types of crops you usually buy")
    
    # Contact person details (optional)
    contact_person_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person_designation = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Buyer Profile - {self.company_name or self.user.username}"

    @property
    def completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = ['company_name', 'gst_number', 'business_type', 'business_address', 'pincode', 'preferred_crops']
        filled_fields = sum(1 for field in fields if getattr(self, field))
        return (filled_fields / len(fields)) * 100