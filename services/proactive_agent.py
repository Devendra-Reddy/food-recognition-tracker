"""
Proactive AI Detection Agent
Monitors food detection quality and improves the system autonomously
"""
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict
import json

class ProactiveDetectionAgent:
    def __init__(self):
        self.is_running = False
        self.agent_thread = None
        
        # Storage for monitoring
        self.daily_stats = {
            'total_scans': 0,
            'low_confidence_detections': [],
            'average_confidence': 0,
            'categories_scanned': defaultdict(int),
            'last_reset': datetime.now()
        }
        
        # Agent reports storage
        self.daily_reports = []
        self.pending_actions = []
        
        # Configuration
        self.low_confidence_threshold = 50  # Below 50% triggers agent action
        self.report_interval = 86400  # 24 hours in seconds (set to 60 for testing)
        
    def start(self):
        """Start the autonomous agent"""
        if not self.is_running:
            self.is_running = True
            self.agent_thread = threading.Thread(target=self._agent_loop, daemon=True)
            self.agent_thread.start()
            print("🤖 Proactive Detection Agent started")
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        if self.agent_thread:
            self.agent_thread.join(timeout=5)
            print("🤖 Proactive Detection Agent stopped")
    
    def log_detection(self, food_name, confidence, category, detection_method):
        """Log each food detection for monitoring"""
        self.daily_stats['total_scans'] += 1
        self.daily_stats['categories_scanned'][category] += 1
        
        # Track low confidence detections
        if confidence < self.low_confidence_threshold:
            self.daily_stats['low_confidence_detections'].append({
                'food_name': food_name,
                'confidence': confidence,
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'method': detection_method
            })
        
        # Update average confidence
        total = self.daily_stats['total_scans']
        current_avg = self.daily_stats['average_confidence']
        self.daily_stats['average_confidence'] = (
            (current_avg * (total - 1) + confidence) / total
        )
    
    def _agent_loop(self):
        """Main agent loop - runs daily analysis"""
        while self.is_running:
            try:
                # Check if it's time for daily report
                time_since_last = datetime.now() - self.daily_stats['last_reset']
                
                if time_since_last.total_seconds() >= self.report_interval:
                    self._generate_daily_report()
                    self._reset_daily_stats()
                
                # Sleep for 1 hour between checks (for production)
                # Use 60 seconds for testing
                time.sleep(3600)  # 1 hour
                
            except Exception as e:
                print(f"Agent error: {e}")
                time.sleep(300)  # 5 minutes on error
    
    def _generate_daily_report(self):
        """Generate daily report and action items"""
        report = {
            'day': len(self.daily_reports) + 1,
            'timestamp': datetime.now().isoformat(),
            'activities': [],
            'recommendations': [],
            'stats': {
                'total_scans': self.daily_stats['total_scans'],
                'low_confidence_count': len(self.daily_stats['low_confidence_detections']),
                'average_confidence': round(self.daily_stats['average_confidence'], 1)
            }
        }
        
        # Activity 1: Scan summary
        report['activities'].append({
            'type': 'scan',
            'description': f"🔍 Scanned {self.daily_stats['total_scans']} images today",
            'details': f"Average confidence: {report['stats']['average_confidence']}%"
        })
        
        # Activity 2: Low confidence analysis
        low_conf = self.daily_stats['low_confidence_detections']
        if low_conf:
            # Group by category
            categories = defaultdict(list)
            for detection in low_conf:
                categories[detection['category']].append(detection)
            
            for category, detections in categories.items():
                avg_conf = sum(d['confidence'] for d in detections) / len(detections)
                
                report['activities'].append({
                    'type': 'low_confidence_found',
                    'description': f"⚠️ Found {len(detections)} low-confidence {category} detections",
                    'details': f"Average confidence: {avg_conf:.1f}%"
                })
                
                # Generate synthetic data suggestion
                synthetic_count = len(detections) * 10
                report['activities'].append({
                    'type': 'generate',
                    'description': f"🎨 Suggesting {synthetic_count} synthetic {category} images for training",
                    'details': f"Based on {len(detections)} low-confidence samples"
                })
                
                # Create pending action
                action = {
                    'id': f"action_day{report['day']}_{category}_{int(time.time())}",
                    'day': report['day'],
                    'category': category,
                    'imageCount': synthetic_count,
                    'lowConfSamples': len(detections),
                    'question': f"I analyzed {len(detections)} low-confidence {category} detections. Should I generate {synthetic_count} synthetic training images?",
                    'options': ['Yes, generate', 'Show samples first', 'No, not needed']
                }
                self.pending_actions.append(action)
        
        # Activity 3: Category distribution
        top_categories = sorted(
            self.daily_stats['categories_scanned'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_categories:
            report['activities'].append({
                'type': 'analysis',
                'description': f"📊 Top categories: {', '.join(f'{cat} ({count})' for cat, count in top_categories)}",
                'details': f"Total categories scanned: {len(self.daily_stats['categories_scanned'])}"
            })
        
        # Recommendations
        if len(low_conf) > 10:
            report['recommendations'].append({
                'type': 'training',
                'text': f"High volume of low-confidence detections ({len(low_conf)}). Priority: improve model training data."
            })
        
        if self.daily_stats['average_confidence'] < 70:
            report['recommendations'].append({
                'type': 'model',
                'text': f"Average confidence is {report['stats']['average_confidence']}%. Consider model fine-tuning or adding more training data."
            })
        
        # Save report
        self.daily_reports.insert(0, report)  # Most recent first
        
        # Keep only last 30 days
        if len(self.daily_reports) > 30:
            self.daily_reports = self.daily_reports[:30]
        
        print(f"🤖 Daily report generated: {len(low_conf)} low-confidence detections found")
    
    def _reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_stats = {
            'total_scans': 0,
            'low_confidence_detections': [],
            'average_confidence': 0,
            'categories_scanned': defaultdict(int),
            'last_reset': datetime.now()
        }
    
    def get_dashboard_data(self):
        """Get data for dashboard display"""
        return {
            'daily_reports': self.daily_reports[:10],  # Last 10 reports
            'pending_actions': self.pending_actions,
            'current_stats': {
                'total_scans_today': self.daily_stats['total_scans'],
                'low_confidence_today': len(self.daily_stats['low_confidence_detections']),
                'average_confidence_today': round(self.daily_stats['average_confidence'], 1),
                'is_running': self.is_running
            }
        }
    
    def handle_action_response(self, action_id, response):
        """Handle human response to pending action"""
        action = next((a for a in self.pending_actions if a['id'] == action_id), None)
        
        if not action:
            return {'success': False, 'error': 'Action not found'}
        
        # Remove from pending
        self.pending_actions = [a for a in self.pending_actions if a['id'] != action_id]
        
        # Log the decision
        result = {
            'success': True,
            'action_id': action_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        if response == 'Yes, generate':
            result['message'] = f"Queued generation of {action['imageCount']} synthetic {action['category']} images"
            # Here you would trigger actual synthetic data generation
            # For now, we just log the intent
            print(f"🎨 Would generate {action['imageCount']} synthetic {action['category']} images")
        
        elif response == 'Show samples first':
            result['message'] = "Preparing sample images for review"
            print(f"📸 Would show {action['lowConfSamples']} low-confidence samples")
        
        else:
            result['message'] = "Action dismissed"
        
        return result
    
    def trigger_immediate_report(self):
        """Manually trigger a report (for testing)"""
        if self.daily_stats['total_scans'] > 0:
            self._generate_daily_report()
            return {'success': True, 'message': 'Report generated'}
        else:
            return {'success': False, 'message': 'No data to report yet'}

# Global agent instance
_agent_instance = None

def get_proactive_agent():
    """Get or create the agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ProactiveDetectionAgent()
    return _agent_instance

def start_agent():
    """Start the agent"""
    agent = get_proactive_agent()
    agent.start()
    return agent

def stop_agent():
    """Stop the agent"""
    agent = get_proactive_agent()
    agent.stop()
