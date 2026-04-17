import streamlit as st
import streamlit.components.v1 as components
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN E IDENTIDAD VISUAL
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
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 38px; font-weight: 800; color: #fff; margin: 5px 0; }
    
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px 30px !important;
        width: 100%; transition: 0.3s; text-transform: uppercase;
    }
    
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
    "Pozo 15/17-1 (Central North Sea)": {"ahorro": 394000, "mejora": 18.2, "fee": 4500, "co2": 112.0, "m_ratio": 0.25, "n": 0.569, "eur": 85000, "label": "PRIORIDAD ALTA - CRÍTICO", "bpd": 420},
    "Pozo 15/17-2 (Flanco Sur)": {"ahorro": 125000, "mejora": 12.1, "fee": 1800, "co2": 65.0, "m_ratio": 0.32, "n": 0.569, "eur": 32000, "label": "PRIORIDAD MEDIA - ESTABLE", "bpd": 280},
    "Pozo 15/17-3 (Inyector Norte)": {"ahorro": 280000, "mejora": 15.8, "fee": 3200, "co2": 95.0, "m_ratio": 0.28, "n": 0.569, "eur": 68000, "label": "PRIORIDAD ALTA - ESTABLE", "bpd": 350},
    "Pozo 15/17-4 (Piper Alpha Area)": {"ahorro": 450000, "mejora": 19.5, "fee": 5200, "co2": 130.0, "m_ratio": 0.22, "n": 0.569, "eur": 95000, "label": "PRIORIDAD MÁXIMA", "bpd": 500},
    "Pozo 15/17-5 (Tartan Field)": {"ahorro": 195000, "mejora": 14.2, "fee": 2500, "co2": 82.0, "m_ratio": 0.29, "n": 0.569, "eur": 45000, "label": "PRIORIDAD MEDIA", "bpd": 310},
    "Pozo 15/17-6a (Claymore)": {"ahorro": 310000, "mejora": 16.5, "fee": 3800, "co2": 98.0, "m_ratio": 0.27, "n": 0.569, "eur": 72000, "label": "PRIORIDAD ALTA", "bpd": 380},
    "Pozo 15/17-7 (Saltire)": {"ahorro": 95000, "mejora": 10.5, "fee": 1200, "co2": 45.0, "m_ratio": 0.45, "n": 0.569, "eur": 21000, "label": "PRIORIDAD BAJA", "bpd": 220},
    "Pozo 15/17-8b (Galley)": {"ahorro": 520000, "mejora": 22.1, "fee": 6500, "co2": 145.0, "m_ratio": 0.18, "n": 0.569, "eur": 115000, "label": "PRIORIDAD MÁXIMA", "bpd": 550},
    "Pozo 15/17-9 (Ivanhoe)": {"ahorro": 215000, "mejora": 13.8, "fee": 2900, "co2": 78.0, "m_ratio": 0.31, "n": 0.569, "eur": 51000, "label": "PRIORIDAD MEDIA", "bpd": 340},
    "Pozo 15/17-10 (Rob Roy)": {"ahorro": 380000, "mejora": 17.5, "fee": 4200, "co2": 105.0, "m_ratio": 0.26, "n": 0.569, "eur": 81000, "label": "PRIORIDAD ALTA", "bpd": 400}
}

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17); self.rect(0, 0, 210, 297, 'F') 
        self.set_xy(10, 12); self.set_font('Arial', 'B', 22); self.set_text_color(0, 229, 160)
        self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.ln(10)

def generate_pdf_base64(d, name):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f"Pozo: {name}", 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Ahorro Proyectado: ${d['ahorro']:,} USD/ano", 0, 1, 'L')
    pdf.cell(0, 10, f"Mejora Barrido: {d['mejora']}%", 0, 1, 'L')
    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 4. DASHBOARD UI
# ══════════════════════════════════════════════════════
if st.session_state.screen == 'splash':
    st.markdown("<br><br><br><br><br><h1 style='text-align:center; font-family:Syne; font-size:100px; color:white;'>FlowBio<span style='color:#00E5A0'>.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; letter-spacing:5px;'>AGENT INTELLIGENCE OS</p><br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    if col_btn.button("OBTENER DATOS DE AGENTES (AWS S3)"):
        st.session_state.screen = 'dash'; st.rerun()

elif st.session_state.screen == 'dash':
    st.markdown("<h2 style='font-family:Syne; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    
    # 🌟 BUSCADOR CENTRAL 🌟
    selected_well = st.selectbox("🔍 Selecciona un pozo de los analizados por la IA:", list(AGENT_DATA.keys()))
    d = AGENT_DATA[selected_well]
    
    st.markdown(f"<p style='color:#22D3EE; font-family:DM Mono;'>[{d['label']}]</p>", unsafe_allow_html=True)
    
    # KPIs - Forma simplificada para evitar errores de comillas
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX / AÑO</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA PROYECTADA</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">FEE MENSUAL USD</p><p class="kpi-value" style="color:#22D3EE;">${d["fee"]:,}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">ESG CO2 EVITADO</p><p class="kpi-value" style="color:#F59E0B;">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([2.5, 1.5])
    with cl:
        # Gráfica Plotly
        HTML_CHART = """
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:450px; border-radius:12px; background:#0D1520; margin-top:20px;"></div>
        <script>
            var x = Array.from({length:40}, (_,i)=>i);
            var base = __BASE__;
            var mej = __MEJORA__;
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mej * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {x:x, y:y1, type:'scatter', line:{color:'#EF4444', dash:'dot'}, name:'Base (HPAM)'},
                {x:x, y:y2, type:'scatter', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}
            ], { paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{color:'#64748B'}, margin:{t:30, b:40, l:50, r:20}, xaxis:{gridcolor:'#1A2A3A'}, yaxis:{gridcolor:'#1A2A3A'} }, {responsive: true});
        </script>
        """.replace("__BASE__", str(d['bpd'])).replace("__MEJORA__", str(d['mejora']/100))
        components.html(HTML_CHART, height=480)
        
    with cr:
        st.markdown(f"""<div style="background:#0D1520; padding:20px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); margin-top:20px; height:450px;">
            <p style="color:#00E5A0; font-weight:800; font-size:12px;">🧠 ENGINEERING INSIGHTS</p>
            <p style="color:#64748B; font-size:10px; margin-top:20px;">RATIO MOVILIDAD</p><p style="color:#22D3EE; font-size:24px; font-weight:800; margin:0;">{d['m_ratio']}</p>
            <p style="color:#64748B; font-size:10px; margin-top:20px;">ÍNDICE DE FLUJO (n)</p><p style="color:#F59E0B; font-size:24px; font-weight:800; margin:0;">{d['n']}</p>
            <p style="color:#64748B; font-size:10px; margin-top:20px;">RESERVAS EXTRA</p><p style="color:#00E5A0; font-size:24px; font-weight:800; margin:0;">{d['eur']:,} bbls</p>
        </div>""", unsafe_allow_html=True)

    # Botones de Acción
    st.markdown("<hr style='opacity:0.1;'>", unsafe_allow_html=True)
    c_dw, c_back = st.columns(2)
    with c_dw:
        pdf_b64 = generate_pdf_base64(d, selected_well)
        st.markdown(f'<a href="data:application/pdf;base64,{pdf_b64}" download="FlowBio_{selected_well}.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:800; cursor:pointer;">📥 DESCARGAR REPORTE DEL POZO</button></a>', unsafe_allow_html=True)
    with c_back:
        if st.button("🏠 VOLVER AL INICIO"):
            st.session_state.screen = 'splash'; st.rerun()
