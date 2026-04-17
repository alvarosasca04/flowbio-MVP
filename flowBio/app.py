import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import math
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y ESTILOS
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    
    /* Nuevos estilos para las explicaciones */
    .kpi-desc { font-family: 'Inter'; font-size: 10px; color: #8BA8C0; margin-top: 5px; line-height: 1.3; }
    .insight-desc { font-family: 'Inter'; font-size: 11px; color: #8BA8C0; margin-bottom: 12px; line-height: 1.4; }
    
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne' !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
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
    except Exception as e:
        st.error("Error al cargar datos. Verifica credenciales.")
        return None

def generate_corporate_pdf(well, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, 'FlowBio Executive Report: ' + str(well), 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Fecha: ' + datetime.now().strftime("%Y-%m-%d"), 0, 1)
    pdf.ln(10)
    pdf.set_fill_color(13, 21, 32)
    eur_str = f"{d.get('eur'):,}"
    for k, v in [["PV", str(d.get('visc_p')) + " cP"], ["YP", str(d.get('yield_p')) + " lb/ft2"], ["EUR", eur_str + " bbls"], ["PAYBACK", str(d.get('payback')) + " Meses"]]:
        pdf.cell(95, 12, " " + k, 1, 0, 'L', True)
        pdf.cell(95, 12, " " + v, 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# 3. INTERFAZ DE NAVEGACIÓN
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("SINCRONIZAR"):
            if pwd == "FlowBio2026":
                st.session_state.all_data = load_data_from_s3()
                if st.session_state.all_data:
                    st.session_state.auth = True
                    st.rerun()
else:
    st.markdown("## Command Center")
    wells = list(st.session_state.all_data.keys())
    s_well = st.selectbox("Activo:", wells)
    d = st.session_state.all_data[s_well]
    
    # KPIs CON EXPLICACIONES
    k1, k2, k3, k4 = st.columns(4)
    with k1: 
        st.markdown('<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">$' + f"{d['ahorro']:,}" + '</p><p class="kpi-desc">Reducción en costos de inyección y tratamiento.</p></div>', unsafe_allow_html=True)
    with k2: 
        st.markdown('<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+' + str(d['mejora']) + '%</p><p class="kpi-desc">Eficiencia de desplazamiento del crudo.</p></div>', unsafe_allow_html=True)
    with k3: 
        st.markdown('<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">$' + f"{d['fee']:,}" + '</p><p class="kpi-desc">Valor capturado por incremental verificado.</p></div>', unsafe_allow_html=True)
    with k4: 
        st.markdown('<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">PAYBACK</p><p class="kpi-value">' + str(d['payback']) + ' Meses</p><p class="kpi-desc">Tiempo de retorno de la inversión tecnológica.</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([2.3, 1.7])
    
    with cl:
        mejora_val = str(d['mejora'])
        chart_html = (
            "<div id='plot' style='height:460px; background:#0D1520; border-radius:12px; width:100%; border: 1px solid rgba(255, 255, 255, 0.05);'></div>"
            "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>"
            "<script>"
            "var x = Array.from({length:40}, (_,i)=>i);"
            "var y1 = x.map(i => 350 * Math.exp(-0.06*i));"
            "var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (350 * " + mejora_val + " / 100 * Math.exp(-0.015*(i-5))));"
            "var trace1 = {x:x, y:y1, name:'Base', line:{color:'#EF4444', dash:'dot'}};"
            "var trace2 = {x:x, y:y2, name:'FlowBio AI', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'};"
            "var layout = {paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{color:'#64748B'}, margin:{t:30, b:40, l:50, r:20}};"
            "Plotly.newPlot('plot', [trace1, trace2], layout);"
            "</script>"
        )
        components.html(chart_html, height=480)
        
    with cr:
        # INSIGHTS TÉCNICOS EXPLICADOS
        eur_val = f"{d['eur']:,}"
        insight_html = (
            "<div style='background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:460px;'>"
            "<p style='color:#00E5A0; font-weight:800; font-size:12px; margin-bottom:15px;'>🧠 ENGINEERING INSIGHTS</p>"
            
            "<p style='font-family: \"DM Mono\"; font-size: 13px; color: #22D3EE; margin-bottom: 2px;'>VISCOSIDAD PLÁSTICA (PV): " + str(d['visc_p']) + " cP</p>"
            "<p class='insight-desc'>Garantiza un barrido uniforme empujando el crudo sin crear canalización de agua (fingering).</p>"
            
            "<p style='font-family: \"DM Mono\"; font-size: 13px; color: #22D3EE; margin-bottom: 2px;'>YIELD POINT (YP): " + str(d['yield_p']) + " lb/ft2</p>"
            "<p class='insight-desc'>Indica alta estabilidad estructural. El fluido no se degradará bajo las altas presiones de fondo.</p>"
            
            "<hr style='opacity:0.1; margin:20px 0;'>"
            
            "<p style='color:#64748B; font-size:10px; margin-bottom:5px;'>INCREMENTAL TOTAL (EUR):</p>"
            "<p style='color:#00E5
