from django.contrib import admin
from .models import (
    Category, Crop, CropListing, CropImage, Contract, 
    ContractProgress, ProgressImage, Review, MarketPrice, MLModel
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'variety', 'category', 'current_market_price', 'created_at']
    list_filter = ['category', 'growing_season']
    search_fields = ['name', 'variety', 'scientific_name']

@admin.register(CropListing)
class CropListingAdmin(admin.ModelAdmin):
    list_display = ['crop', 'farmer', 'quantity_available', 'expected_price_per_quintal', 'status', 'created_at']
    list_filter = ['status', 'organic_certified', 'quality_grade']
    search_fields = ['crop__name', 'farmer__username', 'farm_location']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_id', 'listing', 'buyer', 'farmer', 'total_contract_value', 'status', 'created_at']
    list_filter = ['status', 'payment_terms']
    search_fields = ['contract_id', 'buyer__username', 'farmer__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'overall_rating', 'would_recommend', 'created_at']
    list_filter = ['overall_rating', 'would_recommend']

admin.site.register(CropImage)
admin.site.register(ContractProgress)
admin.site.register(ProgressImage)
admin.site.register(MarketPrice)
admin.site.register(MLModel)