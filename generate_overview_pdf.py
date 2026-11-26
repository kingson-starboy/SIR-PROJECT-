import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 756, "SIR Project · Disease Dynamics & Healthcare Capacity Intelligence")
            self.drawRightString(576, 756, "Platform Executive Whitepaper")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 40, 576, 40)
        self.drawString(36, 28, "CONFIDENTIAL & SCIENTIFIC · https://s-i-r-project.streamlit.app/")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_str)
        self.restoreState()

def create_report_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0284C7'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0369A1')
    )

    table_header_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#FFFFFF'),
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_bold = ParagraphStyle(
        'TDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("SIR PROJECT: COMPREHENSIVE PLATFORM WHITEPAPER", title_style))
    story.append(Paragraph("DISEASE DYNAMICS SIMULATION & HEALTHCARE CAPACITY INTELLIGENCE", subtitle_style))
    
    meta_data = [
        [
            Paragraph("<b>Platform Name:</b> SIR Project v2.5", table_cell_style),
            Paragraph("<b>Live URL:</b> s-i-r-project.streamlit.app", table_cell_style),
            Paragraph("<b>Mathematical Engine:</b> Dormand-Prince RK5(4)", table_cell_style)
        ],
        [
            Paragraph("<b>Author / Lead:</b> Kingson Israel", table_cell_style),
            Paragraph("<b>Repository:</b> github.com/kingson-starboy/SIR-PROJECT-", table_cell_style),
            Paragraph("<b>Verification:</b> 146 Automated Tests (100% Pass)", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[180, 180, 180])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Executive Summary Callout
    exec_summary_text = (
        "<b>Executive Purpose:</b> The SIR Project is an enterprise-grade scientific modeling suite designed "
        "to translate non-linear infectious disease epidemiology into actionable healthcare capacity forecasts. "
        "By numerically integrating the Kermack-McKendrick compartmental differential equations with Dormand-Prince "
        "Runge-Kutta 5(4) precision, the platform models transmission velocity, hospital ICU bed breach horizons, "
        "and non-pharmaceutical policy interventions (lockdowns, mask mandates, and mass immunization)."
    )
    t_callout = Table([[Paragraph(exec_summary_text, callout_style)]], colWidths=[540])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E0F2FE')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#38BDF8')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 10))

    # Section 1: What is this Website About?
    story.append(Paragraph("1. What is this Website About?", h1_style))
    story.append(Paragraph(
        "At its core, the <b>SIR Project</b> is an interactive web platform that democratizes computational epidemiology. "
        "During viral respiratory pandemics (such as COVID-19, SARS, or pandemic influenza), policymakers and hospital "
        "executives face severe uncertainty regarding when infection waves will crest, how many patients will require "
        "intensive care, and whether community restrictions can avert catastrophic hospital gridlock.",
        body_style
    ))
    story.append(Paragraph(
        "This platform bridges the gap between complex biomathematics and public health decision-making. "
        "It provides a real-time, interactive environment where users can calibrate epidemic parameters, "
        "observe numerical trajectory curves, and quantify healthcare surge stress under both unmitigated and "
        "intervention-controlled scenarios.",
        body_style
    ))

    # Section 2: Core Purpose & Target Audience
    story.append(Paragraph("2. What is it Used For? (Target Applications)", h1_style))
    
    use_cases = [
        [
            Paragraph("<b>Domain / Sector</b>", table_header_style),
            Paragraph("<b>Primary Use Case</b>", table_header_style),
            Paragraph("<b>Core Value & Impact Delivered</b>", table_header_style)
        ],
        [
            Paragraph("<b>Hospital & ICU Leadership</b>", table_cell_bold),
            Paragraph("Surge Capacity & Bed Allocation", table_cell_style),
            Paragraph("Forecasts the exact calendar day when active patient volume breaches licensed ICU capacity, calculating peak excess bed deficits.", table_cell_style)
        ],
        [
            Paragraph("<b>Public Health Authorities</b>", table_cell_bold),
            Paragraph("Intervention Policy Planning", table_cell_style),
            Paragraph("Simulates 'Flatten the Curve' strategies: social distancing, scheduled circuit-breaker lockdowns, and vaccination rollouts.", table_cell_style)
        ],
        [
            Paragraph("<b>Epidemiologists & Researchers</b>", table_cell_bold),
            Paragraph("Comparative Scenario Benchmarking", table_cell_style),
            Paragraph("Dual-scenario simulation lab comparing baseline spread against tailored interventions, computing infection delta and delay in peak wave timing.", table_cell_style)
        ],
        [
            Paragraph("<b>Academia, Educators & Students</b>", table_cell_bold),
            Paragraph("STEM & Biomathematics Pedagogy", table_cell_style),
            Paragraph("Visualizes the Kermack-McKendrick compartmental pipeline, explaining R₀ reproduction dynamics, herd immunity thresholds, and conservation of mass.", table_cell_style)
        ]
    ]
    t_use = Table(use_cases, colWidths=[130, 140, 270])
    t_use.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_use)
    story.append(Spacer(1, 10))

    # Page Break to Page 2 for clean structure
    story.append(PageBreak())

    # Section 3: Architecture & 4 Core Modules
    story.append(Paragraph("3. Functional Modules of the Platform", h1_style))
    story.append(Paragraph(
        "The web application is engineered as a clean 4-module interactive system, accessible via the sidebar navigation:",
        body_style
    ))

    modules_data = [
        [
            Paragraph("<b>Module View</b>", table_header_style),
            Paragraph("<b>Key Features & Interactive Controls</b>", table_header_style),
            Paragraph("<b>Outputs & Diagnostics</b>", table_header_style)
        ],
        [
            Paragraph("<b>1. Live Dashboard</b>", table_cell_bold),
            Paragraph("• 30-Second Quick Start Guide<br/>• Real-time parameter sliders (β, γ, N, ICU %)<br/>• Non-pharmaceutical intervention toggles<br/>• Pre-vaccination coverage slider", table_cell_style),
            Paragraph("• Threat Intelligence Ribbon<br/>• Real-time interactive Plotly S-I-R curves<br/>• Peak infection day & excess cases<br/>• RK45 conservation invariance metrics", table_cell_style)
        ],
        [
            Paragraph("<b>2. Scenario Comparison Lab</b>", table_cell_bold),
            Paragraph("• Dual parameter calibration (Scenario A vs. B)<br/>• Independent transmission, recovery & intervention tuning<br/>• Unified visual comparison chart", table_cell_style),
            Paragraph("• Peak infection burden delta (%)<br/>• Peak timing delay in days (Timeline shifted)<br/>• Net attack rate variance<br/>• Reproduction ratio (R₀) delta", table_cell_style)
        ],
        [
            Paragraph("<b>3. Model Explorer & Atlas</b>", table_cell_bold),
            Paragraph("• 6-Pathogen Library with 1-click simulation buttons<br/>• Visual S-I-R Compartment Pipeline Cards<br/>• The 3 Golden Mathematical Laws of Outbreaks<br/>• Policy Impact Matrix & Scientific FAQs", table_cell_style),
            Paragraph("• COVID-19, 1918 Flu, SARS-CoV-1, H1N1, Measles<br/>• Educational formulas (dS/dt, dI/dt, dR/dt)<br/>• Herd Immunity Threshold (HIT) calculation<br/>• Healthcare Nullcline analysis", table_cell_style)
        ],
        [
            Paragraph("<b>4. Data & Telemetry Hub</b>", table_cell_bold),
            Paragraph("• Time-series numerical trajectory table<br/>• Multi-format export center<br/>• High-contrast responsive styling", table_cell_style),
            Paragraph("• Download RFC-4180 CSV dataset<br/>• Download JSON run parameters manifest<br/>• Download Executive Summary (.txt)<br/>• Download formal A4 Clinical PDF report", table_cell_style)
        ]
    ]
    t_mod = Table(modules_data, colWidths=[120, 220, 200])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 12))

    # Section 4: Mathematical Foundation & Scientific Rigor
    story.append(Paragraph("4. Mathematical Formulation & Scientific Rigor", h1_style))
    story.append(Paragraph(
        "The platform implements the foundational non-linear Kermack-McKendrick (1927) system of ordinary differential equations (ODEs):",
        body_style
    ))

    math_box = [
        [
            Paragraph("<b>Compartment</b>", table_header_style),
            Paragraph("<b>Governing Differential Equation</b>", table_header_style),
            Paragraph("<b>Biological Mechanics & Conservation Law</b>", table_header_style)
        ],
        [
            Paragraph("<b>Susceptible (S)</b>", table_cell_bold),
            Paragraph("<b>dS / dt = -β · (S · I) / N</b>", table_cell_style),
            Paragraph("Healthy individuals prone to infection. Depletes strictly monotonically as contagious contacts occur.", table_cell_style)
        ],
        [
            Paragraph("<b>Infectious (I)</b>", table_cell_bold),
            Paragraph("<b>dI / dt = β · (S · I) / N - γ · I</b>", table_cell_style),
            Paragraph("Active transmitters. Expands exponentially while S/N &gt; 1/R₀; peaks at dI/dt = 0; decays asymptotically to 0.", table_cell_style)
        ],
        [
            Paragraph("<b>Recovered (R)</b>", table_cell_bold),
            Paragraph("<b>dR / dt = γ · I</b>", table_cell_style),
            Paragraph("Permanently immune convalescent individuals. Strict population conservation: <b>S(t) + I(t) + R(t) ≡ N</b>.", table_cell_style)
        ]
    ]
    t_math = Table(math_box, colWidths=[110, 180, 250])
    t_math.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_math)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Numerical Precision:</b> Unlike naive forward-Euler scripts that accumulate truncation errors and violate population conservation, this platform utilizes SciPy's adaptive <b>Dormand-Prince RK5(4)</b> solver (`scipy.integrate.solve_ivp(method='RK45')`). Step sizes are dynamically adjusted to maintain conservation error |S + I + R - N| strictly within 10⁻¹² precision across 500+ simulation days.", body_style))
    story.append(Spacer(1, 10))

    # Section 5: Technical Specifications & Verification
    story.append(Paragraph("5. Architectural Specifications & Quality Assurance", h1_style))
    spec_data = [
        [Paragraph("<b>Component</b>", table_header_style), Paragraph("<b>Implementation Standard</b>", table_header_style)],
        [Paragraph("Frontend & Application Framework", table_cell_bold), Paragraph("Streamlit with custom Nexafo-inspired CSS, light/dark themes & Plotly responsive charts", table_cell_style)],
        [Paragraph("Differential Equations Engine", table_cell_bold), Paragraph("SciPy integrate (`RK45`), NumPy vectorization, cached execution (`@st.cache_data`)", table_cell_style)],
        [Paragraph("Automated Test Suite", table_cell_bold), Paragraph("146 unit, integration, numerical, and UI regression tests via Pytest (100% pass rate)", table_cell_style)],
        [Paragraph("Continuous Integration", table_cell_bold), Paragraph("GitHub Actions matrix across Python 3.10, 3.11, 3.12, 3.13 with Ruff strict linting", table_cell_style)],
        [Paragraph("Deployment & Infrastructure", table_cell_bold), Paragraph("Streamlit Community Cloud with auto-sync continuous deployment from GitHub main branch", table_cell_style)]
    ]
    t_spec = Table(spec_data, colWidths=[180, 360])
    t_spec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_spec)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated executive report PDF: {filename}")

if __name__ == "__main__":
    out_pdf = "/Users/kingsonisrael/Downloads/SIR PROJECT/SIR_Project_Comprehensive_Executive_Report.pdf"
    create_report_pdf(out_pdf)
