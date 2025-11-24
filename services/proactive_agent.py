import json, os
from datetime import datetime
class ProactiveAgent:
    def __init__(self, log_file='logs/agent_scans.json'):
        self.log_file=log_file; self.scans=[]
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if os.path.exists(self.log_file):
            try: self.scans=json.load(open(self.log_file,'r'))
            except Exception: self.scans=[]
    def log(self, image_id, food_name, confidence, category):
        self.scans.append({'image_id':image_id,'food_name':food_name,'confidence':float(confidence),'category':category,'timestamp':datetime.now().isoformat()})
        try: json.dump(self.scans, open(self.log_file,'w'), indent=2)
        except Exception: pass
    def status(self):
        today=datetime.now().date().isoformat()
        today_scans=sum(1 for s in self.scans if s['timestamp'][:10]==today)
        avg= round(sum(s['confidence'] for s in self.scans)/len(self.scans),3) if self.scans else 0.0
        return {'status':'ok','total_scans':len(self.scans),'today_scans':today_scans,'average_confidence':avg}
