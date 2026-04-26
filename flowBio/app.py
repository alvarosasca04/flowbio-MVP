import streamlit as st
import streamlit.components.v1 as components
import json, boto3, time
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

# Diseño CSS Original Premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    body { font-family: 'Inter', sans-serif !important; color: #E2E8F0; }
    .kpi-box { background: rgba(13,21,32,0.8); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; }
    .kpi-label { font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; }
    .kpi-value { font-size:32px; font-weight:800; color:#fff; margin:5px 0; }
    .kpi-sub { font-size:12px; color:#00E5A0; }
    .console-box { background: #0D1520; border: 1px solid rgba(0,229,160,0.3); border-radius: 8px; padding: 20px; font-family: 'DM Mono'; color: #22D3EE; }
    .diag-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .diag-key { color:#64748B; font-size:12px; }
    .diag-val { color:#fff; font-size:13px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── FUNCIONES LÓGICAS ──
def load_data():
    try:
        s3 = boto3.client('s3', region_name="us-east-2")
        resp = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(resp['Body'].read().decode('utf-8'))
    except: return None

# ── FASE 1: INICIO Y PASSWORD ──
if 'auth' not in st.session_state: st.session_state.auth = False
if 'simulated' not in st.session_state: st.session_state.simulated = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        if st.text_input("PASSWORD:", type="password") == "FlowBio2026":
            if st.button("ACCEDER"): st.session_state.auth = True; st.rerun()

# ── FASE 2: SIMULACIÓN AGENTES EORIA ──
elif st.session_state.auth and not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR SIMULACIÓN AGENTES EORIA"):
            status_box = st.empty()
            for paso in ["Ingeniero Datos...", "Agente Químico...", "Simulador PIML...", "Analista Financiero..."]:
                status_box.markdown(f"<div class='console-box'>> {paso}</div>", unsafe_allow_html=True)
                time.sleep(1)
            st.session_state.all_data = load_data()
            if st.session_state.all_data: st.session_state.simulated = True; st.rerun()

# ── FASE 3: DASHBOARD COMMAND CENTER ──
else:
    c_title, c_logout = st.columns([4, 1])
    with c_title: st.markdown("## Command Center")
    with c_logout:
        if st.button("🏠 SALIR"): st.session_state.auth = False; st.session_state.simulated = False; st.rerun()
    
    db = st.session_state.all_data["dashboard_data"]
    pozo = st.selectbox("📍 Seleccione un pozo:", sorted(list(db.keys())))
    d = db[pozo]
    
    # KPIs Cálculos
    b = float(d['ahorro'].get('barriles', 0))
    v = float(d['ahorro'].get('valor_extra', 0))
    f = float(d['ahorro'].get('fee', 0))
    p = float(d['ahorro'].get('payback', 0))
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL</p><p class="kpi-value">+{int(b):,}</p><p class="kpi-sub">bbls/mes</p></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA</p><p class="kpi-value">${v:,.0f}</p></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${f:,.0f}</p></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{p}</p><p class="kpi-sub">Meses</p></div>', unsafe_allow_html=True)

    # Gráfica y Diagnóstico
    cl, cr = st.columns([2, 1])
    with cr:
        st.markdown("<h4 style='color:#00E5A0'>⚡ Diagnóstico PIML</h4>", unsafe_allow_html=True)
        info = [("Químico", d.get('quimico','Polímero')), ("Dosificación", f"{d.get('ppm', 1500)} ppm"), 
                ("Presión Máx", f"{d.get('lim_psi', 3000)} psi")]
        for k, v in info: st.markdown(f"<div class='diag-row'><span class='diag-key'>{k}</span><span class='diag-val'>{v}</span></div>", unsafe_allow_html=True)
