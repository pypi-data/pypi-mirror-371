# aegis/core/reporting.py

from fpdf import FPDF, HTMLMixin
import pandas as pd
from datetime import datetime
from io import BytesIO
import unicodedata
from .compliance import ComplianceMapper

class PDF(FPDF, HTMLMixin):
    """A custom PDF class that includes a header and footer."""
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        try:
            self.add_font('DejaVu', '', '/System/Library/Fonts/DejaVuSans.ttf', uni=True)
            self.add_font('DejaVu', 'B', '/System/Library/Fonts/DejaVuSans-Bold.ttf', uni=True)
            self.add_font('DejaVu', 'I', '/System/Library/Fonts/DejaVuSans-Oblique.ttf', uni=True)
            self.unicode_font_available = True
        except:
            self.unicode_font_available = False
    
    def safe_text(self, text):
        if self.unicode_font_available:
            return text
        return unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    
    def set_safe_font(self, family, style='', size=0):
        if self.unicode_font_available:
            self.set_font('DejaVu', style, size)
        else:
            self.set_font(family, style, size)

    def header(self):
        self.set_safe_font('Arial', 'B', 12)
        self.cell(0, 10, self.safe_text('Aegis LLM Security Report'), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_safe_font('Arial', 'I', 8)
        self.cell(0, 10, self.safe_text(f'Page {self.page_no()}'), 0, 0, 'C')

    def chapter_title(self, title):
        self.set_safe_font('Arial', 'B', 14)
        self.cell(0, 10, self.safe_text(title), 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, content, color=(0, 0, 0)):
        self.set_safe_font('Arial', '', 10)
        self.set_text_color(*color)
        self.multi_cell(0, 5, self.safe_text(content))
        self.set_text_color(0, 0, 0)
        self.ln()

    def compliance_section(self, category: str):
        """Adds a compliance mapping section to the report."""
        mappings = ComplianceMapper.get_mappings_for_category(category)
        if not mappings:
            return
            
        self.set_safe_font('Arial', 'B', 10)
        self.cell(0, 8, self.safe_text("Compliance & Regulatory Mapping:"), 0, 1, 'L')
        
        for framework, controls in mappings.items():
            self.set_safe_font('Arial', 'B', 9)
            self.cell(5) # Indent
            self.cell(0, 6, self.safe_text(f"- {framework.replace('_', ' ')}:"), 0, 1, 'L')
            self.set_safe_font('Arial', '', 9)
            for control in controls:
                self.cell(10) # Indent further
                self.cell(0, 5, self.safe_text(f"• {control}"), 0, 1, 'L')
        self.ln(2)


def generate_pdf_report(results: list, output_buffer: BytesIO, chart_image_buffer: BytesIO):
    if not results: return

    first_result = results[0]
    df = pd.DataFrame([{"classification": res["analysis"].classification.name, "score": res["analysis"].aegis_risk_score} for res in results])
    
    avg_score = df['score'].mean()
    non_compliant_count = df[df['classification'] == 'NON_COMPLIANT'].shape[0]
    total_prompts = len(df)

    pdf = PDF()
    pdf.add_page()

    pdf.chapter_title(f"Evaluation Summary: '{first_result['prompt'].category}'")
    pdf.set_safe_font('Arial', '', 11)
    pdf.cell(0, 8, pdf.safe_text(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), 0, 1, 'L')
    pdf.cell(0, 8, pdf.safe_text(f"Model Tested: {first_result['response'].model_name}"), 0, 1, 'L')
    pdf.ln(5)

    pdf.set_safe_font('Arial', 'B', 12)
    pdf.cell(0, 10, pdf.safe_text("Key Metrics"), 0, 1, 'L')
    pdf.set_safe_font('Arial', '', 11)
    pdf.cell(0, 8, pdf.safe_text(f"- Total Prompts Evaluated: {total_prompts}"), 0, 1, 'L')
    pdf.cell(0, 8, pdf.safe_text(f"- Non-Compliant Responses: {non_compliant_count} ({(non_compliant_count/total_prompts)*100 if total_prompts > 0 else 0:.1f}%)"), 0, 1, 'L')
    pdf.cell(0, 8, pdf.safe_text(f"- Average Aegis Risk Score (ARS): {avg_score:.2f} / 100.0"), 0, 1, 'L')
    pdf.ln(10)

    pdf.chapter_title("Classification Breakdown")
    if chart_image_buffer.getbuffer().nbytes > 0:
        chart_image_buffer.seek(0)
        pdf.image(chart_image_buffer, x=10, y=None, w=190, type='PNG')
    
    pdf.add_page()
    pdf.chapter_title("Detailed Evaluation Results")

    for i, res in enumerate(results):
        prompt, response, analysis = res["prompt"], res["response"], res["analysis"]

        if i > 0:
            pdf.ln(5)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(5)

        pdf.set_safe_font('Arial', 'B', 11)
        pdf.cell(0, 8, pdf.safe_text(f"Result for Prompt ID: {prompt.id}"), 0, 1, 'L')
        
        color_map = {"NON_COMPLIANT": (220, 50, 50), "COMPLIANT": (0, 128, 0), "PARTIAL_COMPLIANCE": (255, 165, 0)}
        classification_color = color_map.get(analysis.classification.name, (0, 0, 0))
        
        pdf.set_safe_font('Arial', 'B', 10)
        pdf.set_text_color(*classification_color)
        pdf.cell(0, 6, pdf.safe_text(f"Classification: {analysis.classification.name} (ARS: {analysis.aegis_risk_score:.1f})"), 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)

        pdf.compliance_section(prompt.category)

        pdf.set_safe_font('Arial', 'B', 10)
        pdf.cell(0, 8, pdf.safe_text("Adversarial Prompt:"), 0, 1, 'L')
        pdf.chapter_body(prompt.prompt_text)

        pdf.set_safe_font('Arial', 'B', 10)
        pdf.cell(0, 8, pdf.safe_text("Model Output:"), 0, 1, 'L')
        pdf.chapter_body(response.output_text, color=classification_color)
        
        pdf.set_safe_font('Arial', 'B', 10)
        pdf.cell(0, 8, pdf.safe_text("AI Analysis:"), 0, 1, 'L')
        pdf.chapter_body(analysis.explanation)

    pdf.output(output_buffer)
