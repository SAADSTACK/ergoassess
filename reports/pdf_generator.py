"""
PDF Report Generator - Audit-Ready Ergonomic Assessment Reports

Generates professional PDF reports suitable for:
- HSE/ISO compliance documentation
- Occupational health records
- Research and academic submissions
- Industrial safety audits
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from typing import Optional
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoring.rula_engine import RULAResult
from scoring.reba_engine import REBAResult
from recommendations.recommendation_engine import RecommendationReport
from core.angle_calculator import JointAngles


class PDFReportGenerator:
    """
    Generates professional PDF reports for ergonomic assessments.
    
    Reports are designed to be audit-ready and suitable for
    official documentation and compliance purposes.
    """
    
    def __init__(self):
        """Initialize the PDF generator with styles."""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a5f')
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2d5a87'),
            borderWidth=1,
            borderColor=colors.HexColor('#2d5a87'),
            borderPadding=5
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#3d7ab5')
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Risk text - high priority
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold'
        ))
        
        # Risk text - medium
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#f97316'),
            fontName='Helvetica-Bold'
        ))
        
        # Risk text - low
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#22c55e'),
            fontName='Helvetica-Bold'
        ))
        
        # Score display
        self.styles.add(ParagraphStyle(
            name='ScoreDisplay',
            parent=self.styles['Normal'],
            fontSize=18,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self,
                        rula_result: RULAResult,
                        reba_result: REBAResult,
                        angles: JointAngles,
                        recommendations: RecommendationReport,
                        image_path: Optional[str] = None,
                        annotated_image_path: Optional[str] = None,
                        assessment_id: str = None,
                        assessor_name: str = "Automated System",
                        organization: str = "Ergonomic Assessment System",
                        subject_id: str = "Anonymous") -> bytes:
        """
        Generate complete PDF report.
        
        Args:
            rula_result: RULA assessment results
            reba_result: REBA assessment results
            angles: Computed joint angles
            recommendations: Generated recommendations
            image_path: Path to original image
            annotated_image_path: Path to annotated image
            assessment_id: Unique assessment identifier
            assessor_name: Name of assessor
            organization: Organization name
            subject_id: Subject/worker identifier
            
        Returns:
            PDF file as bytes
        """
        # Create buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build story
        story = []
        
        # Title page elements
        story.extend(self._create_header(organization, assessment_id))
        story.append(Spacer(1, 20))
        
        # Assessment metadata
        story.extend(self._create_metadata(
            assessor_name, subject_id, assessment_id
        ))
        story.append(Spacer(1, 20))
        
        # Risk summary (prominent display)
        story.extend(self._create_risk_summary(rula_result, reba_result))
        story.append(Spacer(1, 20))
        
        # Overall risk statement
        story.extend(self._create_risk_statement(recommendations))
        story.append(Spacer(1, 20))
        
        # RULA Results
        story.extend(self._create_rula_section(rula_result))
        story.append(Spacer(1, 15))
        
        # REBA Results
        story.extend(self._create_reba_section(reba_result))
        story.append(PageBreak())
        
        # Joint Angles Table
        story.extend(self._create_angles_section(angles))
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.extend(self._create_recommendations_section(recommendations))
        story.append(PageBreak())
        
        # Compliance statement
        story.extend(self._create_compliance_statement())
        story.append(Spacer(1, 30))
        
        # Footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _create_header(self, organization: str, assessment_id: str) -> list:
        """Create report header."""
        elements = []
        
        # Title
        elements.append(Paragraph(
            "ERGONOMIC POSTURE ASSESSMENT REPORT",
            self.styles['ReportTitle']
        ))
        
        # Subtitle
        elements.append(Paragraph(
            f"<i>{organization}</i>",
            ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.gray
            )
        ))
        
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#2d5a87'),
            spaceAfter=20
        ))
        
        return elements
    
    def _create_metadata(self, assessor: str, subject: str, 
                         assessment_id: str) -> list:
        """Create assessment metadata section."""
        elements = []
        
        now = datetime.now()
        
        data = [
            ['Assessment Date:', now.strftime('%Y-%m-%d')],
            ['Assessment Time:', now.strftime('%H:%M:%S')],
            ['Assessment ID:', assessment_id or f"EA-{now.strftime('%Y%m%d%H%M%S')}"],
            ['Subject ID:', subject],
            ['Assessed By:', assessor],
            ['Method:', 'RULA & REBA (Automated Image Analysis)']
        ]
        
        table = Table(data, colWidths=[3*cm, 8*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d5a87')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_risk_summary(self, rula: RULAResult, reba: REBAResult) -> list:
        """Create prominent risk summary display."""
        elements = []
        
        elements.append(Paragraph(
            "ASSESSMENT RESULTS SUMMARY",
            self.styles['SectionHeading']
        ))
        
        # Determine colors based on scores
        rula_color = self._get_risk_color(rula.final_score, 'rula')
        reba_color = self._get_risk_color(reba.final_score, 'reba')
        
        # Create score boxes
        data = [[
            Paragraph(f"<b>RULA SCORE</b><br/><font size='24'>{rula.final_score}</font><br/>Action Level {rula.action_level}",
                     ParagraphStyle('ScoreBox', alignment=TA_CENTER, fontSize=10)),
            Paragraph(f"<b>REBA SCORE</b><br/><font size='24'>{reba.final_score}</font><br/>{reba.risk_level} Risk",
                     ParagraphStyle('ScoreBox', alignment=TA_CENTER, fontSize=10))
        ]]
        
        table = Table(data, colWidths=[7*cm, 7*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(rula_color)),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(reba_color)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 2, colors.white),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(table)
        return elements
    
    def _get_risk_color(self, score: int, assessment_type: str) -> str:
        """Get color based on risk level."""
        if assessment_type == 'rula':
            if score >= 7:
                return '#dc2626'  # Red
            elif score >= 5:
                return '#f97316'  # Orange
            elif score >= 3:
                return '#eab308'  # Yellow
            else:
                return '#22c55e'  # Green
        else:  # REBA
            if score >= 11:
                return '#dc2626'
            elif score >= 8:
                return '#f97316'
            elif score >= 4:
                return '#eab308'
            else:
                return '#22c55e'
    
    def _create_risk_statement(self, recommendations: RecommendationReport) -> list:
        """Create overall risk statement section."""
        elements = []
        
        elements.append(Paragraph(
            recommendations.overall_risk_statement,
            self.styles['ReportBody']
        ))
        
        return elements
    
    def _create_rula_section(self, rula: RULAResult) -> list:
        """Create RULA results section."""
        elements = []
        
        elements.append(Paragraph(
            "RULA DETAILED BREAKDOWN",
            self.styles['SectionHeading']
        ))
        
        # Group A
        elements.append(Paragraph("Group A - Upper Limb Assessment", self.styles['SubsectionHeading']))
        
        data_a = [
            ['Component', 'Score', 'Details'],
            ['Upper Arm', str(rula.upper_arm.final_score), rula.upper_arm.threshold_crossed],
            ['Lower Arm', str(rula.lower_arm.final_score), rula.lower_arm.threshold_crossed],
            ['Wrist', str(rula.wrist.final_score), rula.wrist.threshold_crossed],
            ['Wrist Twist', str(rula.wrist_twist.final_score), rula.wrist_twist.threshold_crossed],
            ['Table A Score', str(rula.score_a_raw), ''],
            ['+ Muscle Use', str(rula.muscle_use_a), ''],
            ['+ Force/Load', str(rula.force_load_a), ''],
            ['Score A Total', str(rula.score_a), '']
        ]
        
        table_a = Table(data_a, colWidths=[4*cm, 2*cm, 8*cm])
        table_a.setStyle(self._get_table_style())
        elements.append(table_a)
        elements.append(Spacer(1, 10))
        
        # Group B
        elements.append(Paragraph("Group B - Neck/Trunk/Legs Assessment", self.styles['SubsectionHeading']))
        
        data_b = [
            ['Component', 'Score', 'Details'],
            ['Neck', str(rula.neck.final_score), rula.neck.threshold_crossed],
            ['Trunk', str(rula.trunk.final_score), rula.trunk.threshold_crossed],
            ['Legs', str(rula.legs.final_score), rula.legs.threshold_crossed],
            ['Table B Score', str(rula.score_b_raw), ''],
            ['Score B Total', str(rula.score_b), '']
        ]
        
        table_b = Table(data_b, colWidths=[4*cm, 2*cm, 8*cm])
        table_b.setStyle(self._get_table_style())
        elements.append(table_b)
        
        # Action level
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"<b>Action Level {rula.action_level}:</b> {rula.action_recommendation}",
            self.styles['ReportBody']
        ))
        elements.append(Paragraph(
            f"<b>Urgency:</b> {rula.action_urgency}",
            self.styles['ReportBody']
        ))
        
        return elements
    
    def _create_reba_section(self, reba: REBAResult) -> list:
        """Create REBA results section."""
        elements = []
        
        elements.append(Paragraph(
            "REBA DETAILED BREAKDOWN",
            self.styles['SectionHeading']
        ))
        
        # Group A
        elements.append(Paragraph("Group A - Trunk/Neck/Legs", self.styles['SubsectionHeading']))
        
        data_a = [
            ['Component', 'Score', 'Details'],
            ['Trunk', str(reba.trunk.final_score), reba.trunk.threshold_crossed],
            ['Neck', str(reba.neck.final_score), reba.neck.threshold_crossed],
            ['Legs', str(reba.legs.final_score), reba.legs.threshold_crossed],
            ['Table A Score', str(reba.score_a_raw), ''],
            ['+ Load/Force', str(reba.load_force), ''],
            ['Score A Total', str(reba.score_a), '']
        ]
        
        table_a = Table(data_a, colWidths=[4*cm, 2*cm, 8*cm])
        table_a.setStyle(self._get_table_style())
        elements.append(table_a)
        elements.append(Spacer(1, 10))
        
        # Group B
        elements.append(Paragraph("Group B - Arms/Wrist", self.styles['SubsectionHeading']))
        
        data_b = [
            ['Component', 'Score', 'Details'],
            ['Upper Arm', str(reba.upper_arm.final_score), reba.upper_arm.threshold_crossed],
            ['Lower Arm', str(reba.lower_arm.final_score), reba.lower_arm.threshold_crossed],
            ['Wrist', str(reba.wrist.final_score), reba.wrist.threshold_crossed],
            ['Table B Score', str(reba.score_b_raw), ''],
            ['+ Coupling', str(reba.coupling), ''],
            ['Score B Total', str(reba.score_b), '']
        ]
        
        table_b = Table(data_b, colWidths=[4*cm, 2*cm, 8*cm])
        table_b.setStyle(self._get_table_style())
        elements.append(table_b)
        
        # Final score
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"<b>Table C Score:</b> {reba.score_c} + Activity Score: {reba.activity_score} = Final: {reba.final_score}",
            self.styles['ReportBody']
        ))
        elements.append(Paragraph(
            f"<b>Risk Level:</b> {reba.risk_level} - {reba.risk_action}",
            self.styles['ReportBody']
        ))
        
        return elements
    
    def _create_angles_section(self, angles: JointAngles) -> list:
        """Create joint angles table section."""
        elements = []
        
        elements.append(Paragraph(
            "MEASURED JOINT ANGLES",
            self.styles['SectionHeading']
        ))
        
        angles_dict = angles.to_dict()
        
        data = [['Body Region', 'Measurement', 'Value']]
        
        for region, measurements in angles_dict.items():
            if isinstance(measurements, dict):
                for key, value in measurements.items():
                    if isinstance(value, bool):
                        display_value = 'Yes' if value else 'No'
                    elif isinstance(value, (int, float)):
                        display_value = f"{value}°"
                    else:
                        display_value = str(value)
                    data.append([region.replace('_', ' ').title(), 
                                key.replace('_', ' ').title(), 
                                display_value])
            else:
                data.append([region, '', str(measurements)])
        
        table = Table(data, colWidths=[4*cm, 5*cm, 4*cm])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements
    
    def _create_recommendations_section(self, recommendations: RecommendationReport) -> list:
        """Create recommendations section."""
        elements = []
        
        elements.append(Paragraph(
            "ERGONOMIC RECOMMENDATIONS",
            self.styles['SectionHeading']
        ))
        
        # Immediate actions
        if recommendations.immediate_actions:
            elements.append(Paragraph("Immediate Actions Required", self.styles['SubsectionHeading']))
            for rec in recommendations.immediate_actions:
                elements.append(Paragraph(f"<b>• {rec.title}</b>", self.styles['ReportBody']))
                elements.append(Paragraph(rec.description, self.styles['ReportBody']))
                for action in rec.actions[:3]:
                    elements.append(Paragraph(f"  - {action}", self.styles['ReportBody']))
        
        # Short-term actions
        if recommendations.short_term_actions:
            elements.append(Paragraph("Short-Term Improvements", self.styles['SubsectionHeading']))
            for rec in recommendations.short_term_actions[:5]:
                elements.append(Paragraph(f"• {rec.title}", self.styles['ReportBody']))
        
        # Long-term actions
        if recommendations.long_term_actions:
            elements.append(Paragraph("Long-Term Considerations", self.styles['SubsectionHeading']))
            for rec in recommendations.long_term_actions[:3]:
                elements.append(Paragraph(f"• {rec.title}", self.styles['ReportBody']))
        
        # Monitoring plan
        elements.append(Paragraph("Monitoring Plan", self.styles['SubsectionHeading']))
        elements.append(Paragraph(recommendations.monitoring_plan, self.styles['ReportBody']))
        
        return elements
    
    def _create_compliance_statement(self) -> list:
        """Create compliance and methodology statement."""
        elements = []
        
        elements.append(Paragraph(
            "METHODOLOGY & COMPLIANCE STATEMENT",
            self.styles['SectionHeading']
        ))
        
        statement = """
        This assessment was conducted using automated image-based posture analysis 
        implementing the RULA (Rapid Upper Limb Assessment) and REBA (Rapid Entire 
        Body Assessment) methodologies. The analysis utilizes computer vision 
        techniques to detect body landmarks and calculate joint angles, which are 
        then scored according to the official RULA and REBA scoring tables.
        
        <b>Standards Referenced:</b>
        • RULA: McAtamney & Corlett (1993) - Applied Ergonomics
        • REBA: Hignett & McAtamney (2000) - Applied Ergonomics
        • ISO 11226: Ergonomics — Evaluation of static working postures
        • ISO 11228: Ergonomics — Manual handling
        
        <b>Disclaimer:</b>
        This automated assessment provides an objective evaluation of observed 
        posture. It should be used as part of a comprehensive ergonomic program 
        and does not replace professional occupational health assessment where 
        required. Results are ergonomically conclusive based on the image provided.
        """
        
        elements.append(Paragraph(statement, self.styles['ReportBody']))
        
        return elements
    
    def _create_footer(self) -> list:
        """Create report footer."""
        elements = []
        
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.gray,
            spaceBefore=20
        ))
        
        now = datetime.now()
        elements.append(Paragraph(
            f"<i>Report generated: {now.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Ergonomic Assessment System | Confidential</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.gray
            )
        ))
        
        return elements
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table style."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a87')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
        ])
    
    def save_report(self, pdf_bytes: bytes, filepath: str) -> None:
        """Save PDF report to file."""
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
