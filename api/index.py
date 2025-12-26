"""
ErgoAssess - Vercel Serverless Entry Point
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_file, url_for
import json
import base64
import io
import tempfile
from datetime import datetime

# Create Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ergoassess-secret-key')

# Import core modules
try:
    from core.pose_detector import PoseDetector
    from core.angle_calculator import AngleCalculator
    from scoring.rula_engine import RULAEngine
    from scoring.reba_engine import REBAEngine
    from scoring.score_justifier import ScoreJustifier
    from recommendations.recommendation_engine import RecommendationEngine
    from reports.pdf_generator import PDFReportGenerator
    
    # Initialize components
    pose_detector = PoseDetector()
    angle_calculator = AngleCalculator()
    rula_engine = RULAEngine()
    reba_engine = REBAEngine()
    score_justifier = ScoreJustifier()
    recommendation_engine = RecommendationEngine()
    pdf_generator = PDFReportGenerator()
    
    MODULES_LOADED = True
except Exception as e:
    print(f"Warning: Could not load some modules: {e}")
    MODULES_LOADED = False


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze image endpoint"""
    if not MODULES_LOADED:
        return jsonify({
            'success': False,
            'error': 'Analysis modules not available in serverless mode. Please use the desktop app for full functionality.'
        }), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read image
        import numpy as np
        import cv2
        from PIL import Image
        
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'success': False, 'error': 'Invalid image format'}), 400
        
        # Detect pose
        landmarks = pose_detector.detect(image)
        if landmarks is None:
            return jsonify({
                'success': False,
                'error': 'Could not detect pose in image. Please ensure the person is clearly visible.'
            }), 400
        
        # Calculate angles
        angles = angle_calculator.calculate_all(landmarks, image.shape)
        
        # Get modifiers from request
        load_weight = float(request.form.get('load_weight', 0))
        coupling = request.form.get('coupling', 'good')
        
        # Calculate scores
        rula_result = rula_engine.calculate(angles)
        reba_result = reba_engine.calculate(angles, load_weight, coupling)
        
        # Get justifications
        rula_justification = score_justifier.justify_rula(rula_result, angles)
        reba_justification = score_justifier.justify_reba(reba_result, angles)
        
        # Get recommendations
        recommendations = recommendation_engine.generate(rula_result, reba_result, angles)
        
        # Create annotated image
        annotated = pose_detector.draw_landmarks(image.copy(), landmarks)
        _, buffer = cv2.imencode('.jpg', annotated)
        annotated_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'rula': {
                'score': rula_result.final_score,
                'action_level': rula_result.action_level,
                'description': rula_result.description,
                'components': rula_result.components,
                'justification': rula_justification
            },
            'reba': {
                'score': reba_result.final_score,
                'risk_level': reba_result.risk_level,
                'description': reba_result.description,
                'components': reba_result.components,
                'justification': reba_justification
            },
            'angles': angles.to_dict(),
            'recommendations': recommendations,
            'annotated_image': f'data:image/jpeg;base64,{annotated_b64}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'modules_loaded': MODULES_LOADED,
        'timestamp': datetime.now().isoformat()
    })


# Vercel serverless handler
def handler(request):
    """Vercel serverless function handler"""
    return app(request)


# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
