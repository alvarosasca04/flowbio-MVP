import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    body, p, div { font-family: 'Inter', -apple-system, sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    .kpi-box { background: rgba(13,21,32,0.8); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; margin-bottom:0px; }
    .kpi-value { font-size:32px; font-weight:800; color:#fff; margin:5px 0; }
    .kpi-sub   { font-size:13px; font-weight:600; color:#00E5A0; margin:0; }
    .kpi-desc  { font-size:10px; color:#8BA8C0; margin-top:5px; line-height:1.2; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne', font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0,229,160,0.4); }
    .console-box { background: #0D1520; border: 1px solid rgba(0,229,160,0.3); border-radius: 8px; padding: 20px; font-family: 'DM Mono', monospace; color: #22D3EE; }
    .diag-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .diag-key { color:#64748B; font-size:12px; }
    .diag-val { color:#fff; font-size:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

def load_data_from_s3():
    try:
        aws_key = st.secrets.get("aws", {}).get("AWS_ACCESS_KEY_ID", st.secrets.get("AWS_ACCESS_KEY_ID"))
        aws_sec = st.secrets.get("aws", {}).get("AWS_SECRET_ACCESS_KEY", st.secrets.get("AWS_SECRET_ACCESS_KEY"))
        s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_sec, region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error AWS S3: {e}"); return None

# ── LECTURA ESTRICTA DE LOS DATOS REALES (CON PROTECCIÓN) ──
def calcular_kpis(ahorro):
    # ESCUDO PROTECTOR: Evita que el programa crashee si los datos en S3 son de una versión antigua
    if not isinstance(ahorro, dict):
        ahorro = {}
        
    return {
        'eur_val': round(float(ahorro.get('eur', 0)), 0),
        'barriles_extra_mes': round(float(ahorro.get('barriles', 0)), 0),
        'valor_extra': round(float(ahorro.get('valor_extra', 0)), 0),
        'success_fee': round(float(ahorro.get('fee', 0)), 0),
        'payback_val': round(float(ahorro.get('payback', 0)), 1)
    }

if 'auth' not in st.session_state: st.session_state.auth = False
if 'simulated' not in st.session_state: st.session_state.simulated = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("ACCEDER AL SISTEMA") and pwd == "FlowBio2026": 
            st.session_state.auth = True; st.rerun()

elif st.session_state.auth and not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR LECTURA DE S3"):
            status_box = st.empty(); progress_bar = st.progress(0)
            for i, p in enumerate(["Conectando a S3...", "Procesando JSON...", "Listando pozos reales..."]):
                status_box.markdown(f"<div class='console-box'>> {p}</div>", unsafe_allow_html=True)
                progress_bar.progress((i+1)*33); time.sleep(0.5)
            st.session_state.all_data = load_data_from_s3()
            if st.session_state.all_data: st.session_state.simulated = True; st.rerun()

elif st.session_state.auth and st.session_state.simulated:
    c_title, c_logout = st.columns([4, 1])
    with c_title: st.markdown("## Command Center")
    with c_logout:
        if st.button("🏠 CERRAR SESIÓN"): st.session_state.auth = False; st.session_state.simulated = False; st.rerun()

    datos_pozos = st.session_state.all_data
    if "dashboard_data" in datos_pozos: datos_pozos = datos_pozos["dashboard_data"]
    
    lista_pozos = list(datos_pozos.keys())
    if not lista_pozos: st.error("⚠️ Carpeta vacía en S3."); st.stop()

    pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis:", lista_pozos)
    d = datos_pozos[pozo_seleccionado]

    proyeccion = d.get('proyeccion', [])
    kpis = calcular_kpis(d.get('ahorro', {}))

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.
