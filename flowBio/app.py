import streamlit as st
import streamlit.components.v1 as components
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM FLOWBIO (CSS)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; max-width: 100vw !important; }
    
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; transition: 0.3s;
    }
    .kpi-box:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.4); }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 38px; font-weight: 800; color: #fff; margin: 5px 0; }
    
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px 30px !important;
        width: 100%; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton > button:hover { box-shadow: 0 0 25px rgba(0,229,160,0.4); transform: translateY(-2px); }
    
    /* Estilizar el buscador para que se vea premium */
    div[data-baseweb="select"] > div {
        background-color: #0D1520; border: 1px solid #00E5A0; color: white; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

if 'screen' not in st.session_state: st.session_state.screen = 'splash'

# ══════════════════════════════════════════════════════
# 2. BASE DE DATOS JUPYTER (10 POZOS SIMULADOS)
# ══════════════════════════════════════════════════════
AGENT_DATA = {
    "Pozo 15/17-1 (Central North Sea)": {"ahorro": 394000.0, "mejora": 18.2, "fee": 4500.0, "co2": 112.0, "m_ratio": 0.25, "n": 0.569, "eur": 85000.0, "k": 151.4, "bpd": 420, "label": "PRIORIDAD ALTA - CRÍTICO"},
    "Pozo 15/17-2 (Flanco Sur)": {"ahorro": 125000.0, "mejora": 12.1, "fee": 1800.0, "co2": 65.0, "m_ratio": 0.32, "n": 0.569, "eur": 32000.0, "k": 151.4, "bpd": 280, "label": "PRIORIDAD MEDIA - ESTABLE"},
    "Pozo 15/17-3 (Inyector Norte)": {"ahorro": 280000.0, "mejora": 15.8, "fee": 3200.0, "co2": 95.0, "m_ratio": 0.28, "n": 0.569, "eur": 68000.0, "k": 151.4, "bpd": 350, "label": "PRIORIDAD ALTA - ESTABLE"},
    "Pozo 15/17-4 (Piper Alpha Area)": {"ahorro": 450000.0, "mejora": 19.5, "fee": 5200.0, "co2": 130.0, "m_ratio": 0.22, "n": 0.569, "eur": 95000.0, "k": 151.4, "bpd": 500, "label": "PRIORIDAD MÁXIMA - DECLINACIÓN"},
    "Pozo 15/17-5 (Tartan Field)": {"ahorro": 195000.0, "mejora": 14.2, "fee": 2500.0, "co2": 82.0, "m_ratio": 0.29, "n": 0.569, "eur": 45000.0, "k": 151.4, "bpd": 310, "label": "PRIORIDAD MEDIA - ESTABLE"},
    "Pozo 15/17-6a (Claymore)": {"ahorro": 310000.0, "mejora": 16.5, "fee": 3800.0, "co2": 98.0, "m_ratio": 0.27, "n": 0.569, "eur": 72000.0, "k": 151.4, "bpd": 380, "label": "PRIORIDAD ALTA - ESTABLE"},
    "Pozo 15/17-7 (Saltire)": {"ahorro": 95000.0, "mejora": 10.5, "fee": 1200.0, "co2": 45.0, "m_ratio": 0.45, "n": 0.569, "eur": 21000.0, "k": 151.4, "bpd": 220, "label": "PRIORIDAD BAJA - MADURO"},
    "Pozo 15/17-8b (Galley)": {"ahorro": 520000.0, "mejora": 22.1, "fee": 6500.0, "co2": 145.0, "m_ratio": 0.18, "n": 0.569, "eur": 115000.0, "k": 151.4, "bpd": 550, "label": "PRIORIDAD MÁXIMA - SWEET SPOT"},
    "Pozo 15/17-9 (Ivanhoe)": {"ahorro": 215000.0, "mejora": 13.8, "fee": 2900.0, "co2": 78.0, "m_ratio": 0.31, "n": 0.569, "eur": 51000.0, "k": 151.4, "bpd": 340, "label": "PRIORIDAD MEDIA - ESTABLE"},
    "Pozo 15/17-10 (Rob Roy)": {"ahorro": 380000.0, "mejora": 17.5, "fee": 4200.0, "co2": 105.0, "m_ratio": 0.26, "n": 0.569, "eur": 81000.0, "k": 151.4, "bpd": 400, "label": "PRIORIDAD ALTA - ESTABLE"}
}

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF (DARK MODE)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17); self.rect(0, 0, 210, 297, 'F') 
        self.set_xy(10, 12)
        self.set_font('Arial', 'B', 22); self.set_text_color(0, 229, 160)
        self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.set_font('Arial', '', 10); self.set_text_color(100, 116, 139)
        self.cell(0, 5, 'Reporte Ejecutivo de Agentes - PIML', 0, 1, 'L')
        self.ln(10)

    def draw_section_header(self, title):
        self.ln(5)
        self.set_font('Arial', 'B', 12); self.set_text_color(255, 255, 255)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 229, 160); self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(5)

    def draw_metric_card(self, label, value, x, y):
        self.set_fill_color(13, 21, 32); self.set_draw_color(26, 42, 58)
        self.rect(x, y, 45, 22, 'FD')
        self.set_xy(x, y + 4)
        self.set_font('Arial', 'B', 14); self.set_text_color(0, 229, 160)
        self.cell(45, 8, str(value).encode('ascii', 'ignore').decode('ascii'), border=0, ln=0, align='C')
        self.set_xy(x, y + 13)
        self.set_font('Arial', '', 8); self.set_text_color(100, 116, 139)
        self.cell(45, 5, str(label).encode('ascii', 'ignore').decode('ascii'), border=0, ln=0, align='C')

def generate_pdf_base64(d, nombre_pozo):
    pdf = FlowBioReport()
    pdf.add_page()
    safe_nombre = str(nombre_pozo).encode('latin-1', 'ignore').decode('latin-1')
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f"Activo Analizado: {safe_nombre}", 0, 1, 'L')
    
    pdf.draw_section_header('Impacto Economico Anual Proyectado')
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 18, f"${d['ahorro']:,.0f} USD/ano", 0, 1, 'L') 
    
    pdf.draw_metric_card("ROI Estimado", "15%", 10, 95)
    pdf.draw_metric_card("Ahorro/bbl", "$2.57", 58, 95)
    pdf.draw_metric_card("OPEX Actual", "$19.80", 106, 95)
    pdf.draw_metric_card("OPEX FlowBio", "$17.23", 154, 95)
    
    pdf.set_xy(10, 125)
    pdf.draw_section_header('Analisis Reologico - Motor PIML')
    pdf.draw_metric_card("Indice flujo (n)", str(d['n']), 10, 142)
    pdf.draw_metric_card("Consistencia K", f"{d['k']} mPas", 58, 142)
    pdf.draw_metric_card("Ratio movilidad", str(d['m_ratio']), 106, 142)
    pdf.draw_metric_card("Ef. barrido", f"{d['mejora']}%", 154, 142)
    
    pdf.set_xy(10, 175)
    pdf.draw_section_header('Resolucion Estrategica')
    pdf.set_font('Arial', '', 10.5); pdf.set_text_color(200, 200, 200)
    conclu = (f"El orquestador determino viabilidad de inyeccion ({d['label']}). "
              f"Al presentar un Ratio de Movilidad de {d['m_ratio']}, se previene la canalizacion prematura de agua. "
              f"Se estima una recuperacion EUR adicional de {d['eur']:,.0f} barriles.")
    pdf.multi_cell(0, 7, conclu)

    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 4. NAVEGACIÓN Y DASHBOARD
# ══════════════════════════════════════════════════════
if st.session_state.screen == 'splash':
    st.markdown("""<div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:120px; font-weight:800; margin:0; letter-spacing:-6px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">AGENT INTELLIGENCE OS</p></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("OBTENER DATOS DE AGENTES (AWS S3)"):
            st.session_state.screen = 'dash'
            st.rerun()

elif st.session_state.screen == 'dash':
    
    # --- CABECERA PRINCIPAL Y BUSCADOR CENTRAL ---
    col_t, col_btn = st.columns([4, 1])
    with col_t:
        st.markdown("<h2 style='font-family:Syne; margin-bottom:10px; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔌 DESCONECTAR"):
            st.session_state.screen = 'splash'
            st.rerun()

    st.markdown("<p style='color:#64748B; font-weight:600; font-size:14px;'>🔍 Haz clic en la caja de abajo y escribe para buscar el pozo a analizar:</p>", unsafe_allow_html=True)
    
    # 🌟 AQUÍ ESTÁ EL BUSCADOR EN EL CENTRO DE LA PANTALLA 🌟
    selected_well = st.selectbox(
        "", 
        list(AGENT_DATA.keys()),
        label_visibility="collapsed"
    )
    d = AGENT_DATA[selected_well]
    
    st.markdown("<p style='color:#22D3EE; font-family:\"DM Mono\"; font-size:12px; margin-top:10px; margin-bottom:20px;'>STATUS: [" + str(d['label']) + "]</p>", unsafe_allow_html=True)
    
    # --- KPIs ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st
