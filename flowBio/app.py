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
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 0px; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-desc { font-family: 'Inter'; font-size: 10px; color: #8BA8C0; margin-top: 5px; line-height: 1.2; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne' !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES DE CORE (S3 Y PDF)
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"], aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"], region_name="us-east-2")
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
    # PANTALLA DE ACCESO
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
    # DASHBOARD PRINCIPAL
    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.markdown("## Command Center")
    with c_logout:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 CERRAR SESIÓN"):
            st.session_state.auth = False  # Destruye la sesión
            st.rerun()                     # Recarga la app al inicio

    wells = list(st.session_state.all_data.keys())
    s_well = st.selectbox("Activo:", wells)
    d = st.session_state.all_data[s_well]
    
    # KPIs EXPLICADOS
    k1, k2, k3, k4 = st.columns(4)
    with k1: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">${d["ahorro"]:,}</p><p class="kpi-desc">Reducción en costos de inyección y tratamiento.</p></div>', unsafe_allow_html=True)
    with k2: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+{d["mejora"]}%</p><p class="kpi-desc">Eficiencia de desplazamiento del crudo.</p></div>', unsafe_allow_html=True)
    with k3: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${d["fee"]:,}</p><p class="kpi-desc">Valor capturado por incremental verificado.</p></div>', unsafe_allow_html=True)
    with k4: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{d["payback"]} Meses</p><p class="kpi-desc">Tiempo de retorno de la inversión tecnológica.</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([2.3, 1.7])
    
    with cl:
        # Gráfica segura
        script_parts = [
            "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>",
            "<div id='plot' style='height:400px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05);'></div>",
            "<script>",
            "var x = Array.from({length:40}, (_,i)=>i);",
            "var y1 = x.map(i => 350 * Math.exp(-0.06*i));",
            f"var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (350 * {d['mejora']} / 100 * Math.exp(-0.015*(i-5))));",
            "var t1 = {x:x, y:y1, name:'Base', line:{color:'#EF4444', dash:'dot'}};",
            "var t2 = {x:x, y:y2, name:'FlowBio', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'};",
            "var lay = {paper_bgcolor:'transparent', plot_bgcolor:'transparent', font:{color:'#64748B'}, margin:{t:30, b:40, l:50, r:20}};",
            "Plotly.newPlot('plot', [t1, t2], lay);",
            "</script>"
        ]
        components.html("".join(script_parts), height=420)
        
    with cr:
        # Insights Explicados
        html_parts = [
            "<div style='background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:415px;'>",
            "<p style='color:#00E5A0; font-weight:800; font-size:12px;'>🧠 ENGINEERING INSIGHTS</p>",
            f"<p style='font-family:\"DM Mono\"; font-size:14px; color:#22D3EE; margin-bottom:2px;'>PV: {d['visc_p']} cP</p>",
            "<p style='font-size:11px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Evita la canalización del agua (fingering).</p>",
            f"<p style='font-family:\"DM Mono\"; font-size:14px; color:#22D3EE; margin-bottom:2px;'>YP: {d['yield_p']} lb/ft2</p>",
            "<p style='font-size:11px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Garantiza estabilidad bajo presión de fondo.</p>",
            "<hr style='opacity:0.1; margin:15px 0;'>",
            f"<p style='color:#64748B; font-size:10px; font-weight:600;'>INCREMENTAL TOTAL (EUR):</p>",
            f"<p style='color:#00E5A0; font-size:32px; font-weight:800; margin:0;'>{d['eur']:,} <span style='font-size:14px; color:#64748B;'>bbls</span></p>",
            "</div>"
        ]
        st.markdown("".join(html_parts), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📥 DESCARGAR REPORTE PDF", data=generate_corporate_pdf(s_well, d), file_name="Reporte_FlowBio.pdf", mime="application/pdf")
