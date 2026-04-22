import streamlit as st
import streamlit.components.v1 as components
import json, math
import boto3
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"],[data-testid="stSidebar"],footer{display:none!important}
    .stApp{background:#060B11}
    .block-container{padding:2rem 3rem!important}
    body, p, div { font-family: 'Inter', sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    .kpi-box{background:rgba(13,21,32,0.8);border:1px solid rgba(255,255,255,0.05);
             border-radius:12px;padding:22px;border-top:4px solid #00E5A0;height:100%}
    .kpi-box.cyan{border-top-color:#22D3EE}
    .kpi-box.amber{border-top-color:#F59E0B}
    .kpi-box.red{border-top-color:#EF4444}
    .kpi-label{font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
    .kpi-value{font-size:32px;font-weight:800;color:#fff;margin:5px 0}
    .kpi-desc{font-size:10px;color:#8BA8C0;margin-top:5px;line-height:1.3}
    .stButton>button{background:#00E5A0!important;color:#060B11!important;font-weight:800!important;border-radius:8px!important;padding:15px 30px!important;width:100%}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. S3 y DATOS
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def load_dashboard_data():
    try:
        try:
            aws_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
        except:
            aws_key = st.secrets["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["AWS_SECRET_ACCESS_KEY"]
        s3 = boto3.client("s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_sec, region_name="us-east-2")
        obj = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(obj["Body"].read().decode("utf-8")), True
    except:
        return None, False

def demo_data():
    return {"Well-UKCS-Alpha": {"ahorro":12000,"mejora":18.5,"extra_bpd":92.5,"extra_mes":2775,"valor_extra":206831,"fee":13875,"eur":135150,"payback":4.2,"oil_price_usd":74.5,"visc_p":102.3,"yield_p":18.4,"quimico":"Na-CMC FlowBio","ppm":1760,"vol_pv":0.31,"bwpd":478,"lim_psi":3240,"wc_red":19.2,"skin":8.4,"temp_c":78.0,"recomendacion":"INYECTAR"}}

# ══════════════════════════════════════════════════════
# 3. PDF CORPORATIVO (FIXED)
# ══════════════════════════════════════════════════════
def generate_pdf(well, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6,11,17); pdf.rect(0,0,210,297,'F')
    pdf.set_text_color(255,255,255)
    pdf.set_font('Arial','B',18)
    pdf.cell(0,15,f"FlowBio Executive Report: {well}",0,1)
    rows_pdf = [["Barriles Extra/Día", f"{d.get('extra_bpd',0):.1f}"],["Valor Extra", f"${d.get('valor_extra',0):,}"]]
    for k,v in rows_pdf:
        pdf.cell(95,11,f" {k}",1,0,'L',True)
        pdf.cell(95,11,f" {v}",1,1,'R')
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ══════════════════════════════════════════════════════
# 4. AUTENTICACIÓN
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center'>FlowBio<span style='color:#00E5A0'>.</span></h1>", unsafe_allow_html=True)
    pwd = st.text_input("PASSWORD:", type="password")
    if st.button("SINCRONIZAR"):
        if pwd == "FlowBio2026":
            raw, ok = load_dashboard_data()
            st.session_state.all_data = (raw["dashboard_data"] if raw and "dashboard_data" in raw else raw) or demo_data()
            st.session_state.s3_ok = ok
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════
# 5. DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════════════
datos_pozos = st.session_state.all_data
pozo_sel = st.selectbox("📍 Selecciona un pozo:", list(datos_pozos.keys()))
d = datos_pozos[pozo_sel]

# KPIs
k1,k2,k3,k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-box'><p class='kpi-label'>CRUDO INCREMENTAL</p><p class='kpi-value'>+{d.get('extra_mes',0):,}</p></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-box cyan'><p class='kpi-label'>VALOR EXTRA</p><p class='kpi-value'>${d.get('valor_extra',0):,}</p></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-box amber'><p class='kpi-label'>SUCCESS FEE</p><p class='kpi-value'>${d.get('fee',0):,}</p></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-box'><p class='kpi-label'>PAYBACK</p><p class='kpi-value'>{d.get('payback',0)}</p></div>", unsafe_allow_html=True)

# Gráfica
st.subheader("Simulación EOR")
components.html(f"<div id='plot'></div><script>/* Lógica JS original */</script>", height=400)

# Descarga
st.download_button("📥 DESCARGAR PDF", data=generate_pdf(pozo_sel, d), file_name="Reporte.pdf", mime="application/pdf")
