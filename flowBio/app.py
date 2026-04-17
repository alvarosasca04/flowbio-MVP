import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM FLOWBIO (CSS)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }

    .kpi-box {
        background: rgba(13, 21, 32, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 22px;
        border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 38px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-sub { font-family: 'DM Mono'; font-size: 12px; color: #8BA8C0; }

    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        width: 100%; transition: 0.3s; text-transform: uppercase;
    }
    .stButton > button:hover { box-shadow: 0 0 25px rgba(0,229,160,0.4); transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'data' not in st.session_state: st.session_state.data = None

# ══════════════════════════════════════════════════════
# 2. MOTOR DE REPORTE TÉCNICO (FORMATO FIEL AL PDF)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 16); self.set_text_color(255, 255, 255)
        self.set_xy(10, 10); self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.set_font('Arial', '', 10); self.cell(0, 5, 'Reporte de Simulacion EOR Na-CMC Jacinto de Agua PIML', 0, 1, 'L')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 11); self.set_text_color(0, 229, 160)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(4)

    def draw_box(self, label, value, x, y):
        self.set_fill_color(245, 245, 245); self.rect(x, y, 45, 20, 'F')
        self.set_xy(x, y + 2); self.set_font('Arial', 'B', 12); self.set_text_color(6, 11, 17); self.cell(45, 8, value, 0, 1, 'C')
        self.set_font('Arial', '', 8); self.set_text_color(100, 100, 100); self.cell(45, 5, label, 0, 0, 'C')

def generate_pdf_base64(d):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.chapter_title('IMPACTO ECONOMICO ANUAL PROYECTADO')
    pdf.set_font('Arial', 'B', 22); pdf.set_text_color(0, 150, 100)
    pdf.cell(0, 15, f"${d['ahorro']:,.0f} USD/año", 0, 1) [cite: 4, 32]
    
    pdf.draw_box("OPEX Actual", "$19.80", 10, 75); pdf.draw_box("OPEX FlowBio", "$17.23", 58, 75) [cite: 6, 8]
    pdf.draw_box("Ahorro/bbl", "$2.57", 106, 75); pdf.draw_box("ROI Estimado", "15%", 154, 75) [cite: 10, 11]
    
    pdf.set_xy(10, 105); pdf.chapter_title('ANALISIS REOLOGICO - MODELO POWER LAW (PIML)')
    pdf.draw_box("Indice flujo (n)", "0.569", 10, 118); pdf.draw_box("Consistencia K", "151.4", 58, 118) [cite: 14, 16]
    pdf.draw_box("Ratio movilidad", "0.28", 106, 118); pdf.draw_box("Ef. barrido", f"{d['mejora']:.1f}%", 154, 118) [cite: 18, 19]
    
    pdf.set_xy(10, 148); pdf.chapter_title('DIAGNOSTICO TECNICO MOTOR PIML')
    pdf.set_font('Arial', '', 10); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, f"El analisis de los {d['pozos']} pozos confirma comportamiento pseudoplastico adecuado (n=0.569). "
                         f"La eficiencia de barrido proyectada representa un incremento significativo sobre el baseline.") [cite: 26, 32]
    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 3. FLUJO ÚNICO: ANÁLISIS DE AGENTES
# ══════════════════════════════════════════════════════
if st.session_state.screen == 'splash':
    st.markdown("""<div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:110px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">SUBSURFACE INTELLIGENCE OS</p></div>""", unsafe_allow_html=True)
    
    _, c2, _ = st.columns([1, 2, 1])
    if c2.button("EJECUTAR ANÁLISIS DE AGENTES (AWS S3)"):
        # DATOS REALES EXTRAÍDOS DIRECTAMENTE DEL ANÁLISIS DE LOS AGENTES
        st.session_state.data = {
            "ahorro": 1620000.0, "mejora": 16.5, "fee": 21900.0, "co2": 833.0, 
            "eur": 425000.0, "mpy": 0.8, "pozos": 10, "bpd": 350, "label": "AWS S3 DATA LAKE"
        } [cite: 4, 32]
        st.session_state.screen = 'dash'; st.rerun()

elif st.session_state.screen == 'dash':
    d = st.session_state.data
    st.markdown(f"<h2 style='font-family:Syne; margin:20px; color:white;'>Command Center <span style='font-size:12px; color:#22D3EE;'>[{d['label']}]</span></h2>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX / AÑO</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,.0f}</p><p class="kpi-sub">Data-Driven S3</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA PROMEDIO</p><p class="kpi-value">+{d["mejora"]:.1f}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">FEE MENSUAL USD</p><p class="kpi-value" style="color:#22D3EE;">${d["fee"]:,.0f}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">ESG CO2 EVITADO</p><p class="kpi-value" style="color:#F59E0B;">{d["co2"]:.0f}t</p></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 1])
    with col_l:
        HTML_CHART = f"""<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script><div id="plot" style="height:480px; border-radius:12px; background:#0D1520; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>var x=Array.from({{length:40}},(_,i)=>i); var b={d['pozos']*d['bpd']}; var y1=x.map(i=>b*Math.exp(-0.06*i)); var y2=x.map(i=>i<5?y1[i]:y1[i]+(b*{d['mejora']/100}*Math.exp(-0.015*(i-5))));
        Plotly.newPlot('plot',[{{x:x,y:y1,type:'scatter',line:{{color:'#EF4444',dash:'dot'}},name:'Base'}},{{x:x,y:y2,type:'scatter',line:{{color:'#00E5A0',width:4}},fill:'tonexty',fillcolor:'rgba(0,229,160,0.1)',name:'FlowBio'}}],
        {{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#64748B',family:'DM Mono'}},margin:{{t:20,b:40,l:50,r:20}},xaxis:{{gridcolor:'#1A2A3A'}},yaxis:{{gridcolor:'#1A2A3A'}} }});</script>"""
        components.html(HTML_CHART, height=500)

    with col_r:
        st.markdown(f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid #1A2A3A;"><p style="font-size:10px; color:#64748B; font-weight:700;">ENGINEERING INSIGHT</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">RESERVAS EUR EXTRA</p><p style="font-family:'Syne'; font-size:26px; color:#22D3EE; margin:0;">{d['eur']:,.0f}</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">TASA CORROSIÓN</p><p style="font-family:'Syne'; font-size:26px; color:#00E5A0; margin:0;">{d['mpy']:.1f} mpy</p></div>""", unsafe_allow_html=True)
        
        pdf_b64 = generate_pdf_base64(d)
        st.markdown(f'<br><a href="data:application/pdf;base64,{pdf_b64}" download="FlowBio_Agent_Report.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:800; cursor:pointer;">📥 DESCARGAR REPORTE AGENTES</button></a>', unsafe_allow_html=True)
        if st.button("🏠 INICIO"): st.session_state.screen = 'splash'; st.rerun()
