#!/usr/bin/env python3
"""
Real-time Food Analysis Module
Enhanced food detection with Roboflow API priority
"""

import os
import base64
import requests
import time
from typing import Dict, Any, List
from PIL import Image
import io


class FoodDetector:
    """Enhanced food detection prioritizing Roboflow API"""
    
    def __init__(self):
        self.roboflow_api_key = os.environ.get('ROBOFLOW_API_KEY', 'CDxqqcJkI8wWdBX4IVrl')
        self.roboflow_model_url = "https://detect.roboflow.com/food-recognition/1"
        
    def detect_food(self, image_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Detect food using Roboflow API with high accuracy
        """
        if progress_callback:
            progress_callback(5, {'stage': 'loading_image', 'message': 'Loading image...'})
        
        # Always try Roboflow API first
        roboflow_result = self._detect_with_roboflow(image_path, progress_callback)
        
        if roboflow_result['success']:
            return roboflow_result
        
        # Only if Roboflow completely fails, use fallback
        if progress_callback:
            progress_callback(40, {'stage': 'fallback', 'message': 'Using fallback detection...'})
        
        return self._fallback_detection(image_path)
    
    def _detect_with_roboflow(self, image_path: str, progress_callback=None) -> Dict[str, Any]:
        """Detect food using Roboflow API"""
        try:
            if progress_callback:
                progress_callback(10, {'stage': 'encoding_image', 'message': 'Encoding image for analysis...'})
            
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            if progress_callback:
                progress_callback(20, {'stage': 'calling_api', 'message': 'Sending to Roboflow AI...'})
            
            # Make API request
            response = requests.post(
                f"{self.roboflow_model_url}?api_key={self.roboflow_api_key}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=image_data,
                timeout=15
            )
            
            if progress_callback:
                progress_callback(40, {'stage': 'processing_response', 'message': 'Processing detection results...'})
            
            if response.status_code == 200:
                result = response.json()
                predictions = result.get('predictions', [])
                
                if predictions:
                    # Sort by confidence
                    sorted_predictions = sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)
                    
                    # Get best prediction
                    best_prediction = sorted_predictions[0]
                    food_name = best_prediction.get('class', 'unknown food')
                    confidence = best_prediction.get('confidence', 0)
                    
                    # Get alternatives
                    alternatives = []
                    for pred in sorted_predictions[1:4]:
                        alternatives.append({
                            'name': pred.get('class', 'unknown'),
                            'confidence': round(pred.get('confidence', 0) * 100, 1)
                        })
                    
                    print(f"✅ Roboflow detected: {food_name} ({confidence:.2%} confidence)")
                    
                    return {
                        'success': True,
                        'method': 'roboflow_api',
                        'food_name': self._normalize_food_name(food_name),
                        'confidence': confidence,
                        'confidence_percent': round(confidence * 100, 1),
                        'alternatives': alternatives,
                        'raw_predictions': sorted_predictions[:5]
                    }
                else:
                    print("⚠️ No predictions from Roboflow")
            else:
                print(f"⚠️ Roboflow API error: Status {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("❌ Roboflow API timeout")
        except Exception as e:
            print(f"❌ Roboflow API error: {e}")
        
        return {'success': False, 'method': 'roboflow_api'}
    
    def _fallback_detection(self, image_path: str) -> Dict[str, Any]:
        """Fallback detection when API fails"""
        try:
            # Try color-based detection
            img = Image.open(image_path)
            img = img.convert('RGB')
            img_small = img.resize((100, 100))
            pixels = list(img_small.getdata())
            
            # Average color
            avg_color = [
                sum(p[0] for p in pixels) // len(pixels),
                sum(p[1] for p in pixels) // len(pixels),
                sum(p[2] for p in pixels) // len(pixels)
            ]
            
            r, g, b = avg_color
            
            # Basic color detection
            if r > 160 and g < 100 and b < 100:
                food_guess = 'tomato'
            elif r > 200 and g > 150 and b < 100:
                food_guess = 'orange'
            elif r < 100 and g > 150 and b < 100:
                food_guess = 'salad'
            elif r > 180 and g > 140 and b < 100:
                food_guess = 'burger'
            elif r > 200 and g > 180 and b < 120:
                food_guess = 'fries'
            else:
                food_guess = 'mixed food'
            
            print(f"⚠️ Using fallback detection: {food_guess}")
            
            return {
                'success': True,
                'method': 'color_fallback',
                'food_name': food_guess,
                'confidence': 0.4,
                'confidence_percent': 40,
                'alternatives': [],
                'note': 'Roboflow API unavailable. Using basic detection.'
            }
            
        except Exception as e:
            print(f"❌ Fallback detection failed: {e}")
            return {
                'success': True,
                'method': 'emergency_fallback',
                'food_name': 'mixed food',
                'confidence': 0.3,
                'confidence_percent': 30,
                'alternatives': [],
                'note': 'Could not detect food accurately.'
            }
    
    def _normalize_food_name(self, food_name: str) -> str:
        """Normalize food name to match database"""
        food_lower = food_name.lower().strip()
        
        # Common mappings
        mappings = {
            'hamburger': 'burger',
            'cheeseburger': 'burger',
            'french fries': 'fries',
            'fried chicken': 'chicken',
            'grilled chicken': 'chicken',
            'ice-cream': 'ice cream',
            'doughnut': 'donut',
            'spaghetti': 'pasta',
            'noodles': 'pasta',
            'green salad': 'salad',
            'fruit salad': 'salad',
            'soft drink': 'soda',
            'pop': 'soda',
            'potato chips': 'chips',
            'crisps': 'chips'
        }
        
        # Check mappings
        for key, value in mappings.items():
            if key in food_lower:
                return value
        
        return food_lower
    
    def get_multiple_detections(self, image_path: str) -> List[Dict[str, Any]]:
        """Get multiple food detections from image"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = requests.post(
                f"{self.roboflow_model_url}?api_key={self.roboflow_api_key}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=image_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                predictions = result.get('predictions', [])
                
                detections = []
                for pred in predictions:
                    if pred.get('confidence', 0) > 0.4:
                        detections.append({
                            'food_name': self._normalize_food_name(pred.get('class', 'unknown')),
                            'confidence': pred.get('confidence', 0),
                            'confidence_percent': round(pred.get('confidence', 0) * 100, 1),
                            'bbox': {
                                'x': pred.get('x', 0),
                                'y': pred.get('y', 0),
                                'width': pred.get('width', 0),
                                'height': pred.get('height', 0)
                            }
                        })
                
                return detections
        
        except Exception as e:
            print(f"❌ Multiple detection error: {e}")
        
        return []


class RealTimeFoodAnalyzer:
    """Complete real-time food analysis system"""
    
    def __init__(self):
        self.detector = FoodDetector()
    
    def analyze(self, image_path: str, progress_callback=None) -> Dict[str, Any]:
        """Complete food analysis with real-time updates"""
        start_time = time.time()
        
        if progress_callback:
            progress_callback(0, {'stage': 'starting', 'message': 'Starting analysis...'})
        
        # Detect food
        detection_result = self.detector.detect_food(image_path, progress_callback)
        
        # Check for multiple foods
        if progress_callback:
            progress_callback(45, {'stage': 'checking_multiple', 'message': 'Checking for multiple items...'})
        
        multiple_detections = self.detector.get_multiple_detections(image_path)
        
        if progress_callback:
            progress_callback(50, {'stage': 'preparing_results', 'message': 'Finalizing detection...'})
        
        analysis_time = round(time.time() - start_time, 2)
        
        result = {
            'detection': detection_result,
            'multiple_items': multiple_detections if len(multiple_detections) > 1 else [],
            'analysis_time': analysis_time,
            'timestamp': time.time()
        }
        
        if progress_callback:
            progress_callback(50, {
                'stage': 'detection_complete', 
                'message': f'Detected: {detection_result["food_name"].title()} ({detection_result["confidence_percent"]}%)'
            })
        
        return result
