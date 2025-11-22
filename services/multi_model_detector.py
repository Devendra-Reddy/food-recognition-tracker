import statistics, io, base64, re
from datetime import datetime
from collections import defaultdict
try:
    from PIL import Image
except Exception:
    Image = None
from services.expanded_food_db import ExpandedFoodDatabase

class MultiModelDetector:
    def __init__(self):
        self.models = {
            'vit_large': {'name':'ViT-Large','enabled':True,'strengths':['food','textures'],'speed':'slow','accuracy_weight':0.40},
            'resnet50': {'name':'ResNet-50','enabled':True,'strengths':['general','objects'],'speed':'fast','accuracy_weight':0.35},
            'efficientnet': {'name':'EfficientNet-B3','enabled':True,'strengths':['colors','food'],'speed':'medium','accuracy_weight':0.25}
        }
        self.history = defaultdict(list)

    def _dominant_color_hint(self, image_data):
        if not Image: return None
        try:
            if isinstance(image_data, dict) and 'base64' in image_data:
                img = Image.open(io.BytesIO(base64.b64decode(image_data['base64']))).convert('RGB').resize((32,32))
            else:
                return None
            pixels = list(img.getdata())
            r = sum(p[0] for p in pixels)/len(pixels)
            g = sum(p[1] for p in pixels)/len(pixels)
            b = sum(p[2] for p in pixels)/len(pixels)
            if g>r*1.1 and g>b*1.1: return 'green'
            if r>g*1.1 and r>b*1.1: return 'red'
            if r>200 and g>200 and b>200: return 'white'
            if r>180 and g>160 and b<120: return 'yellow'
            return 'brown'
        except Exception:
            return None

    def predict_label_from_image(self, image_data, filename_hint=None):
        db = ExpandedFoodDatabase()
        if filename_hint:
            canon, score = db.canonicalize(filename_hint)
            if canon and score>=0.6: return canon, max(0.55, min(0.9, score))
        color = self._dominant_color_hint(image_data)
        candidates = []
        if color=='green':
            candidates = ['Caesar Salad','Greek Salad','Caprese Salad','Veggie Pizza']
        elif color=='red':
            candidates = ['Margherita Pizza','Pepperoni Pizza','Spaghetti Bolognese','Butter Chicken']
        elif color=='yellow':
            candidates = ['Fettuccine Alfredo','Masala Dosa','Aloo Paratha']
        else:
            candidates = [f['name'] for f in db.all_foods[:30]]
        import random
        label = random.choice(candidates) if candidates else 'Margherita Pizza'
        canon,_ = db.canonicalize(label)
        return canon or label, 0.65

    def _simulate_model_detection(self, model_id, model_info):
        import random
        base = random.uniform(0.5, 0.95)
        if model_info['speed']=='fast': base*=random.uniform(0.92,1.0)
        elif model_info['speed']=='slow': base*=random.uniform(0.96,1.03)
        return {
            'model': model_info['name'],
            'confidence': round(max(0.1,min(0.99,base)), 3),
            'timestamp': datetime.now().isoformat()
        }

    def detect_with_all_models(self, image_data, filename_hint=None):
        # In production call real models here; for now simulate confidences and add heuristic label
        results = {}
        for mid, mi in self.models.items():
            if not mi['enabled']: continue
            results[mid] = self._simulate_model_detection(mid, mi)

        # Weighted average
        ws, tw, confs = 0.0, 0.0, []
        for mid, res in results.items():
            w = self.models[mid]['accuracy_weight']
            ws += res['confidence']*w; tw += w; confs.append(res['confidence'])
        consensus = ws/tw if tw>0 else 0.0

        # model agreement heuristic
        if not confs:
            agreement = 'none'
        else:
            span = max(confs)-min(confs)
            agreement = 'high' if span<0.08 else ('medium' if span<0.18 else 'low')

        predicted_label, heuristic_conf = self.predict_label_from_image(image_data, filename_hint)
        return {
            'predicted_label': predicted_label,
            'predicted_label_confidence': heuristic_conf,
            'consensus_confidence': round(consensus,3),
            'model_agreement': agreement,
            'all_results': results,
            'models_used': len(results),
            'best_model': max(results.items(), key=lambda kv: kv[1]['confidence'])[1] if results else None
        }
