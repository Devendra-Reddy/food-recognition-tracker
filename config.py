#!/usr/bin/env python3
"""
Configuration settings for Food Recognition Tracker
Week 1-2 MVP Implementation
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'food-tracker-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Roboflow API Configuration
    ROBOFLOW_API_KEY = 'CDxqqcJkI8wWdBX4IVrl'
    ROBOFLOW_WORKFLOW_URL = 'https://app.roboflow.com/workflows/mobile/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3JrZmxvd0lkIjoiUHVsaXJSbjU2dzM5Y3prcHM2UnkiLCJ3b3Jrc3BhY2VJZCI6IjcxbjNXdUJZS2dTMjc0VUVzbjgyTHkwUzI0SjIiLCJ1c2VySWQiOiI3MW4zV3VCWUtnUzI3NFVFc244Mkx5MFMyNEoyIiwiaWF0IjoxNzU4MzE3MTI5fQ.-OSp1t6L0Qw_Io3rNhpf4kIN7Ac9ajwQk9PkcJjomRc'
    ROBOFLOW_MODEL_ENDPOINT = 'https://detect.roboflow.com/food-recognition/1'
    
    # Nutritionix API Configuration (Week 2)
    NUTRITIONIX_APP_ID = os.environ.get('NUTRITIONIX_APP_ID') or 'your_nutritionix_app_id'
    NUTRITIONIX_API_KEY = os.environ.get('NUTRITIONIX_API_KEY') or 'your_nutritionix_api_key'
    NUTRITIONIX_BASE_URL = 'https://trackapi.nutritionix.com/v2'
    
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/food_tracker'
    MONGODB_DB_NAME = 'food_tracker'
    
    # Redis Configuration (for caching)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100 per hour, 10 per minute"
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Development database
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/food_tracker_dev'
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    MONGODB_URI = 'mongodb://localhost:27017/food_tracker_test'
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Test file upload settings
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB for testing

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGODB_URI = os.environ.get('MONGODB_URI')
    NUTRITIONIX_APP_ID = os.environ.get('NUTRITIONIX_APP_ID')
    NUTRITIONIX_API_KEY = os.environ.get('NUTRITIONIX_API_KEY')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# API Endpoints Configuration
class APIEndpoints:
    """API endpoint configurations"""
    
    # Roboflow API endpoints
    ROBOFLOW_DETECT = f"https://detect.roboflow.com/{Config.ROBOFLOW_API_KEY}"
    ROBOFLOW_WORKFLOW = Config.ROBOFLOW_WORKFLOW_URL
    
    # Nutritionix API endpoints
    NUTRITIONIX_NATURAL = f"{Config.NUTRITIONIX_BASE_URL}/natural/nutrients"
    NUTRITIONIX_SEARCH = f"{Config.NUTRITIONIX_BASE_URL}/search/instant"
    
    # External food databases
    USDA_FOOD_DATA = "https://api.nal.usda.gov/fdc/v1/foods/search"
    OPEN_FOOD_FACTS = "https://world.openfoodfacts.org/api/v0/product"

# Food Recognition Model Configuration
class ModelConfig:
    """Model-specific configuration"""
    
    # Image processing settings
    MAX_IMAGE_SIZE = (1024, 1024)
    SUPPORTED_FORMATS = ['PNG', 'JPEG', 'JPG', 'WEBP', 'GIF']
    IMAGE_QUALITY = 85
    
    # Recognition thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.5  # 50% minimum confidence
    MAX_PREDICTIONS = 5  # Maximum number of predictions to return
    
    # Model performance settings
    TIMEOUT_SECONDS = 30  # API timeout
    RETRY_ATTEMPTS = 3  # Number of retry attempts
    RETRY_DELAY = 1  # Delay between retries in seconds

# Database Schema Configuration
class DatabaseSchema:
    """Database collection and field configurations"""
    
    # Collection names
    FOOD_ENTRIES = 'food_entries'
    USER_PROFILES = 'user_profiles'
    NUTRITION_CACHE = 'nutrition_cache'
    API_LOGS = 'api_logs'
    
    # Index configurations
    INDEXES = {
        FOOD_ENTRIES: [
            ('timestamp', -1),
            ('user_id', 1),
            ('food_name', 'text')
        ],
        NUTRITION_CACHE: [
            ('food_name', 1),
            ('created_at', 1)
        ],
        API_LOGS: [
            ('timestamp', -1),
            ('endpoint', 1),
            ('status_code', 1)
        ]
    }

# Feature Flags
class FeatureFlags:
    """Feature toggle configuration"""
    
    # Week 1-2 features (enabled)
    ENABLE_IMAGE_UPLOAD = True
    ENABLE_ROBOFLOW_API = True
    ENABLE_NUTRITION_API = True
    ENABLE_DEMO_MODE = True
    
    # Future features (disabled for MVP)
    ENABLE_USER_AUTH = False
    ENABLE_DAILY_TRACKING = False
    ENABLE_SOCIAL_FEATURES = False
    ENABLE_BARCODE_SCANNER = False
    ENABLE_RECIPE_SUGGESTIONS = False
    
    # Development features
    ENABLE_DEBUG_LOGS = True
    ENABLE_API_METRICS = True
    ENABLE_ERROR_REPORTING = True

# Get configuration based on environment
def get_config():
    """Return configuration based on environment variable"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])

# Validation functions
def validate_api_keys():
    """Validate that required API keys are present"""
    required_keys = {
        'ROBOFLOW_API_KEY': Config.ROBOFLOW_API_KEY,
    }
    
    missing_keys = []
    for key_name, key_value in required_keys.items():
        if not key_value or key_value.startswith('your_'):
            missing_keys.append(key_name)
    
    if missing_keys:
        print(f"Warning: Missing API keys: {', '.join(missing_keys)}")
        print("Please check your environment variables or update config.py")
    
    return len(missing_keys) == 0

# Initialize validation on import
if __name__ != '__main__':
    validate_api_keys()
