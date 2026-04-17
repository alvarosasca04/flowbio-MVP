import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import math
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; }

    /* Centrado del Botón Splash */
    [data-testid="stVerticalBlock"] > div:has(button) {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px 45px !important;
        border: none !important; transition: 0.3s all ease;
        text-transform: uppercase; letter-spacing: 2px;
    }
    .stButton > button:hover {
        transform: scale(1.05); box-shadow: 0 0 40px rgba(0, 229, 160, 0.4);
    }

    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }

    div[data-baseweb="select"] > div {
        background-color: #0D1520; border: 1px solid #00E5A0; color: white; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. GENERADOR DE REPORTE PDF (ESTRUCTURA BLINDADA)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17) # Fondo oscuro corporativo
        self.rect(0, 0, 210, 297, 'F')
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'FlowBio.', 0, 1, 'L')
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, 'SUBSURFACE INTELLIGENCE OS | REPORTE EJECUTIVO', 0, 1, 'L')
        self.ln(10)

def create_pdf_report(well_name, data):
    pdf = FlowBioReport()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'Activo: {well_name}', 0, 1)
    pdf.ln(5)

    # Tabla Técnica de KPIs
    pdf.set_fill_color(13, 21, 32)
    pdf.set_text_color(0, 229, 160)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(190, 12, ' RESULTADOS DE INGENIERIA (5-AGENT CONSENSUS)', 0, 1, 'L', True)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(255, 255, 255)
    
    stats = [
        ["VISCOSIDAD PLASTICA (PV)", f"{data.get('visc_p')} cP"],
        ["YIELD POINT (YP)", f"{data.get('yield_p')} lb/100ft2"],
        ["AHORRO OPEX PROYECTADO", f"${data.get('ahorro'):,}"],
        ["MEJORA DE BARRIDO", f"+{data.get('mejora')}%"],
        ["INCREMENTAL TOTAL (EUR)", f"{data.get('eur'):,} bbls"],
        ["PAYBACK INVERSION", f"{data.get('payback')} Meses"]
    ]

    for item in stats:
        pdf.cell(100, 12, f" {item[0]}", 1, 0, 'L')
        pdf.cell(90, 12, f" {item[1]}", 1, 1, 'R')

    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'INTERPRETACION TECNICA:', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(139, 168, 192)
    
    txt = (f"La simulacion PIML para el pozo {well_name} confirma que el uso de Na-CMC mantiene "
           f"una viscosidad de {data.get('visc_p')} cP, evitando la canalización del agua. "
           f"Con un incremento de {data.get('eur'):,} barriles, el retorno de inversión es de {data.get('payback')} meses.")
    pdf.multi_cell(0, 8, txt)
    
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE NAVEGACIÓN Y DASHBOARD
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=1)
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                          aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"], region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        response = s3.get_object(Bucket=bucket, Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

if 'screen' not in st.session_state: st.session_state.screen = 'splash'

if st.session_state.screen == 'splash':
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 65vh; text-align: center;">
            <h1 style='font-family:Syne; font-size:120px; color:white; margin-bottom:0;'>FlowBio<span style='color:#00E5A0'>.</span></h1>
            <p style='color:#64748B; letter-spacing:10px; font-size:14px; margin-bottom:40px;'>AGENT INTELLIGENCE OS</p>
        </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("SINCRONIZAR CON NUBE S3"):
            data = load_data_from_s3()
            if data:
                st.session_state.all_data = data
                st.session_state.screen = 'dash'
                st.rerun()

elif st.session_state.screen == 'dash':
    st.markdown("<div style='padding: 2rem 3rem;'><h2 style='font-family:Syne; color:white; margin-bottom:20px;'>Command Center</h2>", unsafe_allow_html=True)
    wells = list(st.session_state.all_data.keys())
    selected_well = st.selectbox("Activo analizado:", wells)
    d = st.session_state.all_data[selected_well]
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${d["fee"]:,}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">CO2 EVITADO</p><p class="kpi-value">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([2.3, 1.7])
    with cl:
        # Gráfica interactiva de declinación
        chart_html = f"""<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script><div id="plot" style="height:500px; border-radius:12px; background:#0D1520; margin-top:20px; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i); var base = 350; var mej = {d['mejora']} / 100;
            var y1 = x.map(i => base * Math.exp(-0.06*i)); var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mej * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [{{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot'}}, name:'Base (HPAM)'}},{{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio AI'}}], 
            {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:40, b:40, l:50, r:20}} }});
        </script>"""
        components.html(chart_html, height=530)
        
    with cr:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        # Insights TÉCNICOS Premium
        pv_val = d.get('visc_p', '95.49')
        yp_val = d.get('yield_p', '28.1')
        eur_val = f"{d.get('eur', 0):,}"

        insight_html = f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:450px; overflow-y:auto; margin-bottom:20px;">
<p style="color:#00E5A0; font-weight:800; font-size:12px; margin-bottom:15px;">🧠 ENGINEERING INSIGHTS</p>
<p style="font-family: 'DM Mono'; font-size: 14px; color: #22D3EE;">VISCOSIDAD (PV): {pv_val} cP</p>
<p style="font-family: 'DM Mono'; font-size: 14px; color: #22D3EE;">YIELD POINT (YP): {yp_val} lb/100ft2</p>
<hr style="opacity:0.1">
<p style="color:#64748B; font-size:10px; text-transform: uppercase;">INCREMENTAL PROYECTADO:</p>
<p style="color:#00E5A0; font-size:38px; font-weight:800; margin:0;">{eur_val} <span style="font-size:14px; color:#64748B;">bbls</span></p>
</div>"""
        st.write(insight_html, unsafe_allow_html=True)
        
        # Botón de Descarga Blindado
        pdf_data = create_pdf_report(selected_well, d)
        st.download_button("📥 DESCARGAR REPORTE PDF CORPORATIVO", data=pdf_data, file_name=f"FlowBio_{selected_well}.pdf", mime="application/pdf")

    st.markdown("</div>", unsafe_allow_html=True)
