#!/usr/bin/env python3
"""
Nutrition API Module for Food Recognition Tracker
Week 3 Implementation with multiple API support
"""

import requests
import os
from typing import Dict, Any, Optional

class NutritionAPI:
    """Nutrition data fetcher with multiple API support"""
    
    def __init__(self):
        self.nutritionix_app_id = os.environ.get('NUTRITIONIX_APP_ID', 'demo_app_id')
        self.nutritionix_api_key = os.environ.get('NUTRITIONIX_API_KEY', 'demo_api_key')
        self.nutritionix_url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        
        # Comprehensive nutrition database for common foods
        self.nutrition_database = {
            # Fruits
            "apple": {"calories": 95, "protein": 0.5, "fat": 0.3, "carbs": 25, "fiber": 4, "sugar": 19, "sodium": 2},
            "banana": {"calories": 105, "protein": 1.3, "fat": 0.4, "carbs": 27, "fiber": 3, "sugar": 14, "sodium": 1},
            "orange": {"calories": 62, "protein": 1.2, "fat": 0.2, "carbs": 15, "fiber": 3, "sugar": 12, "sodium": 0},
            "grape": {"calories": 62, "protein": 0.6, "fat": 0.2, "carbs": 16, "fiber": 1, "sugar": 15, "sodium": 2},
            "strawberry": {"calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 8, "fiber": 2, "sugar": 5, "sodium": 1},
            "blueberry": {"calories": 84, "protein": 1.1, "fat": 0.5, "carbs": 21, "fiber": 4, "sugar": 15, "sodium": 1},
            
            # Vegetables
            "broccoli": {"calories": 25, "protein": 3, "fat": 0.3, "carbs": 5, "fiber": 3, "sugar": 1.5, "sodium": 33},
            "carrot": {"calories": 25, "protein": 0.5, "fat": 0.1, "carbs": 6, "fiber": 2, "sugar": 3, "sodium": 42},
            "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 4, "fiber": 1.2, "sugar": 2.6, "sodium": 5},
            "lettuce": {"calories": 5, "protein": 0.5, "fat": 0.1, "carbs": 1, "fiber": 0.6, "sugar": 0.4, "sodium": 3},
            "potato": {"calories": 161, "protein": 4.3, "fat": 0.2, "carbs": 37, "fiber": 4, "sugar": 2, "sodium": 8},
            "onion": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9, "fiber": 1.7, "sugar": 4.2, "sodium": 4},
            
            # Proteins
            "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 74},
            "beef": {"calories": 250, "protein": 26, "fat": 17, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 72},
            "fish": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 59},
            "salmon": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 59},
            "tuna": {"calories": 154, "protein": 25, "fat": 5, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 39},
            "shrimp": {"calories": 99, "protein": 18, "fat": 1.4, "carbs": 1, "fiber": 0, "sugar": 0, "sodium": 111},
            "egg": {"calories": 78, "protein": 6, "fat": 5, "carbs": 0.6, "fiber": 0, "sugar": 0.6, "sodium": 62},
            
            # Grains & Carbs
            "rice": {"calories": 205, "protein": 4.3, "fat": 0.4, "carbs": 45, "fiber": 0.6, "sugar": 0.1, "sodium": 1},
            "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49, "fiber": 3, "sugar": 5, "sodium": 491},
            "pasta": {"calories": 220, "protein": 8, "fat": 1.5, "carbs": 44, "fiber": 2, "sugar": 2, "sodium": 4},
            "noodle": {"calories": 220, "protein": 8, "fat": 1.5, "carbs": 44, "fiber": 2, "sugar": 2, "sodium": 4},
            
            # Fast Food / Processed
            "pizza": {"calories": 285, "protein": 12, "fat": 10, "carbs": 36, "fiber": 2, "sugar": 4, "sodium": 640},
            "burger": {"calories": 540, "protein": 25, "fat": 31, "carbs": 40, "fiber": 3, "sugar": 5, "sodium": 1040},
            "sandwich": {"calories": 300, "protein": 15, "fat": 12, "carbs": 35, "fiber": 3, "sugar": 4, "sodium": 650},
            "taco": {"calories": 170, "protein": 8, "fat": 10, "carbs": 13, "fiber": 3, "sugar": 1, "sodium": 310},
            "burrito": {"calories": 445, "protein": 21, "fat": 16, "carbs": 58, "fiber": 6, "sugar": 4, "sodium": 957},
            "hot dog": {"calories": 150, "protein": 5, "fat": 13, "carbs": 2, "fiber": 0, "sugar": 1, "sodium": 572},
            
            # Dairy
            "milk": {"calories": 103, "protein": 8, "fat": 2.4, "carbs": 12, "fiber": 0, "sugar": 12, "sodium": 107},
            "cheese": {"calories": 113, "protein": 7, "fat": 9, "carbs": 1, "fiber": 0, "sugar": 0.5, "sodium": 174},
            "yogurt": {"calories": 59, "protein": 10, "fat": 0.4, "carbs": 3.6, "fiber": 0, "sugar": 3.2, "sodium": 36},
            "butter": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1, "fiber": 0, "sugar": 0.1, "sodium": 11},
            
            # Desserts
            "cake": {"calories": 257, "protein": 3, "fat": 10, "carbs": 42, "fiber": 1, "sugar": 25, "sodium": 242},
            "cookie": {"calories": 49, "protein": 0.6, "fat": 2.3, "carbs": 6.8, "fiber": 0.2, "sugar": 3.9, "sodium": 32},
            "chocolate": {"calories": 546, "protein": 4.9, "fat": 31, "carbs": 61, "fiber": 7, "sugar": 48, "sodium": 6},
            "ice cream": {"calories": 207, "protein": 3.5, "fat": 11, "carbs": 24, "fiber": 0.7, "sugar": 21, "sodium": 80},
            "donut": {"calories": 195, "protein": 2.3, "fat": 11, "carbs": 23, "fiber": 0.9, "sugar": 10, "sodium": 181},
            
            # Drinks & Others
            "salad": {"calories": 65, "protein": 3, "fat": 0.5, "carbs": 12, "fiber": 4, "sugar": 6, "sodium": 15},
            "soup": {"calories": 85, "protein": 4, "fat": 2, "carbs": 12, "fiber": 2, "sugar": 3, "sodium": 800},
            "sushi": {"calories": 200, "protein": 8, "fat": 1, "carbs": 40, "fiber": 3, "sugar": 8, "sodium": 335},
            "ramen": {"calories": 436, "protein": 20, "fat": 14, "carbs": 54, "fiber": 4, "sugar": 5, "sodium": 1500},
            
            # Generic categories
            "fruit": {"calories": 60, "protein": 1, "fat": 0.2, "carbs": 15, "fiber": 3, "sugar": 12, "sodium": 2},
            "vegetable": {"calories": 25, "protein": 2, "fat": 0.2, "carbs": 5, "fiber": 3, "sugar": 3, "sodium": 20},
            "meat": {"calories": 200, "protein": 25, "fat": 10, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 70},
            "dish": {"calories": 250, "protein": 12, "fat": 10, "carbs": 30, "fiber": 3, "sugar": 5, "sodium": 400},
            "meal": {"calories": 400, "protein": 20, "fat": 15, "carbs": 45, "fiber": 5, "sugar": 8, "sodium": 600},
            "mixed food": {"calories": 200, "protein": 8, "fat": 8, "carbs": 25, "fiber": 2, "sugar": 6, "sodium": 150},
            "unknown food": {"calories": 150, "protein": 6, "fat": 6, "carbs": 20, "fiber": 2, "sugar": 4, "sodium": 100}
        }
    
    def get_nutrition(self, food_name: str) -> Dict[str, Any]:
        """
        Get nutrition data for a food item
        
        Args:
            food_name: Name of the food item
            
        Returns:
            Dictionary containing nutrition information
        """
        try:
            # First try to get from local database
            nutrition_data = self.get_from_database(food_name)
            
            if nutrition_data:
                return {
                    **nutrition_data,
                    "data_source": "local_database",
                    "food_name": food_name.title()
                }
            
            # If not found, try Nutritionix API (if credentials available)
            if (self.nutritionix_app_id != 'demo_app_id' and 
                self.nutritionix_api_key != 'demo_api_key'):
                api_data = self.get_from_nutritionix(food_name)
                if api_data:
                    return api_data
            
            # Fallback to generic food data
            return self.get_generic_nutrition(food_name)
            
        except Exception as e:
            print(f"Error getting nutrition data: {e}")
            return self.get_generic_nutrition(food_name)
    
    def get_from_database(self, food_name: str) -> Optional[Dict[str, Any]]:
        """Get nutrition data from local database"""
        food_name_lower = food_name.lower().strip()
        
        # Direct match
        if food_name_lower in self.nutrition_database:
            return self.nutrition_database[food_name_lower].copy()
        
        # Partial match
        for db_food, nutrition in self.nutrition_database.items():
            if (db_food in food_name_lower or 
                food_name_lower in db_food or
                self.foods_are_similar(db_food, food_name_lower)):
                return nutrition.copy()
        
        return None
    
    def foods_are_similar(self, food1: str, food2: str) -> bool:
        """Check if two food names are similar"""
        # Simple similarity check
        food1_words = set(food1.split())
        food2_words = set(food2.split())
        
        # If they share any words, consider them similar
        return len(food1_words.intersection(food2_words)) > 0
    
    def get_from_nutritionix(self, food_name: str) -> Optional[Dict[str, Any]]:
        """Get nutrition data from Nutritionix API"""
        try:
            headers = {
                'x-app-id': self.nutritionix_app_id,
                'x-app-key': self.nutritionix_api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'query': food_name,
                'timezone': 'US/Eastern'
            }
            
            response = requests.post(
                self.nutritionix_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                foods = data.get('foods', [])
                
                if foods:
                    food = foods[0]  # Take first result
                    return {
                        'calories': food.get('nf_calories', 0),
                        'protein': food.get('nf_protein', 0),
                        'fat': food.get('nf_total_fat', 0),
                        'carbs': food.get('nf_total_carbohydrate', 0),
                        'fiber': food.get('nf_dietary_fiber', 0),
                        'sugar': food.get('nf_sugars', 0),
                        'sodium': food.get('nf_sodium', 0),
                        'data_source': 'nutritionix_api',
                        'food_name': food.get('food_name', food_name).title()
                    }
            
        except Exception as e:
            print(f"Nutritionix API error: {e}")
        
        return None
    
    def get_generic_nutrition(self, food_name: str) -> Dict[str, Any]:
        """Get generic nutrition data based on food type"""
        food_lower = food_name.lower()
        
        # Categorize food and return appropriate generic values
        if any(fruit in food_lower for fruit in ['fruit', 'apple', 'banana', 'berry']):
            base = self.nutrition_database['fruit'].copy()
        elif any(veg in food_lower for veg in ['vegetable', 'salad', 'green']):
            base = self.nutrition_database['vegetable'].copy()
        elif any(meat in food_lower for meat in ['meat', 'chicken', 'beef', 'fish']):
            base = self.nutrition_database['meat'].copy()
        elif any(fast in food_lower for fast in ['pizza', 'burger', 'fried']):
            base = self.nutrition_database['burger'].copy()  # Use burger as high-calorie reference
        else:
            base = self.nutrition_database['mixed food'].copy()
        
        return {
            **base,
            "data_source": "generic_estimate",
            "food_name": food_name.title(),
            "note": "Estimated nutritional values"
        }
    
    def get_spoonacular_data(self, food_name: str) -> Dict[str, Any]:
        """Mock Spoonacular API response"""
        base_nutrition = self.get_nutrition(food_name)
        
        # Add Spoonacular-specific fields
        return {
            **base_nutrition,
            "recipe_id": 12345,
            "servings": 1,
            "ready_in_minutes": 0,
            "data_source": "spoonacular_mock",
            "api_used": "Spoonacular (Mock)"
        }
    
    def get_daily_requirements(self) -> Dict[str, Any]:
        """Get recommended daily nutritional requirements"""
        return {
            "calories": "2000-2500 kcal",
            "protein": "50-70g",
            "fat": "65-80g", 
            "carbohydrates": "225-325g",
            "fiber": "25-30g",
            "sugar": "< 50g",
            "sodium": "< 2300mg",
            "data_source": "daily_requirements",
            "note": "Recommended daily intake for average adult",
            "based_on": "2000-2500 calorie diet"
        }
    
    def analyze_nutrition_quality(self, nutrition_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze the nutritional quality of food"""
        try:
            calories = float(str(nutrition_data.get('calories', 0)).replace('kcal', '').strip() or 0)
            protein = float(str(nutrition_data.get('protein', 0)).replace('g', '').strip() or 0)
            fat = float(str(nutrition_data.get('fat', 0)).replace('g', '').strip() or 0)
            carbs = float(str(nutrition_data.get('carbs', 0)).replace('g', '').strip() or 0)
            fiber = float(str(nutrition_data.get('fiber', 0)).replace('g', '').strip() or 0)
            sugar = float(str(nutrition_data.get('sugar', 0)).replace('g', '').strip() or 0)
            sodium = float(str(nutrition_data.get('sodium', 0)).replace('mg', '').strip() or 0)
            
            # Nutritional analysis
            analysis = {
                "calorie_level": self._analyze_calories(calories),
                "protein_level": self._analyze_protein(protein, calories),
                "fat_level": self._analyze_fat(fat, calories),
                "carb_level": self._analyze_carbs(carbs, calories),
                "fiber_level": self._analyze_fiber(fiber),
                "sugar_level": self._analyze_sugar(sugar),
                "sodium_level": self._analyze_sodium(sodium)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _analyze_calories(self, calories: float) -> str:
        """Analyze calorie content"""
        if calories < 50:
            return "Very Low"
        elif calories < 150:
            return "Low"
        elif calories < 300:
            return "Moderate"
        elif calories < 500:
            return "High"
        else:
            return "Very High"
    
    def _analyze_protein(self, protein: float, calories: float) -> str:
        """Analyze protein content"""
        if calories > 0:
            protein_pct = (protein * 4) / calories * 100
            if protein_pct > 30:
                return "High Protein"
            elif protein_pct > 15:
                return "Good Protein"
            elif protein_pct > 10:
                return "Adequate Protein"
            else:
                return "Low Protein"
        return "Unknown"
    
    def _analyze_fat(self, fat: float, calories: float) -> str:
        """Analyze fat content"""
        if calories > 0:
            fat_pct = (fat * 9) / calories * 100
            if fat_pct > 35:
                return "High Fat"
            elif fat_pct > 20:
                return "Moderate Fat"
            else:
                return "Low Fat"
        return "Unknown"
    
    def _analyze_carbs(self, carbs: float, calories: float) -> str:
        """Analyze carbohydrate content"""
        if calories > 0:
            carb_pct = (carbs * 4) / calories * 100
            if carb_pct > 60:
                return "High Carb"
            elif carb_pct > 45:
                return "Moderate Carb"
            else:
                return "Low Carb"
        return "Unknown"
    
    def _analyze_fiber(self, fiber: float) -> str:
        """Analyze fiber content"""
        if fiber >= 5:
            return "High Fiber"
        elif fiber >= 3:
            return "Good Fiber"
        elif fiber >= 1:
            return "Some Fiber"
        else:
            return "Low Fiber"
    
    def _analyze_sugar(self, sugar: float) -> str:
        """Analyze sugar content"""
        if sugar < 5:
            return "Low Sugar"
        elif sugar < 15:
            return "Moderate Sugar"
        elif sugar < 25:
            return "High Sugar"
        else:
            return "Very High Sugar"
    
    def _analyze_sodium(self, sodium: float) -> str:
        """Analyze sodium content"""
        if sodium < 140:
            return "Low Sodium"
        elif sodium < 400:
            return "Moderate Sodium"
        elif sodium < 600:
            return "High Sodium"
        else:
            return "Very High Sodium"

# Test function
if __name__ == "__main__":
    # Test the nutrition API
    nutrition_api = NutritionAPI()
    
    test_foods = ["apple", "pizza", "chicken", "unknown food"]
    
    for food in test_foods:
        print(f"\n=== Testing: {food} ===")
        nutrition = nutrition_api.get_nutrition(food)
        print(f"Nutrition data: {nutrition}")
        
        analysis = nutrition_api.analyze_nutrition_quality(nutrition)
        print(f"Analysis: {analysis}")