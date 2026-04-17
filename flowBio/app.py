import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import math
import plotly.graph_objects as go
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
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. GENERADOR DE REPORTE PDF CORPORATIVO
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17)
        self.rect(0, 0, 210, 297, 'F')
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'FlowBio.', 0, 1, 'L')
        self.ln(5)

def create_pdf_report(well_name, data):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'Reporte de Optimización: {well_name}', 0, 1)
    
    # Gráfica corregida
    base = 350
    mej = data['mejora'] / 100
    x = list(range(40))
    y1 = [base * math.exp(-0.06*i) for i in x]
    y2 = [(y1[i] + (base * mej * math.exp(-0.015*(i-5)))) if i>=5 else y1[i] for i in x]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y1, line=dict(color='#EF4444', dash='dot'), name='Base (HPAM)'))
    fig.add_trace(go.Scatter(x=x, y=y2, line=dict(color='#00E5A0', width=4), fill='tonexty', fillcolor='rgba(0,229,160,0.1)', name='FlowBio AI'))
    
    # CORRECCIÓN DE SINTAXIS (l=10, r=10)
    fig.update_layout(paper_bgcolor='#060B11', plot_bgcolor='#0D1520', font=dict(color='#64748B'), margin=dict(t=10, b=10, l=10, r=10))
    
    img_bytes = fig.to_image(format="png", width=800, height=400, scale=2)
    pdf.image(BytesIO(img_bytes), x=15, y=pdf.get_y(), w=180)
    
    return pdf.output(dest='S')

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE NAVEGACIÓN
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=1)
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                          aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"], region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

if 'screen' not in st.session_state: st.session_state.screen = 'splash'

if st.session_state.screen == 'splash':
    st.markdown("<br><br><br><h1 style='text-align:center; font-family:Syne; font-size:120px; color:white;'>FlowBio<span style='color:#00E5A0'>.</span></h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    if c2.button("SINCROZINAR CON NUBE S3"):
        data = load_data_from_s3()
        if data:
            st.session_state.all_data = data
            st.session_state.screen = 'dash'
            st.rerun()

elif st.session_state.screen == 'dash':
    wells = list(st.session_state.all_data.keys())
    selected_well = st.selectbox("Pozo:", wells)
    d = st.session_state.all_data[selected_well]
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    
    # Insights y Reporte
    cl, cr = st.columns([2.3, 1.7])
    with cr:
        st.write(f"### 🧠 Engineering Insights", unsafe_allow_html=True)
        st.info(f"**PV:** {d.get('visc_p')} cP | **YP:** {d.get('yield_p')} lb/100ft²")
        
        pdf_data = create_pdf_report(selected_well, d)
        st.download_button("📥 DESCARGAR REPORTE CORPORATIVO", data=pdf_data, file_name="Reporte.pdf", mime="application/pdf")
