import io, base64
try:
    from PIL import Image
except Exception:
    Image=None
from services.expanded_food_db import ExpandedFoodDatabase

class MultiModelDetector:
    """
    Heuristic multi-model stub (offline safe). In production, plug in your external detector/classifier
    (e.g., Roboflow) and feed the results into canonicalization.
    """
    def _dominant(self, data):
        if not Image: return None
        try:
            img=Image.open(io.BytesIO(base64.b64decode(data['base64']))).convert('RGB').resize((32,32))
            px=list(img.getdata()); r=sum(p[0] for p in px)/len(px); g=sum(p[1] for p in px)/len(px); b=sum(p[2] for p in px)/len(px)
            if g>r*1.15 and g>b*1.15: return 'green'
            if r>g*1.15 and r>b*1.15: return 'red'
            return 'neutral'
        except Exception: return None

    def predict_label(self, image_data, filename_hint=None):
        db=ExpandedFoodDatabase()
        if filename_hint:
            c,s=db.canonicalize(filename_hint)
            if c and s>=0.6: return c, 0.8
        col=self._dominant(image_data); cand=['Margherita Pizza','Pepperoni Pizza','Ramen','Butter Chicken','Caesar Salad']
        if col=='green': cand=['Caesar Salad','Greek Salad','Veggie Pizza']
        if col=='red': cand=['Margherita Pizza','Pepperoni Pizza','Butter Chicken']
        import random; guess=random.choice(cand)
        guess,_=db.canonicalize(guess)
        return guess, 0.65

    def aggregate_confidence(self):
        # Simulated consensus confidence range
        import random
        return max(0.5, min(0.95, random.uniform(0.6, 0.9)))
