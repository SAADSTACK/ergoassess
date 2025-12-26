"""
RULA Engine - Rapid Upper Limb Assessment Scoring

Implements the complete RULA methodology as published by
McAtamney & Corlett (1993). All scoring is deterministic
and based on the official scoring tables.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.angle_calculator import JointAngles
from .rula_tables import (
    TABLE_A, TABLE_B, TABLE_C, get_action_level,
    UPPER_ARM_POSITION, LOWER_ARM_POSITION, WRIST_POSITION,
    NECK_POSITION, TRUNK_POSITION, LEGS_POSITION,
    UPPER_ARM_MODIFIERS, LOWER_ARM_MODIFIERS, WRIST_MODIFIERS,
    NECK_MODIFIERS, TRUNK_MODIFIERS, WRIST_TWIST,
    MUSCLE_USE_SCORE, FORCE_LOAD_SCORE
)


@dataclass
class RULAComponentScore:
    """Individual component score with justification."""
    component: str
    raw_score: int
    modifiers_applied: list
    final_score: int
    angle_measured: float
    threshold_crossed: str
    justification: str


@dataclass
class RULAResult:
    """Complete RULA assessment result."""
    # Component scores
    upper_arm: RULAComponentScore = None
    lower_arm: RULAComponentScore = None
    wrist: RULAComponentScore = None
    wrist_twist: RULAComponentScore = None
    neck: RULAComponentScore = None
    trunk: RULAComponentScore = None
    legs: RULAComponentScore = None
    
    # Group scores
    score_a_raw: int = 0  # Table A result
    score_a: int = 0      # After muscle/force adjustment
    score_b_raw: int = 0  # Table B result
    score_b: int = 0      # After muscle/force adjustment
    
    # Muscle and force
    muscle_use_a: int = 0
    force_load_a: int = 0
    muscle_use_b: int = 0
    force_load_b: int = 0
    
    # Final score
    final_score: int = 0
    
    # Action level
    action_level: int = 1
    action_description: str = ""
    action_recommendation: str = ""
    action_urgency: str = ""
    action_color: str = "#22c55e"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'components': {
                'upper_arm': self._component_to_dict(self.upper_arm) if self.upper_arm else None,
                'lower_arm': self._component_to_dict(self.lower_arm) if self.lower_arm else None,
                'wrist': self._component_to_dict(self.wrist) if self.wrist else None,
                'wrist_twist': self._component_to_dict(self.wrist_twist) if self.wrist_twist else None,
                'neck': self._component_to_dict(self.neck) if self.neck else None,
                'trunk': self._component_to_dict(self.trunk) if self.trunk else None,
                'legs': self._component_to_dict(self.legs) if self.legs else None
            },
            'group_scores': {
                'score_a_raw': self.score_a_raw,
                'score_a': self.score_a,
                'score_b_raw': self.score_b_raw,
                'score_b': self.score_b
            },
            'modifiers': {
                'muscle_use_a': self.muscle_use_a,
                'force_load_a': self.force_load_a,
                'muscle_use_b': self.muscle_use_b,
                'force_load_b': self.force_load_b
            },
            'final_score': self.final_score,
            'action_level': {
                'level': self.action_level,
                'description': self.action_description,
                'recommendation': self.action_recommendation,
                'urgency': self.action_urgency,
                'color': self.action_color
            }
        }
    
    def _component_to_dict(self, component: RULAComponentScore) -> dict:
        return {
            'raw_score': component.raw_score,
            'modifiers': component.modifiers_applied,
            'final_score': component.final_score,
            'angle': component.angle_measured,
            'threshold': component.threshold_crossed,
            'justification': component.justification
        }


class RULAEngine:
    """
    RULA (Rapid Upper Limb Assessment) scoring engine.
    
    Implements the complete RULA methodology for assessing
    upper limb posture risks. All calculations are deterministic
    and based on the official RULA tables.
    """
    
    def __init__(self, is_static: bool = True, load_kg: float = 0.0,
                 is_repetitive: bool = False, is_shock_load: bool = False):
        """
        Initialize RULA engine with task context.
        
        Args:
            is_static: Whether the posture is held statically (>1 min)
            load_kg: Weight of load being handled in kg
            is_repetitive: Whether action is repeated >4x/min
            is_shock_load: Whether there are shock/rapid force buildups
        """
        self.is_static = is_static
        self.load_kg = load_kg
        self.is_repetitive = is_repetitive
        self.is_shock_load = is_shock_load
    
    def calculate(self, angles: JointAngles) -> RULAResult:
        """
        Calculate complete RULA score from joint angles.
        
        Args:
            angles: JointAngles object with all computed angles
            
        Returns:
            RULAResult with complete assessment
        """
        result = RULAResult()
        
        # Group A: Upper arm, lower arm, wrist
        result.upper_arm = self._score_upper_arm(angles)
        result.lower_arm = self._score_lower_arm(angles)
        result.wrist = self._score_wrist(angles)
        result.wrist_twist = self._score_wrist_twist(angles)
        
        # Group B: Neck, trunk, legs
        result.neck = self._score_neck(angles)
        result.trunk = self._score_trunk(angles)
        result.legs = self._score_legs(angles)
        
        # Calculate Table A score
        result.score_a_raw = self._lookup_table_a(
            result.upper_arm.final_score,
            result.lower_arm.final_score,
            result.wrist.final_score,
            result.wrist_twist.final_score
        )
        
        # Calculate Table B score
        result.score_b_raw = self._lookup_table_b(
            result.neck.final_score,
            result.trunk.final_score,
            result.legs.final_score
        )
        
        # Apply muscle use and force scores
        result.muscle_use_a = self._get_muscle_use_score()
        result.force_load_a = self._get_force_load_score()
        result.muscle_use_b = result.muscle_use_a  # Same for both groups
        result.force_load_b = result.force_load_a
        
        result.score_a = result.score_a_raw + result.muscle_use_a + result.force_load_a
        result.score_b = result.score_b_raw + result.muscle_use_b + result.force_load_b
        
        # Clamp scores to valid ranges for Table C lookup
        score_a_clamped = min(max(result.score_a, 1), 8)
        score_b_clamped = min(max(result.score_b, 1), 7)
        
        # Calculate final score from Table C
        result.final_score = self._lookup_table_c(score_a_clamped, score_b_clamped)
        
        # Get action level
        action = get_action_level(result.final_score)
        result.action_level = action['level']
        result.action_description = action['description']
        result.action_recommendation = action['action']
        result.action_urgency = action['urgency']
        result.action_color = action['color']
        
        return result
    
    def _score_upper_arm(self, angles: JointAngles) -> RULAComponentScore:
        """Score the upper arm position."""
        # Determine the primary angle (flexion or extension)
        angle = angles.upper_arm_flexion if angles.upper_arm_flexion > 0 else -angles.upper_arm_extension
        abs_angle = abs(angle)
        
        # Get base score from angle ranges
        if -20 <= angle <= 20:
            raw_score = 1
            threshold = "20° extension to 20° flexion"
        elif 20 < angle <= 45:
            raw_score = 2
            threshold = "20°-45° flexion"
        elif 45 < angle <= 90:
            raw_score = 3
            threshold = "45°-90° flexion"
        elif angle > 90:
            raw_score = 4
            threshold = ">90° flexion"
        elif -45 <= angle < -20:
            raw_score = 2
            threshold = "20°-45° extension"
        else:  # angle < -45
            raw_score = 3
            threshold = ">45° extension"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if angles.shoulder_raised:
            modifiers.append("+1 shoulder raised")
            modifier_total += 1
        
        if angles.upper_arm_abduction > 45:
            modifiers.append("+1 arm abducted >45°")
            modifier_total += 1
        
        if angles.arm_supported:
            modifiers.append("-1 arm supported")
            modifier_total -= 1
        
        final_score = max(1, min(6, raw_score + modifier_total))
        
        justification = (
            f"Upper arm at {angles.upper_arm_flexion:.1f}° flexion. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return RULAComponentScore(
            component="upper_arm",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_lower_arm(self, angles: JointAngles) -> RULAComponentScore:
        """Score the lower arm (elbow) position."""
        angle = angles.lower_arm_flexion
        
        # Get base score from angle ranges
        if 60 <= angle <= 100:
            raw_score = 1
            threshold = "60°-100° flexion (optimal)"
        else:
            raw_score = 2
            threshold = "<60° or >100° flexion"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if angles.lower_arm_across_midline:
            modifiers.append("+1 arm across midline")
            modifier_total += 1
        
        # Check for arm working out to side (based on abduction)
        if angles.upper_arm_abduction > 30:
            modifiers.append("+1 arm out to side")
            modifier_total += 1
        
        final_score = max(1, min(3, raw_score + modifier_total))
        
        justification = (
            f"Lower arm (elbow) at {angle:.1f}° flexion. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return RULAComponentScore(
            component="lower_arm",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_wrist(self, angles: JointAngles) -> RULAComponentScore:
        """Score the wrist position."""
        # Use whichever is greater - flexion or extension
        angle = max(angles.wrist_flexion, angles.wrist_extension)
        
        # Get base score from angle ranges
        if angle == 0:
            raw_score = 1
            threshold = "Neutral position"
        elif angle <= 15:
            raw_score = 2
            threshold = "0°-15° flexion/extension"
        else:
            raw_score = 3
            threshold = ">15° flexion/extension"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if angles.wrist_deviation > 15:
            modifiers.append("+1 wrist deviated from midline")
            modifier_total += 1
        
        final_score = max(1, min(4, raw_score + modifier_total))
        
        justification = (
            f"Wrist at {angle:.1f}° from neutral. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Deviation: {angles.wrist_deviation:.1f}°. "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return RULAComponentScore(
            component="wrist",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_wrist_twist(self, angles: JointAngles) -> RULAComponentScore:
        """Score wrist twist/rotation."""
        if angles.wrist_twist:
            raw_score = 2
            threshold = "Near end of twisting range"
        else:
            raw_score = 1
            threshold = "Mid-range of twist"
        
        justification = (
            f"Wrist twist: {threshold}. "
            f"Score: {raw_score}."
        )
        
        return RULAComponentScore(
            component="wrist_twist",
            raw_score=raw_score,
            modifiers_applied=[],
            final_score=raw_score,
            angle_measured=0.0,  # Twist is not easily quantified as angle
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_neck(self, angles: JointAngles) -> RULAComponentScore:
        """Score neck position."""
        angle = angles.neck_flexion if angles.neck_flexion > 0 else -angles.neck_extension
        
        # Get base score from angle ranges
        if angles.neck_extension > 0:
            raw_score = 4
            threshold = "Neck in extension"
        elif 0 <= angles.neck_flexion <= 10:
            raw_score = 1
            threshold = "0°-10° flexion"
        elif 10 < angles.neck_flexion <= 20:
            raw_score = 2
            threshold = "10°-20° flexion"
        else:
            raw_score = 3
            threshold = ">20° flexion"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if abs(angles.neck_twist) > 10:
            modifiers.append("+1 neck twisted")
            modifier_total += 1
        
        if abs(angles.neck_side_bend) > 10:
            modifiers.append("+1 neck side-bending")
            modifier_total += 1
        
        final_score = max(1, min(6, raw_score + modifier_total))
        
        justification = (
            f"Neck at {angles.neck_flexion:.1f}° flexion, {angles.neck_extension:.1f}° extension. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Side bend: {angles.neck_side_bend:.1f}°, twist: {angles.neck_twist:.1f}°. "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return RULAComponentScore(
            component="neck",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angles.neck_flexion,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_trunk(self, angles: JointAngles) -> RULAComponentScore:
        """Score trunk position."""
        angle = angles.trunk_flexion
        
        # Get base score from angle ranges
        if angle == 0:
            raw_score = 1
            threshold = "Upright/well supported"
        elif 0 < angle <= 20:
            raw_score = 2
            threshold = "0°-20° flexion"
        elif 20 < angle <= 60:
            raw_score = 3
            threshold = "20°-60° flexion"
        else:
            raw_score = 4
            threshold = ">60° flexion"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if abs(angles.trunk_twist) > 10:
            modifiers.append("+1 trunk twisted")
            modifier_total += 1
        
        if abs(angles.trunk_side_bend) > 10:
            modifiers.append("+1 trunk side-bending")
            modifier_total += 1
        
        final_score = max(1, min(6, raw_score + modifier_total))
        
        justification = (
            f"Trunk at {angle:.1f}° flexion. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Side bend: {angles.trunk_side_bend:.1f}°. "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return RULAComponentScore(
            component="trunk",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_legs(self, angles: JointAngles) -> RULAComponentScore:
        """Score leg/feet position."""
        if angles.leg_supported and angles.leg_weight_even:
            raw_score = 1
            threshold = "Legs supported, weight balanced"
        else:
            raw_score = 2
            threshold = "Legs not supported or weight uneven"
        
        justification = (
            f"Legs supported: {'Yes' if angles.leg_supported else 'No'}, "
            f"Weight even: {'Yes' if angles.leg_weight_even else 'No'}. "
            f"Score: {raw_score}."
        )
        
        return RULAComponentScore(
            component="legs",
            raw_score=raw_score,
            modifiers_applied=[],
            final_score=raw_score,
            angle_measured=angles.leg_flexion,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _lookup_table_a(self, upper_arm: int, lower_arm: int, 
                        wrist: int, wrist_twist: int) -> int:
        """Look up score in Table A."""
        # Clamp values to valid ranges
        ua = min(max(upper_arm, 1), 6)
        la = min(max(lower_arm, 1), 3)
        w = min(max(wrist, 1), 4)
        wt = min(max(wrist_twist, 1), 2)
        
        return TABLE_A[ua][la][w][wt]
    
    def _lookup_table_b(self, neck: int, trunk: int, legs: int) -> int:
        """Look up score in Table B."""
        # Clamp values to valid ranges
        n = min(max(neck, 1), 6)
        t = min(max(trunk, 1), 6)
        l = min(max(legs, 1), 2)
        
        return TABLE_B[n][t][l]
    
    def _lookup_table_c(self, score_a: int, score_b: int) -> int:
        """Look up final score in Table C."""
        return TABLE_C[score_a][score_b]
    
    def _get_muscle_use_score(self) -> int:
        """Calculate muscle use score."""
        if self.is_static or self.is_repetitive:
            return 1
        return 0
    
    def _get_force_load_score(self) -> int:
        """Calculate force/load score."""
        if self.is_shock_load:
            return 3
        elif self.load_kg > 10:
            return 3 if self.is_static else 2
        elif self.load_kg >= 2:
            return 2 if self.is_static else 1
        else:
            return 0
    
    def get_summary(self, result: RULAResult) -> str:
        """Generate human-readable summary of RULA assessment."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    RULA ASSESSMENT SUMMARY                   ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "",
            "GROUP A (UPPER LIMB):",
            f"  Upper Arm Score: {result.upper_arm.final_score}",
            f"  Lower Arm Score: {result.lower_arm.final_score}",
            f"  Wrist Score: {result.wrist.final_score}",
            f"  Wrist Twist: {result.wrist_twist.final_score}",
            f"  Table A Score: {result.score_a_raw}",
            f"  + Muscle Use: {result.muscle_use_a}",
            f"  + Force/Load: {result.force_load_a}",
            f"  = Score A: {result.score_a}",
            "",
            "GROUP B (NECK/TRUNK/LEGS):",
            f"  Neck Score: {result.neck.final_score}",
            f"  Trunk Score: {result.trunk.final_score}",
            f"  Legs Score: {result.legs.final_score}",
            f"  Table B Score: {result.score_b_raw}",
            f"  + Muscle Use: {result.muscle_use_b}",
            f"  + Force/Load: {result.force_load_b}",
            f"  = Score B: {result.score_b}",
            "",
            "═" * 64,
            f"  FINAL RULA SCORE: {result.final_score}",
            f"  ACTION LEVEL: {result.action_level} - {result.action_description}",
            "═" * 64,
            "",
            f"RECOMMENDATION: {result.action_recommendation}",
            f"URGENCY: {result.action_urgency}",
            "",
            "╚══════════════════════════════════════════════════════════════╝"
        ]
        
        return "\n".join(lines)
