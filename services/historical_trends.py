import json, os
from datetime import datetime, timedelta
from collections import defaultdict

class HistoricalTrendsTracker:
    def __init__(self, history_file='data/detection_history.json'):
        self.history_file = history_file
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            json.dump([], open(self.history_file,'w'))

    def _load(self):
        try:
            return json.load(open(self.history_file,'r'))
        except Exception:
            return []

    def _save(self, data):
        json.dump(data, open(self.history_file,'w'), indent=2)

    def log_detection(self, food_name, confidence, category, model_used):
        data = self._load()
        data.append({
            'food_name': food_name,
            'confidence': float(confidence),
            'category': category,
            'model': model_used,
            'timestamp': datetime.now().isoformat()
        })
        self._save(data)

    def get_daily_trends(self, days=7):
        data = self._load()
        cutoff = datetime.now() - timedelta(days=days)
        bins = defaultdict(int)
        for d in data:
            ts = datetime.fromisoformat(d['timestamp'])
            if ts >= cutoff:
                bins[ts.strftime('%Y-%m-%d')] += 1
        return [{'date':k,'count':v} for k,v in sorted(bins.items())]

    def get_weekly_trends(self, weeks=4):
        data = self._load()
        cutoff = datetime.now() - timedelta(days=7*weeks)
        bins = defaultdict(int)
        for d in data:
            ts = datetime.fromisoformat(d['timestamp'])
            if ts >= cutoff:
                yearweek = ts.strftime('%Y-W%U')
                bins[yearweek]+=1
        return [{'week':k,'count':v} for k,v in sorted(bins.items())]

    def get_popular_foods(self, days=30, top_n=10):
        data = self._load()
        cutoff = datetime.now() - timedelta(days=days)
        counts = defaultdict(lambda: {'count':0,'confs':[]})
        for d in data:
            ts = datetime.fromisoformat(d['timestamp'])
            if ts >= cutoff:
                counts[d['food_name']]['count'] += 1
                counts[d['food_name']]['confs'].append(d['confidence'])
        rows = []
        for f,v in counts.items():
            avg = round(sum(v['confs'])/len(v['confs']),2) if v['confs'] else 0.0
            rows.append({'food_name':f,'count':v['count'],'avg_confidence':avg,'trend':'stable'})
        rows.sort(key=lambda r: (-r['count'], -r['avg_confidence']))
        return rows[:top_n]
