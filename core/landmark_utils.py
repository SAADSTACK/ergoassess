"""
Landmark Utilities - Helper functions for pose landmark processing

Provides utilities for coordinate conversion, landmark interpolation,
and visibility analysis.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Point3D:
    """3D point representation for geometric calculations."""
    x: float
    y: float
    z: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.x, self.y, self.z])
    
    def to_2d(self) -> np.ndarray:
        """Convert to 2D array (x, y only)."""
        return np.array([self.x, self.y])
    
    @classmethod
    def from_landmark(cls, landmark) -> 'Point3D':
        """Create Point3D from a Landmark object."""
        return cls(x=landmark.x, y=landmark.y, z=landmark.z)
    
    def distance_to(self, other: 'Point3D') -> float:
        """Calculate Euclidean distance to another point."""
        return np.linalg.norm(self.to_array() - other.to_array())
    
    def midpoint(self, other: 'Point3D') -> 'Point3D':
        """Calculate midpoint between this point and another."""
        return Point3D(
            x=(self.x + other.x) / 2,
            y=(self.y + other.y) / 2,
            z=(self.z + other.z) / 2
        )


class LandmarkProcessor:
    """
    Utility class for processing and transforming pose landmarks.
    """
    
    @staticmethod
    def to_pixel_coordinates(landmarks: Dict, width: int, height: int) -> Dict[str, Tuple[int, int]]:
        """
        Convert all normalized landmarks to pixel coordinates.
        
        Args:
            landmarks: Dictionary of Landmark objects
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Dictionary mapping landmark names to (x, y) pixel coordinates
        """
        pixel_coords = {}
        for name, landmark in landmarks.items():
            pixel_coords[name] = landmark.to_pixel(width, height)
        return pixel_coords
    
    @staticmethod
    def get_point_3d(landmarks: Dict, name: str) -> Optional[Point3D]:
        """
        Get a Point3D from landmarks by name.
        
        Args:
            landmarks: Dictionary of Landmark objects
            name: Landmark name
            
        Returns:
            Point3D object or None if landmark not found
        """
        if name in landmarks:
            return Point3D.from_landmark(landmarks[name])
        return None
    
    @staticmethod
    def calculate_midpoint(landmarks: Dict, name1: str, name2: str) -> Optional[Point3D]:
        """
        Calculate midpoint between two landmarks.
        
        Args:
            landmarks: Dictionary of Landmark objects
            name1: First landmark name
            name2: Second landmark name
            
        Returns:
            Midpoint as Point3D, or None if either landmark is missing
        """
        if name1 not in landmarks or name2 not in landmarks:
            return None
        
        p1 = Point3D.from_landmark(landmarks[name1])
        p2 = Point3D.from_landmark(landmarks[name2])
        return p1.midpoint(p2)
    
    @staticmethod
    def get_body_center(landmarks: Dict) -> Optional[Point3D]:
        """
        Calculate the center of the body (midpoint of hips).
        
        Args:
            landmarks: Dictionary of Landmark objects
            
        Returns:
            Body center as Point3D
        """
        return LandmarkProcessor.calculate_midpoint(landmarks, 'left_hip', 'right_hip')
    
    @staticmethod
    def get_shoulder_center(landmarks: Dict) -> Optional[Point3D]:
        """
        Calculate the center of shoulders.
        
        Args:
            landmarks: Dictionary of Landmark objects
            
        Returns:
            Shoulder center as Point3D
        """
        return LandmarkProcessor.calculate_midpoint(landmarks, 'left_shoulder', 'right_shoulder')
    
    @staticmethod
    def get_head_position(landmarks: Dict) -> Optional[Point3D]:
        """
        Calculate the approximate head position (between ears or at nose).
        
        Args:
            landmarks: Dictionary of Landmark objects
            
        Returns:
            Head position as Point3D
        """
        # Try midpoint between ears first
        head = LandmarkProcessor.calculate_midpoint(landmarks, 'left_ear', 'right_ear')
        if head:
            return head
        
        # Fall back to nose
        if 'nose' in landmarks:
            return Point3D.from_landmark(landmarks['nose'])
        
        return None
    
    @staticmethod
    def get_spine_line(landmarks: Dict) -> Optional[Tuple[Point3D, Point3D]]:
        """
        Get the spine line from hip center to shoulder center.
        
        Args:
            landmarks: Dictionary of Landmark objects
            
        Returns:
            Tuple of (hip_center, shoulder_center) as Point3D objects
        """
        hip_center = LandmarkProcessor.get_body_center(landmarks)
        shoulder_center = LandmarkProcessor.get_shoulder_center(landmarks)
        
        if hip_center and shoulder_center:
            return (hip_center, shoulder_center)
        return None
    
    @staticmethod
    def calculate_visibility_score(landmarks: Dict, required_names: List[str]) -> float:
        """
        Calculate overall visibility score for required landmarks.
        
        Args:
            landmarks: Dictionary of Landmark objects
            required_names: List of required landmark names
            
        Returns:
            Average visibility score (0-1)
        """
        if not required_names:
            return 0.0
        
        total_visibility = 0.0
        count = 0
        
        for name in required_names:
            if name in landmarks:
                total_visibility += landmarks[name].visibility
                count += 1
        
        return total_visibility / len(required_names) if count > 0 else 0.0
    
    @staticmethod
    def interpolate_missing_landmark(
        landmarks: Dict, 
        missing_name: str, 
        reference_pairs: List[Tuple[str, str, float]]
    ) -> Optional[Point3D]:
        """
        Interpolate a missing landmark based on known landmarks.
        
        Args:
            landmarks: Dictionary of Landmark objects
            missing_name: Name of the missing landmark
            reference_pairs: List of (landmark1, landmark2, ratio) tuples
                           where the missing point is at ratio between l1 and l2
            
        Returns:
            Interpolated Point3D or None if interpolation not possible
        """
        for ref1, ref2, ratio in reference_pairs:
            if ref1 in landmarks and ref2 in landmarks:
                p1 = Point3D.from_landmark(landmarks[ref1])
                p2 = Point3D.from_landmark(landmarks[ref2])
                
                # Linear interpolation
                interpolated = Point3D(
                    x=p1.x + ratio * (p2.x - p1.x),
                    y=p1.y + ratio * (p2.y - p1.y),
                    z=p1.z + ratio * (p2.z - p1.z)
                )
                return interpolated
        
        return None
    
    @staticmethod
    def determine_view_orientation(landmarks: Dict) -> str:
        """
        Determine if the image shows a front, back, or side view.
        
        Args:
            landmarks: Dictionary of Landmark objects
            
        Returns:
            'front', 'back', 'left_side', 'right_side', or 'unknown'
        """
        if 'left_shoulder' not in landmarks or 'right_shoulder' not in landmarks:
            return 'unknown'
        
        left_shoulder = landmarks['left_shoulder']
        right_shoulder = landmarks['right_shoulder']
        
        # Calculate shoulder width (x difference)
        shoulder_width = abs(right_shoulder.x - left_shoulder.x)
        
        # Calculate depth difference
        depth_diff = abs(right_shoulder.z - left_shoulder.z)
        
        # If shoulders are roughly aligned horizontally, it's front/back view
        if shoulder_width > 0.15:  # Significant horizontal spread
            # Check nose/face visibility to determine front vs back
            if 'nose' in landmarks and landmarks['nose'].visibility > 0.5:
                return 'front'
            else:
                return 'back'
        else:
            # Side view - determine which side
            if 'left_shoulder' in landmarks and landmarks['left_shoulder'].visibility > landmarks.get('right_shoulder', landmarks['left_shoulder']).visibility:
                return 'right_side'  # We see the left shoulder more, so we're viewing from the right
            else:
                return 'left_side'
    
    @staticmethod
    def get_dominant_side(landmarks: Dict) -> str:
        """
        Determine which side of the body is more visible.
        
        Args:
            landmarks: Dictionary of Landmark objects
            
        Returns:
            'left', 'right', or 'both'
        """
        left_landmarks = ['left_shoulder', 'left_elbow', 'left_wrist', 'left_hip', 'left_knee']
        right_landmarks = ['right_shoulder', 'right_elbow', 'right_wrist', 'right_hip', 'right_knee']
        
        left_visibility = sum(
            landmarks[name].visibility 
            for name in left_landmarks 
            if name in landmarks
        )
        right_visibility = sum(
            landmarks[name].visibility 
            for name in right_landmarks 
            if name in landmarks
        )
        
        threshold = 0.3  # Minimum difference to declare dominance
        
        if abs(left_visibility - right_visibility) < threshold:
            return 'both'
        elif left_visibility > right_visibility:
            return 'left'
        else:
            return 'right'
