"""
Recommendation Engine - Standards-Aligned Ergonomic Recommendations

Generates precise, actionable recommendations based on RULA/REBA
scores and individual body part assessments. All recommendations
are aligned with ISO/HSE standards and ergonomic best practices.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoring.rula_engine import RULAResult
from scoring.reba_engine import REBAResult
from core.angle_calculator import JointAngles
from .standards_database import (
    BODY_PART_GUIDANCE, 
    WORKSTATION_GUIDANCE,
    ERGONOMIC_PRINCIPLES,
    ISO_STANDARDS
)


@dataclass
class Recommendation:
    """Single ergonomic recommendation."""
    priority: int  # 1 = highest priority
    category: str  # 'immediate', 'short_term', 'long_term'
    body_part: str
    title: str
    description: str
    actions: List[str]
    standards_reference: str = ""
    expected_improvement: str = ""


@dataclass
class RecommendationReport:
    """Complete recommendation report."""
    overall_risk_statement: str
    immediate_actions: List[Recommendation] = field(default_factory=list)
    short_term_actions: List[Recommendation] = field(default_factory=list)
    long_term_actions: List[Recommendation] = field(default_factory=list)
    workstation_adjustments: List[Recommendation] = field(default_factory=list)
    task_redesign: List[Recommendation] = field(default_factory=list)
    training_needs: List[str] = field(default_factory=list)
    monitoring_plan: str = ""
    
    def to_dict(self) -> dict:
        return {
            'overall_risk_statement': self.overall_risk_statement,
            'immediate_actions': [self._rec_to_dict(r) for r in self.immediate_actions],
            'short_term_actions': [self._rec_to_dict(r) for r in self.short_term_actions],
            'long_term_actions': [self._rec_to_dict(r) for r in self.long_term_actions],
            'workstation_adjustments': [self._rec_to_dict(r) for r in self.workstation_adjustments],
            'task_redesign': [self._rec_to_dict(r) for r in self.task_redesign],
            'training_needs': self.training_needs,
            'monitoring_plan': self.monitoring_plan
        }
    
    def _rec_to_dict(self, rec: Recommendation) -> dict:
        return {
            'priority': rec.priority,
            'category': rec.category,
            'body_part': rec.body_part,
            'title': rec.title,
            'description': rec.description,
            'actions': rec.actions,
            'standards_reference': rec.standards_reference,
            'expected_improvement': rec.expected_improvement
        }


class RecommendationEngine:
    """
    Generates ergonomic recommendations based on assessment results.
    
    All recommendations are:
    - Standards-aligned (ISO 11226, ISO 11228, HSE guidance)
    - Specific and actionable
    - Prioritized by risk level
    - Non-medical and non-diagnostic
    """
    
    # Risk thresholds for triggering recommendations
    RULA_THRESHOLDS = {
        'high': 5,    # Score 5+ requires action
        'medium': 3,  # Score 3-4 needs investigation
        'low': 1      # Score 1-2 acceptable
    }
    
    REBA_THRESHOLDS = {
        'very_high': 11,  # Immediate action
        'high': 8,        # Implement change
        'medium': 4,      # Further investigation
        'low': 1          # Negligible
    }
    
    # Body part score thresholds
    COMPONENT_THRESHOLDS = {
        'upper_arm': 3,
        'lower_arm': 2,
        'wrist': 2,
        'neck': 3,
        'trunk': 3,
        'legs': 2
    }
    
    def generate_recommendations(self, 
                                  angles: JointAngles,
                                  rula_result: RULAResult,
                                  reba_result: REBAResult) -> RecommendationReport:
        """
        Generate comprehensive recommendation report.
        
        Args:
            angles: Computed joint angles
            rula_result: RULA assessment result
            reba_result: REBA assessment result
            
        Returns:
            Complete recommendation report
        """
        report = RecommendationReport(
            overall_risk_statement=self._generate_risk_statement(rula_result, reba_result)
        )
        
        # Generate body-part specific recommendations
        self._add_neck_recommendations(report, angles, rula_result, reba_result)
        self._add_trunk_recommendations(report, angles, rula_result, reba_result)
        self._add_upper_arm_recommendations(report, angles, rula_result, reba_result)
        self._add_lower_arm_recommendations(report, angles, rula_result, reba_result)
        self._add_wrist_recommendations(report, angles, rula_result, reba_result)
        self._add_leg_recommendations(report, angles, rula_result, reba_result)
        
        # Generate overall workstation recommendations
        self._add_workstation_recommendations(report, rula_result, reba_result)
        
        # Add task redesign if high risk
        if rula_result.final_score >= 5 or reba_result.final_score >= 8:
            self._add_task_redesign_recommendations(report, rula_result, reba_result)
        
        # Add training needs
        self._add_training_recommendations(report, rula_result, reba_result)
        
        # Set monitoring plan
        report.monitoring_plan = self._generate_monitoring_plan(rula_result, reba_result)
        
        # Sort by priority
        report.immediate_actions.sort(key=lambda x: x.priority)
        report.short_term_actions.sort(key=lambda x: x.priority)
        report.long_term_actions.sort(key=lambda x: x.priority)
        
        return report
    
    def _generate_risk_statement(self, rula: RULAResult, reba: REBAResult) -> str:
        """Generate overall risk statement."""
        if rula.final_score >= 7 or reba.final_score >= 11:
            return (
                "CRITICAL ERGONOMIC RISK IDENTIFIED. "
                f"RULA Score: {rula.final_score}/7 (Action Level {rula.action_level}), "
                f"REBA Score: {reba.final_score}/15 ({reba.risk_level} Risk). "
                "Immediate intervention is required to prevent musculoskeletal injury. "
                "The current posture presents significant risk factors that must be addressed without delay."
            )
        elif rula.final_score >= 5 or reba.final_score >= 8:
            return (
                "HIGH ERGONOMIC RISK DETECTED. "
                f"RULA Score: {rula.final_score}/7 (Action Level {rula.action_level}), "
                f"REBA Score: {reba.final_score}/15 ({reba.risk_level} Risk). "
                "Investigation and corrective action should be implemented soon. "
                "Multiple risk factors have been identified requiring workstation modifications."
            )
        elif rula.final_score >= 3 or reba.final_score >= 4:
            return (
                "MODERATE ERGONOMIC RISK PRESENT. "
                f"RULA Score: {rula.final_score}/7 (Action Level {rula.action_level}), "
                f"REBA Score: {reba.final_score}/15 ({reba.risk_level} Risk). "
                "Further investigation is recommended. Consider implementing suggested improvements "
                "to enhance workplace ergonomics and reduce potential strain."
            )
        else:
            return (
                "LOW ERGONOMIC RISK. "
                f"RULA Score: {rula.final_score}/7 (Action Level {rula.action_level}), "
                f"REBA Score: {reba.final_score}/15 ({reba.risk_level} Risk). "
                "Current posture is within acceptable limits. Maintain good practices and "
                "continue periodic monitoring to ensure sustained ergonomic health."
            )
    
    def _add_neck_recommendations(self, report: RecommendationReport,
                                   angles: JointAngles,
                                   rula: RULAResult,
                                   reba: REBAResult) -> None:
        """Add neck-specific recommendations."""
        neck_score = max(rula.neck.final_score, reba.neck.final_score)
        
        if neck_score >= 3:
            category = 'immediate' if neck_score >= 4 else 'short_term'
            priority = 1 if neck_score >= 4 else 2
            
            rec = Recommendation(
                priority=priority,
                category=category,
                body_part='neck',
                title='Neck Posture Correction Required',
                description=f'Neck flexion of {angles.neck_flexion:.1f}° exceeds optimal range. '
                           f'Sustained neck flexion increases cervical spine loading.',
                actions=[
                    'Position computer monitor at eye level or slightly below',
                    'Use a document holder positioned beside the monitor',
                    'Ensure adequate lighting to prevent forward leaning',
                    'Take micro-breaks every 20 minutes to reset neck position',
                    'Perform gentle neck stretches (chin tucks, rotation) hourly'
                ],
                standards_reference='ISO 11226 - Neck flexion should be <25° for acceptable posture',
                expected_improvement='Reducing neck flexion to <20° can decrease RULA/REBA neck scores by 1-2 points'
            )
            
            if category == 'immediate':
                report.immediate_actions.append(rec)
            else:
                report.short_term_actions.append(rec)
        
        # Add recommendations for neck twist or side bend
        if abs(angles.neck_twist) > 10 or abs(angles.neck_side_bend) > 10:
            rec = Recommendation(
                priority=2,
                category='short_term',
                body_part='neck',
                title='Reduce Neck Twisting and Side Bending',
                description='Neck rotation and lateral bending increase strain on cervical structures.',
                actions=[
                    'Reposition work items to face directly forward',
                    'Adjust chair to face primary work area',
                    'Consider dual monitor setup if referencing multiple sources',
                    'Avoid cradling phone between shoulder and ear'
                ],
                standards_reference='ISO 11226 - Asymmetric neck postures are conditionally acceptable only'
            )
            report.short_term_actions.append(rec)
    
    def _add_trunk_recommendations(self, report: RecommendationReport,
                                    angles: JointAngles,
                                    rula: RULAResult,
                                    reba: REBAResult) -> None:
        """Add trunk-specific recommendations."""
        trunk_score = max(rula.trunk.final_score, reba.trunk.final_score)
        
        if trunk_score >= 3:
            category = 'immediate' if trunk_score >= 4 else 'short_term'
            priority = 1 if trunk_score >= 4 else 2
            
            rec = Recommendation(
                priority=priority,
                category=category,
                body_part='trunk',
                title='Trunk Posture Improvement Needed',
                description=f'Trunk flexion of {angles.trunk_flexion:.1f}° increases spinal loading. '
                           f'Forward bending significantly elevates intervertebral disc pressure.',
                actions=[
                    'Ensure chair provides adequate lumbar support',
                    'Adjust seat height so feet are flat on floor',
                    'Position work items within easy reach to prevent forward leaning',
                    'Consider a sit-stand workstation to vary posture',
                    'Maintain natural spinal curves (lordosis) when seated'
                ],
                standards_reference='ISO 11226 - Trunk flexion >20° requires support or time limits',
                expected_improvement='Proper lumbar support can reduce trunk flexion and lower scores by 1-2 points'
            )
            
            if category == 'immediate':
                report.immediate_actions.append(rec)
            else:
                report.short_term_actions.append(rec)
        
        if abs(angles.trunk_side_bend) > 10:
            rec = Recommendation(
                priority=3,
                category='short_term',
                body_part='trunk',
                title='Address Trunk Asymmetry',
                description='Lateral trunk bending or twisting increases risk of back injury.',
                actions=[
                    'Position frequently used items centrally',
                    'Avoid reaching to the side for heavy items',
                    'Use swivel chair to turn rather than twist',
                    'Ensure balanced work surface layout'
                ],
                standards_reference='ISO 11226 - Asymmetric trunk postures not acceptable for sustained work'
            )
            report.short_term_actions.append(rec)
    
    def _add_upper_arm_recommendations(self, report: RecommendationReport,
                                        angles: JointAngles,
                                        rula: RULAResult,
                                        reba: REBAResult) -> None:
        """Add upper arm/shoulder recommendations."""
        upper_arm_score = max(rula.upper_arm.final_score, reba.upper_arm.final_score)
        
        if upper_arm_score >= 3:
            priority = 1 if upper_arm_score >= 4 else 2
            
            rec = Recommendation(
                priority=priority,
                category='short_term',
                body_part='shoulder',
                title='Shoulder Posture Optimization',
                description=f'Upper arm elevation of {angles.upper_arm_flexion:.1f}° and abduction of '
                           f'{angles.upper_arm_abduction:.1f}° increase shoulder muscle fatigue.',
                actions=[
                    'Lower work surface or raise seating to reduce arm elevation',
                    'Position keyboard and mouse close to body',
                    'Use armrests to support forearms during typing',
                    'Avoid reaching above shoulder height',
                    'Take regular breaks to relax shoulder muscles'
                ],
                standards_reference='ISO 11226 - Upper arm flexion should be <20° for extended duration',
                expected_improvement='Reducing arm elevation can significantly reduce muscle fatigue'
            )
            report.short_term_actions.append(rec)
        
        if angles.shoulder_raised:
            rec = Recommendation(
                priority=2,
                category='short_term',
                body_part='shoulder',
                title='Shoulder Elevation Detected',
                description='Raised shoulders indicate tension or improper workstation height.',
                actions=[
                    'Lower keyboard to allow relaxed shoulders',
                    'Ensure armrests are at correct height',
                    'Perform shoulder rolls and relaxation exercises',
                    'Check for psychological stress contributing to tension'
                ]
            )
            report.short_term_actions.append(rec)
    
    def _add_lower_arm_recommendations(self, report: RecommendationReport,
                                        angles: JointAngles,
                                        rula: RULAResult,
                                        reba: REBAResult) -> None:
        """Add lower arm/elbow recommendations."""
        lower_arm_score = max(rula.lower_arm.final_score, reba.lower_arm.final_score)
        
        if lower_arm_score >= 2:
            rec = Recommendation(
                priority=3,
                category='short_term',
                body_part='elbow',
                title='Elbow Angle Adjustment',
                description=f'Elbow flexion of {angles.lower_arm_flexion:.1f}° is outside optimal range (60-100°).',
                actions=[
                    'Adjust chair or desk height to achieve 90° elbow angle',
                    'Position keyboard at elbow height',
                    'Use adjustable keyboard tray if needed',
                    'Avoid resting elbows on hard surfaces'
                ],
                standards_reference='Optimal elbow angle is 80-100° for keyboard work'
            )
            report.short_term_actions.append(rec)
        
        if angles.lower_arm_across_midline:
            rec = Recommendation(
                priority=3,
                category='short_term',
                body_part='elbow',
                title='Arm Crossing Midline',
                description='Working across the body midline increases shoulder and back strain.',
                actions=[
                    'Reposition work items in front of the user',
                    'Center the keyboard with the monitor',
                    'Use appropriate mouse positioning'
                ]
            )
            report.short_term_actions.append(rec)
    
    def _add_wrist_recommendations(self, report: RecommendationReport,
                                    angles: JointAngles,
                                    rula: RULAResult,
                                    reba: REBAResult) -> None:
        """Add wrist recommendations."""
        wrist_angle = max(angles.wrist_flexion, angles.wrist_extension)
        
        if wrist_angle > 15 or angles.wrist_deviation > 15:
            rec = Recommendation(
                priority=2,
                category='short_term',
                body_part='wrist',
                title='Wrist Posture Correction',
                description=f'Wrist deviation from neutral ({wrist_angle:.1f}°) increases risk of '
                           'carpal tunnel syndrome and tendon strain.',
                actions=[
                    'Keep wrists straight and neutral during typing',
                    'Consider ergonomic keyboard with split design',
                    'Position mouse at same level as keyboard',
                    'Use whole arm to move mouse, not just wrist',
                    'Avoid resting wrists while actively typing',
                    'Use wrist rest only during pauses'
                ],
                standards_reference='ISO 11228-3 - Wrist deviation increases biomechanical load',
                expected_improvement='Neutral wrist position reduces carpal tunnel pressure by up to 50%'
            )
            report.short_term_actions.append(rec)
        
        if angles.wrist_twist:
            rec = Recommendation(
                priority=3,
                category='short_term',
                body_part='wrist',
                title='Reduce Wrist Pronation/Supination',
                description='Wrist rotation at extreme ranges increases forearm muscle strain.',
                actions=[
                    'Consider vertical mouse design',
                    'Adjust forearm rotation when using mouse',
                    'Take breaks during intensive mouse work'
                ]
            )
            report.short_term_actions.append(rec)
    
    def _add_leg_recommendations(self, report: RecommendationReport,
                                  angles: JointAngles,
                                  rula: RULAResult,
                                  reba: REBAResult) -> None:
        """Add leg/lower body recommendations."""
        if not angles.leg_supported or not angles.leg_weight_even:
            rec = Recommendation(
                priority=3,
                category='short_term',
                body_part='legs',
                title='Lower Body Support Improvement',
                description='Inadequate leg support or uneven weight distribution affects overall posture.',
                actions=[
                    'Ensure feet are flat on floor or footrest',
                    'Adjust chair height for proper thigh clearance',
                    'Use footrest if feet do not reach floor',
                    'Distribute weight evenly on both feet',
                    'Avoid crossing legs for extended periods'
                ]
            )
            report.short_term_actions.append(rec)
        
        if angles.leg_flexion > 90:
            rec = Recommendation(
                priority=3,
                category='long_term',
                body_part='legs',
                title='Seated Posture Assessment',
                description='Excessive knee flexion may indicate chair is too low.',
                actions=[
                    'Raise chair to achieve ~90° knee angle',
                    'Ensure adequate seat depth',
                    'Consider sit-stand desk for posture variation'
                ]
            )
            report.long_term_actions.append(rec)
    
    def _add_workstation_recommendations(self, report: RecommendationReport,
                                          rula: RULAResult,
                                          reba: REBAResult) -> None:
        """Add overall workstation recommendations."""
        if rula.final_score >= 3 or reba.final_score >= 4:
            rec = Recommendation(
                priority=2,
                category='short_term',
                body_part='general',
                title='Workstation Ergonomic Assessment',
                description='Multiple postural issues suggest systematic workstation review is needed.',
                actions=[
                    'Conduct full workstation ergonomic assessment',
                    'Review monitor, keyboard, mouse, and chair positions',
                    'Ensure all equipment is adjustable',
                    'Consider ergonomic accessories (document holder, footrest)',
                    'Verify adequate lighting and reduce glare'
                ],
                standards_reference='HSE L26 - Display Screen Equipment Regulations'
            )
            report.workstation_adjustments.append(rec)
    
    def _add_task_redesign_recommendations(self, report: RecommendationReport,
                                            rula: RULAResult,
                                            reba: REBAResult) -> None:
        """Add task redesign recommendations for high-risk cases."""
        rec = Recommendation(
            priority=1,
            category='immediate',
            body_part='general',
            title='Task Redesign Required',
            description='High risk scores indicate the need for fundamental task or process changes.',
            actions=[
                'Review task requirements and workflow',
                'Implement job rotation to reduce exposure',
                'Introduce mechanical aids where appropriate',
                'Redistribute tasks to reduce individual load',
                'Consider automation of high-risk tasks',
                'Allow adequate rest breaks based on task demands'
            ],
            standards_reference='ISO 11228 - Hierarchy of control measures',
            expected_improvement='Task redesign can eliminate root causes of ergonomic risk'
        )
        report.task_redesign.append(rec)
    
    def _add_training_recommendations(self, report: RecommendationReport,
                                       rula: RULAResult,
                                       reba: REBAResult) -> None:
        """Add training needs."""
        report.training_needs = [
            'Ergonomic awareness and good posture principles',
            'Proper workstation setup and adjustment',
            'Recognition of early signs of musculoskeletal discomfort',
            'Stretching and micro-break exercises',
            'Correct manual handling techniques (if applicable)'
        ]
        
        if rula.final_score >= 5 or reba.final_score >= 8:
            report.training_needs.extend([
                'Risk factor identification and reporting',
                'Job-specific ergonomic hazards',
                'Use of ergonomic equipment and aids'
            ])
    
    def _generate_monitoring_plan(self, rula: RULAResult, reba: REBAResult) -> str:
        """Generate monitoring plan based on risk level."""
        if rula.final_score >= 7 or reba.final_score >= 11:
            return (
                "IMMEDIATE FOLLOW-UP REQUIRED: Re-assess within 1 week after implementing changes. "
                "Continue weekly monitoring until scores improve to acceptable levels. "
                "Document all interventions and outcomes."
            )
        elif rula.final_score >= 5 or reba.final_score >= 8:
            return (
                "SHORT-TERM MONITORING: Re-assess within 2 weeks after implementing changes. "
                "Monthly follow-up assessments recommended for 3 months. "
                "Track symptom reports and discomfort levels."
            )
        elif rula.final_score >= 3 or reba.final_score >= 4:
            return (
                "PERIODIC MONITORING: Re-assess within 1 month after implementing changes. "
                "Quarterly assessments recommended to ensure sustained improvement. "
                "Encourage worker feedback on comfort levels."
            )
        else:
            return (
                "MAINTENANCE MONITORING: Annual ergonomic re-assessment recommended. "
                "Encourage workers to report any emerging discomfort. "
                "Review when workstation or tasks change."
            )
    
    def get_summary(self, report: RecommendationReport) -> str:
        """Generate text summary of recommendations."""
        lines = [
            "═" * 70,
            "ERGONOMIC RECOMMENDATIONS SUMMARY",
            "═" * 70,
            "",
            report.overall_risk_statement,
            ""
        ]
        
        if report.immediate_actions:
            lines.append("▶ IMMEDIATE ACTIONS REQUIRED:")
            for rec in report.immediate_actions:
                lines.append(f"  • {rec.title}")
                for action in rec.actions[:3]:
                    lines.append(f"    - {action}")
            lines.append("")
        
        if report.short_term_actions:
            lines.append("▶ SHORT-TERM IMPROVEMENTS (1-2 weeks):")
            for rec in report.short_term_actions[:5]:
                lines.append(f"  • {rec.title}")
            lines.append("")
        
        if report.workstation_adjustments:
            lines.append("▶ WORKSTATION ADJUSTMENTS:")
            for rec in report.workstation_adjustments:
                lines.append(f"  • {rec.title}")
            lines.append("")
        
        lines.extend([
            "▶ MONITORING PLAN:",
            f"  {report.monitoring_plan}",
            "",
            "═" * 70
        ])
        
        return "\n".join(lines)
