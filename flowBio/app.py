import streamlit as st
import streamlit.components.v1 as components
import base64
from fpdf import FPDF
import io

# ══════════════════════════════════════════════════════
# MOTOR DE REPORTE PROFESIONAL FLOWBIO (ESTILO PDF ADJUNTO)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        # Fondo oscuro en el encabezado
        self.set_fill_color(6, 11, 17)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Reporte de Simulación EOR Na-CMC Jacinto de Agua PIML', 0, 1, 'L')
        self.ln(5)

    def chapter_title(self, title, color=(0, 229, 160)):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*color)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def add_metric_box(self, label, value, x, y, w=45):
        self.set_xy(x, y)
        self.set_fill_color(240, 240, 240)
        self.rect(x, y, w, 20, 'F')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(6, 11, 17)
        self.cell(w, 10, value, 0, 1, 'C')
        self.set_font('Arial', '', 8)
        self.set_xy(x, y + 10)
        self.cell(w, 5, label, 0, 1, 'C')

def generate_flowbio_pdf(data):
    pdf = FlowBioReport()
    pdf.add_page()
    
    # 1. IMPACTO ECONÓMICO ANUAL PROYECTADO
    pdf.chapter_title('Impacto Económico Anual Proyectado')
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(0, 150, 100)
    pdf.cell(0, 15, f"{data['ahorro_usd']}/año", 0, 1, 'L')
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"ahorro anual estimado con Na-CMC FlowBio en {data['label']}", 0, 1, 'L')
    pdf.ln(5)
    
    # Grid de métricas económicas
    pdf.add_metric_box("OPEX Actual", "$19.80", 10, 75)
    pdf.add_metric_box("OPEX FlowBio", "$17.23", 60, 75)
    pdf.add_metric_box("Ahorro/bbl", "$2.57", 110, 75)
    pdf.add_metric_box("ROI Estimado", "15%", 160, 75)
    pdf.ln(25)
    
    # 2. ANÁLISIS REOLÓGICO PIML
    pdf.chapter_title('Análisis Reológico - Modelo Power Law (PIML)')
    pdf.add_metric_box("Indice flujo (n)", "0.569", 10, 115)
    pdf.add_metric_box("Consistencia K", "151.4", 60, 115)
    pdf.add_metric_box("Ratio movilidad", "0.28", 110, 115)
    pdf.add_metric_box("Ef. barrido", "43%", 160, 115)
    pdf.ln(30)

    # 3. COMPARATIVA TÉCNICA
    pdf.chapter_title('Comparativa - HPAM Sintético vs Na-CMC FlowBio')
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(230, 230, 230)
    # Encabezados de tabla
    pdf.cell(45, 8, "Parámetro", 1, 0, 'C', True)
    pdf.cell(70, 8, "HPAM", 1, 0, 'C', True)
    pdf.cell(70, 8, "FlowBio Na-CMC", 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 9)
    comparativa = [
        ["Biodegradabilidad", "No biodegradable", "100% biodegradable"],
        ["Skin Damage", "Alto riesgo", "Mínimo"],
        ["HSE Risk Factor", "Tóxico", "Seguro"],
        ["Agua residual", "Difícil tratamiento", "Fácil tratamiento"]
    ]
    for row in comparativa:
        pdf.cell(45, 8, row[0], 1)
        pdf.cell(70, 8, row[1], 1)
        pdf.cell(70, 8, row[2], 1, 1)
    
    pdf.ln(10)
    
    # 4. DIAGNÓSTICO TÉCNICO
    pdf.chapter_title('Diagnóstico Técnico Motor PIML')
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(50, 50, 50)
    diag = (
        f"El índice de flujo n=0.569 confirma comportamiento pseudoplástico adecuado. "
        f"La eficiencia de barrido proyectada de {data['mejora']}% representa un incremento significativo "
        f"sobre el baseline, optimizando la recuperación final en los {data['pozos']} pozos analizados."
    )
    pdf.multi_cell(0, 5, diag)
    
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# RECEPTOR DE DATOS Y BOTÓN (PYTHON SIDE)
# ══════════════════════════════════════════════════════
query_params = st.query_params
if query_params:
    report_data = {
        'ahorro_usd': query_params.get('ahorro_usd', '$394.0K'),
        'mejora': query_params.get('mejora', '43'),
        'pozos': query_params.get('pozos', '10'),
        'label': query_params.get('label', 'Central North Sea')
    }

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pdf_bytes = generate_flowbio_pdf(report_data)
        st.download_button(
            label="📥 DESCARGAR REPORTE TÉCNICO PIML (PDF)",
            data=pdf_bytes,
            file_name=f"FlowBio_Technical_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
