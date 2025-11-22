def estimate_calories(food_name:str, quantity_value, quantity_unit):
    if not food_name: return None
    db = {
        "Margherita Pizza": {"per_100g":266, "serving_kcal":300},
        "Pepperoni Pizza": {"per_100g":298, "serving_kcal":320},
        "Veggie Pizza": {"per_100g":250, "serving_kcal":290},
        "Bulgogi": {"per_100g":245, "serving_kcal":350},
        "Ramen": {"per_100g":130, "serving_kcal":450},
        "Butter Chicken": {"per_100g":156, "serving_kcal":300},
        "Paneer Butter Masala": {"per_100g":215, "serving_kcal":320},
        "Aloo Paratha": {"per_100g":290, "serving_kcal":290},
        "Vegetable Biryani": {"per_100g":150, "serving_kcal":300},
        "Chicken Biryani": {"per_100g":165, "serving_kcal":330},
        "Idli Sambar": {"per_100g":110, "serving_kcal":180},
        "Cheeseburger": {"per_100g":295, "serving_kcal":350},
        "French Fries": {"per_100g":312, "serving_kcal":312}
    }
    info = db.get(food_name)
    if not info: return None
    if not quantity_value or not quantity_unit: return None
    q = float(quantity_value); unit = quantity_unit.lower()
    if unit=='g':
        return {'kcal': round(info['per_100g']*(q/100.0), 1), 'basis':'per_100g'}
    if unit in ('slice','piece','serving'):
        per = info.get('serving_kcal')
        if per: return {'kcal': round(per*q, 1), 'basis': unit}
    if unit=='ml':
        return {'kcal': round(info['per_100g']*(q/100.0), 1), 'basis':'per_100g~ml'}
    return None
