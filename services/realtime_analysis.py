#!/usr/bin/env python3
"""
Real-time Food Analysis Module
Enhanced food detection with better accuracy and real-time feedback
"""

import os
import base64
import requests
import time
from typing import Dict, Any, List, Optional
from PIL import Image
import io


class FoodDetector:
    """Enhanced food detection with multiple methods"""
    
    def __init__(self):
        self.roboflow_api_key = os.environ.get('ROBOFLOW_API_KEY', 'CDxqqcJkI8wWdBX4IVrl')
        self.roboflow_model_url = "https://detect.roboflow.com/food-recognition/1"
        
        # Comprehensive food database for fallback detection
        self.food_keywords = {
            # Fruits
            'apple': ['apple', 'apples', 'red apple', 'green apple'],
            'banana': ['banana', 'bananas', 'plantain'],
            'orange': ['orange', 'oranges', 'mandarin', 'tangerine'],
            'grape': ['grape', 'grapes'],
            'strawberry': ['strawberry', 'strawberries'],
            'watermelon': ['watermelon', 'melon'],
            'mango': ['mango', 'mangoes'],
            
            # Vegetables
            'broccoli': ['broccoli'],
            'carrot': ['carrot', 'carrots'],
            'tomato': ['tomato', 'tomatoes', 'cherry tomato'],
            'lettuce': ['lettuce', 'salad', 'green salad'],
            'potato': ['potato', 'potatoes', 'fries', 'french fries'],
            
            # Proteins
            'chicken': ['chicken', 'poultry', 'fried chicken', 'grilled chicken'],
            'beef': ['beef', 'steak', 'meat', 'hamburger'],
            'fish': ['fish', 'salmon', 'tuna', 'seafood'],
            'egg': ['egg', 'eggs', 'omelet', 'omelette'],
            
            # Grains & Carbs
            'rice': ['rice', 'fried rice', 'white rice', 'brown rice'],
            'bread': ['bread', 'toast', 'baguette', 'sandwich'],
            'pasta': ['pasta', 'spaghetti', 'noodles', 'noodle'],
            'pizza': ['pizza'],
            
            # Fast Food
            'burger': ['burger', 'hamburger', 'cheeseburger'],
            'hot dog': ['hot dog', 'hotdog'],
            'fries': ['fries', 'french fries'],
            
            # Desserts
            'cake': ['cake', 'cupcake'],
            'cookie': ['cookie', 'cookies', 'biscuit'],
            'ice cream': ['ice cream', 'icecream', 'gelato'],
            'donut': ['donut', 'doughnut'],
            'chocolate': ['chocolate']
        }
    
    def detect_food(self, image_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Detect food with multiple methods for better accuracy
        """
        if progress_callback:
            progress_callback(5, {'stage': 'loading_image', 'message': 'Loading image...'})
        
        # Try Roboflow API first
        roboflow_result = self._detect_with_roboflow(image_path, progress_callback)
        
        if roboflow_result['success'] and roboflow_result['confidence'] > 0.6:
            return roboflow_result
        
        # Fallback: Try filename analysis
        if progress_callback:
            progress_callback(35, {'stage': 'analyzing_filename', 'message': 'Analyzing filename...'})
        
        filename_result = self._detect_from_filename(image_path)
        
        if filename_result['success']:
            return filename_result
        
        # Final fallback: Image analysis
        if progress_callback:
            progress_callback(38, {'stage': 'image_analysis', 'message': 'Analyzing image properties...'})
        
        return self._detect_from_image_properties(image_path)
    
    def _detect_with_roboflow(self, image_path: str, progress_callback=None) -> Dict[str, Any]:
        """Detect food using Roboflow API"""
        try:
            if progress_callback:
                progress_callback(10, {'stage': 'encoding_image', 'message': 'Encoding image...'})
            
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            if progress_callback:
                progress_callback(20, {'stage': 'calling_api', 'message': 'Calling Roboflow API...'})
            
            # Make API request
            response = requests.post(
                f"{self.roboflow_model_url}?api_key={self.roboflow_api_key}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=image_data,
                timeout=10
            )
            
            if progress_callback:
                progress_callback(35, {'stage': 'processing_response', 'message': 'Processing API response...'})
            
            if response.status_code == 200:
                result = response.json()
                predictions = result.get('predictions', [])
                
                if predictions:
                    # Get all predictions sorted by confidence
                    sorted_predictions = sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)
                    
                    # Get top prediction
                    best_prediction = sorted_predictions[0]
                    food_name = best_prediction.get('class', 'unknown food')
                    confidence = best_prediction.get('confidence', 0)
                    
                    # Get alternative predictions
                    alternatives = []
                    for pred in sorted_predictions[1:4]:  # Get top 3 alternatives
                        alternatives.append({
                            'name': pred.get('class', 'unknown'),
                            'confidence': round(pred.get('confidence', 0) * 100, 1)
                        })
                    
                    print(f"✅ Roboflow detected: {food_name} (confidence: {confidence:.2%})")
                    
                    return {
                        'success': True,
                        'method': 'roboflow_api',
                        'food_name': self._normalize_food_name(food_name),
                        'confidence': confidence,
                        'confidence_percent': round(confidence * 100, 1),
                        'alternatives': alternatives,
                        'raw_predictions': sorted_predictions[:5]
                    }
            
            print(f"⚠️ Roboflow API returned status {response.status_code}")
            
        except Exception as e:
            print(f"❌ Roboflow API error: {e}")
        
        return {'success': False, 'method': 'roboflow_api'}
    
    def _detect_from_filename(self, image_path: str) -> Dict[str, Any]:
        """Detect food from filename"""
        try:
            filename = os.path.basename(image_path).lower()
            filename_no_ext = os.path.splitext(filename)[0]
            
            # Remove common prefixes/suffixes
            filename_clean = filename_no_ext.replace('_', ' ').replace('-', ' ')
            
            # Check against food keywords
            for food_name, keywords in self.food_keywords.items():
                for keyword in keywords:
                    if keyword in filename_clean:
                        print(f"✅ Detected from filename: {food_name}")
                        return {
                            'success': True,
                            'method': 'filename_analysis',
                            'food_name': food_name,
                            'confidence': 0.7,
                            'confidence_percent': 70,
                            'alternatives': []
                        }
            
        except Exception as e:
            print(f"⚠️ Filename analysis error: {e}")
        
        return {'success': False, 'method': 'filename_analysis'}
    
    def _detect_from_image_properties(self, image_path: str) -> Dict[str, Any]:
        """Detect food from image properties (color analysis)"""
        try:
            # Open image
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            # Get dominant colors
            img_small = img.resize((50, 50))
            pixels = list(img_small.getdata())
            
            # Calculate average color
            avg_color = [
                sum(p[0] for p in pixels) // len(pixels),
                sum(p[1] for p in pixels) // len(pixels),
                sum(p[2] for p in pixels) // len(pixels)
            ]
            
            # Guess food based on color
            r, g, b = avg_color
            
            # Simple color-based detection
            if r > 150 and g < 100 and b < 100:
                food_guess = 'tomato'  # Red
            elif r > 200 and g > 150 and b < 100:
                food_guess = 'orange'  # Orange
            elif r < 100 and g > 150 and b < 100:
                food_guess = 'salad'  # Green
            elif r > 150 and g > 100 and b < 80:
                food_guess = 'chicken'  # Brown/Orange
            else:
                food_guess = 'mixed food'  # Default
            
            print(f"ℹ️ Color-based guess: {food_guess}")
            
            return {
                'success': True,
                'method': 'color_analysis',
                'food_name': food_guess,
                'confidence': 0.5,
                'confidence_percent': 50,
                'alternatives': [],
                'note': 'Detection based on color analysis. Accuracy may be limited.'
            }
            
        except Exception as e:
            print(f"❌ Image analysis error: {e}")
        
        # Ultimate fallback
        return {
            'success': True,
            'method': 'fallback',
            'food_name': 'mixed food',
            'confidence': 0.3,
            'confidence_percent': 30,
            'alternatives': [],
            'note': 'Could not identify food accurately. Using generic food data.'
        }
    
    def _normalize_food_name(self, food_name: str) -> str:
        """Normalize food name to match our database"""
        food_lower = food_name.lower().strip()
        
        # Check if it matches any of our known foods
        for known_food, keywords in self.food_keywords.items():
            if food_lower in keywords or any(keyword in food_lower for keyword in keywords):
                return known_food
        
        return food_lower
    
    def get_multiple_detections(self, image_path: str) -> List[Dict[str, Any]]:
        """Get multiple food detections from image (for mixed plates)"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = requests.post(
                f"{self.roboflow_model_url}?api_key={self.roboflow_api_key}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=image_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                predictions = result.get('predictions', [])
                
                # Group similar predictions
                detections = []
                for pred in predictions:
                    if pred.get('confidence', 0) > 0.5:
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
        """
        Complete food analysis with real-time updates
        """
        start_time = time.time()
        
        # Step 1: Detect food (0-40%)
        if progress_callback:
            progress_callback(0, {'stage': 'starting', 'message': 'Starting analysis...'})
        
        detection_result = self.detector.detect_food(image_path, progress_callback)
        
        # Step 2: Check for multiple foods (40-45%)
        if progress_callback:
            progress_callback(40, {'stage': 'checking_multiple', 'message': 'Checking for multiple items...'})
        
        multiple_detections = self.detector.get_multiple_detections(image_path)
        
        # Step 3: Prepare results (45-50%)
        if progress_callback:
            progress_callback(45, {'stage': 'preparing_results', 'message': 'Preparing results...'})
        
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
                'message': f'Detected: {detection_result["food_name"]} ({detection_result["confidence_percent"]}%)'
            })
        
        return result
