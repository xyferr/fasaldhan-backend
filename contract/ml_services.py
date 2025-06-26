# import numpy as np
# import pandas as pd
from django.conf import settings
import os
# import joblib
from datetime import datetime, timedelta
# import requests
# from PIL import Image
# import io
# import tensorflow as tf
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# from sklearn.preprocessing import StandardScaler
import json


class PricePredictionService:
    """
    ML service for crop price prediction - ML DISABLED
    """
    
    def __init__(self):
        # ML models disabled for now
        self.model = None
        self.scaler = None
        print("ML Price Prediction Service initialized without ML models")
    
    def load_model(self):
        """Load trained model and scaler - DISABLED"""
        pass
    
    def predict_price(self, crop_id, location, quantity, season='current'):
        """
        Predict crop price based on various factors - FALLBACK MODE
        """
        # Always use fallback prediction without ML
        return self._fallback_prediction(crop_id)
    
    def _prepare_features(self, crop_id, location, quantity, season):
        """Prepare features for ML model - DISABLED"""
        return []
    
    def _fallback_prediction(self, crop_id):
        """Fallback prediction when ML model is not available"""
        try:
            from .models import Crop, MarketPrice
            
            crop = Crop.objects.get(id=crop_id)
            recent_prices = MarketPrice.objects.filter(
                crop=crop,
                date__gte=datetime.now().date() - timedelta(days=30)
            ).values_list('price_per_quintal', flat=True)
            
            if recent_prices:
                # Simple average calculation without numpy
                prices_list = list(recent_prices)
                avg_price = sum(prices_list) / len(prices_list)
                return {
                    'predicted_price': round(avg_price, 2),
                    'confidence': 0.6,
                    'price_range': {
                        'min': round(avg_price * 0.85, 2),
                        'max': round(avg_price * 1.15, 2)
                    },
                    'method': 'historical_average'
                }
            
            base_price = crop.current_market_price or 100  # Default base price
            return {
                'predicted_price': base_price,
                'confidence': 0.3,
                'price_range': {
                    'min': round(base_price * 0.8, 2),
                    'max': round(base_price * 1.2, 2)
                },
                'method': 'base_price_estimation'
            }
        except Exception as e:
            print(f"Error in fallback prediction: {e}")
            return {
                'predicted_price': 100,
                'confidence': 0.1,
                'price_range': {'min': 80, 'max': 120},
                'method': 'default_fallback'
            }
    
    def _get_weather_score(self, location):
        """Get weather score for the location - SIMPLIFIED"""
        return 0.7
    
    def _get_demand_score(self, crop_id, season):
        """Calculate demand score based on historical data - SIMPLIFIED"""
        return 0.6
    
    def _season_to_numeric(self, season):
        """Convert season to numeric value"""
        season_map = {'spring': 1, 'summer': 2, 'monsoon': 3, 'winter': 4, 'current': 2.5}
        return season_map.get(season, 2.5)
    
    def _location_to_numeric(self, location):
        """Convert location to numeric value"""
        return hash(location) % 100 / 100
    
    def _calculate_confidence(self, features):
        """Calculate prediction confidence - SIMPLIFIED"""
        return 0.6


class QualityAssessmentService:
    """
    ML service for crop quality assessment from images - ML DISABLED
    """
    
    def __init__(self):
        # ML models disabled
        self.model = None
        print("Quality Assessment Service initialized without ML models")
    
    def load_model(self):
        """Load trained CNN model - DISABLED"""
        pass
    
    def assess_quality(self, image_path):
        """
        Assess crop quality from image - FALLBACK MODE
        """
        # Always use fallback assessment
        return self._fallback_assessment()
    
    def _preprocess_image(self, image_path):
        """Preprocess image for model input - DISABLED"""
        pass
    
    def _score_to_grade(self, score):
        """Convert quality score to grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        else:
            return 'C'
    
    def _get_recommendations(self, score):
        """Get recommendations based on quality score"""
        if score >= 0.8:
            return ["Good quality detected!", "Consider premium pricing."]
        elif score >= 0.6:
            return ["Average quality.", "Suitable for standard markets."]
        else:
            return ["Manual quality assessment recommended."]
    
    def _fallback_assessment(self):
        """Fallback assessment when ML model is not available"""
        # Generate a reasonable default assessment
        default_score = 0.75  # Default quality score
        return {
            'quality_score': default_score,
            'ripeness_score': default_score,
            'quality_grade': self._score_to_grade(default_score),
            'health_indicators': {
                'color_uniformity': 0.7,
                'size_consistency': 0.7,
                'defect_level': 0.3
            },
            'recommendations': ["Manual assessment recommended.", "Upload clear images for better analysis."],
            'method': 'default_assessment'
        }


class YieldPredictionService:
    """
    ML service for crop yield prediction - SIMPLIFIED
    """
    
    def __init__(self):
        print("Yield Prediction Service initialized without ML models")
    
    def predict_yield(self, crop_id, land_size, farming_type, location, images=None):
        """
        Predict crop yield based on various factors - SIMPLIFIED CALCULATION
        """
        try:
            from .models import Crop
            
            crop = Crop.objects.get(id=crop_id)
            base_yield = crop.average_yield_per_acre or 10  # Default 10 quintals per acre
            
            # Adjust based on farming type
            farming_multiplier = {
                'organic': 0.8,
                'traditional': 1.0,
                'hydroponic': 1.5,
                'mixed': 1.1
            }.get(farming_type, 1.0)
            
            # Simple location and weather factors
            location_factor = 1.0  # Simplified
            weather_factor = 1.0   # Simplified
            image_factor = 1.0     # No image analysis
            
            predicted_yield = (
                base_yield * 
                land_size * 
                farming_multiplier * 
                location_factor * 
                weather_factor * 
                image_factor
            )
            
            return {
                'predicted_yield': round(predicted_yield, 2),
                'yield_per_acre': round(predicted_yield / land_size, 2) if land_size > 0 else 0,
                'confidence': 0.5,  # Lower confidence without ML
                'factors': {
                    'farming_type_factor': farming_multiplier,
                    'location_factor': location_factor,
                    'weather_factor': weather_factor,
                    'image_factor': image_factor
                },
                'method': 'simplified_calculation'
            }
        except Exception as e:
            print(f"Error in yield prediction: {e}")
            return {
                'predicted_yield': 0, 
                'confidence': 0,
                'method': 'error_fallback'
            }
    
    def _get_location_yield_factor(self, location):
        """Get yield factor based on location - SIMPLIFIED"""
        return 1.0
    
    def _get_weather_yield_factor(self, location):
        """Get yield factor based on weather conditions - SIMPLIFIED"""
        return 1.0
    
    def _assess_crop_health_from_images(self, images):
        """Assess crop health from field images - DISABLED"""
        return 1.0  # Default factor


class ContractRiskAssessment:
    """
    ML service for contract risk assessment - SIMPLIFIED
    """
    
    def __init__(self):
        print("Contract Risk Assessment initialized without ML models")
    
    def assess_contract_risk(self, contract):
        """
        Assess risk factors for a contract - SIMPLIFIED LOGIC
        """
        try:
            risk_factors = {
                'farmer_reliability': self._assess_farmer_reliability(contract.farmer),
                'buyer_reliability': self._assess_buyer_reliability(contract.buyer),
                'crop_volatility': self._assess_crop_volatility(contract.listing.crop),
                'weather_risk': 0.3,  # Fixed moderate risk
                'market_risk': 0.4,   # Fixed moderate risk
                'quantity_risk': self._assess_quantity_risk(contract.agreed_quantity, contract.listing.quantity_available)
            }
            
            # Calculate overall risk score
            weights = {
                'farmer_reliability': 0.25,
                'buyer_reliability': 0.20,
                'crop_volatility': 0.15,
                'weather_risk': 0.15,
                'market_risk': 0.15,
                'quantity_risk': 0.10
            }
            
            overall_risk = sum(
                risk_factors[factor] * weights[factor] 
                for factor in risk_factors
            )
            
            return {
                'overall_risk_score': round(overall_risk, 3),
                'risk_level': self._categorize_risk(overall_risk),
                'risk_factors': risk_factors,
                'recommendations': self._get_risk_recommendations(overall_risk, risk_factors),
                'method': 'simplified_assessment'
            }
        except Exception as e:
            print(f"Error in contract risk assessment: {e}")
            return {
                'overall_risk_score': 0.5, 
                'risk_level': 'medium',
                'method': 'error_fallback'
            }
    
    def _assess_farmer_reliability(self, farmer):
        """Assess farmer reliability based on history"""
        try:
            completed_contracts = farmer.farmer_contracts.filter(status='completed').count()
            total_contracts = farmer.farmer_contracts.count()
            
            if total_contracts == 0:
                return 0.5  # Neutral for new farmers
            
            completion_rate = completed_contracts / total_contracts
            
            # Simple reliability calculation without complex ML
            reliability_score = completion_rate * 0.8 + 0.2  # Give some benefit of doubt
            return 1 - reliability_score  # Convert to risk score
        except Exception as e:
            print(f"Error assessing farmer reliability: {e}")
            return 0.5
    
    def _assess_buyer_reliability(self, buyer):
        """Assess buyer reliability"""
        try:
            completed_contracts = buyer.buyer_contracts.filter(status='completed').count()
            total_contracts = buyer.buyer_contracts.count()
            
            if total_contracts == 0:
                return 0.5
            
            completion_rate = completed_contracts / total_contracts
            return 1 - (completion_rate * 0.8 + 0.2)
        except Exception as e:
            print(f"Error assessing buyer reliability: {e}")
            return 0.5
    
    def _assess_crop_volatility(self, crop):
        """Assess crop price volatility"""
        return crop.price_volatility_score or 0.5
    
    def _assess_quantity_risk(self, contracted_quantity, available_quantity):
        """Assess risk related to quantity commitments"""
        try:
            if available_quantity == 0:
                return 1.0
            
            ratio = contracted_quantity / available_quantity
            if ratio > 1:
                return min(ratio - 1, 1.0)  # Over-commitment risk
            return 0.1  # Low risk
        except Exception as e:
            print(f"Error assessing quantity risk: {e}")
            return 0.5
    
    def _categorize_risk(self, risk_score):
        """Categorize risk score"""
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.6:
            return 'medium'
        else:
            return 'high'
    
    def _get_risk_recommendations(self, overall_risk, risk_factors):
        """Get recommendations based on risk assessment"""
        recommendations = []
        
        if overall_risk > 0.7:
            recommendations.append("High risk contract - consider additional safeguards")
        
        if risk_factors.get('farmer_reliability', 0) > 0.6:
            recommendations.append("Farmer has limited track record - consider milestone payments")
        
        if risk_factors.get('quantity_risk', 0) > 0.5:
            recommendations.append("High quantity commitment - ensure adequate supply")
        
        if not recommendations:
            recommendations.append("Moderate risk contract - proceed with standard terms")
        
        return recommendations


# Initialize services (without heavy ML dependencies)
price_service = PricePredictionService()
quality_service = QualityAssessmentService()
yield_service = YieldPredictionService()
risk_service = ContractRiskAssessment()