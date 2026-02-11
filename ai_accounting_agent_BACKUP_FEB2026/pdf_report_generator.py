"""
PDF Report Generator Module
Creates professional PDF reports using ReportLab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import pandas as pd

class PDFReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        """Initialize PDF generator"""
        self.output_dir = "outputs/pdf"
        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4e78'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f4e78'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#1f4e78'),
            borderPadding=5,
            backColor=colors.HexColor('#f0f0f0')
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Insight style
        self.styles.add(ParagraphStyle(
            name='Insight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leftIndent=20,
            fontName='Helvetica'
        ))
    
    def generate_report(self, data: dict) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            data: Dictionary containing all report data
        
        Returns:
            Path to generated PDF file
        """
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        period = data.get('period', 'Report').replace(' ', '_')
        filename = f"Financial_Report_{period}_{timestamp}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._create_title_page(data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(data))
        story.append(PageBreak())
        
        # Data quality
        story.extend(self._create_data_quality_section(data))
        story.append(PageBreak())
        
        # Financial performance
        story.extend(self._create_financial_section(data))
        story.append(PageBreak())
        
        # AI insights
        story.extend(self._create_insights_section(data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return output_path
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to pages"""
        canvas_obj.saveState()
        
        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#1f4e78'))
        canvas_obj.drawString(72, letter[1] - 50, "Financial Analysis Report")
        
        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        page_num = canvas_obj.getPageNumber()
        footer_text = f"Page {page_num} | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas_obj.drawRightString(letter[0] - 72, 50, footer_text)
        
        canvas_obj.restoreState()
    
    def _create_title_page(self, data: dict) -> list:
        """Create title page content"""
        content = []
        
        # Add space from top
        content.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph(data.get('title', 'Financial Analysis Report'), self.styles['CustomTitle'])
        content.append(title)
        content.append(Spacer(1, 0.5*inch))
        
        # Period
        period = Paragraph(f"Period: {data.get('period', 'N/A')}", self.styles['CustomSubtitle'])
        content.append(period)
        content.append(Spacer(1, 0.3*inch))
        
        # Date
        date = Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        )
        date.style.alignment = TA_CENTER
        content.append(date)
        
        return content
    
    def _create_executive_summary(self, data: dict) -> list:
        """Create executive summary section"""
        content = []
        
        # Section header
        header = Paragraph("Executive Summary", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 0.2*inch))
        
        # Key metrics table
        data_summary = data.get('data_summary', {})
        
        table_data = [
            ['Metric', 'Value'],
            ['Total Transactions', f"{data_summary.get('total_transactions', 0):,}"],
            ['Date Range', data_summary.get('date_range', 'N/A')],
            ['Unique Accounts', str(data_summary.get('accounts', 0))],
            ['Departments', str(data_summary.get('departments', 0))],
        ]
        
        table = Table(table_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.3*inch))
        
        return content
    
    def _create_data_quality_section(self, data: dict) -> list:
        """Create data quality section"""
        content = []
        
        # Section header
        header = Paragraph("Data Quality Assessment", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 0.2*inch))
        
        # Validation summary
        validation_summary = data.get('validation_summary', {})
        total_issues = sum(len(issues) for issues in validation_summary.values())
        
        # Status
        if total_issues == 0:
            status_text = '<font color="green"><b>✓ PASSED</b></font> - All validation checks completed successfully'
        else:
            status_text = f'<font color="red"><b>⚠ {total_issues} ISSUES DETECTED</b></font> - Review required'
        
        status = Paragraph(status_text, self.styles['Normal'])
        content.append(status)
        content.append(Spacer(1, 0.2*inch))
        
        # Issues by category
        if total_issues > 0:
            for category, issues in validation_summary.items():
                if issues:
                    cat_header = Paragraph(f"<b>{category}</b> ({len(issues)} issue(s))", self.styles['Normal'])
                    content.append(cat_header)
                    
                    for issue in issues[:3]:  # Show max 3 per category
                        issue_text = Paragraph(f"• {issue}", self.styles['Insight'])
                        content.append(issue_text)
                    
                    content.append(Spacer(1, 0.1*inch))
        
        return content
    
    def _create_financial_section(self, data: dict) -> list:
        """Create financial performance section"""
        content = []
        
        # Section header
        header = Paragraph("Financial Performance", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 0.2*inch))
        
        # P&L summary
        pl_statement = data.get('pl_statement')
        
        if pl_statement is not None and not pl_statement.empty:
            # Extract key figures
            try:
                revenue = pl_statement[pl_statement['Line Item'] == 'Total Revenue']['Amount'].values[0]
                cogs = pl_statement[pl_statement['Line Item'] == 'Total COGS']['Amount'].values[0]
                opex = pl_statement[pl_statement['Line Item'] == 'Total Operating Expenses']['Amount'].values[0]
                net_income_rows = pl_statement[pl_statement['Line Item'] == 'Net Income']
                net_income = net_income_rows['Amount'].values[-1] if len(net_income_rows) > 0 else 0
                
                gross_margin = ((revenue - cogs) / revenue * 100) if revenue != 0 else 0
                net_margin = (net_income / revenue * 100) if revenue != 0 else 0
                
                # Create metrics table
                pl_data = [
                    ['Metric', 'Amount', '% of Revenue'],
                    ['Revenue', f'${revenue:,.0f}', '100.0%'],
                    ['Cost of Goods Sold', f'${cogs:,.0f}', f'{(cogs/revenue*100):.1f}%'],
                    ['Gross Margin', f'${revenue-cogs:,.0f}', f'{gross_margin:.1f}%'],
                    ['Operating Expenses', f'${opex:,.0f}', f'{(opex/revenue*100):.1f}%'],
                    ['Net Income', f'${net_income:,.0f}', f'{net_margin:.1f}%'],
                ]
                
                table = Table(pl_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ('LINEABOVE', (0, 3), (-1, 3), 2, colors.black),  # Bold line for gross margin
                    ('LINEABOVE', (0, 5), (-1, 5), 2, colors.black),  # Bold line for net income
                ]))
                
                content.append(table)
                
            except Exception as e:
                error_text = Paragraph(f"Unable to display financial summary: {str(e)}", self.styles['Normal'])
                content.append(error_text)
        else:
            no_data = Paragraph("Financial data not available", self.styles['Normal'])
            content.append(no_data)
        
        return content
    
    def _create_insights_section(self, data: dict) -> list:
        """Create AI insights section"""
        content = []
        
        # Section header
        header = Paragraph("AI-Generated Insights & Recommendations", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 0.2*inch))
        
        # AI insights
        ai_insights = data.get('ai_insights', 'No analysis available')
        
        # Parse and format insights
        lines = ai_insights.split('\n')
        
        for line in lines:
            if line.strip():
                # Check if it's a header
                if line.startswith('#') or (len(line) < 50 and line.isupper()):
                    # It's a header
                    header_text = line.replace('#', '').strip()
                    p = Paragraph(f"<b>{header_text}</b>", self.styles['Normal'])
                    p.style.fontSize = 12
                    p.style.textColor = colors.HexColor('#1f4e78')
                    content.append(p)
                    content.append(Spacer(1, 0.1*inch))
                else:
                    # Regular text
                    p = Paragraph(line.strip(), self.styles['Insight'])
                    content.append(p)
        
        return content
