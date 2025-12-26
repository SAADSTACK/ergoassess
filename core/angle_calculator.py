"""
Biomechanical Angle Calculator - Deterministic Joint Angle Computation

Computes all required joint angles for RULA and REBA assessment
using vector geometry and fixed anatomical reference frames.
"""

import numpy as np
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass

from .landmark_utils import Point3D, LandmarkProcessor


@dataclass
class JointAngles:
    """Container for all computed joint angles."""
    # Neck angles
    neck_flexion: float = 0.0
    neck_extension: float = 0.0
    neck_side_bend: float = 0.0
    neck_twist: float = 0.0
    
    # Trunk angles
    trunk_flexion: float = 0.0
    trunk_extension: float = 0.0
    trunk_side_bend: float = 0.0
    trunk_twist: float = 0.0
    
    # Upper arm angles (using dominant/visible side)
    upper_arm_flexion: float = 0.0
    upper_arm_extension: float = 0.0
    upper_arm_abduction: float = 0.0
    shoulder_raised: bool = False
    arm_supported: bool = False
    
    # Lower arm angle
    lower_arm_flexion: float = 0.0
    lower_arm_across_midline: bool = False
    
    # Wrist angles
    wrist_flexion: float = 0.0
    wrist_extension: float = 0.0
    wrist_deviation: float = 0.0
    wrist_twist: bool = False  # Mid-range or near end of range
    
    # Leg angles
    leg_flexion: float = 0.0
    leg_supported: bool = True  # Both feet on ground
    leg_weight_even: bool = True  # Weight evenly distributed
    
    # Analysis side
    dominant_side: str = 'right'
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'neck': {
                'flexion': round(self.neck_flexion, 1),
                'extension': round(self.neck_extension, 1),
                'side_bend': round(self.neck_side_bend, 1),
                'twist': round(self.neck_twist, 1)
            },
            'trunk': {
                'flexion': round(self.trunk_flexion, 1),
                'extension': round(self.trunk_extension, 1),
                'side_bend': round(self.trunk_side_bend, 1),
                'twist': round(self.trunk_twist, 1)
            },
            'upper_arm': {
                'flexion': round(self.upper_arm_flexion, 1),
                'extension': round(self.upper_arm_extension, 1),
                'abduction': round(self.upper_arm_abduction, 1),
                'shoulder_raised': self.shoulder_raised,
                'arm_supported': self.arm_supported
            },
            'lower_arm': {
                'flexion': round(self.lower_arm_flexion, 1),
                'across_midline': self.lower_arm_across_midline
            },
            'wrist': {
                'flexion': round(self.wrist_flexion, 1),
                'extension': round(self.wrist_extension, 1),
                'deviation': round(self.wrist_deviation, 1),
                'twist': self.wrist_twist
            },
            'legs': {
                'flexion': round(self.leg_flexion, 1),
                'supported': self.leg_supported,
                'weight_even': self.leg_weight_even
            },
            'dominant_side': self.dominant_side
        }


class AngleCalculator:
    """
    Deterministic joint angle calculator for ergonomic assessment.
    
    Uses vector geometry to compute precise joint angles from
    detected pose landmarks. All calculations are reproducible
    and based on anatomical reference frames.
    """
    
    # Vertical reference vector (pointing up in image coordinates)
    VERTICAL_UP = np.array([0, -1, 0])
    VERTICAL_DOWN = np.array([0, 1, 0])
    
    def __init__(self):
        """Initialize angle calculator."""
        self.landmark_processor = LandmarkProcessor()
    
    @staticmethod
    def calculate_angle_3points(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        Calculate angle at point p2 between vectors p2->p1 and p2->p3.
        
        This is the fundamental angle calculation used throughout.
        
        Args:
            p1: First point as numpy array [x, y, z] or [x, y]
            p2: Vertex point (angle calculated here)
            p3: Third point
            
        Returns:
            Angle in degrees (0-180)
        """
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Normalize vectors
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        
        if v1_norm == 0 or v2_norm == 0:
            return 0.0
        
        v1 = v1 / v1_norm
        v2 = v2 / v2_norm
        
        # Calculate angle using dot product
        cos_angle = np.clip(np.dot(v1, v2), -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        
        return angle
    
    @staticmethod
    def calculate_angle_from_vertical(p1: np.ndarray, p2: np.ndarray, 
                                       reference: np.ndarray = None) -> float:
        """
        Calculate the angle of a line segment from vertical.
        
        Args:
            p1: Start point
            p2: End point
            reference: Reference vertical vector (default: up)
            
        Returns:
            Angle from vertical in degrees
        """
        if reference is None:
            reference = AngleCalculator.VERTICAL_UP
        
        direction = p2 - p1
        direction_norm = np.linalg.norm(direction)
        
        if direction_norm == 0:
            return 0.0
        
        direction = direction / direction_norm
        reference = reference / np.linalg.norm(reference)
        
        cos_angle = np.clip(np.dot(direction, reference), -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        
        return angle
    
    @staticmethod
    def calculate_lateral_deviation(p1: np.ndarray, p2: np.ndarray, 
                                    midline: np.ndarray) -> float:
        """
        Calculate lateral deviation of a line segment from midline.
        
        Args:
            p1: Start point
            p2: End point
            midline: Point defining the midline reference
            
        Returns:
            Lateral deviation in degrees (positive = right, negative = left)
        """
        # Project onto frontal plane (x-y)
        direction = p2[:2] - p1[:2]
        direction_norm = np.linalg.norm(direction)
        
        if direction_norm == 0:
            return 0.0
        
        # Calculate horizontal deviation
        horizontal = np.array([1, 0])
        angle = np.degrees(np.arctan2(direction[0], -direction[1]))
        
        return angle
    
    def compute_all_angles(self, landmarks: Dict) -> JointAngles:
        """
        Compute all joint angles required for RULA and REBA assessment.
        
        Args:
            landmarks: Dictionary of detected pose landmarks
            
        Returns:
            JointAngles object with all computed angles
        """
        angles = JointAngles()
        
        # Determine dominant side for analysis
        dominant_side = self.landmark_processor.get_dominant_side(landmarks)
        angles.dominant_side = dominant_side if dominant_side != 'both' else 'right'
        
        # Get key reference points
        shoulder_center = self.landmark_processor.get_shoulder_center(landmarks)
        hip_center = self.landmark_processor.get_body_center(landmarks)
        head_pos = self.landmark_processor.get_head_position(landmarks)
        
        # Compute neck angles
        self._compute_neck_angles(landmarks, angles, shoulder_center, head_pos)
        
        # Compute trunk angles
        self._compute_trunk_angles(landmarks, angles, hip_center, shoulder_center)
        
        # Compute arm angles (use dominant side)
        self._compute_arm_angles(landmarks, angles)
        
        # Compute wrist angles
        self._compute_wrist_angles(landmarks, angles)
        
        # Compute leg angles
        self._compute_leg_angles(landmarks, angles)
        
        return angles
    
    def _compute_neck_angles(self, landmarks: Dict, angles: JointAngles,
                             shoulder_center: Optional[Point3D],
                             head_pos: Optional[Point3D]) -> None:
        """Compute neck flexion, extension, and side bend angles."""
        if not shoulder_center or not head_pos:
            return
        
        # Get ear positions for better neck angle estimation
        left_ear = self.landmark_processor.get_point_3d(landmarks, 'left_ear')
        right_ear = self.landmark_processor.get_point_3d(landmarks, 'right_ear')
        nose = self.landmark_processor.get_point_3d(landmarks, 'nose')
        
        # Calculate neck flexion/extension from shoulder to head
        shoulder_arr = shoulder_center.to_array()
        head_arr = head_pos.to_array()
        
        # Neck angle from vertical
        neck_direction = head_arr - shoulder_arr
        neck_from_vertical = self.calculate_angle_from_vertical(
            shoulder_arr, head_arr, self.VERTICAL_UP
        )
        
        # Determine if flexion (forward) or extension (backward)
        if neck_direction[2] > 0:  # Head is forward (positive z means toward camera)
            angles.neck_flexion = max(0, neck_from_vertical - 10)  # Subtract neutral ~10°
            angles.neck_extension = 0
        else:
            angles.neck_flexion = 0
            angles.neck_extension = max(0, neck_from_vertical - 10)
        
        # Calculate side bend
        if left_ear and right_ear:
            ear_height_diff = left_ear.y - right_ear.y
            ear_distance = abs(left_ear.x - right_ear.x)
            if ear_distance > 0:
                side_bend_ratio = ear_height_diff / ear_distance
                angles.neck_side_bend = np.degrees(np.arctan(side_bend_ratio))
        
        # Estimate neck twist based on nose position relative to shoulders
        if nose:
            left_shoulder = self.landmark_processor.get_point_3d(landmarks, 'left_shoulder')
            right_shoulder = self.landmark_processor.get_point_3d(landmarks, 'right_shoulder')
            if left_shoulder and right_shoulder:
                shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
                nose_offset = nose.x - shoulder_midpoint_x
                shoulder_width = abs(right_shoulder.x - left_shoulder.x)
                if shoulder_width > 0:
                    twist_ratio = nose_offset / (shoulder_width / 2)
                    angles.neck_twist = np.degrees(np.arcsin(np.clip(twist_ratio, -1, 1)))
    
    def _compute_trunk_angles(self, landmarks: Dict, angles: JointAngles,
                              hip_center: Optional[Point3D],
                              shoulder_center: Optional[Point3D]) -> None:
        """Compute trunk flexion, extension, and side bend angles."""
        if not hip_center or not shoulder_center:
            return
        
        hip_arr = hip_center.to_array()
        shoulder_arr = shoulder_center.to_array()
        
        # Trunk angle from vertical
        trunk_from_vertical = self.calculate_angle_from_vertical(
            hip_arr, shoulder_arr, self.VERTICAL_UP
        )
        
        # Determine if flexion or extension based on z-coordinate
        trunk_direction = shoulder_arr - hip_arr
        
        # Check if leaning forward (flexion) or backward (extension)
        # In image coordinates, more negative z = closer to camera
        if shoulder_arr[2] < hip_arr[2]:  # Shoulders forward of hips
            angles.trunk_flexion = trunk_from_vertical
            angles.trunk_extension = 0
        else:
            angles.trunk_flexion = 0
            angles.trunk_extension = trunk_from_vertical
        
        # Calculate side bend from shoulder heights
        left_shoulder = self.landmark_processor.get_point_3d(landmarks, 'left_shoulder')
        right_shoulder = self.landmark_processor.get_point_3d(landmarks, 'right_shoulder')
        left_hip = self.landmark_processor.get_point_3d(landmarks, 'left_hip')
        right_hip = self.landmark_processor.get_point_3d(landmarks, 'right_hip')
        
        if left_shoulder and right_shoulder and left_hip and right_hip:
            # Calculate asymmetry
            left_side_length = left_shoulder.distance_to(left_hip)
            right_side_length = right_shoulder.distance_to(right_hip)
            
            if max(left_side_length, right_side_length) > 0:
                asymmetry = (left_side_length - right_side_length) / max(left_side_length, right_side_length)
                angles.trunk_side_bend = asymmetry * 30  # Scale to degrees
    
    def _compute_arm_angles(self, landmarks: Dict, angles: JointAngles) -> None:
        """Compute upper arm and lower arm angles for the dominant side."""
        side = angles.dominant_side
        
        # Get arm landmarks
        shoulder = self.landmark_processor.get_point_3d(landmarks, f'{side}_shoulder')
        elbow = self.landmark_processor.get_point_3d(landmarks, f'{side}_elbow')
        wrist = self.landmark_processor.get_point_3d(landmarks, f'{side}_wrist')
        hip = self.landmark_processor.get_point_3d(landmarks, f'{side}_hip')
        
        if not shoulder or not elbow:
            return
        
        shoulder_arr = shoulder.to_array()
        elbow_arr = elbow.to_array()
        
        # Upper arm angle from vertical (flexion/extension)
        upper_arm_from_vertical = self.calculate_angle_from_vertical(
            shoulder_arr, elbow_arr, self.VERTICAL_DOWN
        )
        
        # Determine flexion vs extension
        if elbow_arr[2] < shoulder_arr[2]:  # Arm forward
            angles.upper_arm_flexion = upper_arm_from_vertical
            angles.upper_arm_extension = 0
        else:
            angles.upper_arm_flexion = 0
            angles.upper_arm_extension = upper_arm_from_vertical
        
        # Calculate abduction (arm away from body)
        if hip:
            hip_arr = hip.to_array()
            # Vector from hip to shoulder
            torso_line = shoulder_arr - hip_arr
            # Vector from shoulder to elbow
            arm_line = elbow_arr - shoulder_arr
            
            # Project onto frontal plane and calculate abduction
            torso_2d = np.array([torso_line[0], torso_line[1]])
            arm_2d = np.array([arm_line[0], arm_line[1]])
            
            if np.linalg.norm(torso_2d) > 0 and np.linalg.norm(arm_2d) > 0:
                # Abduction angle in frontal plane
                abduct_angle = self.calculate_angle_3points(
                    hip_arr[:2], shoulder_arr[:2], elbow_arr[:2]
                )
                angles.upper_arm_abduction = max(0, abduct_angle - 90)  # Neutral is 90°
        
        # Check for raised shoulder (compare shoulder heights)
        other_side = 'left' if side == 'right' else 'right'
        other_shoulder = self.landmark_processor.get_point_3d(landmarks, f'{other_side}_shoulder')
        if other_shoulder:
            height_diff = other_shoulder.y - shoulder.y  # In image coords, lower y = higher
            if height_diff > 0.02:  # Dominant shoulder is raised
                angles.shoulder_raised = True
        
        # Lower arm angle (elbow flexion)
        if wrist:
            wrist_arr = wrist.to_array()
            lower_arm_angle = self.calculate_angle_3points(
                shoulder_arr, elbow_arr, wrist_arr
            )
            angles.lower_arm_flexion = 180 - lower_arm_angle  # Convert to flexion angle
            
            # Check if arm crosses midline
            shoulder_center = self.landmark_processor.get_shoulder_center(landmarks)
            if shoulder_center:
                if side == 'right' and wrist.x < shoulder_center.x:
                    angles.lower_arm_across_midline = True
                elif side == 'left' and wrist.x > shoulder_center.x:
                    angles.lower_arm_across_midline = True
    
    def _compute_wrist_angles(self, landmarks: Dict, angles: JointAngles) -> None:
        """Compute wrist flexion/extension and deviation angles."""
        side = angles.dominant_side
        
        elbow = self.landmark_processor.get_point_3d(landmarks, f'{side}_elbow')
        wrist = self.landmark_processor.get_point_3d(landmarks, f'{side}_wrist')
        
        # Try to get finger landmarks for wrist angle
        index_finger = self.landmark_processor.get_point_3d(landmarks, f'{side}_index')
        pinky = self.landmark_processor.get_point_3d(landmarks, f'{side}_pinky')
        
        if not elbow or not wrist:
            return
        
        elbow_arr = elbow.to_array()
        wrist_arr = wrist.to_array()
        
        # If we have finger landmarks, calculate wrist angle
        if index_finger and pinky:
            # Use midpoint of fingers as hand direction reference
            hand_center = index_finger.midpoint(pinky)
            hand_arr = hand_center.to_array()
            
            # Calculate wrist angle (deviation from straight line)
            wrist_angle = self.calculate_angle_3points(elbow_arr, wrist_arr, hand_arr)
            
            # Neutral wrist is ~180°, deviation from this
            wrist_deviation_from_neutral = abs(180 - wrist_angle)
            
            # Determine if flexion or extension based on hand position
            forearm_dir = wrist_arr - elbow_arr
            hand_dir = hand_arr - wrist_arr
            
            # Cross product to determine direction
            cross = np.cross(forearm_dir[:2], hand_dir[:2])
            
            if cross > 0:  # One direction
                angles.wrist_flexion = wrist_deviation_from_neutral
                angles.wrist_extension = 0
            else:
                angles.wrist_flexion = 0
                angles.wrist_extension = wrist_deviation_from_neutral
            
            # Calculate ulnar/radial deviation
            # This is the angle in the horizontal plane
            angles.wrist_deviation = abs(index_finger.x - pinky.x) * 45  # Rough estimate
            
            # Check for wrist twist (mid-range or end of range)
            # This is difficult to determine from 2D landmarks
            # Use hand orientation as proxy
            hand_rotation = abs(index_finger.z - pinky.z)
            if hand_rotation > 0.05:
                angles.wrist_twist = True
    
    def _compute_leg_angles(self, landmarks: Dict, angles: JointAngles) -> None:
        """Compute leg support and posture angles."""
        left_hip = self.landmark_processor.get_point_3d(landmarks, 'left_hip')
        right_hip = self.landmark_processor.get_point_3d(landmarks, 'right_hip')
        left_knee = self.landmark_processor.get_point_3d(landmarks, 'left_knee')
        right_knee = self.landmark_processor.get_point_3d(landmarks, 'right_knee')
        left_ankle = self.landmark_processor.get_point_3d(landmarks, 'left_ankle')
        right_ankle = self.landmark_processor.get_point_3d(landmarks, 'right_ankle')
        
        # Calculate knee flexion angles
        knee_angles = []
        
        if left_hip and left_knee and left_ankle:
            left_knee_angle = self.calculate_angle_3points(
                left_hip.to_array(),
                left_knee.to_array(),
                left_ankle.to_array()
            )
            knee_angles.append(180 - left_knee_angle)  # Convert to flexion
        
        if right_hip and right_knee and right_ankle:
            right_knee_angle = self.calculate_angle_3points(
                right_hip.to_array(),
                right_knee.to_array(),
                right_ankle.to_array()
            )
            knee_angles.append(180 - right_knee_angle)
        
        if knee_angles:
            angles.leg_flexion = sum(knee_angles) / len(knee_angles)
        
        # Determine if legs are supported (standing vs sitting)
        # If knees are significantly flexed (>45°), likely sitting
        if angles.leg_flexion > 45:
            angles.leg_supported = True  # Sitting with feet on ground
        else:
            angles.leg_supported = True  # Standing
        
        # Check weight distribution (compare ankle positions)
        if left_ankle and right_ankle:
            height_diff = abs(left_ankle.y - right_ankle.y)
            if height_diff < 0.02:  # Roughly same height
                angles.leg_weight_even = True
            else:
                angles.leg_weight_even = False
    
    def get_angle_summary(self, angles: JointAngles) -> str:
        """
        Generate a human-readable summary of computed angles.
        
        Args:
            angles: Computed joint angles
            
        Returns:
            Formatted string summary
        """
        lines = [
            "=== JOINT ANGLE ANALYSIS ===",
            f"Analysis Side: {angles.dominant_side.upper()}",
            "",
            "NECK:",
            f"  Flexion: {angles.neck_flexion:.1f}°",
            f"  Extension: {angles.neck_extension:.1f}°",
            f"  Side Bend: {angles.neck_side_bend:.1f}°",
            f"  Twist: {angles.neck_twist:.1f}°",
            "",
            "TRUNK:",
            f"  Flexion: {angles.trunk_flexion:.1f}°",
            f"  Extension: {angles.trunk_extension:.1f}°",
            f"  Side Bend: {angles.trunk_side_bend:.1f}°",
            "",
            "UPPER ARM:",
            f"  Flexion: {angles.upper_arm_flexion:.1f}°",
            f"  Extension: {angles.upper_arm_extension:.1f}°",
            f"  Abduction: {angles.upper_arm_abduction:.1f}°",
            f"  Shoulder Raised: {'Yes' if angles.shoulder_raised else 'No'}",
            "",
            "LOWER ARM:",
            f"  Flexion (elbow): {angles.lower_arm_flexion:.1f}°",
            f"  Crosses Midline: {'Yes' if angles.lower_arm_across_midline else 'No'}",
            "",
            "WRIST:",
            f"  Flexion: {angles.wrist_flexion:.1f}°",
            f"  Extension: {angles.wrist_extension:.1f}°",
            f"  Deviation: {angles.wrist_deviation:.1f}°",
            f"  Twist: {'Yes' if angles.wrist_twist else 'No'}",
            "",
            "LEGS:",
            f"  Flexion: {angles.leg_flexion:.1f}°",
            f"  Supported: {'Yes' if angles.leg_supported else 'No'}",
            f"  Weight Even: {'Yes' if angles.leg_weight_even else 'No'}",
        ]
        
        return "\n".join(lines)
