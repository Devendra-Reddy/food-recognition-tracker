import re
import random

class ExpandedFoodDatabase:
    def __init__(self):
        # Core categories (shortened sample; extend freely)
        self.foods = {
            'italian': ['Margherita Pizza','Pepperoni Pizza','Veggie Pizza','Spaghetti Bolognese','Fettuccine Alfredo'],
            'korean': ['Bulgogi','Bibimbap','Kimchi'],
            'japanese': ['Ramen','Salmon Nigiri','Tempura','Udon'],
            'indian': ['Butter Chicken','Paneer Butter Masala','Masala Dosa','Aloo Paratha','Vegetable Biryani','Chicken Biryani','Idli Sambar','Chole Bhature','Vada Pav','Pav Bhaji'],
            'american': ['Cheeseburger','Veggie Burger','French Fries','Grilled Chicken','Steak','Caesar Salad','Greek Salad','Caprese Salad'],
            'mexican': ['Chicken Burrito','Beef Taco','Chicken Quesadilla','Loaded Nachos','Guacamole'],
            'chinese': ['Fried Rice','Fried Noodles','Dumplings','Hot and Sour Soup']
        }
        self.all_foods = []
        for cat, items in self.foods.items():
            for it in items:
                self.all_foods.append({'name': it, 'category': cat})

        # Alias map for robust matching
        self.alias_to_canonical = {}
        for entry in self.all_foods:
            canon = entry['name']
            base = canon.lower()
            tokens = [t for t in re.split(r'[^a-z0-9]+', base) if t]
            aliases = {base, " ".join(tokens), "-".join(tokens), "".join(tokens)}
            # common variants
            if base.endswith('s'): aliases.add(base[:-1])
            else: aliases.add(base+'s')
            if tokens: aliases.add(tokens[-1])
            for a in aliases:
                self.alias_to_canonical[a] = canon

        manual = {
            'pizza':'Margherita Pizza', 'pepperoni':'Pepperoni Pizza', 'bulgogi':'Bulgogi',
            'ramen':'Ramen','nigiri':'Salmon Nigiri','biryani':'Chicken Biryani','veg biryani':'Vegetable Biryani',
            'aloo paratha':'Aloo Paratha','butter chicken':'Butter Chicken','paneer butter masala':'Paneer Butter Masala',
            'fries':'French Fries','burger':'Cheeseburger','salad':'Caesar Salad','dosa':'Masala Dosa'
        }
        for k,v in manual.items():
            self.alias_to_canonical[k] = v

    def _score(self, a:str, b:str)->float:
        ta = set([t for t in re.split(r'[^a-z0-9]+', a.lower()) if t])
        tb = set([t for t in re.split(r'[^a-z0-9]+', b.lower()) if t])
        if not ta or not tb: return 0.0
        inter = len(ta & tb); union = len(ta | tb)
        return inter/union if union else 0.0

    def canonicalize(self, raw:str):
        if not raw: return None, 0.0
        key = raw.lower().strip()
        for ext in ('.jpg','.jpeg','.png','.gif','.webp','.bmp'):
            if key.endswith(ext): key = key[:-len(ext)]
        if key in self.alias_to_canonical:
            return self.alias_to_canonical[key], 1.0
        tokens = [t for t in re.split(r'[^a-z0-9]+', key) if t]
        for v in (" ".join(tokens), "-".join(tokens), "".join(tokens)):
            if v in self.alias_to_canonical:
                return self.alias_to_canonical[v], 0.95
        # fuzzy
        best,score = None,0.0
        for entry in self.all_foods:
            s = self._score(key, entry['name'])
            if s>score: best,score = entry['name'],s
        return best, score

    def get_food_info(self, name:str):
        for f in self.all_foods:
            if f['name'].lower()==name.lower():
                return f
        return None

    def get_random_food(self):
        return random.choice(self.all_foods)
