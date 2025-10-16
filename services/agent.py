#!/usr/bin/env python3
"""
LangChain Agent for Food Recognition Tracker
Automates nutrition data refinement and validation
"""

from typing import Dict, Any, Optional
import json


class NutritionValidationAgent:
    """
    Simple agent that validates and refines nutrition data
    Uses rule-based logic (can be upgraded to LangChain later)
    """
    
    def __init__(self):
        self.validation_rules = {
            "calories": {"min": 0, "max": 2000, "type": "number"},
            "protein": {"min": 0, "max": 200, "type": "number"},
            "fat": {"min": 0, "max": 200, "type": "number"},
            "carbs": {"min": 0, "max": 500, "type": "number"},
            "fiber": {"min": 0, "max": 50, "type": "number"},
            "sugar": {"min": 0, "max": 200, "type": "number"},
            "sodium": {"min": 0, "max": 10000, "type": "number"}
        }
        
        self.food_categories = {
            "healthy": ["apple", "banana", "orange", "broccoli", "carrot", "chicken", "fish", "salad"],
            "moderate": ["rice", "bread", "pasta", "potato", "beef", "cheese"],
            "junk": ["pizza", "burger", "fries", "donut", "ice cream", "cake", "soda", "chips"]
        }
    
    def validate_and_refine(self, food_name: str, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function: validate nutrition data and refine it
        
        Args:
            food_name: Detected food name
            nutrition_data: Raw nutrition data
            
        Returns:
            Refined and validated nutrition data with agent insights
        """
        print(f"🤖 Agent validating: {food_name}")
        
        # Step 1: Validate data ranges
        validated_data = self._validate_ranges(nutrition_data)
        
        # Step 2: Auto-categorize food
        category = self._categorize_food(food_name, validated_data)
        validated_data['category'] = category
        
        # Step 3: Calculate health insights
        health_insights = self._generate_health_insights(validated_data)
        validated_data['agent_insights'] = health_insights
        
        # Step 4: Flag anomalies
        anomalies = self._detect_anomalies(food_name, validated_data)
        if anomalies:
            validated_data['agent_warnings'] = anomalies
        
        # Step 5: Add confidence score
        validated_data['agent_confidence'] = self._calculate_confidence(validated_data)
        
        print(f"✅ Agent validation complete: {validated_data.get('agent_confidence', 0)}% confident")
        
        return validated_data
    
    def _validate_ranges(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that nutrition values are within reasonable ranges"""
        validated = data.copy()
        
        for key, rules in self.validation_rules.items():
            if key in validated:
                value = validated[key]
                
                # Convert to number if string
                if isinstance(value, str):
                    try:
                        value = float(value.replace('g', '').replace('mg', '').replace('kcal', '').strip())
                    except:
                        value = 0
                
                # Clamp to valid range
                value = max(rules['min'], min(rules['max'], value))
                validated[key] = value
        
        return validated
    
    def _categorize_food(self, food_name: str, nutrition_data: Dict[str, Any]) -> str:
        """Automatically categorize food based on name and nutrition"""
        food_lower = food_name.lower()
        
        # Check predefined categories
        for category, foods in self.food_categories.items():
            if any(food in food_lower for food in foods):
                return category
        
        # Use nutrition heuristics
        calories = nutrition_data.get('calories', 0)
        fat = nutrition_data.get('fat', 0)
        sugar = nutrition_data.get('sugar', 0)
        
        if calories > 400 or fat > 20 or sugar > 20:
            return 'junk'
        elif calories < 100 and fat < 5 and sugar < 10:
            return 'healthy'
        else:
            return 'moderate'
    
    def _generate_health_insights(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligent health insights"""
        insights = {}
        
        calories = data.get('calories', 0)
        protein = data.get('protein', 0)
        fat = data.get('fat', 0)
        sugar = data.get('sugar', 0)
        fiber = data.get('fiber', 0)
        sodium = data.get('sodium', 0)
        
        # Calorie insight
        if calories < 100:
            insights['calories'] = "Low calorie - great for weight management"
        elif calories > 500:
            insights['calories'] = "High calorie - consume in moderation"
        else:
            insights['calories'] = "Moderate calories - balanced choice"
        
        # Protein insight
        if protein > 20:
            insights['protein'] = "High protein - excellent for muscle building"
        elif protein < 5:
            insights['protein'] = "Low protein - consider pairing with protein source"
        
        # Fat insight
        if fat > 20:
            insights['fat'] = "High fat content - be mindful of portions"
        
        # Sugar insight
        if sugar > 20:
            insights['sugar'] = "High sugar - limit consumption"
        elif sugar < 5:
            insights['sugar'] = "Low sugar - good choice"
        
        # Fiber insight
        if fiber > 5:
            insights['fiber'] = "High fiber - supports digestive health"
        
        # Sodium insight
        if sodium > 600:
            insights['sodium'] = "High sodium - may impact blood pressure"
        
        return insights
    
    def _detect_anomalies(self, food_name: str, data: Dict[str, Any]) -> list:
        """Detect unusual patterns in nutrition data"""
        anomalies = []
        
        calories = data.get('calories', 0)
        protein = data.get('protein', 0)
        fat = data.get('fat', 0)
        carbs = data.get('carbs', 0)
        
        # Check for impossible combinations
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        
        if abs(calculated_calories - calories) > 200 and calories > 0:
            anomalies.append("Nutritional values may be inconsistent")
        
        # Check category mismatch
        category = data.get('category', '')
        if category == 'healthy' and calories > 400:
            anomalies.append("High calorie count for healthy food category")
        
        if category == 'junk' and calories < 100:
            anomalies.append("Low calorie count for junk food category")
        
        return anomalies
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> int:
        """Calculate confidence score for the validation"""
        confidence = 100
        
        # Reduce confidence if there are warnings
        if 'agent_warnings' in data and data['agent_warnings']:
            confidence -= len(data['agent_warnings']) * 10
        
        # Reduce confidence if data is incomplete
        required_fields = ['calories', 'protein', 'fat', 'carbs']
        missing_fields = [f for f in required_fields if not data.get(f, 0)]
        confidence -= len(missing_fields) * 5
        
        # Ensure minimum confidence
        return max(60, min(100, confidence))
    
    def refine_detection_result(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine the entire detection result using agent intelligence
        
        Args:
            detection_result: Raw detection from Roboflow
            
        Returns:
            Refined detection with agent improvements
        """
        food_name = detection_result.get('food_name', 'unknown')
        confidence = detection_result.get('detection', {}).get('confidence_percent', 0)
        
        # Agent decision: reject low confidence detections
        if confidence < 40:
            detection_result['agent_action'] = 'rejected'
            detection_result['agent_reason'] = 'Confidence too low for reliable nutrition data'
            return detection_result
        
        # Agent decision: validate and refine nutrition
        if 'nutrition' in detection_result:
            validated_nutrition = self.validate_and_refine(
                food_name, 
                detection_result['nutrition']
            )
            detection_result['nutrition'] = validated_nutrition
            detection_result['agent_action'] = 'validated'
        
        return detection_result
    
    def generate_recommendation(self, nutrition_data: Dict[str, Any]) -> str:
        """Generate intelligent food recommendation"""
        category = nutrition_data.get('category', 'moderate')
        insights = nutrition_data.get('agent_insights', {})
        
        if category == 'healthy':
            return f"✅ Great choice! {insights.get('calories', 'Nutritionally balanced')}. Keep up the healthy eating!"
        elif category == 'junk':
            warnings = [v for v in insights.values() if 'High' in v]
            return f"⚠️ Limit intake. {' '.join(warnings[:2])}. Consider healthier alternatives."
        else:
            return f"👍 Moderate choice. {insights.get('calories', 'Okay for occasional consumption')}. Balance with other foods."


# Global agent instance
_agent = None

def get_nutrition_agent() -> NutritionValidationAgent:
    """Get global nutrition validation agent"""
    global _agent
    if _agent is None:
        _agent = NutritionValidationAgent()
        print("🤖 Nutrition Validation Agent initialized")
    return _agent


# Test the agent
if __name__ == "__main__":
    agent = NutritionValidationAgent()
    
    # Test case 1: Validate burger
    print("\n=== Test 1: Burger ===")
    burger_data = {
        "calories": 540,
        "protein": 25,
        "fat": 31,
        "carbs": 40,
        "fiber": 3,
        "sugar": 5,
        "sodium": 1040
    }
    result = agent.validate_and_refine("burger", burger_data)
    print(f"Category: {result['category']}")
    print(f"Insights: {result['agent_insights']}")
    print(f"Confidence: {result['agent_confidence']}%")
    
    # Test case 2: Validate apple
    print("\n=== Test 2: Apple ===")
    apple_data = {
        "calories": 95,
        "protein": 0.5,
        "fat": 0.3,
        "carbs": 25,
        "fiber": 4,
        "sugar": 19,
        "sodium": 2
    }
    result = agent.validate_and_refine("apple", apple_data)
    print(f"Category: {result['category']}")
    print(f"Insights: {result['agent_insights']}")
    print(f"Confidence: {result['agent_confidence']}%")
    
    # Test case 3: Generate recommendation
    print("\n=== Test 3: Recommendation ===")
    recommendation = agent.generate_recommendation(result)
    print(f"Recommendation: {recommendation}")
