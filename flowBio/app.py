import streamlit as st
import streamlit.components.v1 as components
import json, math
import boto3
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="FlowBio Subsurface OS",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"],[data-testid="stSidebar"],footer{display:none!important}
    .stApp{background:#060B11}
    
    /* Aplicación de fuentes con respaldo */
    body, p, div { font-family: 'Inter', sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    
    .block-container{padding:2rem 3rem!important}
    .kpi-box{background:rgba(13,21,32,0.8);border:1px solid rgba(255,255,255,0.05);
             border-radius:12px;padding:22px;border-top:4px solid #00E5A0;height:100%}
    .kpi-box.cyan{border-top-color:#22D3EE}
    .kpi-box.amber{border-top-color:#F59E0B}
    .kpi-box.red{border-top-color:#EF4444}
    .kpi-label{font-size:11px;color:#64748B;font-weight:600;
               text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
    .kpi-value{font-size:32px;font-weight:800;color:#fff;margin:5px 0}
    .kpi-desc{font-size:10px;color:#8BA8C0;margin-top:5px;line-height:1.3}
    .stButton>button{background:#00E5A0!important;color:#060B11!important;
                     font-weight:800!important;
                     border-radius:8px!important;padding:15px 30px!important;width:100%}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 2. S3 — carga dashboard_data.json
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

        s3  = boto3.client("s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_sec,
            region_name="us-east-2")
        obj = s3.get_object(
            Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an",
            Key="agentes/dashboard_data.json")
        return json.loads(obj["Body"].read().decode("utf-8")), True
    except Exception as e:
        st.warning(f"S3: {e} — usando datos demo")
        return None, False

def demo_data():
    return {
        "Well-UKCS-Alpha": {
            "ahorro":12000,"mejora":18.5,"extra_bpd":92.5,"extra_mes":2775,
            "valor_extra":206831,"fee":13875,"eur":135150,"payback":4.2,
            "oil_price_usd":74.5,"visc_p":102.3,"yield_p":18.4,
            "quimico":"Na-CMC FlowBio","ppm":1760,"vol_pv":0.31,"bwpd":478,
            "lim_psi":3240,"wc_red":19.2,"skin":8.4,"temp_c":78.0,
            "recomendacion":"INYECTAR",
        },
        "Well-UKCS-Beta": {
            "ahorro":9500,"mejora":14.2,"extra_bpd":71.0,"extra_mes":2130,
            "valor_extra":158685,"fee":10650,"eur":103880,"payback":5.8,
            "oil_price_usd":74.5,"visc_p":88.7,"yield_p":14.1,
            "quimico":"Goma Xantana","ppm":1320,"vol_pv":0.24,"bwpd":421,
            "lim_psi":2980,"wc_red":15.7,"skin":5.1,"temp_c":62.0,
            "recomendacion":"INYECTAR",
        },
        "Well-UKCS-Gamma": {
            "ahorro":4200,"mejora":6.8,"extra_bpd":34.0,"extra_mes":1020,
            "valor_extra":75990,"fee":5100,"eur":49640,"payback":9.1,
            "oil_price_usd":74.5,"visc_p":65.4,"yield_p":9.8,
            "quimico":"Na-CMC FlowBio","ppm":1540,"vol_pv":0.19,"bwpd":391,
            "lim_psi":2750,"wc_red":12.3,"skin":3.2,"temp_c":91.0,
            "recomendacion":"MONITOREAR",
        },
    }


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
    pdf.set_font('Arial','',11)
    pdf.set_text_color(0,229,160)
    pdf.cell(0,8,f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | PIML v0.3",0,1)
    pdf.ln(6)
    pdf.set_fill_color(13,21,32); pdf.set_text_color(255,255,255)
    
    rows_pdf = [
        ["Barriles Extra/Día",  f"{d.get('extra_bpd',0):.1f} bbl/día"],
        ["Barriles Extra/Mes",  f"{d.get('extra_mes',0):,} bbl/mes"],
        ["Valor Extra Generado",f"${d.get('valor_extra',0):,} USD/mes"],
        ["Success Fee Mensual", f"${d.get('fee',0):,} USD/mes"],
        ["Payback",             f"{d.get('payback',0)} meses"],
        ["PV (Visc. Plástica)", f"{d.get('visc_p',0)} mPa·s"],
        ["YP (Yield Point)",    f"{d.get('yield_p',0)} lb/ft²"],
        ["EUR Acumulado",       f"{d.get('eur',0):,} bbls"],
        ["Químico EOR",         str(d.get('quimico','—'))],
        ["Concentración",       f"{d.get('ppm',0)} ppm"],
        ["Factor Skin",         f"{d.get('skin',0):.2f}"],
        ["Recomendación",       str(d.get('recomendacion','—'))],
    ]
    for k,v in rows_pdf:
        pdf.cell(95,11,f" {k}",1,0,'L',True)
        pdf.cell(95,11,f" {v}",1,1,'R')
    pdf.ln(8)
    pdf.set_text_color(100,116,139)
    pdf.set_font('Arial','I',9)
    pdf.cell(0,8,"FlowBio Intelligence · PIML v0.3 · TRL 4 · Orizaba, Veracruz, MX",0,1,'C')
    # FIX: Manejo de errores de codificación
    return pdf.output(dest='S').encode('latin-1', errors='replace')


# ══════════════════════════════════════════════════════
# 4. AUTENTICACIÓN Y MAIN
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("""
    <div style='text-align:center;margin-top:18vh'>
      <h1 style='color:white;letter-spacing:-3px'>FlowBio<span style='color:#00E5A0'>.</span></h1>
    </div>""", unsafe_allow_html=True)
    _, c, _ = st.columns([1,0.7,1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("SINCRONIZAR"):
            if pwd == "FlowBio2026":
                raw, ok = load_dashboard_data()
                if raw and "dashboard_data" in raw: raw = raw["dashboard_data"]
                st.session_state.all_data = raw or demo_data()
                st.session_state.s3_ok    = ok
                st.session_state.auth     = True
                st.rerun()
    st.stop()

datos_pozos = st.session_state.all_data
pozo_sel = st.selectbox("📍 Selecciona un pozo:", list(datos_pozos.keys()))
d = datos_pozos[pozo_sel]

# Renderizado de KPIs y UI simplificado para brevedad...
st.write(f"Dashboard activo para: {pozo_sel}")
# (Resto de tu lógica de renderizado permanece igual)
