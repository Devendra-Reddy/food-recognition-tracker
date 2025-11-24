import os, uuid, base64, traceback
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

UPLOAD='uploads'; os.makedirs(UPLOAD, exist_ok=True)
ALLOWED={'png','jpg','jpeg','gif','bmp','webp'}

# Services
from services.expanded_food_db import ExpandedFoodDatabase
from services.multi_model_detector import MultiModelDetector
from services.nutrition_api import calories_for
from services.health_advisor import assess_health
from services.historical_trends import HistoricalTrendsTracker
from services.proactive_agent import ProactiveAgent

db=ExpandedFoodDatabase(); detector=MultiModelDetector(); trends=HistoricalTrendsTracker(); agent=ProactiveAgent()

def ok_file(n): return ('.' in n) and (n.rsplit('.',1)[1].lower() in ALLOWED)

@app.route('/')
def home(): return render_template('index.html')

@app.route('/test-dashboard')
def legacy(): return redirect(url_for('agent_dashboard'), code=302)

@app.route('/agent-dashboard')
def agent_dashboard(): return render_template('agent_dashboard.html')

@app.route('/health')
def health(): return jsonify({'services_available': True})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files: return jsonify({'error':'No file provided'}),400
        f=request.files['file']
        if f.filename=='': return jsonify({'error':'No file selected'}),400
        if not ok_file(f.filename): return jsonify({'error':'Invalid file type'}),400

        # Save and encode
        uid=f"{uuid.uuid4()}_{secure_filename(f.filename)}"; path=os.path.join(UPLOAD, uid); f.save(path)
        b64=base64.b64encode(open(path,'rb').read()).decode('utf-8')

        # Quantity
        qv=request.form.get('quantity_value'); qu=request.form.get('quantity_unit')

        # Multi-model heuristic + filename canonicalization
        label_h, conf_h = detector.predict_label({'base64': b64}, filename_hint=f.filename)
        canon_from_file, score_file = db.canonicalize(f.filename)
        # Combine
        final_candidate = label_h or canon_from_file
        conf = detector.aggregate_confidence()
        # Suggestions for confirmation if low
        needs_confirmation = conf < 0.85
        top_suggestions = db.suggest_top_k(f.filename + " " + (label_h or ""), k=3)

        # Nutrition & health (using chosen candidate for now; may be re-run on finalize)
        info = db.info(final_candidate) or {}
        calories = calories_for(info, qv, qu)
        health = assess_health(info.get("per_100g", 160), info.get("tags", []))
        demographics = {"cuisine": info.get("cuisine"), "region": info.get("region"), "allergens": info.get("allergens", [])}

        if not needs_confirmation:
            # Log immediately
            trends.log_detection(final_candidate, conf, info.get("tags", ["unknown"])[0] if info.get("tags") else "unknown", "multi_model", uid)
            agent.log(uid, final_candidate, conf, info.get("tags", ["unknown"])[0] if info.get("tags") else "unknown")

        return jsonify({
            "success": True,
            "image_id": uid,
            "food_name": final_candidate,
            "confidence": conf,
            "multi_model": True,
            "needs_confirmation": needs_confirmation,
            "top_suggestions": top_suggestions,
            "calories": calories["kcal"] if calories else None,
            "calorie_basis": calories["basis"] if calories else None,
            "health": health,
            "demographics": demographics
        })
    except Exception as e:
        print('analyze error:', e); traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/finalize', methods=['POST'])
def finalize():
    try:
        image_id = request.form.get('image_id'); food_name = request.form.get('food_name')
        qv=request.form.get('quantity_value'); qu=request.form.get('quantity_unit')
        if not image_id or not food_name: return jsonify({'error':'Missing image_id or food_name'}),400

        info = db.info(food_name) or {}
        calories = calories_for(info, qv, qu)
        health = assess_health(info.get("per_100g", 160), info.get("tags", []))
        demographics = {"cuisine": info.get("cuisine"), "region": info.get("region"), "allergens": info.get("allergens", [])}

        # Log after confirmation
        trends.log_detection(food_name, 0.99, info.get("tags", ["unknown"])[0] if info.get("tags") else "unknown", "confirmed", image_id)
        agent.log(image_id, food_name, 0.99, info.get("tags", ["unknown"])[0] if info.get("tags") else "unknown")

        return jsonify({
            "success": True,
            "image_id": image_id,
            "food_name": food_name,
            "confidence": 0.99,
            "multi_model": True,
            "needs_confirmation": False,
            "calories": calories["kcal"] if calories else None,
            "calorie_basis": calories["basis"] if calories else None,
            "health": health,
            "demographics": demographics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent-dashboard/data')
def dash_data():
    try:
        return jsonify({'success':True,'data': {
            'agent_status': agent.status(),
            'popular_foods': trends.popular(30, 10),
            'daily_trends': trends.daily(7),
            'total_foods_in_db': len(db.all_foods)
        }})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),500

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',10000)), debug=True)
