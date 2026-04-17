import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import base64
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM Y CSS (ACTUALIZADO)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }

    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px 30px !important; width: 100%;
        border: none !important; transition: 0.3s; text-transform: uppercase;
    }
    
    .download-btn {
        background: rgba(34, 211, 238, 0.1) !important; color: #22D3EE !important;
        border: 1px solid #22D3EE !important; font-family: 'DM Mono' !important; font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. GENERADOR DE REPORTE PDF DE GRADO CORPORATIVO
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        # Fondo Dark Mode Corporativo
        self.set_fill_color(6, 11, 17) # #060B11
        self.rect(0, 0, 210, 297, 'F')
        
        # Logo FlowBio Premium (Simulado con Texto de alta calidad)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'FlowBio.', 0, 0, 'L')
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 116, 139) # #64748B
        self.cell(0, 15, 'SUBSURFACE INTELLIGENCE OS', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Generado por FlowBio AI el {datetime.now().strftime("%d/%m/%Y")} | Confidencial - Uso Operacional', 0, 0, 'C')

def create_pdf_report(well_name, data):
    pdf = FlowBioReport()
    pdf.add_page()
    
    # 1. Título del Reporte
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'Reporte Ejecutivo de Optimización: {well_name}', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 229, 160) # #00E5A0
    pdf.cell(0, 5, f'Tecnología: Na-CMC Validada por Consenso de 5 Agentes', 0, 1, 'L')
    pdf.ln(15)

    # 2. Sección de KPIs (Tabla Corporativa)
    pdf.set_fill_color(13, 21, 32) # #0D1520
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(190, 10, ' Resumen de Impacto Financiero y Operacional', 1, 1, 'L', True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 116, 139) # #64748B
    
    col_width = 190 / 4
    headers = ['AHORRO OPEX', 'MEJORA BARRIDO', 'CO2 EVITADO', 'PAYBACK']
    values = [f"${data['ahorro']:,}", f"+{data['mejora']}%", f"{data['co2']}t", f"{data['payback']} Meses"]
    
    for header in headers: pdf.cell(col_width, 10, header, 1, 0, 'C', True)
    pdf.ln()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    for value in values: pdf.cell(col_width, 10, value, 1, 0, 'C')
    pdf.ln(25)

    # 3. Gráfica de Declinación (Imagen de Grado Corporativo)
    # Generamos la gráfica con Plotly en memoria para alta calidad
    base = data['bpd']
    mej = data['mejora'] / 100
    x = list(range(40))
    y1 = [base * math.exp(-0.06*i) for i in x]
    y2 = [(y1[i] + (base * mej * math.exp(-0.015*(i-5)))) if i>=5 else y1[i] for i in x]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y1, line=dict(color='#EF4444', dash='dot'), name='Base (HPAM)'))
    fig.add_trace(go.Scatter(x=x, y=y2, line=dict(color='#00E5A0', width=4), fill='tonexty', fillcolor='rgba(0,229,160,0.1)', name='FlowBio AI'))
    fig.update_layout(paper_bgcolor='#060B11', plot_bgcolor='#0D1520', font=dict(color='#64748B'), margin=dict(t=10, b=10, l:10, r:10))
    
    # Truco para exportar imagen de Plotly a bytes
    img_bytes = fig.to_image(format="png", width=800, height=400, scale=2)
    img_buffer = BytesIO(img_bytes)
    
    # Insertar imagen en el PDF
    pdf.image(img_buffer, x=15, y=pdf.get_y(), w=180)
    pdf.ln(95)

    # 4. Engineering Insights (Justificación Técnica)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Justificación Técnica de Ingeniería (PIML)', 0, 1, 'L')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(139, 168, 192) # #8BA8C0
    
    insights = [
        f"Viscosidad Plástica (PV): {data['visc_p']} cP - El fluido mantiene la reología óptima para evitar la canalización del agua.",
        f"Yield Point (YP): {data['yield_p']} lb/100ft² - Demuestra estabilidad mecánica en el fondo del pozo.",
        f"Incremental Proyectado (EUR): {data['eur']:,} bbls - Volumen masivo de crudo recuperable gracias al Na-CMC."
    ]
    
    for insight in insights:
        pdf.multi_cell(0, 5, f"> {insight}", 0, 'L')
        pdf.ln(2)

    return pdf.output(dest='S')

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE NAVEGACIÓN Y DASHBOARD
# ══════════════════════════════════════════════════════
# ... (Funciones load_data_from_s3 y navegación splash sin cambios) ...

elif st.session_state.screen == 'dash':
    st.markdown("<h2 style='font-family:Syne; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    wells = list(st.session_state.all_data.keys())
    selected_well = st.selectbox("Pozo analizado por agentes:", wells)
    d = st.session_state.all_data[selected_well]
    
    # KPIs Superiores
    # ... (Bloque de KPIs sin cambios) ...

    # CONTENIDO PRINCIPAL Y BOTÓN DE EXPORTACIÓN
    col_chart, col_insights = st.columns([2.3, 1.7])
    
    with col_chart:
        # ... (Gráfica interactiva sin cambios) ...
        
    with col_insights:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        # Insights TÉCNICOS (Renderizado HTML Blindado)
        tech_html = f"""
        <div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:500px; overflow-y:auto; margin-bottom:20px;">
            <p style="color:#00E5A0; font-weight:800; font-size:12px; margin-bottom:15px;">🧠 ENGINEERING INSIGHTS (5-AGENT CONSENSUS)</p>
            <div class="tech-box">
                <p class="tech-label">VISCOSIDAD PLÁSTICA (PV): {d.get('visc_p', 'N/A')} cP</p>
                <p class="reasoning-text"><b>¿Por qué importa?</b> Evita el "dedeo" viscoso (*fingering*), asegurando que el fluido empuje el crudo uniformemente.</p>
            </div>
            <div class="tech-box">
                <p class="tech-label">YIELD POINT (YP): {d.get('yield_p', 'N/A')} lb/100ft²</p>
                <p class="reasoning-text"><b>¿Por qué importa?</b> Indica estabilidad bajo presión en el fondo; el polímero no se degradará mecánicamente.</p>
            </div>
            <div class="tech-box">
                <p class="tech-label">PAYBACK: {d['payback']} MESES</p>
                <p class="reasoning-text"><b>¿Por qué importa?</b> Retorno casi instantáneo; el crudo extra cubre el costo tecnológico en tiempo récord.</p>
            </div>
            <p style="color:#64748B; font-size:10px; margin-top:20px; text-transform: uppercase;">INCREMENTAL PROYECTADO (EUR):</p>
            <p style="color:#00E5A0; font-size:32px; font-weight:800; margin:0;">{d['eur']:,} <span style="font-size:12px; color:#64748B;">bbls</span></p>
        </div>
        """
        st.markdown(tech_html, unsafe_allow_html=True)
        
        # ⬇️ BOTÓN DE DESCARGA PDF DE GRADO CORPORATIVO ⬇️
        with st.spinner("Generando Reporte Corporativo..."):
            pdf_data = create_pdf_report(selected_well, d)
            st.download_button(
                label="📥 EXPORTAR REPORTE PDF DE OPERACIONES",
                data=pdf_data,
                file_name=f"FlowBio_Report_{selected_well}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="download-btn"
            )

    # REINICIO
    # ... (Botón de inicio sin cambios) ...
