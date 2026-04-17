import streamlit as st
import json
import boto3
import math
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y ESTILOS PREMIUM
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; border-top: 4px solid #00E5A0; }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-desc { font-size: 9px; color: #64748B; margin-top: 5px; line-height: 1.2; }
    
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne' !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
    .stTextInput > div > div > input { background-color: #0D1520 !important; color: white !important; border: 1px solid #00E5A0 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES DE CORE (S3 Y PDF)
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                          aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"], region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

def generate_corporate_pdf(well, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, f'FlowBio Executive Report: {well}', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
    pdf.ln(10)
    pdf.set_fill_color(13, 21, 32)
    for k, v in [["PV", f"{d.get('visc_p')} cP"], ["YP", f"{d.get('yield_p')} lb/ft2"], ["EUR", f"{d.get('eur'):,} bbls"], ["PAYBACK", f"{d.get('payback')} Meses"]]:
        pdf.cell(95, 12, f" {k}", 1, 0, 'L', True)
        pdf.cell(95, 12, f" {v}", 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# 3. INTERFAZ Y LÓGICA
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        if st.text_input("PASSWORD:", type="password") == "FlowBio2026":
            if st.button("SINCRONIZAR Y ACCEDER"):
                st.session_state.all_data = load_data_from_s3()
                st.session_state.auth = True
                st.rerun()
else:
    st.markdown("## Command Center")
    wells = list(st.session_state.all_data.keys())
    s_well = st.selectbox("Activo:", wells)
    d = st.session_state.all_data[s_well]
    
    # KPIs Explicados
    k1, k2, k3, k4 = st.columns(4)
    kpi_data = [("AHORRO", "ahorro", "$", "Reducción en costos operativos."), ("MEJORA", "mejora", "+", "Eficiencia de barrido areal."), ("FEE", "fee", "$", "Success fee por incremental."), ("PAYBACK", "payback", "", "Meses para ROI.")]
    for i, (label, key, pref, desc) in enumerate(kpi_data):
        val = f"{pref}{d[key]:,}" if key != "mejora" and key != "payback" else f"{pref}{d[key]}{'%' if key=='mejora' else ' Meses'}"
        [k1, k2, k3, k4][i].markdown(f'<div class="kpi-box"><p class="kpi-label">{label}</p><p class="kpi-value">{val}</p><p class="kpi-desc">{desc}</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([2.3, 1.7])
    with cl:
        st.markdown("<div id='plot' style='height:400px; background:#0D1520; border-radius:12px;'></div>", unsafe_allow_html=True)
        components.html(f"""<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <script>var x=Array.from({{length:40}},(_,i)=>i); var y1=x.map(i=>350*Math.exp(-0.06*i)); var y2=x.map(i=>i<5?y1[i]:y1[i]+(350*{d['mejora']}/100*Math.exp(-0.015*(i-5))));
        Plotly.newPlot('plot', [{{x:x,y:y1,name:'Base',line:{{color:'#EF4444',dash:'dot'}}}},{{x:x,y:y2,name:'FlowBio',line:{{color:'#00E5A0',width:4}},fill:'tonexty'}}], {{paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}}});</script>""", height=420)
    with cr:
        st.markdown(f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3);">
            <p style="color:#00E5A0; font-weight:800; font-size:12px;">🧠 ENGINEERING INSIGHTS</p>
            <p style="font-family: 'DM Mono'; font-size: 14px; color: #22D3EE;">PV: {d['visc_p']} cP | YP: {d['yield_p']} lb/ft2</p>
            <p style="color:#64748B; font-size:10px;">INCREMENTAL PROYECTADO: {d['eur']:,} bbls</p>
            </div>""", unsafe_allow_html=True)
        st.download_button("📥 DESCARGAR REPORTE PDF", data=generate_corporate_pdf(s_well, d), file_name="Reporte.pdf", mime="application/pdf")
