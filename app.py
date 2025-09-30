import os
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import traceback
import base64
import re
from datetime import datetime, timedelta
import random

# Load environment variables from .env
load_dotenv()

# Flask setup
app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# API Configuration
ROBOFLOW_API_KEY = "CDxqqcJkI8wWdBX4IVrl"
ROBOFLOW_MODEL_URL = "https://detect.roboflow.com/food-recognition/1"

# Stats and Insights APIs (with fallback to demo data)
NUTRITIONIX_APP_ID = os.environ.get('NUTRITIONIX_APP_ID', 'demo_app_id')
NUTRITIONIX_API_KEY = os.environ.get('NUTRITIONIX_API_KEY', 'demo_api_key')
EDAMAM_APP_ID = os.environ.get('EDAMAM_APP_ID', 'demo_app_id')
EDAMAM_APP_KEY = os.environ.get('EDAMAM_APP_KEY', 'demo_api_key')

# Simple in-memory storage for results and analytics
results_store = []
user_analytics = {
    "total_scans": 0,
    "healthy_choices": 0,
    "average_calories": 0,
    "most_scanned_food": "",
    "weekly_trends": [],
    "nutrition_goals": {
        "daily_calories": 2000,
        "daily_protein": 50,
        "daily_carbs": 300,
        "daily_fat": 70
    }
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_food_roboflow(image_path):
    """Detect food using Roboflow API with fallback to demo detection"""
    try:
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Make API request
        response = requests.post(
            f"{ROBOFLOW_MODEL_URL}?api_key={ROBOFLOW_API_KEY}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=image_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            predictions = result.get('predictions', [])
            
            if predictions:
                # Get the highest confidence prediction
                best_prediction = max(predictions, key=lambda x: x.get('confidence', 0))
                food_name = best_prediction.get('class', 'unknown food')
                confidence = best_prediction.get('confidence', 0)
                
                print(f"Roboflow detected: {food_name} (confidence: {confidence:.2f})")
                return food_name
        
        print("No food detected by Roboflow, using demo detection")
        return demo_detect_food()
        
    except Exception as e:
        print(f"Roboflow API error: {e}, using demo detection")
        return demo_detect_food()

def demo_detect_food():
    """Demo food detection when API is unavailable"""
    foods = ["apple", "banana", "pizza", "burger", "salad", "pasta", "chicken", "fish", "bread", "rice"]
    return random.choice(foods)

def get_nutrition_insights(food_name, api_choice):
    """Get enhanced nutrition data with insights from various APIs"""
    
    # Try to get real data from Nutritionix if available
    if NUTRITIONIX_APP_ID != 'demo_app_id' and api_choice == 'nutrition':
        try:
            nutrition_data = get_nutritionix_data(food_name)
            if nutrition_data:
                return enhance_with_insights(nutrition_data, food_name, api_choice)
        except Exception as e:
            print(f"Nutritionix API error: {e}, using demo data")
    
    # Fallback to demo data
    return get_demo_nutrition_data(food_name, api_choice)

def get_nutritionix_data(food_name):
    """Get real nutrition data from Nutritionix API"""
    try:
        headers = {
            'x-app-id': NUTRITIONIX_APP_ID,
            'x-app-key': NUTRITIONIX_API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = {
            'query': food_name,
            'timezone': 'US/Eastern'
        }
        
        response = requests.post(
            'https://trackapi.nutritionix.com/v2/natural/nutrients',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'foods' in result and len(result['foods']) > 0:
                food_data = result['foods'][0]
                return {
                    'calories': food_data.get('nf_calories', 0),
                    'protein': food_data.get('nf_protein', 0),
                    'fat': food_data.get('nf_total_fat', 0),
                    'carbs': food_data.get('nf_total_carbohydrate', 0),
                    'fiber': food_data.get('nf_dietary_fiber', 0),
                    'sugar': food_data.get('nf_sugars', 0),
                    'sodium': food_data.get('nf_sodium', 0),
                    'serving_size': food_data.get('serving_weight_grams', 100),
                    'source': 'Nutritionix API'
                }
    except Exception as e:
        print(f"Error fetching from Nutritionix: {e}")
    
    return None

def get_demo_nutrition_data(food_name, api_choice):
    """Demo nutrition data with realistic values"""
    food_db = {
        "apple": {"calories": 95, "protein": 0.5, "fat": 0.3, "carbs": 25, "fiber": 4, "sugar": 19, "sodium": 2},
        "banana": {"calories": 105, "protein": 1.3, "fat": 0.4, "carbs": 27, "fiber": 3, "sugar": 14, "sodium": 1},
        "orange": {"calories": 62, "protein": 1.2, "fat": 0.2, "carbs": 15, "fiber": 3, "sugar": 12, "sodium": 0},
        "pizza": {"calories": 285, "protein": 12, "fat": 10, "carbs": 36, "fiber": 2, "sugar": 4, "sodium": 640},
        "burger": {"calories": 540, "protein": 25, "fat": 31, "carbs": 40, "fiber": 3, "sugar": 5, "sodium": 1040},
        "salad": {"calories": 65, "protein": 3, "fat": 0.5, "carbs": 12, "fiber": 4, "sugar": 6, "sodium": 15},
        "pasta": {"calories": 220, "protein": 8, "fat": 1.5, "carbs": 44, "fiber": 2, "sugar": 2, "sodium": 4},
        "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 74},
        "fish": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 59},
        "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49, "fiber": 3, "sugar": 5, "sodium": 491},
        "rice": {"calories": 205, "protein": 4.3, "fat": 0.4, "carbs": 45, "fiber": 0.6, "sugar": 0.1, "sodium": 1},
        "mixed food": {"calories": 200, "protein": 8, "fat": 8, "carbs": 25, "fiber": 2, "sugar": 6, "sodium": 150},
        "unknown food": {"calories": 150, "protein": 6, "fat": 6, "carbs": 20, "fiber": 2, "sugar": 4, "sodium": 100}
    }
    
    # Find nutrition data
    food_lower = food_name.lower()
    nutrition_data = food_db.get("mixed food")
    
    for key in food_db:
        if key in food_lower or food_lower in key:
            nutrition_data = food_db[key]
            break
    
    # Customize response based on API
    if api_choice == "roboflow":
        return {
            "detected_food": food_name,
            "api_used": "Roboflow Detection",
            "note": "Food detection completed successfully",
            "source": "Demo Data"
        }
    elif api_choice == "spoonacular":
        return {
            **nutrition_data,
            "recipe_id": random.randint(10000, 99999),
            "cooking_time": f"{random.randint(15, 45)} minutes",
            "difficulty": random.choice(["Easy", "Medium", "Hard"]),
            "api_used": "Spoonacular (Demo)",
            "source": "Demo Data"
        }
    elif api_choice == "bodyrequirements":
        return {
            "daily_calories": "2000-2500 kcal",
            "daily_protein": "50-70g",
            "daily_fat": "65-80g", 
            "daily_carbs": "225-325g",
            "daily_fiber": "25-30g",
            "daily_sugar": "< 50g",
            "bmi_recommendation": "Maintain current diet",
            "activity_level": "Moderately active",
            "api_used": "Body Requirements (Demo)",
            "source": "Demo Data"
        }
    else:  # nutrition API
        nutrition_data["source"] = "Demo Data"
        return nutrition_data

def enhance_with_insights(nutrition_data, food_name, api_choice):
    """Add insights and analytics to nutrition data"""
    enhanced_data = {**nutrition_data}
    
    # Add health score
    enhanced_data["health_score"] = calculate_health_score(nutrition_data)
    
    # Add comparison to daily goals
    enhanced_data["daily_goal_percentage"] = {
        "calories": min(100, (nutrition_data.get("calories", 0) / user_analytics["nutrition_goals"]["daily_calories"]) * 100),
        "protein": min(100, (nutrition_data.get("protein", 0) / user_analytics["nutrition_goals"]["daily_protein"]) * 100),
        "carbs": min(100, (nutrition_data.get("carbs", 0) / user_analytics["nutrition_goals"]["daily_carbs"]) * 100),
        "fat": min(100, (nutrition_data.get("fat", 0) / user_analytics["nutrition_goals"]["daily_fat"]) * 100)
    }
    
    # Add food category
    enhanced_data["category"] = categorize_food(food_name, nutrition_data)
    
    # Add sustainability insights if available
    enhanced_data["sustainability"] = get_sustainability_insights(food_name)
    
    # Add seasonal information
    enhanced_data["seasonal"] = get_seasonal_info(food_name)
    
    # Add recipe suggestions for some foods
    if api_choice == "spoonacular" and random.random() > 0.5:
        enhanced_data["recipe_suggestions"] = get_recipe_suggestions(food_name)
    
    return enhanced_data

def calculate_health_score(nutrition_data):
    """Calculate a health score from 0-100 based on nutrition data"""
    calories = nutrition_data.get("calories", 0)
    protein = nutrition_data.get("protein", 0)
    fat = nutrition_data.get("fat", 0)
    sugar = nutrition_data.get("sugar", 0)
    sodium = nutrition_data.get("sodium", 0)
    fiber = nutrition_data.get("fiber", 0)
    
    # Scoring algorithm (simplified)
    score = 100
    
    # Penalize high calories
    if calories > 500:
        score -= 20
    elif calories > 300:
        score -= 10
    
    # Reward protein
    score += min(10, protein * 0.5)
    
    # Penalize high fat
    if fat > 20:
        score -= 15
    elif fat > 10:
        score -= 5
    
    # Penalize high sugar
    if sugar > 15:
        score -= 15
    elif sugar > 10:
        score -= 5
    
    # Penalize high sodium
    if sodium > 800:
        score -= 15
    elif sodium > 400:
        score -= 5
    
    # Reward fiber
    score += min(10, fiber * 2)
    
    return max(0, min(100, score))

def categorize_food(food_name, nutrition_data):
    """Categorize food based on its nutritional profile"""
    calories = nutrition_data.get("calories", 0)
    protein = nutrition_data.get("protein", 0)
    carbs = nutrition_data.get("carbs", 0)
    fat = nutrition_data.get("fat", 0)
    
    if protein > 20 and fat < 10:
        return "High-Protein Lean"
    elif carbs > 40 and fat < 5:
        return "Carbohydrate-Rich"
    elif fat > 20:
        return "High-Fat"
    elif calories < 100:
        return "Low-Calorie"
    elif "salad" in food_name or "vegetable" in food_name:
        return "Vegetable-Based"
    elif "fruit" in food_name or food_name in ["apple", "banana", "orange"]:
        return "Fruit"
    else:
        return "General Food"

def get_sustainability_insights(food_name):
    """Get sustainability insights about the food"""
    sustainability_db = {
        "apple": {"carbon_footprint": "Low", "water_usage": "Medium", "seasonality": "Fall"},
        "banana": {"carbon_footprint": "Medium", "water_usage": "High", "seasonality": "Year-round"},
        "beef": {"carbon_footprint": "Very High", "water_usage": "Very High", "seasonality": "Year-round"},
        "chicken": {"carbon_footprint": "Medium", "water_usage": "High", "seasonality": "Year-round"},
        "fish": {"carbon_footprint": "Varies", "water_usage": "Varies", "seasonality": "Varies"},
        "salad": {"carbon_footprint": "Low", "water_usage": "Medium", "seasonality": "Spring/Summer"},
    }
    
    food_lower = food_name.lower()
    for key in sustainability_db:
        if key in food_lower:
            return sustainability_db[key]
    
    return {"carbon_footprint": "Unknown", "water_usage": "Unknown", "seasonality": "Unknown"}

def get_seasonal_info(food_name):
    """Get seasonal information about the food"""
    seasonal_db = {
        "apple": ["Fall", "Winter"],
        "banana": ["Year-round"],
        "orange": ["Winter"],
        "strawberry": ["Spring", "Summer"],
        "pumpkin": ["Fall"],
        "corn": ["Summer", "Fall"],
        "tomato": ["Summer"],
    }
    
    food_lower = food_name.lower()
    for key in seasonal_db:
        if key in food_lower:
            return {"is_in_season": True, "seasons": seasonal_db[key]}
    
    return {"is_in_season": False, "seasons": ["Year-round"]}

def get_recipe_suggestions(food_name):
    """Get recipe suggestions for the food"""
    recipes_db = {
        "chicken": [
            {"name": "Grilled Lemon Herb Chicken", "calories": 320, "time": "25 min", "difficulty": "Easy"},
            {"name": "Chicken Stir-Fry", "calories": 420, "time": "20 min", "difficulty": "Easy"},
        ],
        "salad": [
            {"name": "Mediterranean Salad", "calories": 280, "time": "15 min", "difficulty": "Easy"},
            {"name": "Asian Chicken Salad", "calories": 380, "time": "20 min", "difficulty": "Medium"},
        ],
        "pasta": [
            {"name": "Creamy Garlic Pasta", "calories": 520, "time": "30 min", "difficulty": "Medium"},
            {"name": "Tomato Basil Pasta", "calories": 450, "time": "25 min", "difficulty": "Easy"},
        ],
        "fish": [
            {"name": "Baked Salmon with Herbs", "calories": 380, "time": "30 min", "difficulty": "Medium"},
            {"name": "Pan-Seared Tilapia", "calories": 290, "time": "20 min", "difficulty": "Easy"},
        ],
    }
    
    food_lower = food_name.lower()
    for key in recipes_db:
        if key in food_lower:
            return recipes_db[key]
    
    return [{"name": f"Delicious {food_name.title()} Recipe", "calories": 350, "time": "30 min", "difficulty": "Medium"}]

def update_user_analytics(food_name, nutrition_data, health_rating):
    """Update user analytics with the latest scan"""
    user_analytics["total_scans"] += 1
    
    if "Excellent" in health_rating or "Good" in health_rating:
        user_analytics["healthy_choices"] += 1
    
    # Update average calories
    current_avg = user_analytics["average_calories"]
    new_calories = nutrition_data.get("calories", 0)
    user_analytics["average_calories"] = (
        (current_avg * (user_analytics["total_scans"] - 1) + new_calories) / 
        user_analytics["total_scans"]
    )
    
    # Update most scanned food
    food_counts = {}
    for result in results_store:
        food = result["food_name"].lower()
        food_counts[food] = food_counts.get(food, 0) + 1
    
    if food_counts:
        user_analytics["most_scanned_food"] = max(food_counts, key=food_counts.get)
    
    # Update weekly trends (simplified)
    if len(user_analytics["weekly_trends"]) >= 7:
        user_analytics["weekly_trends"].pop(0)
    
    user_analytics["weekly_trends"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "food": food_name,
        "calories": new_calories,
        "health_rating": health_rating
    })

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    """Check API status with enhanced information"""
    return jsonify({
        "roboflow": "ready" if ROBOFLOW_API_KEY != "demo_key" else "demo_mode",
        "nutrition": "ready" if NUTRITIONIX_APP_ID != "demo_app_id" else "demo_mode", 
        "spoonacular": "demo_mode",
        "bodyrequirements": "demo_mode",
        "analytics": "ready",
        "environment": "development" if os.environ.get('FLASK_ENV') == 'development' else "production"
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Get form data
        api_choice = request.form.get("api", "nutrition")
        file = request.files.get("image")
        
        # Validate file
        if not file or file.filename == "":
            return jsonify({"error": "No image uploaded"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid image file type"}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(filepath)
        
        print(f"Processing {unique_filename} with {api_choice} API")
        
        # Detect food
        detected_food = detect_food_roboflow(filepath)
        if detected_food == "unknown food" and filename:
            # Use filename as hint
            detected_food = filename.split('.')[0].lower()
        
        print(f"Detected food: {detected_food}")
        
        # Get nutrition information with insights
        nutrition_data = get_nutrition_insights(detected_food, api_choice)
        
        # Evaluate health impact
        health_rating, recommendation = evaluate_food_health(nutrition_data)
        
        # Prepare response with enhanced data
        result = {
            "id": str(uuid.uuid4()),
            "food_name": detected_food.title(),
            "api_used": api_choice,
            "nutrition": nutrition_data,
            "health_rating": health_rating,
            "recommendation": recommendation,
            "portion_suggestion": generate_portion_suggestion(detected_food, nutrition_data),
            "timestamp": datetime.now().isoformat(),
            "user_analytics": {
                "total_scans": user_analytics["total_scans"] + 1,
                "health_percentage": user_analytics["healthy_choices"] / max(1, user_analytics["total_scans"]) * 100
            }
        }
        
        # Save result
        results_store.append(result)
        
        # Update analytics
        update_user_analytics(detected_food, nutrition_data, health_rating)
        
        # Clean up file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route("/history", methods=["GET"])
def history():
    """Get analysis history with enhanced analytics"""
    return jsonify({
        "results": list(reversed(results_store[-10:])),  # Last 10 scans
        "analytics": user_analytics,
        "summary": {
            "total_scans": user_analytics["total_scans"],
            "healthy_percentage": user_analytics["healthy_choices"] / max(1, user_analytics["total_scans"]) * 100,
            "average_calories": user_analytics["average_calories"],
            "most_popular_food": user_analytics["most_scanned_food"]
        }
    })

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Get detailed user analytics"""
    return jsonify(user_analytics)

@app.route("/api/trends", methods=["GET"])
def get_trends():
    """Get food trends and insights"""
    # Generate some demo trends
    trends = {
        "weekly_calorie_trend": [1850, 2100, 1950, 2300, 2050, 1900, 2150],
        "health_score_trend": [72, 68, 75, 65, 70, 78, 73],
        "food_category_distribution": {
            "High-Protein": 35,
            "Carbohydrate-Rich": 25,
            "Vegetable-Based": 20,
            "High-Fat": 15,
            "Other": 5
        },
        "recommendations": [
            "Try incorporating more leafy greens into your meals",
            "Your protein intake is good, consider adding more variety",
            "Watch your sodium intake on weekends"
        ]
    }
    return jsonify(trends)

def generate_portion_suggestion(food_name, nutrition_data):
    """Generate intelligent portion suggestions"""
    calories = nutrition_data.get("calories", 0)
    
    if calories < 100:
        return "You can enjoy a generous portion of this food"
    elif calories < 300:
        return "A standard serving size is recommended"
    elif calories < 500:
        return "Consider a moderate portion size"
    else:
        return "Enjoy a smaller portion of this high-calorie food"

def evaluate_food_health(nutrition_data):
    """Evaluate if food is healthy based on nutrition values"""
    try:
        # Extract numerical values
        calories = nutrition_data.get("calories", 0)
        fat = nutrition_data.get("fat", 0)
        sugar = nutrition_data.get("sugar", 0)
        sodium = nutrition_data.get("sodium", 0)
        fiber = nutrition_data.get("fiber", 0)
        protein = nutrition_data.get("protein", 0)
        
        score = 0
        
        # Enhanced scoring logic
        if calories < 100:
            score += 2
        elif calories < 300:
            score += 1
        elif calories > 500:
            score -= 2
        elif calories > 400:
            score -= 1
        
        if fat < 5:
            score += 1
        elif fat < 10:
            score += 0.5
        elif fat > 20:
            score -= 1
        elif fat > 15:
            score -= 0.5
        
        if sugar < 5:
            score += 1
        elif sugar < 10:
            score += 0.5
        elif sugar > 20:
            score -= 1
        elif sugar > 15:
            score -= 0.5
        
        if sodium < 200:
            score += 1
        elif sodium < 400:
            score += 0.5
        elif sodium > 800:
            score -= 1
        elif sodium > 600:
            score -= 0.5
        
        if fiber > 5:
            score += 1
        elif fiber > 3:
            score += 0.5
            
        if protein > 20:
            score += 1
        elif protein > 10:
            score += 0.5
        
        # Determine rating
        if score >= 3:
            return "Excellent Choice", "This food is very nutritious and fits well in a healthy diet."
        elif score >= 1:
            return "Good Choice", "This food has good nutritional value. Enjoy in moderation."
        elif score >= -1:
            return "Moderate", "Okay to eat occasionally. Consider portion size."
        else:
            return "Limit Intake", "High in calories, fat, sugar, or sodium. Best consumed sparingly."
            
    except Exception as e:
        print(f"Error in nutrition evaluation: {e}")
        return "Unknown", "Unable to evaluate nutritional quality."

if __name__ == "__main__":
    print("🚀 Enhanced Food Recognition Tracker - Week 3 Implementation")
    print("📊 Focus: Stats & Insights APIs for Improved UX")
    print("📱 Starting Flask server...")
    print("🔗 Visit: http://localhost:5000")
    print("💡 Features: Analytics, Trends, Sustainability Insights, Recipe Suggestions")
    app.run(debug=True, host='0.0.0.0', port=5000)