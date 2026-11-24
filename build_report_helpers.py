"""Script to build the comprehensive 20-Chapter Visual Academic Project Report in PDF and DOCX."""

import os

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    Paragraph,
)

IMG_DIR = "/Users/kingsonisrael/Downloads/SIR PROJECT/report_illustrations"
PDF_FILENAME = "Disease_Spread_Prediction_Complete_Visual_Project_Report.pdf"


class AcademicNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count, academic running headers and footers."""
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        # Page 1 (Cover Page) is unadorned
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(36, 810, "EPISIM PRO")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(90, 810, "— Academic Project Report: SIR Differential Disease Spread Prediction System")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 804, 559, 804)

            # Running footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(559, 25, page_text)
            self.drawString(36, 25, "Academic Mini-Project Submission — Differential Equations & Applied Computing")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 35, 559, 35)
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    custom = [
        ParagraphStyle("CoverTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=21, leading=26, textColor=colors.HexColor("#0F172A"), alignment=1),
        ParagraphStyle("CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=15, textColor=colors.HexColor("#2563EB"), alignment=1),
        ParagraphStyle("CoverMeta", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=13, textColor=colors.HexColor("#334155")),
        ParagraphStyle("CoverMetaBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=13, textColor=colors.HexColor("#0F172A")),
        ParagraphStyle("ChapTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=colors.HexColor("#1E3A8A"), spaceBefore=14, spaceAfter=8, keepWithNext=True),
        ParagraphStyle("SecTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13.5, textColor=colors.HexColor("#0F172A"), spaceBefore=9, spaceAfter=4, keepWithNext=True),
        ParagraphStyle("SubSecTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.8, leading=12, textColor=colors.HexColor("#334155"), spaceBefore=6, spaceAfter=3, keepWithNext=True),
        ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=8.2, leading=11.8, textColor=colors.HexColor("#334155"), spaceAfter=5),
        ParagraphStyle("BodyBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.2, leading=11.8, textColor=colors.HexColor("#0F172A"), spaceAfter=5),
        ParagraphStyle("Callout", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, leading=11.5, textColor=colors.HexColor("#1E40AF")),
        ParagraphStyle("CodeBlock", parent=styles["Normal"], fontName="Courier", fontSize=7.2, leading=9.5, textColor=colors.HexColor("#0F172A")),
        ParagraphStyle("FigCaption", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=colors.HexColor("#475569"), alignment=1, spaceBefore=4, spaceAfter=8),
        ParagraphStyle("TH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.5, textColor=colors.HexColor("#0F172A")),
        ParagraphStyle("TD", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9, textColor=colors.HexColor("#334155")),
        ParagraphStyle("TOC_Chap", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=colors.HexColor("#1E3A8A")),
        ParagraphStyle("TOC_Sub", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#475569")),
        ParagraphStyle("TOC_Page", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#64748B"), alignment=2),
        ParagraphStyle("VivaQ", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=colors.HexColor("#1E3A8A"), spaceBefore=4, spaceAfter=2),
        ParagraphStyle("VivaA", parent=styles["Normal"], fontName="Helvetica", fontSize=7.8, leading=11, textColor=colors.HexColor("#334155"), spaceAfter=6),
    ]
    for s in custom:
        styles.add(s)
    return styles


def safe_image(filename, width=480, height=180, caption=None, styles=None):
    """Helper to return an Image flowable safely if file exists, along with its caption."""
    path = os.path.join(IMG_DIR, filename)
    flowables = []
    if os.path.exists(path):
        flowables.append(Image(path, width=width, height=height))
        if caption and styles:
            flowables.append(Paragraph(caption, styles["FigCaption"]))
    return flowables
