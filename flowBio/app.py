import streamlit as st
import streamlit.components.v1 as components
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

if 'screen' not in st.session_state: st.session_state.screen = 'splash'

# ══════════════════════════════════════════════════════
# 2. BASE DE DATOS (Simulación de Agentes IA)
# ══════════════════════════════════════════════════════
AGENT_DATA = {
    "Pozo 15/17-1 (Central North Sea)": {"ahorro": 394000, "mejora": 18.2, "fee": 4500, "co2": 112.0, "m_ratio": 0.25, "n": 0.569, "eur": 85000, "label": "PRIORIDAD ALTA - CRÍTICO", "bpd": 420},
    "Pozo 15/17-8b (Galley)": {"ahorro": 520000, "mejora": 22.1, "fee": 6500, "co2": 145.0, "m_ratio": 0.18, "n": 0.569, "eur": 115000, "label": "PRIORIDAD MÁXIMA", "bpd": 550},
    # Agrega aquí los demás pozos si los necesitas
}

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF MEJORADO
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17); self.rect(0, 0, 210, 297, 'F') 
        self.set_xy(10, 15); self.set_font('Arial', 'B', 24); self.set_text_color(0, 229, 160)
        self.cell(0, 10, 'FLOWBIO AGENT REPORT', 0, 1, 'L')
        self.set_draw_color(0, 229, 160); self.line(10, 27, 200, 27)

def generate_pdf_base64(d, name):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.ln(15)
    pdf.set_font('Arial', 'B', 16); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f"Analisis de Activo: {name}", 0, 1, 'L')
    
    # Sección Económica
    pdf.ln(10); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 10, "1. PROYECCION ECONOMICA", 0, 1, 'L')
    pdf.set_font('Arial', '', 12); pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 8, f"- Ahorro Estimado OPEX: ${d['ahorro']:,} USD/ano", 0, 1, 'L')
    pdf.cell(0, 8, f"- Fee de Servicio FlowBio: ${d['fee']:,} USD/mes", 0, 1, 'L')
    pdf.cell(0, 8, f"- Impacto ESG (CO2 evitado): {d['co2']} toneladas/ano", 0, 1, 'L')
    
    # Sección Técnica
    pdf.ln(10); pdf.set_text_color(0, 229, 160); pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "2. PARAMETROS TECNICOS (PIML)", 0, 1, 'L')
    pdf.set_font('Arial', '', 12); pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 8, f"- Mejora en Eficiencia de Barrido: {d['mejora']}%", 0, 1, 'L')
    pdf.cell(0, 8, f"- Ratio de Movilidad (M): {d['m_ratio']}", 0, 1, 'L')
    pdf.cell(0, 8, f"- Indice de Comportamiento (n): {d['n']}", 0, 1, 'L')
    pdf.cell(0, 8, f"- Recuperacion Adicional (EUR): {d['eur']:,} barriles", 0, 1, 'L')
    
    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 4. DASHBOARD
# ══════════════════════════════════════════════════════
if st.session_state.screen == 'splash':
    st.markdown("<br><br><br><h1 style='text-align:center; font-family:Syne; font-size:100px; color:white;'>FlowBio.</h1>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    if col_btn.button("ACCEDER AL TERMINAL"):
        st.session_state.screen = 'dash'; st.rerun()

elif st.session_state.screen == 'dash':
    selected_well = st.selectbox("Seleccione el pozo analizado:", list(AGENT_DATA.keys()))
    d = AGENT_DATA[selected_well]
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO AÑO</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box"><p class="kpi-label">MEJORA</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box"><p class="kpi-label">FEE MENSUAL</p><p class="kpi-value">${d["fee"]:,}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box"><p class="kpi-label">CO2 EVITADO</p><p class="kpi-value">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    # Gráfica e Insights (simplificado para el ejemplo)
    st.markdown("---")
    
    # BOTONES CENTRADOS
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        pdf_b64 = generate_pdf_base64(d, selected_well)
        st.markdown(f'<a href="data:application/pdf;base64,{pdf_b64}" download="Reporte_{selected_well}.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:800; cursor:pointer;">📥 DESCARGAR REPORTE COMPLETO</button></a>', unsafe_allow_html=True)
        st.write("")
        if st.button("🏠 VOLVER AL INICIO"):
            st.session_state.screen = 'splash'; st.rerun()
