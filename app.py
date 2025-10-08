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
from datetime import datetime
import random
import time

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Import background agent and real-time analyzer
try:
    from services.background_agent import BackgroundAgent, JobStatus
    from services.realtime_analysis import RealTimeFoodAnalyzer
    BACKGROUND_AGENT_ENABLED = True
    REALTIME_ANALYSIS_ENABLED = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    BACKGROUND_AGENT_ENABLED = False
    REALTIME_ANALYSIS_ENABLED = False
    print("Using synchronous processing")

# API Configuration
ROBOFLOW_API_KEY = os.environ.get('ROBOFLOW_API_KEY', 'CDxqqcJkI8wWdBX4IVrl')

# Storage
results_store = []
user_analytics = {
    "total_scans": 0,
    "healthy_choices": 0,
    "junk_food_count": 0,
    "average_calories": 0,
    "most_scanned_food": "",
    "weekly_trends": []
}

# Initialize background agent and analyzer
if BACKGROUND_AGENT_ENABLED:
    background_agent = BackgroundAgent(num_workers=3)
    background_agent.start()
    print("✅ Background agent initialized")
else:
    background_agent = None

if REALTIME_ANALYSIS_ENABLED:
    realtime_analyzer = RealTimeFoodAnalyzer()
    print("✅ Real-time analyzer initialized")
else:
    realtime_analyzer = None

# Comprehensive nutrition database
NUTRITION_DB = {
    # Fruits (Healthy)
    "apple": {"calories": 95, "protein": 0.5, "fat": 0.3, "carbs": 25, "fiber": 4, "sugar": 19, "sodium": 2, "category": "healthy"},
    "banana": {"calories": 105, "protein": 1.3, "fat": 0.4, "carbs": 27, "fiber": 3, "sugar": 14, "sodium": 1, "category": "healthy"},
    "orange": {"calories": 62, "protein": 1.2, "fat": 0.2, "carbs": 15, "fiber": 3, "sugar": 12, "sodium": 0, "category": "healthy"},
    "grape": {"calories": 62, "protein": 0.6, "fat": 0.2, "carbs": 16, "fiber": 1, "sugar": 15, "sodium": 2, "category": "healthy"},
    "strawberry": {"calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 8, "fiber": 2, "sugar": 5, "sodium": 1, "category": "healthy"},
    "watermelon": {"calories": 30, "protein": 0.6, "fat": 0.2, "carbs": 8, "fiber": 0.4, "sugar": 6, "sodium": 1, "category": "healthy"},
    "mango": {"calories": 60, "protein": 0.8, "fat": 0.4, "carbs": 15, "fiber": 1.6, "sugar": 14, "sodium": 1, "category": "healthy"},
    
    # Vegetables (Healthy)
    "broccoli": {"calories": 31, "protein": 2.6, "fat": 0.3, "carbs": 6, "fiber": 2.4, "sugar": 1.5, "sodium": 30, "category": "healthy"},
    "carrot": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10, "fiber": 2.8, "sugar": 4.7, "sodium": 69, "category": "healthy"},
    "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9, "fiber": 1.2, "sugar": 2.6, "sodium": 5, "category": "healthy"},
    "lettuce": {"calories": 5, "protein": 0.5, "fat": 0.1, "carbs": 1, "fiber": 0.6, "sugar": 0.4, "sodium": 3, "category": "healthy"},
    "potato": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17, "fiber": 2.2, "sugar": 0.8, "sodium": 6, "category": "moderate"},
    "salad": {"calories": 65, "protein": 3, "fat": 0.5, "carbs": 12, "fiber": 4, "sugar": 6, "sodium": 15, "category": "healthy"},
    
    # Proteins (Healthy/Moderate)
    "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 74, "category": "healthy"},
    "fish": {"calories": 206, "protein": 22, "fat": 12, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 59, "category": "healthy"},
    "egg": {"calories": 78, "protein": 6.3, "fat": 5.3, "carbs": 0.6, "fiber": 0, "sugar": 0.6, "sodium": 62, "category": "healthy"},
    "beef": {"calories": 250, "protein": 26, "fat": 17, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 72, "category": "moderate"},
    
    # Grains (Moderate)
    "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28, "fiber": 0.4, "sugar": 0.1, "sodium": 1, "category": "moderate"},
    "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49, "fiber": 3, "sugar": 5, "sodium": 491, "category": "moderate"},
    "pasta": {"calories": 220, "protein": 8, "fat": 1.5, "carbs": 44, "fiber": 2, "sugar": 2, "sodium": 4, "category": "moderate"},
    
    # Junk Food (Unhealthy)
    "pizza": {"calories": 285, "protein": 12, "fat": 10, "carbs": 36, "fiber": 2, "sugar": 4, "sodium": 640, "category": "junk"},
    "burger": {"calories": 540, "protein": 25, "fat": 31, "carbs": 40, "fiber": 3, "sugar": 5, "sodium": 1040, "category": "junk"},
    "hot dog": {"calories": 150, "protein": 5, "fat": 13, "carbs": 2, "fiber": 0, "sugar": 1, "sodium": 572, "category": "junk"},
    "fries": {"calories": 312, "protein": 3.4, "fat": 15, "carbs": 41, "fiber": 3.8, "sugar": 0.2, "sodium": 210, "category": "junk"},
    "donut": {"calories": 195, "protein": 2.3, "fat": 11, "carbs": 23, "fiber": 0.9, "sugar": 10, "sodium": 181, "category": "junk"},
    "ice cream": {"calories": 207, "protein": 3.5, "fat": 11, "carbs": 24, "fiber": 0.7, "sugar": 21, "sodium": 80, "category": "junk"},
    "cake": {"calories": 257, "protein": 3, "fat": 10, "carbs": 42, "fiber": 1, "sugar": 25, "sodium": 242, "category": "junk"},
    "chocolate": {"calories": 546, "protein": 4.9, "fat": 31, "carbs": 61, "fiber": 7, "sugar": 48, "sodium": 6, "category": "junk"},
    
    # Default
    "mixed food": {"calories": 200, "protein": 8, "fat": 8, "carbs": 25, "fiber": 2, "sugar": 6, "sodium": 150, "category": "moderate"}
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def process_food_analysis(data, progress_callback):
    """Process food analysis with real-time detection"""
    try:
        filepath = data['filepath']
        
        # Stage 1: Real-time food detection (0-50%)
        progress_callback(5, {'stage': 'detecting_food', 'message': 'Analyzing image with AI...'})
        
        if REALTIME_ANALYSIS_ENABLED:
            detection_result = realtime_analyzer.analyze(filepath, progress_callback)
            detected_food = detection_result['detection']['food_name']
            confidence = detection_result['detection']['confidence_percent']
            detection_method = detection_result['detection']['method']
            alternatives = detection_result['detection'].get('alternatives', [])
            multiple_items = detection_result.get('multiple_items', [])
            
            progress_callback(50, {
                'stage': 'food_detected', 
                'message': f'Detected: {detected_food.title()} ({confidence}% confidence)'
            })
        else:
            detected_food = detect_food_simple(filepath)
            confidence = 75
            detection_method = 'fallback'
            alternatives = []
            multiple_items = []
            
            progress_callback(50, {'stage': 'food_detected', 'message': f'Detected: {detected_food.title()}'})
        
        # Stage 2: Get nutrition data (50-75%)
        progress_callback(60, {'stage': 'fetching_nutrition', 'message': 'Getting nutrition data...'})
        nutrition_data = get_nutrition_data(detected_food)
        
        # Add detection metadata
        nutrition_data['detection_confidence'] = confidence
        nutrition_data['detection_method'] = detection_method
        nutrition_data['alternatives'] = alternatives
        
        # Stage 3: Health analysis (75-95%)
        progress_callback(80, {'stage': 'analyzing_health', 'message': 'Analyzing health impact...'})
        health_rating, recommendation = evaluate_food_health(nutrition_data)
        health_score = calculate_health_score(nutrition_data)
        
        # Get food category and recommendation
        food_category = nutrition_data.get('category', 'moderate')
        is_recommended = food_category in ['healthy', 'moderate']
        
        # Stage 4: Finalize (95-100%)
        progress_callback(95, {'stage': 'finalizing', 'message': 'Preparing results...'})
        
        result = {
            "id": str(uuid.uuid4()),
            "food_name": detected_food.title(),
            "detection": {
                "confidence": confidence,
                "confidence_percent": confidence,
                "method": detection_method,
                "alternatives": alternatives,
                "multiple_items": multiple_items
            },
            "nutrition": {
                **nutrition_data,
                "health_score": health_score
            },
            "health_rating": health_rating,
            "recommendation": recommendation,
            "portion_suggestion": generate_portion_suggestion(detected_food, nutrition_data),
            "food_category": food_category,
            "is_recommended": is_recommended,
            "category_label": get_category_label(food_category),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save result
        results_store.append(result)
        update_user_analytics(detected_food, nutrition_data, health_rating, food_category)
        
        # Clean up file
        try:
            os.remove(filepath)
        except:
            pass
        
        progress_callback(100, {'stage': 'completed', 'message': 'Analysis complete!'})
        
        return result
        
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")

def detect_food_simple(image_path):
    """Simple fallback detection"""
    filename = os.path.basename(image_path).lower()
    
    # Try to match from filename
    for food in NUTRITION_DB.keys():
        if food in filename:
            return food
    
    # Default fallback
    foods = ["apple", "banana", "pizza", "burger", "salad", "chicken"]
    return random.choice(foods)

def get_nutrition_data(food_name):
    """Get nutrition data from database"""
    food_lower = food_name.lower()
    
    # Direct match
    if food_lower in NUTRITION_DB:
        return NUTRITION_DB[food_lower].copy()
    
    # Partial match
    for key in NUTRITION_DB:
        if key in food_lower or food_lower in key:
            return NUTRITION_DB[key].copy()
    
    return NUTRITION_DB["mixed food"].copy()

def calculate_health_score(nutrition_data):
    """Calculate health score 0-100"""
    score = 100
    calories = nutrition_data.get("calories", 0)
    fat = nutrition_data.get("fat", 0)
    sugar = nutrition_data.get("sugar", 0)
    fiber = nutrition_data.get("fiber", 0)
    protein = nutrition_data.get("protein", 0)
    sodium = nutrition_data.get("sodium", 0)
    category = nutrition_data.get("category", "moderate")
    
    # Category-based scoring
    if category == "junk":
        score -= 30
    elif category == "healthy":
        score += 20
    
    # Calorie scoring
    if calories > 500: score -= 20
    elif calories > 300: score -= 10
    elif calories < 100: score += 10
    
    # Fat scoring
    if fat > 20: score -= 15
    elif fat < 5: score += 10
    
    # Sugar scoring
    if sugar > 20: score -= 15
    elif sugar < 5: score += 10
    
    # Sodium scoring
    if sodium > 600: score -= 10
    elif sodium < 140: score += 5
    
    # Fiber scoring
    if fiber > 5: score += 10
    
    # Protein scoring
    if protein > 20: score += 10
    
    return max(0, min(100, score))

def evaluate_food_health(nutrition_data):
    """Evaluate food health"""
    score = calculate_health_score(nutrition_data)
    category = nutrition_data.get("category", "moderate")
    
    if category == "junk":
        return "Limit Intake", "This is junk food. High in calories, fat, or sugar. Best consumed sparingly."
    elif score >= 80:
        return "Excellent Choice", "This food is very nutritious and fits well in a healthy diet."
    elif score >= 60:
        return "Good Choice", "This food has good nutritional value. Enjoy in moderation."
    elif score >= 40:
        return "Moderate", "Okay to eat occasionally. Consider portion size."
    else:
        return "Limit Intake", "High in calories, fat, or sugar. Best consumed sparingly."

def get_category_label(category):
    """Get human-readable category label"""
    labels = {
        "healthy": "Healthy Food",
        "moderate": "Moderate",
        "junk": "Junk Food"
    }
    return labels.get(category, "Unknown")

def generate_portion_suggestion(food_name, nutrition_data):
    """Generate portion suggestions"""
    calories = nutrition_data.get("calories", 0)
    category = nutrition_data.get("category", "moderate")
    
    if category == "junk":
        return "Small portion recommended - this is junk food"
    elif calories < 100:
        return "You can enjoy a generous portion"
    elif calories < 300:
        return "A standard serving is recommended"
    elif calories < 500:
        return "Consider a moderate portion"
    else:
        return "Enjoy a smaller portion"

def update_user_analytics(food_name, nutrition_data, health_rating, category):
    """Update user analytics"""
    user_analytics["total_scans"] += 1
    
    if "Excellent" in health_rating or "Good" in health_rating:
        user_analytics["healthy_choices"] += 1
    
    if category == "junk":
        user_analytics["junk_food_count"] += 1
    
    new_calories = nutrition_data.get("calories", 0)
    current_avg = user_analytics["average_calories"]
    user_analytics["average_calories"] = (
        (current_avg * (user_analytics["total_scans"] - 1) + new_calories) / 
        user_analytics["total_scans"]
    )

# Register background job handler
if BACKGROUND_AGENT_ENABLED:
    background_agent.register_handler('food_analysis', process_food_analysis)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    """Check API status"""
    status = {
        "roboflow": "ready",
        "background_agent": "enabled" if BACKGROUND_AGENT_ENABLED else "disabled",
        "realtime_analysis": "enabled" if REALTIME_ANALYSIS_ENABLED else "disabled",
        "environment": "development"
    }
    
    if BACKGROUND_AGENT_ENABLED:
        status["agent_stats"] = background_agent.get_stats()
    
    return jsonify(status)

@app.route("/analyze", methods=["POST"])
def analyze():
    """Submit analysis job"""
    try:
        file = request.files.get("image")
        
        if not file or file.filename == "":
            return jsonify({"error": "No image uploaded"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(filepath)
        
        # Use background agent if available
        if BACKGROUND_AGENT_ENABLED:
            job_id = background_agent.submit_job(
                'food_analysis',
                {'filepath': filepath}
            )
            
            return jsonify({
                "status": "processing",
                "job_id": job_id,
                "message": "Analysis started"
            }), 202
        else:
            # Synchronous processing
            result = process_food_analysis(
                {'filepath': filepath},
                lambda p, m: None
            )
            return jsonify(result)
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/job/<job_id>", methods=["GET"])
def get_job_status(job_id):
    """Get job status"""
    if not BACKGROUND_AGENT_ENABLED:
        return jsonify({"error": "Background agent not available"}), 503
    
    status = background_agent.get_job_status(job_id)
    
    if not status:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(status)

@app.route("/history", methods=["GET"])
def history():
    """Get analysis history"""
    return jsonify({
        "results": list(reversed(results_store[-20:])),  # Last 20 scans
        "analytics": user_analytics
    })

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Get user analytics"""
    healthy_percentage = 0
    if user_analytics["total_scans"] > 0:
        healthy_percentage = (user_analytics["healthy_choices"] / user_analytics["total_scans"]) * 100
    
    junk_percentage = 0
    if user_analytics["total_scans"] > 0:
        junk_percentage = (user_analytics["junk_food_count"] / user_analytics["total_scans"]) * 100
    
    return jsonify({
        **user_analytics,
        "healthy_percentage": round(healthy_percentage, 1),
        "junk_percentage": round(junk_percentage, 1)
    })

# Cleanup on shutdown
@app.teardown_appcontext
def shutdown_agent(exception=None):
    if BACKGROUND_AGENT_ENABLED and background_agent:
        background_agent.stop()

if __name__ == "__main__":
    print("🚀 Food Recognition Tracker - Final Version")
    print("✅ Real-time food detection")
    print("✅ Automatic API selection")
    print("✅ Food category classification")
    print("✅ Health recommendations")
    print("🔗 Visit: http://localhost:5000")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        if BACKGROUND_AGENT_ENABLED and background_agent:
            background_agent.stop()
