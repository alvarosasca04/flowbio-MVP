import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

# Estilos Originales (Recuperados)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    body, p, div { font-family: 'Inter', -apple-system, sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label { font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; }
    .kpi-value { font-size:32px; font-weight:800; color:#fff; margin:5px 0; }
    .kpi-sub { font-size:13px; font-weight:600; color:#00E5A0; margin:0; }
    .diag-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .diag-key { color:#64748B; font-size:12px; }
    .diag-val { color:#fff; font-size:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── FUNCIONES DE NEGOCIO (PDF, KPIs, LIMPIEZA) ──
def clean_text(text):
    return str(text).replace('·','.').replace('²','2').encode('latin-1', errors='replace').decode('latin-1') if text else ""

def generate_pdf(well, kpis, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6,11,17); pdf.rect(0,0,210,297,'F')
    pdf.set_font('Arial','B',24); pdf.set_text_color(255,255,255)
    pdf.cell(0,10,clean_text('FlowBio Executive Report'),0,1,'L')
    pdf.set_font('Arial','B',16); pdf.set_text_color(0,229,160)
    pdf.cell(0,10,clean_text(f'Pozo: {well}'),0,1,'L')
    pdf.ln(10)
    pdf.set_font('Arial','B',14); pdf.set_text_color(34,211,238)
    pdf.cell(0,10,'IMPACTO FINANCIERO',0,1,'L')
    pdf.set_fill_color(13,21,32); pdf.set_text_color(255,255,255); pdf.set_font('Arial','',12)
    pdf.cell(0,10,f"Barriles Extra/Mes: {int(kpis['barriles']):,}", border=1, ln=1, fill=True)
    pdf.cell(0,10,f"Valor Extra: ${kpis['valor']:,.0f} USD", border=1, ln=1, fill=True)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ── LOGICA DE APP ──
def load_data():
    s3 = boto3.client('s3', region_name="us-east-2")
    resp = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
    return json.loads(resp['Body'].read().decode('utf-8'))

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("PASSWORD:", type="password")
    if st.button("ACCEDER") and pwd == "FlowBio2026": st.session_state.auth = True; st.rerun()
else:
    if st.button("CERRAR SESIÓN"): st.session_state.auth = False; st.rerun()
    data = load_data()
    if data and "dashboard_data" in data:
        db = data["dashboard_data"]
        pozo = st.selectbox("Seleccione Pozo:", sorted(list(db.keys())))
        d = db[pozo]
        
        # Extracción de datos del JSON real
        ahorro = d.get('ahorro', {})
        proyeccion = d.get('proyeccion', [])
        
        # KPIs
        kpis = {'barriles': ahorro.get('barriles',0), 'valor': ahorro.get('valor_extra',0), 'fee': ahorro.get('fee',0), 'pb': ahorro.get('payback',0), 'eur': ahorro.get('eur',0)}
        
        # UI Cards
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL</p><p class="kpi-value">+{int(kpis["barriles"]):,}</p><p class="kpi-sub">bbls/mes</p></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA</p><p class="kpi-value">${kpis["valor"]:,.0f}</p></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${kpis["fee"]:,.0f}</p></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{kpis["pb"]}</p></div>', unsafe_allow_html=True)

        cl, cr = st.columns([2, 1])
        with cr:
            st.markdown("<h4 style='color:#00E5A0'>⚡ Diagnóstico PIML</h4>", unsafe_allow_html=True)
            info = [("Químico", d.get('quimico','Polímero')), ("Dosificación", f"{d.get('ppm', 1500)} ppm"), ("Presión Máx", f"{d.get('lim_psi', 3000)} psi")]
            for k, v in info: st.markdown(f"<div class='diag-row'><span class='diag-key'>{k}</span><span class='diag-val'>{v}</span></div>", unsafe_allow_html=True)
            st.download_button("📥 DESCARGAR PDF", data=generate_pdf(pozo, kpis, d), file_name="Reporte.pdf")
