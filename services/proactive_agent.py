import json, os
from datetime import datetime
from collections import defaultdict

class ProactiveAgent:
    def __init__(self, log_file='logs/agent_scans.json'):
        self.log_file = log_file
        self.scans = []
        self.low_confidence_items = defaultdict(list)
        self.agent_reports = []
        self.synthetic_images_generated = 0
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if os.path.exists(self.log_file):
            try:
                self.scans = json.load(open(self.log_file,'r'))
            except Exception:
                self.scans = []

    def save(self):
        try:
            json.dump(self.scans, open(self.log_file,'w'), indent=2)
        except Exception:
            pass

    def log_scan(self, image_id, food_name, confidence, category):
        entry = {
            'image_id': image_id,
            'food_name': food_name,
            'confidence': float(confidence),
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        self.scans.append(entry); self.save()
        if confidence < 0.5:
            self.low_confidence_items[food_name].append(entry)

    def record_synthetic_generation(self, food_name, count):
        self.synthetic_images_generated += int(count)

    def get_agent_status(self):
        today = datetime.now().date().isoformat()
        today_scans = sum(1 for s in self.scans if s['timestamp'][:10]==today)
        avg_conf = round(sum(s['confidence'] for s in self.scans)/len(self.scans), 3) if self.scans else 0.0
        return {
            'status': 'ok',
            'total_scans': len(self.scans),
            'today_scans': today_scans,
            'average_confidence': avg_conf,
            'unique_low_conf_foods': len(self.low_confidence_items),
            'synthetic_images_generated': self.synthetic_images_generated
        }

    def generate_daily_report(self):
        r = {'timestamp': datetime.now().isoformat(), 'summary': self.get_agent_status()}
        self.agent_reports.append(r)
        return r
