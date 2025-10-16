#!/usr/bin/env python3
"""
Chat Support Service for Food Recognition Tracker
Provides backend support for chat assistant with FAQ and support tickets
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid
import json


class ChatSupportService:
    """Handles chat support, FAQs, and support tickets"""
    
    def __init__(self):
        self.faq_database = self._load_faq()
        self.support_tickets = []
        self.chat_logs = []
    
    def _load_faq(self) -> Dict[str, Dict]:
        """Load FAQ database"""
        return {
            "upload_issues": {
                "question": "Why can't I upload my image?",
                "answer": "Check that your image is in a supported format (JPG, PNG, WEBP, GIF) and under 16MB. Also ensure you have a stable internet connection.",
                "category": "upload",
                "keywords": ["upload", "image", "photo", "can't", "won't"]
            },
            "detection_accuracy": {
                "question": "Why is the food detection inaccurate?",
                "answer": "For best accuracy: use clear, well-lit photos; center the food; avoid blurry images; and photograph single items when possible.",
                "category": "accuracy",
                "keywords": ["wrong", "inaccurate", "incorrect", "detection", "recognize"]
            },
            "processing_time": {
                "question": "Why is analysis taking so long?",
                "answer": "Food analysis typically takes 15-30 seconds. Slower times can be due to internet connection, server load, or large image files. Try refreshing if it takes over 1 minute.",
                "category": "performance",
                "keywords": ["slow", "long", "waiting", "stuck", "loading"]
            },
            "nutrition_data": {
                "question": "How accurate is the nutrition information?",
                "answer": "Nutrition data comes from our comprehensive database of 60+ foods. Values are per standard serving and may vary based on preparation method and portion size.",
                "category": "nutrition",
                "keywords": ["nutrition", "calorie", "accurate", "data", "information"]
            },
            "health_score": {
                "question": "How is the health score calculated?",
                "answer": "Health scores (0-100) are based on calories, fat, sugar, sodium, fiber, protein, and food category. Higher scores indicate healthier options.",
                "category": "health",
                "keywords": ["health score", "calculate", "rating", "healthy"]
            },
            "history_tracking": {
                "question": "Where can I see my scan history?",
                "answer": "Scroll down to the 'Analytics & History' section to view your past scans, statistics, and trends. History is saved in your browser automatically.",
                "category": "features",
                "keywords": ["history", "past", "previous", "scans", "track"]
            },
            "supported_foods": {
                "question": "What foods can the app recognize?",
                "answer": "The app recognizes 60+ common foods including fruits, vegetables, proteins, grains, and junk food. New foods are added regularly!",
                "category": "features",
                "keywords": ["foods", "recognize", "support", "list", "detect"]
            },
            "privacy": {
                "question": "Is my food data private?",
                "answer": "Yes! All data is stored locally in your browser. We don't store or share your food images or analysis history on external servers.",
                "category": "privacy",
                "keywords": ["privacy", "data", "safe", "secure", "store"]
            }
        }
    
    def search_faq(self, query: str) -> List[Dict]:
        """Search FAQ based on query"""
        query_lower = query.lower()
        results = []
        
        for faq_id, faq_data in self.faq_database.items():
            # Check if query matches keywords
            if any(keyword in query_lower for keyword in faq_data["keywords"]):
                results.append({
                    "id": faq_id,
                    "question": faq_data["question"],
                    "answer": faq_data["answer"],
                    "category": faq_data["category"]
                })
        
        return results[:3]  # Return top 3 results
    
    def create_support_ticket(self, user_message: str, user_email: Optional[str] = None) -> str:
        """Create a support ticket"""
        ticket_id = str(uuid.uuid4())[:8].upper()
        
        ticket = {
            "ticket_id": ticket_id,
            "message": user_message,
            "email": user_email,
            "status": "open",
            "priority": "normal",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "responses": []
        }
        
        self.support_tickets.append(ticket)
        print(f"📧 Support ticket created: {ticket_id}")
        
        return ticket_id
    
    def log_chat_interaction(self, user_message: str, bot_response: str, session_id: Optional[str] = None):
        """Log chat interaction for analytics"""
        log_entry = {
            "session_id": session_id or str(uuid.uuid4()),
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat()
        }
        
        self.chat_logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(self.chat_logs) > 1000:
            self.chat_logs = self.chat_logs[-1000:]
    
    def get_quick_replies(self) -> List[Dict]:
        """Get quick reply suggestions"""
        return [
            {"id": "how_to_use", "text": "📖 How to use", "action": "how-to-use"},
            {"id": "upload_help", "text": "📸 Upload help", "action": "upload-help"},
            {"id": "nutrition_info", "text": "🥗 Nutrition info", "action": "nutrition-info"},
            {"id": "accuracy_tips", "text": "🎯 Accuracy tips", "action": "accuracy"}
        ]
    
    def get_support_response(self, message: str) -> Dict:
        """Get intelligent support response"""
        msg = message.lower()
        
        # Check for urgent issues
        if any(word in msg for word in ["error", "broken", "crash", "bug"]):
            return {
                "type": "urgent",
                "message": "I'm sorry you're experiencing issues! Here are immediate steps:\n\n1. Refresh the page\n2. Clear browser cache\n3. Try a different browser\n\nIf the problem persists, I can create a support ticket for you.",
                "actions": [
                    {"text": "Create Support Ticket", "action": "create_ticket"}
                ]
            }
        
        # Search FAQ
        faq_results = self.search_faq(message)
        if faq_results:
            return {
                "type": "faq",
                "message": faq_results[0]["answer"],
                "related_questions": [
                    {"question": r["question"], "id": r["id"]} 
                    for r in faq_results[1:3]
                ]
            }
        
        # Default helpful response
        return {
            "type": "general",
            "message": "I'm here to help! I can assist with:\n\n• App usage and features\n• Upload and photo tips\n• Nutrition information\n• Technical issues\n\nWhat would you like to know more about?",
            "quick_replies": self.get_quick_replies()
        }
    
    def get_analytics(self) -> Dict:
        """Get chat analytics"""
        total_chats = len(self.chat_logs)
        total_tickets = len(self.support_tickets)
        open_tickets = len([t for t in self.support_tickets if t["status"] == "open"])
        
        return {
            "total_chat_interactions": total_chats,
            "total_support_tickets": total_tickets,
            "open_tickets": open_tickets,
            "average_response_time": "< 1s",  # Instant bot responses
            "most_common_topics": self._get_common_topics()
        }
    
    def _get_common_topics(self) -> Dict[str, int]:
        """Analyze most common topics from chat logs"""
        topics = {
            "upload": 0,
            "accuracy": 0,
            "nutrition": 0,
            "features": 0,
            "technical": 0
        }
        
        for log in self.chat_logs:
            msg = log["user_message"].lower()
            if any(word in msg for word in ["upload", "image", "photo"]):
                topics["upload"] += 1
            if any(word in msg for word in ["wrong", "accurate", "detect"]):
                topics["accuracy"] += 1
            if any(word in msg for word in ["nutrition", "calorie", "health"]):
                topics["nutrition"] += 1
            if any(word in msg for word in ["feature", "how", "use"]):
                topics["features"] += 1
            if any(word in msg for word in ["error", "bug", "broken"]):
                topics["technical"] += 1
        
        return topics


# Global instance
_chat_support = None

def get_chat_support() -> ChatSupportService:
    """Get global chat support instance"""
    global _chat_support
    if _chat_support is None:
        _chat_support = ChatSupportService()
    return _chat_support


# Test the service
if __name__ == "__main__":
    support = ChatSupportService()
    
    # Test FAQ search
    print("=== Testing FAQ Search ===")
    results = support.search_faq("My image won't upload")
    for r in results:
        print(f"Q: {r['question']}")
        print(f"A: {r['answer']}\n")
    
    # Test support ticket
    print("=== Testing Support Ticket ===")
    ticket_id = support.create_support_ticket("App is not loading properly", "user@example.com")
    print(f"Ticket ID: {ticket_id}")
    
    # Test analytics
    print("\n=== Testing Analytics ===")
    support.log_chat_interaction("How do I upload?", "Here's how to upload...")
    support.log_chat_interaction("Wrong food detected", "Try these tips...")
    analytics = support.get_analytics()
    print(f"Analytics: {analytics}")
