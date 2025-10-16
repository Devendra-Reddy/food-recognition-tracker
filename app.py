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

# Import agent services first
try:
    from services.agent import get_nutrition_agent
    AGENT_ENABLED = True
except ImportError:
    AGENT_ENABLED = False
    print("⚠️ Agent not available")

try:
    from services.chat_support import get_chat_support
    CHAT_SUPPORT_ENABLED = True
except ImportError:
    CHAT_SUPPORT_ENABLED = False
    print("⚠️ Chat support not available")

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

# ===== CREATE FLASK APP HERE - BEFORE ANY ROUTES =====
app = Flask(__name__)
CORS(app)

# Upload folder configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

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

# Initialize agents AFTER Flask app
if AGENT_ENABLED:
    nutrition_agent = get_nutrition_agent()
    print("✅ Nutrition validation agent initialized")
else:
    nutrition_agent = None

if CHAT_SUPPORT_ENABLED:
    chat_support = get_chat_support()
    print("✅ Chat support initialized")
else:
    chat_support = None

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

# Comprehensive nutrition database (keep your existing NUTRITION_DB here)
NUTRITION_DB = {
    # ... your existing nutrition database ...
}

# Helper functions (keep all your existing helper functions here)
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def process_food_analysis(data, progress_callback):
    # ... your existing function ...
    pass

def detect_food_simple(image_path):
    # ... your existing function ...
    pass

def get_nutrition_data(food_name):
    # ... your existing function ...
    pass

def calculate_health_score(nutrition_data):
    # ... your existing function ...
    pass

def evaluate_food_health(nutrition_data):
    # ... your existing function ...
    pass

def get_category_label(category):
    # ... your existing function ...
    pass

def generate_portion_suggestion(food_name, nutrition_data):
    # ... your existing function ...
    pass

def update_user_analytics(food_name, nutrition_data, health_rating, category):
    # ... your existing function ...
    pass

# Register background job handler
if BACKGROUND_AGENT_ENABLED:
    background_agent.register_handler('food_analysis', process_food_analysis)

# ===== NOW ALL YOUR ROUTES - AFTER APP IS CREATED =====

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    # ... your existing route ...
    pass

@app.route("/api/agent/validate", methods=["POST"])
def validate_nutrition():
    # ... your existing route ...
    pass

@app.route("/api/agent/status", methods=["GET"])
def agent_status():
    # ... your existing route ...
    pass

@app.route("/api/chat/message", methods=["POST"])
def chat_message():
    # ... your existing route ...
    pass

@app.route("/api/chat/faq", methods=["GET"])
def get_faq():
    # ... your existing route ...
    pass

@app.route("/api/chat/search", methods=["POST"])
def search_faq():
    # ... your existing route ...
    pass

@app.route("/api/chat/support-ticket", methods=["POST"])
def create_support_ticket():
    # ... your existing route ...
    pass

@app.route("/api/chat/analytics", methods=["GET"])
def get_chat_analytics():
    # ... your existing route ...
    pass

@app.route("/api/chat/quick-replies", methods=["GET"])
def get_quick_replies():
    # ... your existing route ...
    pass

@app.route("/analyze", methods=["POST"])
def analyze():
    # ... your existing route ...
    pass

@app.route("/job/<job_id>", methods=["GET"])
def get_job_status(job_id):
    # ... your existing route ...
    pass

@app.route("/history", methods=["GET"])
def history():
    # ... your existing route ...
    pass

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    # ... your existing route ...
    pass

# Cleanup on shutdown
@app.teardown_appcontext
def shutdown_agent(exception=None):
    if BACKGROUND_AGENT_ENABLED and background_agent:
        background_agent.stop()

if __name__ == "__main__":
    print("🚀 Food Recognition Tracker - Enhanced Version")
    print("✅ Real-time food detection with Roboflow AI")
    print("✅ Accurate food classification")
    print("✅ Health recommendations & body requirements")
    print("✅ Background processing enabled")
    print("🔗 Visit: http://localhost:5000")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        if BACKGROUND_AGENT_ENABLED and background_agent:
            background_agent.stop()
