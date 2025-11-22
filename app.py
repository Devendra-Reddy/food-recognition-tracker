import os, uuid, base64, traceback, random
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','bmp','webp'}

# External model (optional)
ROBOFLOW_API_KEY = os.getenv('ROBOFLOW_API_KEY')
ROBOFLOW_MODEL_ENDPOINT = os.getenv('ROBOFLOW_MODEL_ENDPOINT')

# Services
services_available = True
try:
    from services.expanded_food_db import ExpandedFoodDatabase
    from services.multi_model_detector import MultiModelDetector
    from services.historical_trends import HistoricalTrendsTracker
    from services.proactive_agent import ProactiveAgent
    from services.synthetic_images import SyntheticImageGenerator
    from services.nutrition_api import estimate_calories
    db = ExpandedFoodDatabase()
    detector = MultiModelDetector()
    trends = HistoricalTrendsTracker()
    agent = ProactiveAgent()
    synth = SyntheticImageGenerator()
except Exception as e:
    services_available = False
    print('Service init failed:', e)

def allowed_file(name:str)->bool:
    return '.' in name and name.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agent-dashboard')
def agent_dashboard():
    return render_template('agent_dashboard.html')

@app.route('/health')
def health():
    return jsonify({
        'status':'healthy',
        'services_available': services_available
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error':'No file provided'}), 400
        f = request.files['file']
        if f.filename=='': return jsonify({'success': False, 'error':'No file selected'}), 400
        if not allowed_file(f.filename): return jsonify({'success': False, 'error':'Invalid file type'}), 400

        fname = secure_filename(f.filename)
        uid = f"{uuid.uuid4()}_{fname}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], uid)
        f.save(path)
        with open(path,'rb') as fh:
            b64 = base64.b64encode(fh.read()).decode('utf-8')

        # Quantity (optional)
        quantity_value = request.form.get('quantity_value')
        quantity_unit  = request.form.get('quantity_unit')

        # Choose path
        force_multi = not (ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ENDPOINT)
        use_multi = request.form.get('use_multi_model', 'true' if force_multi else 'false').lower()=='true'

        if use_multi and services_available:
            det = detector.detect_with_all_models({'base64': b64}, filename_hint=fname)
            conf = det['consensus_confidence']
            raw = det.get('predicted_label') or fname
            label, score = db.canonicalize(raw)
            food_name = label or db.get_random_food()['name']
            result = {
                'success': True,
                'food_name': food_name,
                'confidence': conf,
                'multi_model': True,
                'model_agreement': det['model_agreement'],
                'models_used': det['models_used'],
                'best_model': det['best_model']['model'] if det['best_model'] else None,
                'all_model_results': det['all_results']
            }
        else:
            # External model path (Roboflow) – optional (not called here to keep sample offline-safe)
            # If no external keys, simulate but stabilize via filename canonicalization
            if services_available:
                guess, _ = db.canonicalize(fname)
                food_name = guess or db.get_random_food()['name']
            else:
                food_name = 'Margherita Pizza'
            result = {
                'success': True,
                'food_name': food_name,
                'confidence': round(random.uniform(0.55,0.88),2),
                'simulated': True
            }

        # Log and calories
        if services_available and result.get('success'):
            info = db.get_food_info(result['food_name']) or {'category':'unknown'}
            trends.log_detection(result['food_name'], float(result['confidence']), info['category'], 'multi_model' if use_multi else 'external_or_sim')
            agent.log_scan(uid, result['food_name'], float(result['confidence']), info['category'])

        # Calories
        cal = estimate_calories(result['food_name'], quantity_value, quantity_unit) if services_available else None
        if cal:
            result['calories'] = cal['kcal']
            result['calorie_basis'] = cal['basis']
            result['quantity'] = {'value': quantity_value, 'unit': quantity_unit}

        return jsonify(result)
    except Exception as e:
        print('analyze error:', e); traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agent-dashboard/data')
def dashboard_data():
    try:
        if not services_available:
            return jsonify({'success': False, 'error':'Services not available'}), 503
        status = agent.get_agent_status()
        popular = trends.get_popular_foods(days=30, top_n=10)
        daily = trends.get_daily_trends(days=7)
        return jsonify({'success': True, 'data': {
            'agent_status': status,
            'popular_foods': popular,
            'daily_trends': daily,
            'total_foods_in_db': len(db.all_foods)
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__=='__main__':
    port = int(os.getenv('PORT', 10000))
    print(f"Open -> http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
