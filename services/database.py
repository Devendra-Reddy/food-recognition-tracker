#!/usr/bin/env python3
"""
Database Operations Module for Food Recognition Tracker
Week 3 Implementation with in-memory storage and MongoDB support
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# In-memory storage for development
_memory_store = {
    "food_entries": [],
    "user_sessions": {},
    "api_logs": []
}

class FoodDatabase:
    """Database operations for food recognition results"""
    
    def __init__(self, use_mongodb: bool = False):
        self.use_mongodb = use_mongodb
        self.mongodb_client = None
        self.db = None
        
        if use_mongodb:
            self._setup_mongodb()
        else:
            self._setup_file_storage()
    
    def _setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            from pymongo import MongoClient
            mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/food_tracker')
            self.mongodb_client = MongoClient(mongodb_uri)
            self.db = self.mongodb_client.get_default_database()
            print("✅ MongoDB connected")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("🔄 Falling back to file storage")
            self.use_mongodb = False
            self._setup_file_storage()
    
    def _setup_file_storage(self):
        """Setup file-based storage"""
        self.storage_dir = "data"
        os.makedirs(self.storage_dir, exist_ok=True)
        self.results_file = os.path.join(self.storage_dir, "food_results.json")
        
        # Load existing data
        self._load_from_file()
    
    def _load_from_file(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
                    _memory_store.update(data)
                    print(f"📂 Loaded {len(_memory_store['food_entries'])} food entries from file")
        except Exception as e:
            print(f"⚠️ Could not load from file: {e}")
    
    def _save_to_file(self):
        """Save data to JSON file"""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(_memory_store, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Could not save to file: {e}")
    
    def save_food_entry(self, entry: Dict[str, Any]) -> str:
        """
        Save a food recognition entry
        
        Args:
            entry: Dictionary containing food entry data
            
        Returns:
            Entry ID as string
        """
        try:
            # Add metadata
            entry_id = entry.get('id', str(uuid.uuid4()))
            timestamp = datetime.now().isoformat()
            
            full_entry = {
                'id': entry_id,
                'timestamp': timestamp,
                'created_at': timestamp,
                **entry
            }
            
            if self.use_mongodb:
                # Save to MongoDB
                collection = self.db.food_entries
                collection.insert_one(full_entry)
            else:
                # Save to memory and file
                _memory_store['food_entries'].append(full_entry)
                self._save_to_file()
            
            print(f"💾 Saved food entry: {entry.get('food_name', 'Unknown')} (ID: {entry_id[:8]}...)")
            return entry_id
            
        except Exception as e:
            print(f"❌ Error saving food entry: {e}")
            return ""
    
    def get_food_entries(self, limit: int = 50, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get food entries from database
        
        Args:
            limit: Maximum number of entries to return
            user_id: Filter by user ID (optional)
            
        Returns:
            List of food entries
        """
        try:
            if self.use_mongodb:
                # Query MongoDB
                collection = self.db.food_entries
                query = {}
                if user_id:
                    query['user_id'] = user_id
                
                entries = list(collection.find(query)
                             .sort('timestamp', -1)
                             .limit(limit))
                
                # Convert ObjectId to string for JSON serialization
                for entry in entries:
                    if '_id' in entry:
                        entry['_id'] = str(entry['_id'])
                
                return entries
            else:
                # Get from memory
                entries = _memory_store['food_entries']
                
                # Filter by user if specified
                if user_id:
                    entries = [e for e in entries if e.get('user_id') == user_id]
                
                # Sort by timestamp (newest first) and limit
                entries = sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)
                return entries[:limit]
                
        except Exception as e:
            print(f"❌ Error getting food entries: {e}")
            return []
    
    def get_food_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific food entry by ID"""
        try:
            if self.use_mongodb:
                collection = self.db.food_entries
                entry = collection.find_one({'id': entry_id})
                if entry and '_id' in entry:
                    entry['_id'] = str(entry['_id'])
                return entry
            else:
                for entry in _memory_store['food_entries']:
                    if entry.get('id') == entry_id:
                        return entry
                return None
                
        except Exception as e:
            print(f"❌ Error getting food entry by ID: {e}")
            return None
    
    def delete_food_entry(self, entry_id: str) -> bool:
        """Delete a food entry by ID"""
        try:
            if self.use_mongodb:
                collection = self.db.food_entries
                result = collection.delete_one({'id': entry_id})
                return result.deleted_count > 0
            else:
                original_length = len(_memory_store['food_entries'])
                _memory_store['food_entries'] = [
                    e for e in _memory_store['food_entries'] 
                    if e.get('id') != entry_id
                ]
                success = len(_memory_store['food_entries']) < original_length
                if success:
                    self._save_to_file()
                return success
                
        except Exception as e:
            print(f"❌ Error deleting food entry: {e}")
            return False
    
    def log_api_call(self, api_name: str, endpoint: str, status_code: int, 
                     response_time: float = None, error: str = None):
        """Log API call for monitoring"""
        try:
            log_entry = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'api_name': api_name,
                'endpoint': endpoint,
                'status_code': status_code,
                'response_time': response_time,
                'error': error
            }
            
            if self.use_mongodb:
                collection = self.db.api_logs
                collection.insert_one(log_entry)
            else:
                _memory_store['api_logs'].append(log_entry)
                
                # Keep only recent logs (last 1000)
                if len(_memory_store['api_logs']) > 1000:
                    _memory_store['api_logs'] = _memory_store['api_logs'][-1000:]
                
                self._save_to_file()
            
        except Exception as e:
            print(f"⚠️ Error logging API call: {e}")
    
    def get_api_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            from datetime import timedelta
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            if self.use_mongodb:
                collection = self.db.api_logs
                recent_logs = list(collection.find({
                    'timestamp': {'$gte': cutoff_time}
                }))
            else:
                recent_logs = [
                    log for log in _memory_store['api_logs']
                    if log.get('timestamp', '') >= cutoff_time
                ]
            
            # Calculate statistics
            total_calls = len(recent_logs)
            successful_calls = len([log for log in recent_logs if log.get('status_code', 0) == 200])
            failed_calls = total_calls - successful_calls
            
            api_breakdown = {}
            for log in recent_logs:
                api_name = log.get('api_name', 'unknown')
                if api_name not in api_breakdown:
                    api_breakdown[api_name] = {'success': 0, 'failed': 0}
                
                if log.get('status_code') == 200:
                    api_breakdown[api_name]['success'] += 1
                else:
                    api_breakdown[api_name]['failed'] += 1
            
            return {
                'period_hours': hours,
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': failed_calls,
                'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
                'api_breakdown': api_breakdown,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting API stats: {e}")
            return {'error': str(e)}
    
    def get_nutrition_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get nutrition trends over time"""
        try:
            from datetime import timedelta
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            entries = self.get_food_entries(limit=1000)
            recent_entries = [
                entry for entry in entries
                if entry.get('timestamp', '') >= cutoff_time
                and entry.get('nutrition', {}).get('calories')
            ]
            
            if not recent_entries:
                return {'error': 'No nutrition data available for the specified period'}
            
            # Calculate trends
            total_calories = 0
            total_protein = 0
            total_fat = 0
            total_carbs = 0
            food_types = {}
            
            for entry in recent_entries:
                nutrition = entry.get('nutrition', {})
                
                calories = float(str(nutrition.get('calories', 0)).replace('kcal', '').strip() or 0)
                protein = float(str(nutrition.get('protein', 0)).replace('g', '').strip() or 0)
                fat = float(str(nutrition.get('fat', 0)).replace('g', '').strip() or 0)
                carbs = float(str(nutrition.get('carbs', 0)).replace('g', '').strip() or 0)
                
                total_calories += calories
                total_protein += protein
                total_fat += fat
                total_carbs += carbs
                
                food_name = entry.get('food_name', 'unknown')
                food_types[food_name] = food_types.get(food_name, 0) + 1
            
            num_entries = len(recent_entries)
            
            return {
                'period_days': days,
                'total_entries': num_entries,
                'average_calories_per_item': round(total_calories / num_entries, 1) if num_entries > 0 else 0,
                'average_protein_per_item': round(total_protein / num_entries, 1) if num_entries > 0 else 0,
                'average_fat_per_item': round(total_fat / num_entries, 1) if num_entries > 0 else 0,
                'average_carbs_per_item': round(total_carbs / num_entries, 1) if num_entries > 0 else 0,
                'total_calories': round(total_calories, 1),
                'total_protein': round(total_protein, 1),
                'total_fat': round(total_fat, 1),
                'total_carbs': round(total_carbs, 1),
                'most_common_foods': dict(sorted(food_types.items(), key=lambda x: x[1], reverse=True)[:10]),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting nutrition trends: {e}")
            return {'error': str(e)}

# Global database instance
_db_instance = None

def get_database() -> FoodDatabase:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = FoodDatabase(use_mongodb=False)  # Use file storage by default
    return _db_instance

# Convenience functions for backward compatibility
def save_result(result: Dict[str, Any]) -> str:
    """Save a food recognition result"""
    db = get_database()
    return db.save_food_entry(result)

def get_results(limit: int = 50) -> List[Dict[str, Any]]:
    """Get food recognition results"""
    db = get_database()
    return db.get_food_entries(limit=limit)

def get_result_by_id(result_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific result by ID"""
    db = get_database()
    return db.get_food_entry_by_id(result_id)

def delete_result(result_id: str) -> bool:
    """Delete a result by ID"""
    db = get_database()
    return db.delete_food_entry(result_id)

# Test function
if __name__ == "__main__":
    # Test the database operations
    db = FoodDatabase(use_mongodb=False)
    
    # Test saving an entry
    test_entry = {
        'food_name': 'Test Apple',
        'nutrition': {'calories': 95, 'protein': 0.5, 'fat': 0.3},
        'health_rating': 'Good Choice',
        'api_used': 'test'
    }
    
    entry_id = db.save_food_entry(test_entry)
    print(f"Saved test entry with ID: {entry_id}")
    
    # Test retrieving entries
    entries = db.get_food_entries(limit=10)
    print(f"Retrieved {len(entries)} entries")
    
    # Test API logging
    db.log_api_call('roboflow', '/detect', 200, 1.5)
    stats = db.get_api_stats(hours=1)
    print(f"API stats: {stats}")
    
    # Test nutrition trends
    trends = db.get_nutrition_trends(days=1)
    print(f"Nutrition trends: {trends}")