"""
MediaPipe Pose Detector - Offline Pose Estimation Engine

This module provides deterministic, offline pose detection using MediaPipe.
All operations are performed locally without any network calls.
"""

import mediapipe as mp
import numpy as np
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MEDIAPIPE_CONFIG, LANDMARK_CONFIDENCE


@dataclass
class Landmark:
    """Represents a single body landmark with 3D coordinates and visibility."""
    x: float  # Normalized x coordinate (0-1)
    y: float  # Normalized y coordinate (0-1)
    z: float  # Depth estimate
    visibility: float  # Confidence score (0-1)
    name: str  # Landmark name
    
    def to_pixel(self, width: int, height: int) -> Tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates."""
        return (int(self.x * width), int(self.y * height))
    
    def is_visible(self, threshold: float = None) -> bool:
        """Check if landmark meets visibility threshold."""
        threshold = threshold or LANDMARK_CONFIDENCE['minimum_visibility']
        return self.visibility >= threshold


class PoseDetector:
    """
    MediaPipe-based pose detector for ergonomic analysis.
    
    Detects 33 body landmarks from a single RGB image.
    Operates completely offline with deterministic results.
    """
    
    # MediaPipe Pose landmark indices
    LANDMARK_NAMES = {
        0: 'nose',
        1: 'left_eye_inner',
        2: 'left_eye',
        3: 'left_eye_outer',
        4: 'right_eye_inner',
        5: 'right_eye',
        6: 'right_eye_outer',
        7: 'left_ear',
        8: 'right_ear',
        9: 'mouth_left',
        10: 'mouth_right',
        11: 'left_shoulder',
        12: 'right_shoulder',
        13: 'left_elbow',
        14: 'right_elbow',
        15: 'left_wrist',
        16: 'right_wrist',
        17: 'left_pinky',
        18: 'right_pinky',
        19: 'left_index',
        20: 'right_index',
        21: 'left_thumb',
        22: 'right_thumb',
        23: 'left_hip',
        24: 'right_hip',
        25: 'left_knee',
        26: 'right_knee',
        27: 'left_ankle',
        28: 'right_ankle',
        29: 'left_heel',
        30: 'right_heel',
        31: 'left_foot_index',
        32: 'right_foot_index'
    }
    
    # Landmarks required for RULA/REBA analysis
    REQUIRED_LANDMARKS = [
        'nose', 'left_ear', 'right_ear',
        'left_shoulder', 'right_shoulder',
        'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist',
        'left_hip', 'right_hip',
        'left_knee', 'right_knee',
        'left_ankle', 'right_ankle'
    ]
    
    def __init__(self):
        """Initialize MediaPipe Pose detector with configured settings."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=MEDIAPIPE_CONFIG['static_image_mode'],
            model_complexity=MEDIAPIPE_CONFIG['model_complexity'],
            enable_segmentation=MEDIAPIPE_CONFIG['enable_segmentation'],
            min_detection_confidence=MEDIAPIPE_CONFIG['min_detection_confidence'],
            min_tracking_confidence=MEDIAPIPE_CONFIG['min_tracking_confidence']
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
    def detect(self, image: np.ndarray) -> Optional[Dict[str, Landmark]]:
        """
        Detect pose landmarks from an RGB image.
        
        Args:
            image: RGB image as numpy array (H, W, 3)
            
        Returns:
            Dictionary mapping landmark names to Landmark objects,
            or None if detection fails.
        """
        # Ensure image is in RGB format
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError("Image must be RGB format with shape (H, W, 3)")
        
        # Process image through MediaPipe
        results = self.pose.process(image)
        
        if not results.pose_landmarks:
            return None
        
        # Extract landmarks
        landmarks = {}
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            name = self.LANDMARK_NAMES.get(idx, f'landmark_{idx}')
            landmarks[name] = Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                name=name
            )
        
        return landmarks
    
    def detect_with_world_landmarks(self, image: np.ndarray) -> Tuple[Optional[Dict[str, Landmark]], Optional[Dict[str, Landmark]]]:
        """
        Detect both image landmarks and world landmarks.
        
        World landmarks provide real-world 3D coordinates in meters,
        useful for more accurate angle calculations.
        
        Args:
            image: RGB image as numpy array
            
        Returns:
            Tuple of (image_landmarks, world_landmarks)
        """
        results = self.pose.process(image)
        
        if not results.pose_landmarks:
            return None, None
        
        # Image landmarks (normalized to image)
        image_landmarks = {}
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            name = self.LANDMARK_NAMES.get(idx, f'landmark_{idx}')
            image_landmarks[name] = Landmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                name=name
            )
        
        # World landmarks (real-world coordinates)
        world_landmarks = {}
        if results.pose_world_landmarks:
            for idx, landmark in enumerate(results.pose_world_landmarks.landmark):
                name = self.LANDMARK_NAMES.get(idx, f'landmark_{idx}')
                world_landmarks[name] = Landmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                    visibility=landmark.visibility,
                    name=name
                )
        
        return image_landmarks, world_landmarks
    
    def validate_landmarks(self, landmarks: Dict[str, Landmark]) -> Dict[str, bool]:
        """
        Validate that all required landmarks are detected with sufficient visibility.
        
        Args:
            landmarks: Dictionary of detected landmarks
            
        Returns:
            Dictionary mapping landmark names to validation status
        """
        validation = {}
        for name in self.REQUIRED_LANDMARKS:
            if name in landmarks:
                validation[name] = landmarks[name].is_visible()
            else:
                validation[name] = False
        return validation
    
    def get_missing_landmarks(self, landmarks: Dict[str, Landmark]) -> List[str]:
        """
        Get list of required landmarks that are missing or not visible.
        
        Args:
            landmarks: Dictionary of detected landmarks
            
        Returns:
            List of missing/invisible landmark names
        """
        validation = self.validate_landmarks(landmarks)
        return [name for name, valid in validation.items() if not valid]
    
    def draw_landmarks(self, image: np.ndarray, landmarks: Dict[str, Landmark]) -> np.ndarray:
        """
        Draw detected landmarks on the image.
        
        Args:
            image: RGB image as numpy array
            landmarks: Dictionary of detected landmarks
            
        Returns:
            Image with landmarks drawn
        """
        annotated = image.copy()
        height, width = image.shape[:2]
        
        # Draw connections
        connections = [
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle'),
            ('nose', 'left_shoulder'),
            ('nose', 'right_shoulder'),
            ('left_ear', 'left_shoulder'),
            ('right_ear', 'right_shoulder')
        ]
        
        import cv2
        
        # Draw skeleton connections
        for start_name, end_name in connections:
            if start_name in landmarks and end_name in landmarks:
                start = landmarks[start_name]
                end = landmarks[end_name]
                if start.is_visible() and end.is_visible():
                    start_px = start.to_pixel(width, height)
                    end_px = end.to_pixel(width, height)
                    cv2.line(annotated, start_px, end_px, (0, 255, 0), 2)
        
        # Draw landmark points
        for name, landmark in landmarks.items():
            if landmark.is_visible():
                px = landmark.to_pixel(width, height)
                color = (0, 255, 0) if name in self.REQUIRED_LANDMARKS else (255, 165, 0)
                cv2.circle(annotated, px, 5, color, -1)
                cv2.circle(annotated, px, 7, (255, 255, 255), 1)
        
        return annotated
    
    def close(self):
        """Release MediaPipe resources."""
        self.pose.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
