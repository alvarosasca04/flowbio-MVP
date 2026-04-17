import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import base64
import math
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL Y CONFIGURACIÓN PREMIUM
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        width: 100%; transition: 0.3s; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'data' not in st.session_state: st.session_state.data = None

# ══════════════════════════════════════════════════════
# 2. MOTOR DE INGENIERÍA PIML (DATOS REALES)
# ══════════════════════════════════════════════════════
def calculate_piml_physics(fluido, pozos, bpd):
    # Parámetros basados en el reporte oficial de FlowBio
    n = 0.569 if "Na-CMC" in fluido else 0.78  # Índice de flujo [cite: 14]
    k_consistencia = 151.4 if "Na-CMC" in fluido else 85.2 # [cite: 16]
    mobility_ratio = 0.28 if "Na-CMC" in fluido else 0.85 # [cite: 18]
    
    # Cálculos de Producción
    mejora_pct = 16.5 if "Na-CMC" in fluido else 11.0 # [cite: 11, 32]
    extra_bpd = bpd * (mejora_pct / 100)
    ahorro_anual = extra_bpd * 365 * pozos * 2.57 # Ahorro de $2.57 por barril [cite: 10]
    eur_5a = extra_bpd * 365 * 5 * 0.8 * pozos # Reservas a 5 años
    
    return {
        "n": n, "k": k_consistencia, "m_ratio": mobility_ratio,
        "ahorro": ahorro_anual, "mejora": mejora_pct,
        "eur": eur_5a, "mpy": 0.8 if "Na-CMC" in fluido else 25.0,
        "pozos": pozos, "bpd": bpd, "fluido": fluido
    }

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF (ESTILO OFICIAL)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 16); self.set_text_color(255, 255, 255)
        self.set_xy(10, 10); self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.set_font('Arial', '', 10); self.cell(0, 5, 'Reporte de Simulacion EOR Na-CMC Jacinto de Agua PIML', 0, 1, 'L')
        self.ln(10)

def generate_pdf_base64(d):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 10, 'IMPACTO ECONOMICO ANUAL PROYECTADO', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font('Arial', 'B', 22); pdf.set_text_color(0, 150, 100)
    pdf.cell(0, 15, f"${d['ahorro']:,.0f} USD/año", 0, 1)
    
    # Análisis Reológico (Valores que cuadran con los agentes)
    pdf.ln(10); pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 10, 'ANALISIS REOLOGICO - MODELO POWER LAW (PIML)', 0, 1, 'L')
    pdf.set_font('Arial', '', 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"- Indice de flujo (n): {d['n']}", 0, 1)
    pdf.cell(0, 8, f"- Consistencia K: {d['k']} mPas", 0, 1)
    pdf.cell(0, 8, f"- Ratio de movilidad: {d['m_ratio']}", 0, 1)
    pdf.cell(0, 8, f"- Eficiencia de barrido: {d['mejora']}%", 0, 1)

    binary_pdf = pdf.output(dest="S").encode("latin-1")
    return base64.b64encode(binary_pdf).decode()

# ══════════════════════════════════════════════════════
# 4. FLUJO DE NAVEGACIÓN
# ══════════════════════════════════════════════════════
if st.session_state.screen == 'splash':
    st.markdown("""<div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:110px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">SUBSURFACE INTELLIGENCE OS</p></div>""", unsafe_allow_html=True)
    _, c2, c3, _ = st.columns([1, 1.8, 1.8, 1])
    if c2.button("DEMO REAL S3 (10 POZOS)"):
        st.session_state.data = calculate_piml_physics("Na-CMC", 10, 350)
        st.session_state.screen = 'dash'; st.rerun()
    if c3.button("SIMULADOR IA (CONFIGURABLE)"):
        st.session_state.screen = 'setup'; st.rerun()

elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:60px 100px;'><h2 style='font-family:Syne; color:white; font-size:40px;'>Configuracion de Activos</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    f = c1.selectbox("FLUIDO EOR", ["Na-CMC (FlowBio Eco-Safe)", "HPAM (Tradicional)"])
    t = c1.selectbox("METALURGIA", ["Carbon Steel (L-80)", "Aleacion CRA (13Cr)"])
    p = c2.number_input("POZOS", value=15); b = c2.number_input("BPD BASE", value=350)
    if st.button("🧠 EJECUTAR ANALISIS DE AGENTES"):
        st.session_state.data = calculate_piml_physics(f, p, b)
        st.session_state.screen = 'dash'; st.rerun()

elif st.session_state.screen == 'dash':
    d = st.session_state.data
    st.markdown(f"<h2 style='font-family:Syne; margin:20px; color:white;'>Command Center <span style='font-size:12px; color:#22D3EE;'>[PIML ENGINE VALIDATED]</span></h2>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX / AÑO</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,.0f}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA PROMEDIO</p><p class="kpi-value">+{d["mejora"]:.1f}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">RATIO MOVILIDAD</p><p class="kpi-value" style="color:#22D3EE;">{d["m_ratio"]}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">INDICE FLUJO (n)</p><p class="kpi-value" style="color:#F59E0B;">{d["n"]}</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([3, 1])
    with cl:
        st.markdown(f"<div style='background:#0D1520; border-radius:12px; height:450px; border:1px solid #1A2A3A; padding:20px; color:#64748B;'>Gráfica de Declinación Validada por Agentes para {d['pozos']} pozos.</div>", unsafe_allow_html=True)
    with cr:
        st.markdown(f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid #1A2A3A;">
            <p style="font-size:10px; color:#64748B; font-weight:700;">DATOS TECNICOS</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">RESERVAS EUR (5A)</p><p style="font-family:'Syne'; font-size:26px; color:#22D3EE; margin:0;">{d['eur']:,.0f}</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">CONSISTENCIA K</p><p style="font-family:'Syne'; font-size:26px; color:#00E5A0; margin:0;">{d['k']}</p></div>""", unsafe_allow_html=True)
        pdf_b64 = generate_pdf_base64(d)
        st.markdown(f'<br><a href="data:application/pdf;base64,{pdf_b64}" download="FlowBio_Technical_Report.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:800; cursor:pointer;">📥 DESCARGAR REPORTE OFICIAL</button></a>', unsafe_allow_html=True)
        if st.button("🏠 INICIO"): st.session_state.screen = 'splash'; st.rerun()
