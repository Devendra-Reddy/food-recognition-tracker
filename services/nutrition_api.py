def calories_for(food_info:dict, quantity_value, quantity_unit):
    if not food_info: return None
    per100 = float(food_info.get("per_100g", 160))
    default_g = float(food_info.get("typical_serving_g", 100))
    if not quantity_value or not quantity_unit:
        # Fall back to typical serving if not provided
        return {"kcal": round(per100 * (default_g/100.0), 1), "basis": f"typical_serving_{int(default_g)}g"}
    q = float(quantity_value); u = (quantity_unit or "").lower()
    if u == "g":
        return {"kcal": round(per100 * (q/100.0), 1), "basis": "per_100g"}
    if u in ("slice","piece","serving"):
        # assume typical serving weight
        return {"kcal": round(per100 * (default_g * q/100.0), 1), "basis": f"{u}_~{int(default_g)}g_each"}
    if u == "ml":
        # rough equivalence for many liquids; user should prefer g for precision
        return {"kcal": round(per100 * (q/100.0), 1), "basis": "per_100ml~approx"}
    return None
