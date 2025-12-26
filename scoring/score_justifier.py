"""
Score Justifier - Diagram-Based Score Justification Engine

Generates detailed, transparent explanations for each RULA and REBA
score component. Maps measured angles to official diagram conditions
and documents why specific scores were assigned.
"""

from typing import Dict, List
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.angle_calculator import JointAngles
from .rula_engine import RULAResult
from .reba_engine import REBAResult


@dataclass
class JustificationItem:
    """Single justification item for a body part."""
    body_part: str
    measured_angle: float
    score_assigned: int
    diagram_condition: str
    threshold_crossed: str
    alternatives_excluded: List[str]
    modifiers: List[str]
    detailed_reasoning: str


class ScoreJustifier:
    """
    Generates detailed justifications for RULA and REBA scores.
    
    Each score is mapped to specific diagram conditions from the
    official assessment tools, with clear explanations of why
    particular thresholds were crossed.
    """
    
    # RULA Diagram Conditions
    RULA_DIAGRAMS = {
        'upper_arm': {
            1: "Diagram 1A: Upper arm 20° extension to 20° flexion - Neutral zone",
            2: "Diagram 2A: Upper arm 20°-45° flexion or >20° extension - Mild deviation",
            3: "Diagram 3A: Upper arm 45°-90° flexion - Moderate elevation",
            4: "Diagram 4A: Upper arm >90° flexion - High elevation"
        },
        'lower_arm': {
            1: "Diagram 1B: Lower arm 60°-100° flexion - Optimal elbow angle",
            2: "Diagram 2B: Lower arm <60° or >100° - Extended or acute elbow"
        },
        'wrist': {
            1: "Diagram 1C: Wrist in neutral position",
            2: "Diagram 2C: Wrist 0°-15° flexion/extension - Mild deviation",
            3: "Diagram 3C: Wrist >15° flexion/extension - Significant deviation"
        },
        'neck': {
            1: "Diagram 1D: Neck 0°-10° flexion - Near neutral",
            2: "Diagram 2D: Neck 10°-20° flexion - Mild forward tilt",
            3: "Diagram 3D: Neck >20° flexion - Significant forward bend",
            4: "Diagram 4D: Neck in extension - Backward tilt"
        },
        'trunk': {
            1: "Diagram 1E: Trunk upright/well supported",
            2: "Diagram 2E: Trunk 0°-20° flexion - Slight forward lean",
            3: "Diagram 3E: Trunk 20°-60° flexion - Moderate bend",
            4: "Diagram 4E: Trunk >60° flexion - Significant bend"
        },
        'legs': {
            1: "Diagram 1F: Legs/feet well supported, balanced weight",
            2: "Diagram 2F: Legs/feet not supported or unbalanced"
        }
    }
    
    # REBA Diagram Conditions
    REBA_DIAGRAMS = {
        'trunk': {
            1: "REBA Trunk 1: Upright position",
            2: "REBA Trunk 2: 0°-20° flexion or extension",
            3: "REBA Trunk 3: 20°-60° flexion or >20° extension",
            4: "REBA Trunk 4: >60° flexion"
        },
        'neck': {
            1: "REBA Neck 1: 0°-20° flexion",
            2: "REBA Neck 2: >20° flexion or in extension"
        },
        'legs': {
            1: "REBA Legs 1: Bilateral weight bearing, walking, sitting",
            2: "REBA Legs 2: Unilateral weight bearing or unstable"
        },
        'upper_arm': {
            1: "REBA Upper Arm 1: 20° extension to 20° flexion",
            2: "REBA Upper Arm 2: 20°-45° flexion or >20° extension",
            3: "REBA Upper Arm 3: 45°-90° flexion",
            4: "REBA Upper Arm 4: >90° flexion"
        },
        'lower_arm': {
            1: "REBA Lower Arm 1: 60°-100° flexion",
            2: "REBA Lower Arm 2: <60° or >100° flexion"
        },
        'wrist': {
            1: "REBA Wrist 1: 0°-15° flexion/extension",
            2: "REBA Wrist 2: >15° flexion/extension"
        }
    }
    
    def justify_rula(self, angles: JointAngles, result: RULAResult) -> Dict[str, JustificationItem]:
        """
        Generate complete justifications for a RULA assessment.
        
        Args:
            angles: The computed joint angles
            result: The RULA scoring result
            
        Returns:
            Dictionary mapping body parts to their justification
        """
        justifications = {}
        
        # Upper Arm
        justifications['upper_arm'] = self._justify_component(
            body_part='upper_arm',
            measured_angle=result.upper_arm.angle_measured,
            score=result.upper_arm.final_score,
            raw_score=result.upper_arm.raw_score,
            modifiers=result.upper_arm.modifiers_applied,
            diagrams=self.RULA_DIAGRAMS['upper_arm'],
            thresholds=[
                ((-20, 20), 1, "20° extension to 20° flexion"),
                ((20, 45), 2, "20°-45° flexion"),
                ((45, 90), 3, "45°-90° flexion"),
                ((90, 180), 4, ">90° flexion")
            ]
        )
        
        # Lower Arm
        justifications['lower_arm'] = self._justify_component(
            body_part='lower_arm',
            measured_angle=result.lower_arm.angle_measured,
            score=result.lower_arm.final_score,
            raw_score=result.lower_arm.raw_score,
            modifiers=result.lower_arm.modifiers_applied,
            diagrams=self.RULA_DIAGRAMS['lower_arm'],
            thresholds=[
                ((60, 100), 1, "60°-100° flexion (optimal)"),
                ((0, 60), 2, "<60° or >100° flexion"),
                ((100, 180), 2, ">100° flexion")
            ]
        )
        
        # Wrist
        justifications['wrist'] = self._justify_component(
            body_part='wrist',
            measured_angle=result.wrist.angle_measured,
            score=result.wrist.final_score,
            raw_score=result.wrist.raw_score,
            modifiers=result.wrist.modifiers_applied,
            diagrams=self.RULA_DIAGRAMS['wrist'],
            thresholds=[
                ((0, 0), 1, "Neutral position"),
                ((0, 15), 2, "0°-15° deviation"),
                ((15, 180), 3, ">15° deviation")
            ]
        )
        
        # Neck
        justifications['neck'] = self._justify_component(
            body_part='neck',
            measured_angle=result.neck.angle_measured,
            score=result.neck.final_score,
            raw_score=result.neck.raw_score,
            modifiers=result.neck.modifiers_applied,
            diagrams=self.RULA_DIAGRAMS['neck'],
            thresholds=[
                ((0, 10), 1, "0°-10° flexion"),
                ((10, 20), 2, "10°-20° flexion"),
                ((20, 90), 3, ">20° flexion"),
                ((-90, 0), 4, "Extension")
            ]
        )
        
        # Trunk
        justifications['trunk'] = self._justify_component(
            body_part='trunk',
            measured_angle=result.trunk.angle_measured,
            score=result.trunk.final_score,
            raw_score=result.trunk.raw_score,
            modifiers=result.trunk.modifiers_applied,
            diagrams=self.RULA_DIAGRAMS['trunk'],
            thresholds=[
                ((0, 0), 1, "Upright/well supported"),
                ((0, 20), 2, "0°-20° flexion"),
                ((20, 60), 3, "20°-60° flexion"),
                ((60, 180), 4, ">60° flexion")
            ]
        )
        
        # Legs
        justifications['legs'] = JustificationItem(
            body_part='legs',
            measured_angle=result.legs.angle_measured,
            score_assigned=result.legs.final_score,
            diagram_condition=self.RULA_DIAGRAMS['legs'][result.legs.raw_score],
            threshold_crossed=result.legs.threshold_crossed,
            alternatives_excluded=self._get_excluded_alternatives(
                result.legs.raw_score, self.RULA_DIAGRAMS['legs']
            ),
            modifiers=result.legs.modifiers_applied,
            detailed_reasoning=result.legs.justification
        )
        
        return justifications
    
    def justify_reba(self, angles: JointAngles, result: REBAResult) -> Dict[str, JustificationItem]:
        """
        Generate complete justifications for a REBA assessment.
        
        Args:
            angles: The computed joint angles
            result: The REBA scoring result
            
        Returns:
            Dictionary mapping body parts to their justification
        """
        justifications = {}
        
        # Trunk
        justifications['trunk'] = self._justify_component(
            body_part='trunk',
            measured_angle=result.trunk.angle_measured,
            score=result.trunk.final_score,
            raw_score=result.trunk.raw_score,
            modifiers=result.trunk.modifiers_applied,
            diagrams=self.REBA_DIAGRAMS['trunk'],
            thresholds=[
                ((0, 0), 1, "Upright"),
                ((0, 20), 2, "0°-20° flexion"),
                ((20, 60), 3, "20°-60° flexion"),
                ((60, 180), 4, ">60° flexion")
            ]
        )
        
        # Neck
        justifications['neck'] = self._justify_component(
            body_part='neck',
            measured_angle=result.neck.angle_measured,
            score=result.neck.final_score,
            raw_score=result.neck.raw_score,
            modifiers=result.neck.modifiers_applied,
            diagrams=self.REBA_DIAGRAMS['neck'],
            thresholds=[
                ((0, 20), 1, "0°-20° flexion"),
                ((20, 180), 2, ">20° flexion or extension")
            ]
        )
        
        # Legs
        justifications['legs'] = JustificationItem(
            body_part='legs',
            measured_angle=result.legs.angle_measured,
            score_assigned=result.legs.final_score,
            diagram_condition=self.REBA_DIAGRAMS['legs'][min(result.legs.raw_score, 2)],
            threshold_crossed=result.legs.threshold_crossed,
            alternatives_excluded=self._get_excluded_alternatives(
                result.legs.raw_score, self.REBA_DIAGRAMS['legs']
            ),
            modifiers=result.legs.modifiers_applied,
            detailed_reasoning=result.legs.justification
        )
        
        # Upper Arm
        justifications['upper_arm'] = self._justify_component(
            body_part='upper_arm',
            measured_angle=result.upper_arm.angle_measured,
            score=result.upper_arm.final_score,
            raw_score=result.upper_arm.raw_score,
            modifiers=result.upper_arm.modifiers_applied,
            diagrams=self.REBA_DIAGRAMS['upper_arm'],
            thresholds=[
                ((-20, 20), 1, "20° extension to 20° flexion"),
                ((20, 45), 2, "20°-45° flexion"),
                ((45, 90), 3, "45°-90° flexion"),
                ((90, 180), 4, ">90° flexion")
            ]
        )
        
        # Lower Arm
        justifications['lower_arm'] = self._justify_component(
            body_part='lower_arm',
            measured_angle=result.lower_arm.angle_measured,
            score=result.lower_arm.final_score,
            raw_score=result.lower_arm.raw_score,
            modifiers=result.lower_arm.modifiers_applied,
            diagrams=self.REBA_DIAGRAMS['lower_arm'],
            thresholds=[
                ((60, 100), 1, "60°-100° flexion"),
                ((0, 60), 2, "<60° or >100° flexion"),
                ((100, 180), 2, ">100° flexion")
            ]
        )
        
        # Wrist
        justifications['wrist'] = self._justify_component(
            body_part='wrist',
            measured_angle=result.wrist.angle_measured,
            score=result.wrist.final_score,
            raw_score=result.wrist.raw_score,
            modifiers=result.wrist.modifiers_applied,
            diagrams=self.REBA_DIAGRAMS['wrist'],
            thresholds=[
                ((0, 15), 1, "0°-15° flexion/extension"),
                ((15, 180), 2, ">15° flexion/extension")
            ]
        )
        
        return justifications
    
    def _justify_component(self, body_part: str, measured_angle: float,
                           score: int, raw_score: int, modifiers: List[str],
                           diagrams: Dict[int, str],
                           thresholds: List[tuple]) -> JustificationItem:
        """Generate justification for a single component."""
        
        # Find which threshold was crossed
        threshold_crossed = "Unknown threshold"
        for (min_val, max_val), thresh_score, description in thresholds:
            if min_val <= abs(measured_angle) <= max_val:
                if thresh_score == raw_score:
                    threshold_crossed = description
                    break
        
        # Get diagram condition
        diagram_score = min(raw_score, max(diagrams.keys()))
        diagram_condition = diagrams.get(diagram_score, f"Score {raw_score} condition")
        
        # Get excluded alternatives
        alternatives_excluded = self._get_excluded_alternatives(raw_score, diagrams)
        
        # Build detailed reasoning
        reasoning = (
            f"Measured angle: {measured_angle:.1f}°. "
            f"This falls within the '{threshold_crossed}' range, "
            f"corresponding to {diagram_condition}. "
        )
        
        if modifiers:
            reasoning += f"Modifiers applied: {', '.join(modifiers)}. "
        else:
            reasoning += "No modifiers applicable. "
        
        if raw_score != score:
            reasoning += f"Base score {raw_score} adjusted to final score {score}."
        else:
            reasoning += f"Final score: {score}."
        
        return JustificationItem(
            body_part=body_part,
            measured_angle=measured_angle,
            score_assigned=score,
            diagram_condition=diagram_condition,
            threshold_crossed=threshold_crossed,
            alternatives_excluded=alternatives_excluded,
            modifiers=modifiers,
            detailed_reasoning=reasoning
        )
    
    def _get_excluded_alternatives(self, selected_score: int, 
                                   diagrams: Dict[int, str]) -> List[str]:
        """Get list of diagram conditions that were NOT selected."""
        excluded = []
        for score, condition in diagrams.items():
            if score != selected_score:
                excluded.append(f"Score {score}: {condition}")
        return excluded
    
    def generate_full_justification_report(self, angles: JointAngles,
                                           rula_result: RULAResult,
                                           reba_result: REBAResult) -> str:
        """
        Generate a comprehensive justification report for both assessments.
        
        Args:
            angles: Computed joint angles
            rula_result: RULA scoring result
            reba_result: REBA scoring result
            
        Returns:
            Formatted justification report
        """
        rula_just = self.justify_rula(angles, rula_result)
        reba_just = self.justify_reba(angles, reba_result)
        
        lines = [
            "=" * 80,
            "ERGONOMIC ASSESSMENT JUSTIFICATION REPORT",
            "=" * 80,
            "",
            "-" * 40,
            "RULA SCORE JUSTIFICATIONS",
            "-" * 40,
        ]
        
        for part, just in rula_just.items():
            lines.extend([
                "",
                f"▶ {part.upper().replace('_', ' ')}:",
                f"  Measured Angle: {just.measured_angle:.1f}°",
                f"  Score Assigned: {just.score_assigned}",
                f"  Diagram Condition: {just.diagram_condition}",
                f"  Threshold: {just.threshold_crossed}",
                f"  Modifiers: {', '.join(just.modifiers) if just.modifiers else 'None'}",
                f"  Alternatives Excluded:",
            ])
            for alt in just.alternatives_excluded[:2]:  # Limit for brevity
                lines.append(f"    - {alt}")
        
        lines.extend([
            "",
            "-" * 40,
            "REBA SCORE JUSTIFICATIONS",
            "-" * 40,
        ])
        
        for part, just in reba_just.items():
            lines.extend([
                "",
                f"▶ {part.upper().replace('_', ' ')}:",
                f"  Measured Angle: {just.measured_angle:.1f}°",
                f"  Score Assigned: {just.score_assigned}",
                f"  Diagram Condition: {just.diagram_condition}",
                f"  Threshold: {just.threshold_crossed}",
                f"  Modifiers: {', '.join(just.modifiers) if just.modifiers else 'None'}",
            ])
        
        lines.extend([
            "",
            "=" * 80,
            "END OF JUSTIFICATION REPORT",
            "=" * 80
        ])
        
        return "\n".join(lines)
    
    def to_dict(self, justifications: Dict[str, JustificationItem]) -> Dict:
        """Convert justifications to dictionary for JSON."""
        return {
            part: {
                'body_part': just.body_part,
                'measured_angle': round(just.measured_angle, 1),
                'score_assigned': just.score_assigned,
                'diagram_condition': just.diagram_condition,
                'threshold_crossed': just.threshold_crossed,
                'alternatives_excluded': just.alternatives_excluded,
                'modifiers': just.modifiers,
                'detailed_reasoning': just.detailed_reasoning
            }
            for part, just in justifications.items()
        }
