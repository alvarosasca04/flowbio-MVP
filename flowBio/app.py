import streamlit as st
import streamlit.components.v1 as components
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM FLOWBIO (CSS)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; max-width: 100vw !important; }
    
    /* Estilos del Sidebar */
    [data-testid="stSidebar"] { background-color: #0D1520 !important; border-right: 1px solid rgba(0,229,160,0.2); }
    
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
</style>
""", unsafe_allow_html=True)

if 'screen' not in st.session_state: st.session_state.screen = 'splash'

# ══════════════════════════════════════════════════════
# 2. BASE DE DATOS DE AGENTES 
# ══════════════════════════════════════════════════════
AGENT_DATA = {
    "Pozo 15/17-1 (Central North Sea)": {
        "ahorro": 394000.0, "mejora": 18.2, "fee": 4500.0, "co2": 112.0,
        "m_ratio": 0.25, "n": 0.569, "eur": 85000.0, "k": 151.4, "mpy": 0.08,
        "pozos": 1, "bpd": 420, "label": "POZO CRÍTICO - PRIORIDAD ALTA"
    },
    "Pozo 15/17-2 (Flanco Sur)": {
        "ahorro": 125000.0, "mejora": 12.1, "fee": 1800.0, "co2": 65.0,
        "m_ratio": 0.32, "n": 0.569, "eur": 32000.0, "k": 151.4, "mpy": 0.15,
        "pozos": 1, "bpd": 280, "label": "POZO ESTABLE - PRIORIDAD MEDIA"
    },
    "Pozo 15/17-3 (Inyector Norte)": {
        "ahorro": 280000.0, "mejora": 15.8, "fee": 3200.0, "co2": 95.0,
        "m_ratio": 0.28, "n": 0.569, "eur": 68000.0, "k": 151.4, "mpy": 0.11,
        "pozos": 1, "bpd": 350, "label": "POZO ESTABLE - PRIORIDAD ALTA"
    }
}

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF DINÁMICO
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17); self.rect(0, 0, 210, 40, 'F')
        self.set_xy(10, 12)
        self.set_font('Arial', 'B', 22); self.set_text_color(0, 229, 160)
        self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.set_font('Arial', '', 10); self.set_text_color(255, 255, 255)
        self.cell(0, 5, 'Reporte Ejecutivo de Agentes - PIML', 0, 1, 'L')
        self.ln(10)

    def draw_section_header(self, title):
        self.ln(5)
        self.set_font('Arial', 'B', 12); self.set_text_color(60, 60, 60)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 229, 160); self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(5)

    def draw_metric_card(self, label, value, x, y):
        self.set_fill_color(250, 250, 250); self.set_draw_color(230, 230, 230)
        self.rect(x, y, 45, 22, 'FD')
        self.set_xy(x, y + 4)
        self.set_font('Arial', 'B', 14); self.set_text_color(0, 120, 80)
        safe_value = str(value).encode('ascii', 'ignore').decode('ascii')
        self.cell(45, 8, safe_value, border=0, ln=0, align='C')
        self.set_xy(x, y + 13)
        self.set_font('Arial', '', 8); self.set_text_color(120, 120, 120)
        safe_label = str(label).encode('ascii', 'ignore').decode('ascii')
        self.cell(45, 5, safe_label, border=0, ln=0, align='C')

def generate_pdf_base64(d, nombre_pozo):
    pdf = FlowBioReport()
    pdf.add_page()
    
    safe_nombre = str(nombre_pozo).encode('latin-1', 'ignore').decode('latin-1')
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(6, 11, 17)
    pdf.cell(0, 10, f"Activo Analizado: {safe_nombre}", 0, 1, 'L')
    
    pdf.draw_section_header('Impacto Economico Anual Proyectado')
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(0, 150, 100)
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
    pdf.draw_section_header('Resolucion de Agentes de IA')
    pdf.set_font('Arial', '', 10.5); pdf.set_text_color(50, 50, 50)
    conclu = (f"El orquestador de Groq determino la viabilidad de inyeccion para este activo. "
              f"Se estima una recuperacion EUR adicional de {d['eur']:,.0f} barriles, con un Success Fee "
              f"estimado de ${d['fee']:,.0f} USD. La reduccion de huella de carbono es de {d['co2']} toneladas.")
    pdf.multi_cell(0, 7, conclu)

    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 4. UI: DASHBOARD Y NAVEGACIÓN
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
    st.sidebar.markdown("<h3 style='font-family:Syne; color:#00E5A0;'>🧬 DATA LAKE</h3>", unsafe_allow_html=True)
    
    selected_well = st.sidebar.selectbox(
        "🔍 Buscar y seleccionar activo:",
        list(AGENT_DATA.keys())
    )
    d = AGENT_DATA[selected_well]
    
    st.sidebar.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
    if st.sidebar.button("🔌 DESCONECTAR"):
        st.session_state.screen = 'splash'
        st.rerun()

    st.markdown(f"<h2 style='font-family:Syne; margin-bottom:0px; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#22D3EE; font-family:\"DM Mono\"; font-size:14px; margin-bottom:20px;'>[{d['label']}] ➔ {selected_well}</p>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX / AÑO</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,.0f}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA PROYECTADA</p><p class="kpi-value">+{d["mejora"]:.1f}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">FEE MENSUAL USD</p><p class="kpi-value" style="color:#22D3EE;">${d["fee"]:,.0f}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">ESG CO2 EVITADO</p><p class="kpi-value" style="color:#F59E0B;">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([3, 1])
    with cl:
        # Se elimina el uso de llaves en f-string y se usa .replace() para evitar SyntaxError de Python
        HTML_CHART = """
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:480px; border-radius:12px; background:#0D1520; border:1px solid rgba(255,255,255,0.05); margin-top:20px;"></div>
        <script>
            var x = Array.from({length:40}, (_,i)=>i);
            var base = __BASE_BPD__;
            var mejora = __MEJORA_PCT__;
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mejora * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {x:x, y:y1, type:'scatter', line:{color:'#EF4444', dash:'dot', width:2}, name:'Base (HPAM)'},
                {x:x, y:y2, type:'scatter', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio Na-CMC'}
            ], { paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{color:'#64748B', family:'DM Mono'}, margin:{t:30, b:40, l:50, r:20}, xaxis:{gridcolor:'#1A2A3A'}, yaxis:{gridcolor:'#1A2A3A'} }, {responsive: true, displayModeBar: false});
        </script>
        """.replace("__BASE_BPD__", str(d['bpd'])).replace("__MEJORA_PCT__", str(d['mejora']/100))
        
        components.html(HTML_CHART, height=520)
        
    with cr:
        st.markdown(f"""
        <div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid #1A2A3A; margin-top:20px;">
            <p style="font-size:10px; color:#64748B; font-weight:700; letter-spacing:1px;">FÍSICA DEL POZO</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">RATIO DE MOVILIDAD</p>
            <p style="font-family:'Syne'; font-size:26px; color:#22D3EE; margin:0;">{d['m_ratio']}</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">ÍNDICE
