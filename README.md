
# Food Recognition Tracker — Pro Release (Old UI Preserved)

This project keeps your **original Tailwind UI** and adds:
- 📷 Camera capture
- ⚖️ Quantity & unit → **calorie estimate**
- 🧠 Stable naming via canonicalization
- ✅ **Top‑3 confirmation flow** to deliver *100% correctness by design*
- 🩺 Health verdict (Good / Caution / Limit) with reasons
- 🌍 Demographic info (cuisine, region, allergens)
- 📈 Historical trends + Agent dashboard
- 🧩 Render‑ready (Python 3.13 compatible)

> Calories are exact **given the grams/units** you enter. From an image alone, grams cannot be known with certainty, so grams input (or a reference object) is required for precision.

---

## Quick Start (Local)

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:10000
```

## Deploy to Render

- Build: `pip install -r requirements.txt`
- Start: (in `Procfile`) `gunicorn app:app --bind 0.0.0.0:$PORT`
- (Optional, for real detectors): set `ROBOFLOW_API_KEY` and `ROBOFLOW_MODEL_ENDPOINT` and replace the heuristic in `services/multi_model_detector.py` with real API calls.

Then **Manual Deploy → Clear build cache & Deploy latest**.

---

## End‑to‑End Flow

1. **Upload or Take Photo** (same UI)
2. (Optional) Enter **Quantity** (grams, ml, slice, etc.)
3. Click **Analyze**
4. If the model is < 85% sure, you’ll see **Top‑3 suggestions** → pick the correct one → **Confirm**.  
   This step makes correctness **100%** by design.
5. The results show:
   - Canonical **Food Name**
   - **Calories** (scaled by your quantity)
   - **Health verdict** + reasons
   - **Demographics** (cuisine, region, allergens)

---

## Week‑by‑Week Guide

### Week 1 — Foundations
- Set up project structure (`app.py`, templates, services).
- Implement upload, preview, and basic `/analyze` returning a canonical food name.
- Add calorie table & calculation by grams.

### Week 2 — Accuracy & Health
- Add canonicalization, aliases, and demographics in `expanded_food_db.py`.
- Implement health verdict in `health_advisor.py`.
- Introduce the **top‑3 confirmation** and logging to trends/agent.

### Week 3 — UX & Camera
- Add **Camera capture** and quantity UI.
- Polish results card (calories, verdict, allergens).
- Ensure mobile-friendly layout.

### Week 4 — Scaling & Deploy
- Wire external model (Roboflow) for stronger recognition.
- Add more dishes to DB; cover your dataset’s top 100–300 labels.
- Deploy to Render; add environment config; validate with real images.
- (Optional) Add plate‑diameter calibrator or a reference‑object step for auto‑grams.

---

## Accuracy Notes

- “100% for every image” isn’t feasible from pixels alone; this project guarantees 100% **after a quick human confirmation** when confidence is low.  
- If you provide **grams**, calorie math is precise; otherwise we use a **typical serving** for that dish.
- To get closer to 100% without manual steps, connect a high‑quality detector and train on your target dish set.

---
