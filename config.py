"""
Application Configuration for Ergonomic Posture Analysis System
All settings are optimized for offline, deterministic operation.
"""

import os

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
REPORTS_FOLDER = os.path.join(BASE_DIR, 'reports', 'generated')

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Flask Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ergonomic-analysis-offline-key-2024')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    UPLOAD_FOLDER = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# MediaPipe Pose Configuration
MEDIAPIPE_CONFIG = {
    'static_image_mode': True,
    'model_complexity': 2,  # Highest accuracy
    'enable_segmentation': False,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5
}

# Landmark Confidence Thresholds
LANDMARK_CONFIDENCE = {
    'minimum_visibility': 0.5,
    'minimum_presence': 0.5
}

# Image Processing Settings
IMAGE_PROCESSING = {
    'max_width': 1920,
    'max_height': 1080,
    'normalize_lighting': True,
    'enhance_contrast': True
}

# RULA Configuration
RULA_CONFIG = {
    'muscle_use_threshold': 4,  # Times per minute for static posture
    'force_thresholds': {
        'light': 2,      # < 2 kg
        'moderate': 10,  # 2-10 kg
        'heavy': 10      # > 10 kg
    }
}

# REBA Configuration
REBA_CONFIG = {
    'load_thresholds': {
        'light': 5,       # < 5 kg
        'moderate': 10,   # 5-10 kg
        'heavy': 10       # > 10 kg
    },
    'coupling_types': ['good', 'fair', 'poor', 'unacceptable']
}

# Report Configuration
REPORT_CONFIG = {
    'logo_path': os.path.join(BASE_DIR, 'static', 'images', 'logo.png'),
    'organization_name': 'Ergonomic Assessment System',
    'report_title': 'Ergonomic Posture Assessment Report',
    'include_timestamp': True,
    'include_compliance_statement': True
}

# Risk Level Colors (for visualization)
RISK_COLORS = {
    'negligible': '#22c55e',  # Green
    'low': '#84cc16',         # Lime
    'medium': '#eab308',      # Yellow
    'high': '#f97316',        # Orange
    'very_high': '#ef4444'    # Red
}

# Action Level Colors (for RULA)
ACTION_LEVEL_COLORS = {
    1: '#22c55e',  # Green - Acceptable
    2: '#84cc16',  # Lime - Investigate
    3: '#f97316',  # Orange - Soon
    4: '#ef4444'   # Red - Immediate
}
