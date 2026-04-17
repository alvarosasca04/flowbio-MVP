import streamlit as st
import json
import boto3
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. ESTILOS Y ESTRUCTURA (CENTRADO Y DARK MODE)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio OS", layout="wide")
st.markdown("""
<style>
    .stApp { background: #060B11; color: white; }
    .stButton > button { background: #00E5A0; color: #060B11; font-weight: 800; border-radius: 8px; width: 100%; }
    .kpi-box { background: #0D1520; padding: 20px; border-radius: 10px; border-top: 4px solid #00E5A0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. GENERADOR DE PDF BLINDADO (SIN DEPENDENCIAS EXTERNAS)
# ══════════════════════════════════════════════════════
def create_pdf(name, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Reporte FlowBio: {name}', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Viscosidad: {data.get("visc_p")} cP', 0, 1)
    pdf.cell(0, 10, f'Incremental: {data.get("eur")} bbls', 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# 3. INTERFAZ (SPLASH Y DASHBOARD)
# ══════════════════════════════════════════════════════
if 'screen' not in st.session_state: st.session_state.screen = 'splash'

if st.session_state.screen == 'splash':
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.title("FlowBio.")
        if st.button("SINCRONIZAR CON S3"):
            # Aquí iría tu lógica de carga de S3
            st.session_state.screen = 'dash'
            st.rerun()

elif st.session_state.screen == 'dash':
    st.header("Command Center")
    # Ejemplo de datos estables
    d = {"ahorro": 1431900, "mejora": 79.55, "fee": 5966, "co2": 202.9, "visc_p": 95.49, "yield_p": 28.1, "payback": 1.0, "eur": 517075}
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box">AHORRO: ${d["ahorro"]:,}</div>', unsafe_allow_html=True)
    
    if st.download_button("DESCARGAR PDF", data=create_pdf("Pozo-0", d), file_name="reporte.pdf"):
        st.success("Reporte generado")
