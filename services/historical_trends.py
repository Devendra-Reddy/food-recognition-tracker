import json, os
from datetime import datetime, timedelta
from collections import defaultdict
class HistoricalTrendsTracker:
    def __init__(self, path='data/detection_history.json'):
        self.path=path; os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path): json.dump([], open(self.path,'w'))
    def _load(self): 
        try: return json.load(open(self.path,'r'))
        except Exception: return []
    def _save(self,d): json.dump(d, open(self.path,'w'), indent=2)
    def log_detection(self, food_name, confidence, category, model_used, image_id):
        d=self._load(); d.append({'food_name':food_name,'confidence':float(confidence),'category':category,'model':model_used,'image_id':image_id,'timestamp':datetime.now().isoformat()}); self._save(d)
    def popular(self, days=30, top_n=10):
        d=self._load(); cutoff=datetime.now()-timedelta(days=days); from collections import defaultdict
        cnt=defaultdict(lambda:{'c':0,'s':0})
        for x in d:
            ts=datetime.fromisoformat(x['timestamp'])
            if ts>=cutoff: cnt[x['food_name']]['c']+=1; cnt[x['food_name']]['s']+=x['confidence']
        rows=[{'food_name':k,'count':v['c'],'avg_confidence': round(v['s']/v['c'],2) if v['c'] else 0,'trend':'stable'} for k,v in cnt.items()]
        rows.sort(key=lambda r: (-r['count'], -r['avg_confidence'])); return rows[:top_n]
    def daily(self, days=7):
        d=self._load(); cutoff=datetime.now()-timedelta(days=days); from collections import defaultdict
        bins=defaultdict(int)
        for x in d:
            ts=datetime.fromisoformat(x['timestamp'])
            if ts>=cutoff: bins[ts.strftime('%Y-%m-%d')]+=1
        return [{'date':k,'count':v} for k,v in sorted(bins.items())]
