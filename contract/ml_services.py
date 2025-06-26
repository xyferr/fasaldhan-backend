import numpy as np
import pandas as pd
from django.conf import settings
import os
import joblib
from datetime import datetime, timedelta
import requests
from PIL import Image
import io
import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import json


class PricePredictionService:
    """
    ML service for crop price prediction
    """
    
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'price_prediction.joblib')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'price_scaler.joblib')
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load trained model and scaler"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
        except Exception as e:
            print(f"Error loading price prediction model: {e}")
    
    def predict_price(self, crop_id, location, quantity, season='current'):
        """
        Predict crop price based on various factors
        """
        if not self.model:
            return self._fallback_prediction(crop_id)
        
        try:
            # Get historical data
            features = self._prepare_features(crop_id, location, quantity, season)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict
            predicted_price = self.model.predict(features_scaled)[0]
            
            # Get confidence interval
            confidence = self._calculate_confidence(features)
            
            return {
                'predicted_price': round(predicted_price, 2),
                'confidence': confidence,
                'price_range': {
                    'min': round(predicted_price * 0.9, 2),
                    'max': round(predicted_price * 1.1, 2)
                }
            }
        except Exception as e:
            print(f"Error in price prediction: {e}")
            return self._fallback_prediction(crop_id)
    
    def _prepare_features(self, crop_id, location, quantity, season):
        """Prepare features for ML model"""
        from .models import Crop, MarketPrice
        
        # Get crop data
        crop = Crop.objects.get(id=crop_id)
        
        # Historical price data
        recent_prices = MarketPrice.objects.filter(
            crop=crop,
            date__gte=datetime.now().date() - timedelta(days=90)
        ).values_list('price_per_quintal', flat=True)
        
        avg_recent_price = np.mean(list(recent_prices)) if recent_prices else crop.current_market_price or 0
        
        # Weather data (you can integrate with weather APIs)
        weather_score = self._get_weather_score(location)
        
        # Market demand (can be enhanced with more data)
        demand_score = self._get_demand_score(crop_id, season)
        
        features = [
            float(crop.average_yield_per_acre or 0),
            float(avg_recent_price),
            float(quantity),
            weather_score,
            demand_score,
            self._season_to_numeric(season),
            self._location_to_numeric(location)
        ]
        
        return features
    
    def _fallback_prediction(self, crop_id):
        """Fallback prediction when ML model is not available"""
        from .models import Crop, MarketPrice
        
        crop = Crop.objects.get(id=crop_id)
        recent_prices = MarketPrice.objects.filter(
            crop=crop,
            date__gte=datetime.now().date() - timedelta(days=30)
        ).values_list('price_per_quintal', flat=True)
        
        if recent_prices:
            avg_price = np.mean(list(recent_prices))
            return {
                'predicted_price': round(avg_price, 2),
                'confidence': 0.6,
                'price_range': {
                    'min': round(avg_price * 0.85, 2),
                    'max': round(avg_price * 1.15, 2)
                }
            }
        
        return {
            'predicted_price': crop.current_market_price or 0,
            'confidence': 0.3,
            'price_range': {
                'min': 0,
                'max': (crop.current_market_price or 0) * 2
            }
        }
    
    def _get_weather_score(self, location):
        """Get weather score for the location"""
        # Integrate with weather API (OpenWeatherMap, etc.)
        # For now, return a dummy score
        return 0.7
    
    def _get_demand_score(self, crop_id, season):
        """Calculate demand score based on historical data"""
        # This can be enhanced with actual market data
        return 0.6
    
    def _season_to_numeric(self, season):
        """Convert season to numeric value"""
        season_map = {'spring': 1, 'summer': 2, 'monsoon': 3, 'winter': 4, 'current': 2.5}
        return season_map.get(season, 2.5)
    
    def _location_to_numeric(self, location):
        """Convert location to numeric value (can use lat/lon)"""
        # Simple hash-based approach, can be improved
        return hash(location) % 100 / 100
    
    def _calculate_confidence(self, features):
        """Calculate prediction confidence"""
        # Simple confidence calculation, can be improved
        return 0.75


class QualityAssessmentService:
    """
    ML service for crop quality assessment from images
    """
    
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'quality_model.h5')
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load trained CNN model"""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
        except Exception as e:
            print(f"Error loading quality assessment model: {e}")
    
    def assess_quality(self, image_path):
        """
        Assess crop quality from image
        """
        if not self.model:
            return self._fallback_assessment()
        
        try:
            # Preprocess image
            image = self._preprocess_image(image_path)
            
            # Predict
            prediction = self.model.predict(image)
            
            # Extract quality metrics
            quality_score = float(prediction[0][0])
            ripeness_score = float(prediction[0][1]) if len(prediction[0]) > 1 else quality_score
            
            # Classify quality grade
            quality_grade = self._score_to_grade(quality_score)
            
            return {
                'quality_score': round(quality_score, 3),
                'ripeness_score': round(ripeness_score, 3),
                'quality_grade': quality_grade,
                'health_indicators': {
                    'color_uniformity': round(quality_score * 0.9, 3),
                    'size_consistency': round(quality_score * 0.85, 3),
                    'defect_level': round((1 - quality_score) * 0.7, 3)
                },
                'recommendations': self._get_recommendations(quality_score)
            }
        except Exception as e:
            print(f"Error in quality assessment: {e}")
            return self._fallback_assessment()
    
    def _preprocess_image(self, image_path):
        """Preprocess image for model input"""
        image = Image.open(image_path)
        image = image.resize((224, 224))  # Standard input size
        image_array = np.array(image) / 255.0
        return np.expand_dims(image_array, axis=0)
    
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
            return ["Excellent quality! Consider premium pricing.", "Perfect for export markets."]
        elif score >= 0.6:
            return ["Good quality.", "Suitable for domestic markets.", "Consider minor improvements."]
        else:
            return ["Quality needs improvement.", "Consider better farming practices.", "May need processing."]
    
    def _fallback_assessment(self):
        """Fallback assessment when ML model is not available"""
        return {
            'quality_score': 0.7,
            'ripeness_score': 0.7,
            'quality_grade': 'B+',
            'health_indicators': {
                'color_uniformity': 0.7,
                'size_consistency': 0.7,
                'defect_level': 0.3
            },
            'recommendations': ["Manual assessment recommended."]
        }


class YieldPredictionService:
    """
    ML service for crop yield prediction
    """
    
    def predict_yield(self, crop_id, land_size, farming_type, location, images=None):
        """
        Predict crop yield based on various factors
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
            
            # Weather and location factors
            location_factor = self._get_location_yield_factor(location)
            weather_factor = self._get_weather_yield_factor(location)
            
            # Image-based assessment if available
            image_factor = 1.0
            if images:
                image_factor = self._assess_crop_health_from_images(images)
            
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
                'confidence': 0.7,
                'factors': {
                    'farming_type_factor': farming_multiplier,
                    'location_factor': location_factor,
                    'weather_factor': weather_factor,
                    'image_factor': image_factor
                }
            }
        except Exception as e:
            print(f"Error in yield prediction: {e}")
            return {'predicted_yield': 0, 'confidence': 0}
    
    def _get_location_yield_factor(self, location):
        """Get yield factor based on location"""
        # This can be enhanced with actual geographic and soil data
        return 1.0
    
    def _get_weather_yield_factor(self, location):
        """Get yield factor based on weather conditions"""
        # Integrate with weather APIs
        return 1.0
    
    def _assess_crop_health_from_images(self, images):
        """Assess crop health from field images"""
        # Use the quality assessment service
        quality_service = QualityAssessmentService()
        total_health = 0
        count = 0
        
        for image in images:
            assessment = quality_service.assess_quality(image.image.path)
            total_health += assessment['quality_score']
            count += 1
        
        return total_health / count if count > 0 else 1.0


class ContractRiskAssessment:
    """
    ML service for contract risk assessment
    """
    
    def assess_contract_risk(self, contract):
        """
        Assess risk factors for a contract
        """
        try:
            risk_factors = {
                'farmer_reliability': self._assess_farmer_reliability(contract.farmer),
                'buyer_reliability': self._assess_buyer_reliability(contract.buyer),
                'crop_volatility': self._assess_crop_volatility(contract.listing.crop),
                'weather_risk': self._assess_weather_risk(contract.listing.farm_location),
                'market_risk': self._assess_market_risk(contract.listing.crop),
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
                'recommendations': self._get_risk_recommendations(overall_risk, risk_factors)
            }
        except Exception as e:
            print(f"Error in contract risk assessment: {e}")
            return {'overall_risk_score': 0.5, 'risk_level': 'medium'}
    
    def _assess_farmer_reliability(self, farmer):
        """Assess farmer reliability based on history"""
        # Check past contract performance
        completed_contracts = farmer.farmer_contracts.filter(status='completed').count()
        total_contracts = farmer.farmer_contracts.count()
        
        if total_contracts == 0:
            return 0.5  # Neutral for new farmers
        
        completion_rate = completed_contracts / total_contracts
        
        # Check average ratings
        from .models import Review
        reviews = Review.objects.filter(reviewee=farmer)
        avg_rating = reviews.aggregate(avg=models.Avg('overall_rating'))['avg'] or 3.0
        
        reliability_score = (completion_rate * 0.7) + ((avg_rating / 5.0) * 0.3)
        return 1 - reliability_score  # Convert to risk score (lower is better)
    
    def _assess_buyer_reliability(self, buyer):
        """Assess buyer reliability"""
        # Similar to farmer reliability
        completed_contracts = buyer.buyer_contracts.filter(status='completed').count()
        total_contracts = buyer.buyer_contracts.count()
        
        if total_contracts == 0:
            return 0.5
        
        completion_rate = completed_contracts / total_contracts
        return 1 - completion_rate
    
    def _assess_crop_volatility(self, crop):
        """Assess crop price volatility"""
        return crop.price_volatility_score or 0.5
    
    def _assess_weather_risk(self, location):
        """Assess weather-related risks"""
        # This can be enhanced with historical weather data
        return 0.3
    
    def _assess_market_risk(self, crop):
        """Assess market-related risks"""
        # Based on market trends and demand
        return 0.4
    
    def _assess_quantity_risk(self, contracted_quantity, available_quantity):
        """Assess risk related to quantity commitments"""
        if available_quantity == 0:
            return 1.0
        
        ratio = contracted_quantity / available_quantity
        if ratio > 1:
            return min(ratio - 1, 1.0)  # Over-commitment risk
        return 0.1  # Low risk
    
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
        
        if risk_factors.get('weather_risk', 0) > 0.6:
            recommendations.append("High weather risk - consider crop insurance")
        
        if not recommendations:
            recommendations.append("Low risk contract - proceed with standard terms")
        
        return recommendations


# Initialize ML services
price_service = PricePredictionService()
quality_service = QualityAssessmentService()
yield_service = YieldPredictionService()
risk_service = ContractRiskAssessment()