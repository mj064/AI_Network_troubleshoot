"""
PDF Reporting Module
Generate professional network reports with charts and summaries
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Optional
import json


class NetworkReport:
    """Generate network performance reports"""
    
    def __init__(self, title: str = "Network Performance Report", author: str = "Network Operations"):
        self.title = title
        self.author = author
        self.creation_date = datetime.utcnow()
    
    def generate_pdf(self, data: Dict) -> BytesIO:
        """
        Generate PDF report from data
        
        Args:
            data: Dictionary containing report sections and metrics
            
        Returns:
            BytesIO object containing PDF data
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        story.append(self._create_title_page(styles))
        story.append(PageBreak())
        
        # Executive summary
        if 'summary' in data:
            story.append(self._create_summary_section(data['summary'], styles))
            story.append(PageBreak())
        
        # Device health overview
        if 'device_health' in data:
            story.append(self._create_device_health_section(data['device_health'], styles))
            story.append(PageBreak())
        
        # Metrics analysis
        if 'metrics' in data:
            story.append(self._create_metrics_section(data['metrics'], styles))
            story.append(PageBreak())
        
        # Incidents overview
        if 'incidents' in data:
            story.append(self._create_incidents_section(data['incidents'], styles))
            story.append(PageBreak())
        
        # Recommendations
        if 'recommendations' in data:
            story.append(self._create_recommendations_section(data['recommendations'], styles))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
    
    def _create_title_page(self, styles):
        """Create report title page"""
        elements = []
        
        elements.append(Spacer(1, 2 * inch))
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(self.title, title_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(f"Report Generated: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S UTC')}", info_style))
        elements.append(Paragraph(f"Author: {self.author}", info_style))
        elements.append(Paragraph(f"Classification: Internal", info_style))
        
        return elements
    
    def _create_summary_section(self, summary: Dict, styles):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # KPIs table
        kpi_data = [
            ['Metric', 'Value', 'Status'],
            ['Network Health', summary.get('health_percentage', 0) + '%', 
             'Good' if summary.get('health_percentage', 0) >= 80 else 'Warning'],
            ['Total Devices', str(summary.get('total_devices', 0)), 'Monitored'],
            ['Healthy Devices', str(summary.get('healthy_devices', 0)), 'Operational'],
            ['Open Incidents', str(summary.get('open_incidents', 0)), 
             'Resolved' if summary.get('open_incidents', 0) == 0 else 'Action Needed'],
            ['Critical Alerts', str(summary.get('critical_alerts', 0)), '24hr'],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2*inch, 2*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary text
        summary_text = summary.get('narrative', 'Network performance summary pending detailed analysis.')
        elements.append(Paragraph(summary_text, styles['Normal']))
        
        return elements
    
    def _create_device_health_section(self, device_health: Dict, styles):
        """Create device health overview"""
        elements = []
        
        elements.append(Paragraph("Device Health Overview", styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Device status breakdown
        device_data = [
            ['Status', 'Count', 'Percentage'],
            ['Healthy (UP)', str(device_health.get('up', 0)), 
             f"{device_health.get('up_percent', 0):.1f}%"],
            ['Degraded', str(device_health.get('degraded', 0)), 
             f"{device_health.get('degraded_percent', 0):.1f}%"],
            ['Down', str(device_health.get('down', 0)), 
             f"{device_health.get('down_percent', 0):.1f}%"],
        ]
        
        device_table = Table(device_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(device_table)
        return elements
    
    def _create_metrics_section(self, metrics: Dict, styles):
        """Create metrics analysis section"""
        elements = []
        
        elements.append(Paragraph("Performance Metrics", styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Top metrics table
        metric_data = [['Metric Name', 'Average', 'Min', 'Max', 'Status']]
        
        for metric in metrics.get('top_metrics', [])[:10]:
            metric_data.append([
                metric.get('name', ''),
                f"{metric.get('avg', 0):.2f}",
                f"{metric.get('min', 0):.2f}",
                f"{metric.get('max', 0):.2f}",
                metric.get('status', 'OK')
            ])
        
        metrics_table = Table(metric_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(metrics_table)
        return elements
    
    def _create_incidents_section(self, incidents: Dict, styles):
        """Create incidents analysis section"""
        elements = []
        
        elements.append(Paragraph("Incident Summary", styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        incident_data = [['Ticket', 'Title', 'Severity', 'Status', 'Duration']]
        
        for incident in incidents.get('recent', [])[:10]:
            duration = incident.get('duration', 'N/A')
            incident_data.append([
                incident.get('ticket_id', ''),
                incident.get('title', '')[:30],
                incident.get('severity', ''),
                incident.get('status', ''),
                duration
            ])
        
        incident_table = Table(incident_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1*inch, 1.5*inch])
        incident_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(incident_table)
        return elements
    
    def _create_recommendations_section(self, recommendations: List[str], styles):
        """Create recommendations section"""
        elements = []
        
        elements.append(Paragraph("Recommendations", styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        for i, rec in enumerate(recommendations[:5], 1):
            elements.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
        
        return elements
