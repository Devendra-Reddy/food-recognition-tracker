import re, random

class ExpandedFoodDatabase:
    def __init__(self):
        # Canonical items with metadata
        # NOTE: For brevity, a compact list is shown. Extend as needed.
        self.meta = {
            "Margherita Pizza": {"cuisine":"Italian","region":"Naples","per_100g":266,"typical_serving_g":120,"tags":["pizza","baked","cheese"],"allergens":["gluten","dairy"]},
            "Pepperoni Pizza": {"cuisine":"Italian-American","region":"US","per_100g":298,"typical_serving_g":120,"tags":["pizza","processed_meat"],"allergens":["gluten","dairy"]},
            "Veggie Pizza": {"cuisine":"Italian","region":"Naples","per_100g":250,"typical_serving_g":120,"tags":["pizza","vegetarian"],"allergens":["gluten","dairy"]},
            "Butter Chicken": {"cuisine":"Indian","region":"North India","per_100g":156,"typical_serving_g":180,"tags":["curry","butter","cream"],"allergens":["dairy","nuts?(depends)"]},
            "Paneer Butter Masala": {"cuisine":"Indian","region":"North India","per_100g":215,"typical_serving_g":180,"tags":["curry","vegetarian","butter"],"allergens":["dairy","nuts?(depends)"]},
            "Aloo Paratha": {"cuisine":"Indian","region":"Punjab","per_100g":290,"typical_serving_g":150,"tags":["fried","flatbread"],"allergens":["gluten","dairy"]},
            "Vegetable Biryani": {"cuisine":"Indian","region":"Hyderabad","per_100g":150,"typical_serving_g":200,"tags":["rice","vegetarian","spiced"],"allergens":[]},
            "Chicken Biryani": {"cuisine":"Indian","region":"Hyderabad","per_100g":165,"typical_serving_g":220,"tags":["rice","poultry","spiced"],"allergens":[]},
            "Ramen": {"cuisine":"Japanese","region":"Japan","per_100g":130,"typical_serving_g":400,"tags":["noodles","broth"],"allergens":["gluten","egg (sometimes)","soy"]},
            "Salmon Nigiri": {"cuisine":"Japanese","region":"Japan","per_100g":142,"typical_serving_g":50,"tags":["sushi","seafood"],"allergens":["fish","soy (if sauce)"]},
            "Caesar Salad": {"cuisine":"American","region":"US/Mexico","per_100g":190,"typical_serving_g":180,"tags":["salad","dressing","cheese"],"allergens":["dairy","egg","fish"]},
            "Greek Salad": {"cuisine":"Greek","region":"Greece","per_100g":120,"typical_serving_g":200,"tags":["salad","feta","olive"],"allergens":["dairy"]},
            "French Fries": {"cuisine":"Belgian/French","region":"Western Europe","per_100g":312,"typical_serving_g":150,"tags":["fried","potato"],"allergens":[]},
            "Cheeseburger": {"cuisine":"American","region":"US","per_100g":295,"typical_serving_g":200,"tags":["red_meat","cheese","bun"],"allergens":["gluten","dairy","sesame?"]},
        }
        # Canonical list
        self.all_foods = [{"name":k, **v} for k,v in self.meta.items()]

        # Alias map
        self.alias_to_canonical = {}
        for name in self.meta:
            base = name.lower()
            tokens = [t for t in re.split(r'[^a-z0-9]+', base) if t]
            variants = {base, " ".join(tokens), "-".join(tokens), "".join(tokens)}
            if base.endswith('s'): variants.add(base[:-1])
            else: variants.add(base+'s')
            if tokens: variants.add(tokens[-1])
            for v in variants: self.alias_to_canonical[v] = name

        # Manual synonyms
        self.alias_to_canonical.update({
            "pizza":"Margherita Pizza",
            "pepperoni":"Pepperoni Pizza",
            "veg pizza":"Veggie Pizza",
            "margarita pizza":"Margherita Pizza",
            "butter chicken curry":"Butter Chicken",
            "paneer butter masala":"Paneer Butter Masala",
            "biryani":"Chicken Biryani",
            "veg biryani":"Vegetable Biryani",
            "fries":"French Fries",
            "burger":"Cheeseburger",
            "salad":"Caesar Salad",
            "nigiri":"Salmon Nigiri"
        })

    def _score(self, a:str, b:str)->float:
        ta=set([t for t in re.split(r'[^a-z0-9]+', a.lower()) if t]); tb=set([t for t in re.split(r'[^a-z0-9]+', b.lower()) if t])
        return (len(ta & tb)/len(ta | tb)) if (ta and tb) else 0.0

    def canonicalize(self, raw:str):
        if not raw: return (None,0.0)
        k = raw.lower().strip()
        for ext in ('.jpg','.jpeg','.png','.gif','.webp','.bmp'):
            if k.endswith(ext): k = k[:-len(ext)]
        if k in self.alias_to_canonical: return (self.alias_to_canonical[k], 1.0)
        tokens = [t for t in re.split(r'[^a-z0-9]+', k) if t]
        for v in (" ".join(tokens), "-".join(tokens), "".join(tokens)):
            if v in self.alias_to_canonical: return (self.alias_to_canonical[v], 0.95)
        best,score=None,0.0
        for name in self.meta:
            s = self._score(k, name)
            if s>score: best,score = name,s
        return (best,score)

    def suggest_top_k(self, raw:str, k:int=3):
        k = max(1, k)
        key = raw or ""
        scored = []
        for name in self.meta:
            scored.append((name, self._score(key, name)))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return [n for n,_ in scored[:k]]

    def info(self, name:str):
        return self.meta.get(name)

    def typical_weight_for(self, name:str):
        info = self.info(name) or {}
        return info.get("typical_serving_g", 100)
