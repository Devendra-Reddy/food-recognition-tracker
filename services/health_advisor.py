def assess_health(per_100g:int, tags:list):
    """
    Simple rubric for a friendly verdict:
    - Score starts from 100; penalties for fried/processed/high-cal items; bonuses for salads/vegetarian.
    - Verdict: Good (>=70), Caution (40-69), Limit (<40)
    """
    score = 100
    reasons = []

    if per_100g >= 300:
        score -= 35; reasons.append("High calorie density")
    elif per_100g >= 220:
        score -= 20; reasons.append("Moderate calorie density")

    t = set((tags or []))
    if "fried" in t:
        score -= 25; reasons.append("Fried item")
    if "processed_meat" in t:
        score -= 20; reasons.append("Processed meat")
    if "red_meat" in t:
        score -= 10; reasons.append("Red meat")
    if "vegetarian" in t or "salad" in t:
        score += 10; reasons.append("Vegetable-forward")

    score = max(0, min(100, score))
    verdict = "Good" if score >= 70 else ("Caution" if score >= 40 else "Limit")
    return {"score": score, "verdict": verdict, "reasons": reasons}
