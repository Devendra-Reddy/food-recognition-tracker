from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os, io, base64, random
from datetime import datetime

class SyntheticImageGenerator:
    def __init__(self, log_file='logs/synthetic_generations.json'):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f: f.write('[]')

    def generate_batch(self, food_name:str, count:int=6, confidence_score:float=0.5):
        imgs = []
        for i in range(count):
            img = Image.new('RGB', (256,256), (20,20,20))
            dr = ImageDraw.Draw(img)
            # random circle/pattern to simulate data
            for _ in range(8):
                x1,y1 = random.randint(0,200), random.randint(0,200)
                x2,y2 = x1+random.randint(20,56), y1+random.randint(20,56)
                dr.ellipse([x1,y1,x2,y2], outline=(255,140,0))
            buf = io.BytesIO(); img.save(buf, format='PNG'); b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            imgs.append({'food_name': food_name, 'image_base64': b64})
        # (log omitted for brevity)
        return imgs

    def get_generation_stats(self):
        return {'total_generated': 0, 'unique_foods': 0, 'by_category': {}, 'recent_generations': []}
