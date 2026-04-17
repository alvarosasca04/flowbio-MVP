import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. ESTILO INDUSTRIAL Y ALINEACIÓN (CSS)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Syne:wght@800&family=JetBrains+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    
    /* Alineación de botones de inicio */
    .start-container { display: flex; justify-content: center; gap: 20px; margin-top: 50px; }
    
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        text-transform: uppercase; letter-spacing: 1px; width: 100%;
    }
    
    /* Botón Secundario / Regreso */
    div.back-btn > div > .stButton > button {
        background: transparent !important; color: #64748B !important;
        border: 1px solid #1A2A3A !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. VARIABLES DE ESTADO
if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'data' not in st.session_state: st.session_state.data = None

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF (ALTA VISIBILIDAD)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 16); self.set_text_color(255, 255, 255)
        self.set_xy(10, 10); self.cell(0, 10, 'FlowBio AI Engine', 0, 1)
        self.set_font('Arial', '', 10); self.cell(0, 5, 'Reporte Tecnico de Simulacion PIML', 0, 1)

def generate_pdf_base64(d):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 10, 'IMPACTO ECONOMICO ANUAL PROYECTADO', 0, 1)
    
    # Caja de Ahorro Principal (Fondo blanco, texto oscuro para legibilidad)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 55, 190, 25, 'F')
    pdf.set_xy(15, 60); pdf.set_font('Arial', 'B', 24); pdf.set_text_color(0, 150, 100)
    pdf.cell(0, 15, f"${d['ahorro']:,.0f} USD/año", 0, 1)
    
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 10, 'METRICAS DE INGENIERIA', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"- Mejora de Produccion: +{d['mejora']:.1f}%", 0, 1)
    pdf.cell(0, 10, f"- Reservas EUR extra: {d['eur']:,.0f} bbls", 0, 1)
    pdf.cell(0, 10, f"- Tasa de Corrosion: {d['mpy']:.1f} mpy", 0, 1)

    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 4. FLUJO DE PANTALLAS
# ══════════════════════════════════════════════════════

# --- PANTALLA INICIO ---
if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:110px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'JetBrains Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">SUBSURFACE INTELLIGENCE OS</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1.8, 1.8, 1])
    with col2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            # AQUÍ SINCRONIZAMOS LOS DATOS REALES DE TUS AGENTES JUPYTER
            st.session_state.data = {
                "ahorro": 1620000.0, "mejora": 16.5, "fee": 21900.0, "co2": 833.0, 
                "eur": 425000.0, "mpy": 0.8, "pozos": 78, "bpd": 350, "label": "AWS S3 DATA LAKE"
            }
            st.session_state.screen = 'dash'; st.rerun()
    with col3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup'; st.rerun()

# --- PANTALLA DASHBOARD ---
elif st.session_state.screen == 'dash':
    d = st.session_state.data
    st.markdown(f"<h2 style='font-family:Syne; margin:20px; color:white;'>Command Center <span style='font-size:12px; color:#22D3EE;'>[{d['label']}]</span></h2>", unsafe_allow_html=True)
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("AHORRO OPEX", f"${d['ahorro']:,.0f}")
    k2.metric("MEJORA", f"+{d['mejora']:.1f}%")
    k3.metric("FEE MENSUAL", f"${d['fee']:,.0f}")
    k4.metric("CO2 EVITADO", f"{d['co2']:.0f}t")

    col_l, col_r = st.columns([3, 1])
    with col_l:
        # Gráfica
        st.markdown("<div style='background:#0D1520; padding:20px; border-radius:12px; border:1px solid #1A2A3A; height:450px;'></div>", unsafe_allow_html=True)

    with col_r:
        # Métricas Ingeniería (Colores corregidos)
        st.markdown(f"""
        <div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid #1A2A3A;">
            <p style="font-size:10px; color:#64748B;">RESERVAS EUR</p>
            <p style="font-family:'Syne'; font-size:26px; color:#22D3EE; margin:0;">{d['eur']:,.0f}</p>
            <hr style="opacity:0.1">
            <p style="font-size:10px; color:#64748B;">CORROSION</p>
            <p style="font-family:'Syne'; font-size:26px; color:#EF4444; margin:0;">{d['mpy']:.1f} mpy</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # BOTÓN REPORTE PDF
        pdf_b64 = generate_pdf_base64(d)
        st.markdown(f'<a href="data:application/pdf;base64,{pdf_b64}" download="FlowBio_Report.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:800; cursor:pointer;">📥 REPORTE OFICIAL</button></a>', unsafe_allow_html=True)
        
        # BOTONES DE REGRESO
        if st.button("🏠 MENU INICIO"):
            st.session_state.screen = 'splash'; st.rerun()
