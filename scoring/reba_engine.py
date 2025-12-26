"""
REBA Engine - Rapid Entire Body Assessment Scoring

Implements the complete REBA methodology as published by
Hignett & McAtamney (2000). All scoring is deterministic
and based on the official scoring tables.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.angle_calculator import JointAngles
from .reba_tables import (
    TABLE_A, TABLE_B, TABLE_C, get_risk_level,
    TRUNK_POSITION, NECK_POSITION, LEGS_POSITION,
    UPPER_ARM_POSITION, LOWER_ARM_POSITION, WRIST_POSITION,
    LOAD_FORCE_SCORE, COUPLING_SCORE, ACTIVITY_SCORE
)


@dataclass
class REBAComponentScore:
    """Individual component score with justification."""
    component: str
    raw_score: int
    modifiers_applied: list
    final_score: int
    angle_measured: float
    threshold_crossed: str
    justification: str


@dataclass
class REBAResult:
    """Complete REBA assessment result."""
    # Group A: Trunk, Neck, Legs
    trunk: REBAComponentScore = None
    neck: REBAComponentScore = None
    legs: REBAComponentScore = None
    
    # Group B: Upper Arm, Lower Arm, Wrist
    upper_arm: REBAComponentScore = None
    lower_arm: REBAComponentScore = None
    wrist: REBAComponentScore = None
    
    # Group scores
    score_a_raw: int = 0      # Table A result
    load_force: int = 0       # Load/force score
    score_a: int = 0          # Score A + load/force
    
    score_b_raw: int = 0      # Table B result
    coupling: int = 0         # Coupling score
    score_b: int = 0          # Score B + coupling
    
    # Score C and activity
    score_c: int = 0          # From Table C
    activity_score: int = 0   # Activity adjustment
    
    # Final score
    final_score: int = 0
    
    # Risk level
    risk_level: str = "Negligible"
    risk_value: int = 1
    risk_description: str = ""
    risk_action: str = ""
    risk_urgency: str = ""
    risk_color: str = "#22c55e"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'group_a': {
                'trunk': self._component_to_dict(self.trunk) if self.trunk else None,
                'neck': self._component_to_dict(self.neck) if self.neck else None,
                'legs': self._component_to_dict(self.legs) if self.legs else None,
                'score_a_raw': self.score_a_raw,
                'load_force': self.load_force,
                'score_a': self.score_a
            },
            'group_b': {
                'upper_arm': self._component_to_dict(self.upper_arm) if self.upper_arm else None,
                'lower_arm': self._component_to_dict(self.lower_arm) if self.lower_arm else None,
                'wrist': self._component_to_dict(self.wrist) if self.wrist else None,
                'score_b_raw': self.score_b_raw,
                'coupling': self.coupling,
                'score_b': self.score_b
            },
            'score_c': self.score_c,
            'activity_score': self.activity_score,
            'final_score': self.final_score,
            'risk_assessment': {
                'level': self.risk_level,
                'value': self.risk_value,
                'description': self.risk_description,
                'action': self.risk_action,
                'urgency': self.risk_urgency,
                'color': self.risk_color
            }
        }
    
    def _component_to_dict(self, component: REBAComponentScore) -> dict:
        return {
            'raw_score': component.raw_score,
            'modifiers': component.modifiers_applied,
            'final_score': component.final_score,
            'angle': component.angle_measured,
            'threshold': component.threshold_crossed,
            'justification': component.justification
        }


class REBAEngine:
    """
    REBA (Rapid Entire Body Assessment) scoring engine.
    
    Implements the complete REBA methodology for assessing
    whole-body posture risks. All calculations are deterministic
    and based on the official REBA tables.
    """
    
    def __init__(self, load_kg: float = 0.0, coupling: str = 'good',
                 is_static: bool = False, is_repeated: bool = False,
                 has_rapid_change: bool = False, is_shock_load: bool = False):
        """
        Initialize REBA engine with task context.
        
        Args:
            load_kg: Weight of load being handled in kg
            coupling: Coupling quality ('good', 'fair', 'poor', 'unacceptable')
            is_static: Whether posture is held statically (>1 min)
            is_repeated: Whether small range actions repeated (>4x/min)
            has_rapid_change: Whether there are rapid large range posture changes
            is_shock_load: Whether there are shock/rapid force build-ups
        """
        self.load_kg = load_kg
        self.coupling = coupling
        self.is_static = is_static
        self.is_repeated = is_repeated
        self.has_rapid_change = has_rapid_change
        self.is_shock_load = is_shock_load
    
    def calculate(self, angles: JointAngles) -> REBAResult:
        """
        Calculate complete REBA score from joint angles.
        
        Args:
            angles: JointAngles object with all computed angles
            
        Returns:
            REBAResult with complete assessment
        """
        result = REBAResult()
        
        # Group A: Trunk, Neck, Legs
        result.trunk = self._score_trunk(angles)
        result.neck = self._score_neck(angles)
        result.legs = self._score_legs(angles)
        
        # Group B: Upper arm, Lower arm, Wrist
        result.upper_arm = self._score_upper_arm(angles)
        result.lower_arm = self._score_lower_arm(angles)
        result.wrist = self._score_wrist(angles)
        
        # Calculate Table A score
        result.score_a_raw = self._lookup_table_a(
            result.trunk.final_score,
            result.neck.final_score,
            result.legs.final_score
        )
        
        # Add load/force score
        result.load_force = self._get_load_force_score()
        result.score_a = result.score_a_raw + result.load_force
        
        # Calculate Table B score
        result.score_b_raw = self._lookup_table_b(
            result.upper_arm.final_score,
            result.lower_arm.final_score,
            result.wrist.final_score
        )
        
        # Add coupling score
        result.coupling = self._get_coupling_score()
        result.score_b = result.score_b_raw + result.coupling
        
        # Calculate Table C score
        result.score_c = self._lookup_table_c(result.score_a, result.score_b)
        
        # Add activity score
        result.activity_score = self._get_activity_score()
        
        # Final REBA score
        result.final_score = result.score_c + result.activity_score
        
        # Get risk level
        risk = get_risk_level(result.final_score)
        result.risk_level = risk['level']
        result.risk_value = risk['risk_value']
        result.risk_description = risk['description']
        result.risk_action = risk['action']
        result.risk_urgency = risk['urgency']
        result.risk_color = risk['color']
        
        return result
    
    def _score_trunk(self, angles: JointAngles) -> REBAComponentScore:
        """Score trunk position."""
        angle = angles.trunk_flexion
        
        # Get base score from angle ranges
        if angle == 0:
            raw_score = 1
            threshold = "Upright"
        elif 0 < angle <= 20:
            raw_score = 2
            threshold = "0°-20° flexion"
        elif 20 < angle <= 60:
            raw_score = 3
            threshold = "20°-60° flexion"
        else:
            raw_score = 4
            threshold = ">60° flexion"
        
        # Check for extension
        if angles.trunk_extension > 0:
            if angles.trunk_extension <= 20:
                raw_score = 2
                threshold = "0°-20° extension"
            else:
                raw_score = 3
                threshold = ">20° extension"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if abs(angles.trunk_twist) > 10:
            modifiers.append("+1 trunk twisted")
            modifier_total += 1
        
        if abs(angles.trunk_side_bend) > 10:
            modifiers.append("+1 trunk side-bending")
            modifier_total += 1
        
        final_score = max(1, min(5, raw_score + modifier_total))
        
        justification = (
            f"Trunk at {angle:.1f}° flexion. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return REBAComponentScore(
            component="trunk",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_neck(self, angles: JointAngles) -> REBAComponentScore:
        """Score neck position."""
        angle = angles.neck_flexion
        
        # Get base score from angle ranges
        if 0 <= angle <= 20:
            raw_score = 1
            threshold = "0°-20° flexion"
        else:
            raw_score = 2
            threshold = ">20° flexion"
        
        # Check for extension
        if angles.neck_extension > 0:
            raw_score = 2
            threshold = "In extension"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if abs(angles.neck_twist) > 10:
            modifiers.append("+1 neck twisted")
            modifier_total += 1
        
        if abs(angles.neck_side_bend) > 10:
            modifiers.append("+1 neck side-bending")
            modifier_total += 1
        
        final_score = max(1, min(3, raw_score + modifier_total))
        
        justification = (
            f"Neck at {angle:.1f}° flexion, {angles.neck_extension:.1f}° extension. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return REBAComponentScore(
            component="neck",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_legs(self, angles: JointAngles) -> REBAComponentScore:
        """Score leg position."""
        # Base score based on weight distribution
        if angles.leg_weight_even:
            raw_score = 1
            threshold = "Bilateral weight bearing"
        else:
            raw_score = 2
            threshold = "Unilateral weight bearing"
        
        # Apply modifiers based on knee flexion
        modifiers = []
        modifier_total = 0
        
        if 30 <= angles.leg_flexion <= 60:
            modifiers.append("+1 knees 30°-60° flexion")
            modifier_total += 1
        elif angles.leg_flexion > 60:
            modifiers.append("+2 knees >60° flexion")
            modifier_total += 2
        
        final_score = max(1, min(4, raw_score + modifier_total))
        
        justification = (
            f"Legs: weight {'evenly distributed' if angles.leg_weight_even else 'uneven'}. "
            f"Knee flexion: {angles.leg_flexion:.1f}°. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return REBAComponentScore(
            component="legs",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angles.leg_flexion,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_upper_arm(self, angles: JointAngles) -> REBAComponentScore:
        """Score upper arm position."""
        angle = angles.upper_arm_flexion if angles.upper_arm_flexion > 0 else -angles.upper_arm_extension
        
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
            threshold = ">20° extension"
        else:
            raw_score = 3
            threshold = ">45° extension"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if angles.shoulder_raised:
            modifiers.append("+1 shoulder raised")
            modifier_total += 1
        
        if angles.upper_arm_abduction > 45:
            modifiers.append("+1 arm abducted")
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
        
        return REBAComponentScore(
            component="upper_arm",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_lower_arm(self, angles: JointAngles) -> REBAComponentScore:
        """Score lower arm (elbow) position."""
        angle = angles.lower_arm_flexion
        
        # Get base score from angle ranges
        if 60 <= angle <= 100:
            raw_score = 1
            threshold = "60°-100° flexion"
        else:
            raw_score = 2
            threshold = "<60° or >100° flexion"
        
        justification = (
            f"Lower arm (elbow) at {angle:.1f}° flexion. "
            f"Threshold: {threshold}. "
            f"Score: {raw_score}."
        )
        
        return REBAComponentScore(
            component="lower_arm",
            raw_score=raw_score,
            modifiers_applied=[],
            final_score=raw_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _score_wrist(self, angles: JointAngles) -> REBAComponentScore:
        """Score wrist position."""
        # Use whichever is greater - flexion or extension
        angle = max(angles.wrist_flexion, angles.wrist_extension)
        
        # Get base score from angle ranges
        if angle <= 15:
            raw_score = 1
            threshold = "0°-15° flexion/extension"
        else:
            raw_score = 2
            threshold = ">15° flexion/extension"
        
        # Apply modifiers
        modifiers = []
        modifier_total = 0
        
        if angles.wrist_deviation > 15 or angles.wrist_twist:
            modifiers.append("+1 wrist bent/twisted")
            modifier_total += 1
        
        final_score = max(1, min(3, raw_score + modifier_total))
        
        justification = (
            f"Wrist at {angle:.1f}° from neutral. "
            f"Threshold: {threshold} (base score {raw_score}). "
            f"Deviation: {angles.wrist_deviation:.1f}°. "
            f"Modifiers: {', '.join(modifiers) if modifiers else 'none'}."
        )
        
        return REBAComponentScore(
            component="wrist",
            raw_score=raw_score,
            modifiers_applied=modifiers,
            final_score=final_score,
            angle_measured=angle,
            threshold_crossed=threshold,
            justification=justification
        )
    
    def _lookup_table_a(self, trunk: int, neck: int, legs: int) -> int:
        """Look up score in Table A."""
        # Clamp values to valid ranges
        t = min(max(trunk, 1), 5)
        n = min(max(neck, 1), 3)
        l = min(max(legs, 1), 4)
        
        return TABLE_A[t][n][l]
    
    def _lookup_table_b(self, upper_arm: int, lower_arm: int, wrist: int) -> int:
        """Look up score in Table B."""
        # Clamp values to valid ranges
        ua = min(max(upper_arm, 1), 6)
        la = min(max(lower_arm, 1), 2)
        w = min(max(wrist, 1), 3)
        
        return TABLE_B[ua][la][w]
    
    def _lookup_table_c(self, score_a: int, score_b: int) -> int:
        """Look up score in Table C."""
        # Clamp values to valid ranges
        a = min(max(score_a, 1), 12)
        b = min(max(score_b, 1), 12)
        
        return TABLE_C[a][b]
    
    def _get_load_force_score(self) -> int:
        """Calculate load/force score."""
        if self.load_kg < 5:
            base = 0
        elif self.load_kg <= 10:
            base = 1
        else:
            base = 2
        
        # Add shock loading
        if self.is_shock_load:
            base += 1
        
        return min(base, 3)
    
    def _get_coupling_score(self) -> int:
        """Calculate coupling score."""
        coupling_map = {
            'good': 0,
            'fair': 1,
            'poor': 2,
            'unacceptable': 3
        }
        return coupling_map.get(self.coupling.lower(), 0)
    
    def _get_activity_score(self) -> int:
        """Calculate activity score."""
        score = 0
        if self.is_static:
            score += 1
        if self.is_repeated:
            score += 1
        if self.has_rapid_change:
            score += 1
        return min(score, 3)
    
    def get_summary(self, result: REBAResult) -> str:
        """Generate human-readable summary of REBA assessment."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    REBA ASSESSMENT SUMMARY                   ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "",
            "GROUP A (TRUNK/NECK/LEGS):",
            f"  Trunk Score: {result.trunk.final_score}",
            f"  Neck Score: {result.neck.final_score}",
            f"  Legs Score: {result.legs.final_score}",
            f"  Table A Score: {result.score_a_raw}",
            f"  + Load/Force: {result.load_force}",
            f"  = Score A: {result.score_a}",
            "",
            "GROUP B (ARMS/WRIST):",
            f"  Upper Arm Score: {result.upper_arm.final_score}",
            f"  Lower Arm Score: {result.lower_arm.final_score}",
            f"  Wrist Score: {result.wrist.final_score}",
            f"  Table B Score: {result.score_b_raw}",
            f"  + Coupling: {result.coupling}",
            f"  = Score B: {result.score_b}",
            "",
            f"TABLE C SCORE: {result.score_c}",
            f"+ ACTIVITY SCORE: {result.activity_score}",
            "",
            "═" * 64,
            f"  FINAL REBA SCORE: {result.final_score}",
            f"  RISK LEVEL: {result.risk_level} ({result.risk_description})",
            "═" * 64,
            "",
            f"ACTION REQUIRED: {result.risk_action}",
            f"URGENCY: {result.risk_urgency}",
            "",
            "╚══════════════════════════════════════════════════════════════╝"
        ]
        
        return "\n".join(lines)
