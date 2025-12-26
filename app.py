"""
Flask Application - Ergonomic Posture Analysis System

Main web application that provides:
- Image upload and analysis endpoint
- RULA/REBA scoring
- Annotated visualization
- PDF report generation
- RESTful API for integration

100% OFFLINE - No external API calls
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
import base64
import uuid
from datetime import datetime
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, UPLOAD_FOLDER, REPORTS_FOLDER
from core.pose_detector import PoseDetector
from core.image_processor import ImageProcessor
from core.angle_calculator import AngleCalculator
from scoring.rula_engine import RULAEngine
from scoring.reba_engine import REBAEngine
from scoring.score_justifier import ScoreJustifier
from recommendations.recommendation_engine import RecommendationEngine
from reports.pdf_generator import PDFReportGenerator


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
pose_detector = PoseDetector()
image_processor = ImageProcessor()
angle_calculator = AngleCalculator()
score_justifier = ScoreJustifier()
pdf_generator = PDFReportGenerator()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_posture():
    """
    Analyze posture from uploaded image.
    
    Expects: multipart/form-data with 'image' file
    Optional form fields:
        - is_static: bool (default: true)
        - load_kg: float (default: 0)
        - coupling: str (default: 'good')
        - subject_id: str (default: 'Anonymous')
    
    Returns: JSON with complete analysis results
    """
    try:
        # Check for image file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use JPEG or PNG'}), 400
        
        # Get optional parameters
        is_static = request.form.get('is_static', 'true').lower() == 'true'
        load_kg = float(request.form.get('load_kg', 0))
        coupling = request.form.get('coupling', 'good')
        subject_id = request.form.get('subject_id', 'Anonymous')
        is_repetitive = request.form.get('is_repetitive', 'false').lower() == 'true'
        
        # Generate assessment ID
        assessment_id = f"EA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        # Read and preprocess image
        image_bytes = file.read()
        image = image_processor.preprocess(image_bytes)
        
        # Detect pose
        landmarks = pose_detector.detect(image)
        
        if not landmarks:
            return jsonify({
                'error': 'Could not detect pose in image. Please ensure the person is clearly visible.',
                'suggestion': 'Try a different image with better lighting and full body visibility.'
            }), 400
        
        # Check for missing landmarks
        missing = pose_detector.get_missing_landmarks(landmarks)
        warning = None
        if missing:
            warning = f"Some landmarks have low visibility: {', '.join(missing[:5])}"
        
        # Compute joint angles
        angles = angle_calculator.compute_all_angles(landmarks)
        
        # Initialize scoring engines with task context
        rula_engine = RULAEngine(
            is_static=is_static,
            load_kg=load_kg,
            is_repetitive=is_repetitive
        )
        reba_engine = REBAEngine(
            load_kg=load_kg,
            coupling=coupling,
            is_static=is_static,
            is_repeated=is_repetitive
        )
        
        # Calculate scores
        rula_result = rula_engine.calculate(angles)
        reba_result = reba_engine.calculate(angles)
        
        # Generate justifications
        rula_justifications = score_justifier.justify_rula(angles, rula_result)
        reba_justifications = score_justifier.justify_reba(angles, reba_result)
        
        # Generate recommendations
        recommendation_engine = RecommendationEngine()
        recommendations = recommendation_engine.generate_recommendations(
            angles, rula_result, reba_result
        )
        
        # Create annotated image
        annotated_image = pose_detector.draw_landmarks(image, landmarks)
        annotated_base64 = image_processor.to_base64(annotated_image)
        
        # Build response
        response = {
            'success': True,
            'assessment_id': assessment_id,
            'timestamp': datetime.now().isoformat(),
            'subject_id': subject_id,
            'warning': warning,
            
            'angles': angles.to_dict(),
            
            'rula': {
                'score': rula_result.final_score,
                'action_level': rula_result.action_level,
                'action_description': rula_result.action_description,
                'action_recommendation': rula_result.action_recommendation,
                'action_urgency': rula_result.action_urgency,
                'color': rula_result.action_color,
                'details': rula_result.to_dict(),
                'justifications': score_justifier.to_dict(rula_justifications)
            },
            
            'reba': {
                'score': reba_result.final_score,
                'risk_level': reba_result.risk_level,
                'risk_description': reba_result.risk_description,
                'risk_action': reba_result.risk_action,
                'risk_urgency': reba_result.risk_urgency,
                'color': reba_result.risk_color,
                'details': reba_result.to_dict(),
                'justifications': score_justifier.to_dict(reba_justifications)
            },
            
            'recommendations': recommendations.to_dict(),
            
            'annotated_image': annotated_base64
        }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/report', methods=['POST'])
def generate_report():
    """
    Generate PDF report from analysis results.
    
    Expects: JSON with analysis results from /api/analyze
    Returns: PDF file download
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Reconstruct result objects from JSON
        # (In production, you might store/retrieve these from a database)
        
        # For now, we'll need the client to send back the full analysis data
        # and we'll generate the PDF from that
        
        # Create a simplified PDF generator call
        assessment_id = data.get('assessment_id', 'Unknown')
        subject_id = data.get('subject_id', 'Anonymous')
        
        # Since we need the actual result objects, we should store them
        # For this demo, return a message
        return jsonify({
            'error': 'PDF generation requires re-analysis. Use the download button on the results page.',
            'assessment_id': assessment_id
        }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/generate', methods=['POST'])
def generate_pdf_from_analysis():
    """
    Generate PDF from a new analysis (combines analyze + PDF generation).
    
    Expects: multipart/form-data with 'image' file
    Returns: PDF file
    """
    try:
        # First run the analysis
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get parameters
        is_static = request.form.get('is_static', 'true').lower() == 'true'
        load_kg = float(request.form.get('load_kg', 0))
        coupling = request.form.get('coupling', 'good')
        subject_id = request.form.get('subject_id', 'Anonymous')
        is_repetitive = request.form.get('is_repetitive', 'false').lower() == 'true'
        
        assessment_id = f"EA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        # Process image
        image_bytes = file.read()
        image = image_processor.preprocess(image_bytes)
        
        # Detect pose
        landmarks = pose_detector.detect(image)
        
        if not landmarks:
            return jsonify({'error': 'Could not detect pose in image'}), 400
        
        # Compute angles
        angles = angle_calculator.compute_all_angles(landmarks)
        
        # Calculate scores
        rula_engine = RULAEngine(is_static=is_static, load_kg=load_kg, is_repetitive=is_repetitive)
        reba_engine = REBAEngine(load_kg=load_kg, coupling=coupling, is_static=is_static, is_repeated=is_repetitive)
        
        rula_result = rula_engine.calculate(angles)
        reba_result = reba_engine.calculate(angles)
        
        # Generate recommendations
        recommendation_engine = RecommendationEngine()
        recommendations = recommendation_engine.generate_recommendations(angles, rula_result, reba_result)
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_report(
            rula_result=rula_result,
            reba_result=reba_result,
            angles=angles,
            recommendations=recommendations,
            assessment_id=assessment_id,
            subject_id=subject_id
        )
        
        # Return PDF file
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'ergonomic_assessment_{assessment_id}.pdf'
        )
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'offline': True,
        'components': {
            'pose_detector': 'ready',
            'rula_engine': 'ready',
            'reba_engine': 'ready',
            'pdf_generator': 'ready'
        }
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error."""
    return jsonify({
        'error': 'Internal server error. Please try again.'
    }), 500


if __name__ == '__main__':
    # Ensure upload directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    
    print("=" * 60)
    print("  ERGONOMIC POSTURE ANALYSIS SYSTEM")
    print("  100% Offline | RULA & REBA Assessment")
    print("=" * 60)
    print(f"  Server running at: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
