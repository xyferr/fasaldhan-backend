from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'crops', views.CropViewSet)
router.register(r'listings', views.CropListingViewSet)
router.register(r'contracts', views.ContractViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Dashboard and analytics
    path('dashboard/', views.dashboard_data, name='dashboard'),
    path('market-trends/', views.market_trends, name='market-trends'),
    
    # ML endpoints
    path('ml/predict-price/', views.predict_price, name='predict-price'),
    path('ml/assess-quality/', views.assess_quality, name='assess-quality'),
    path('ml/predict-yield/', views.predict_yield, name='predict-yield'),
]