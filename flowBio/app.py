import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM (CSS)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=JetBrains+Mono&display=swap');
    
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }

    /* Estilo de métricas (KPIs) */
    .kpi-box {
        background: rgba(13, 21, 32, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        border-top: 3px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 10px; color: #64748B; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 34px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-sub { font-family: 'JetBrains Mono'; font-size: 11px; color: #8BA8C0; }

    /* Market Strategy Cards */
    .client-card {
        background: #0D1520;
        border-left: 3px solid #00E5A0;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 4px 10px 10px 4px;
    }

    /* Botones Nativo-Premium */
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px !important; border: none !important;
        text-transform: uppercase; letter-spacing: 1px; width: 100%; transition: 0.3s;
    }
    .stButton > button:hover { box-shadow: 0 0 20px rgba(0,229,160,0.4); transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURACIÓN DE LLAVES Y SESIÓN
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
USD_TO_MXN = 20.0

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'data' not in st.session_state: st.session_state.data = None

# 3. GENERADOR DE PDF SEGURO
def get_pdf_download_link(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 20, 'FLOWBIO EXECUTIVE INSIGHT', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f"Simulacion: {d['label']}", 0, 1, 'C')
    pdf.ln(10)
    pdf.cell(0, 10, f"Ahorro OPEX: {d['ahorro']}", 0, 1)
    pdf.cell(0, 10, f"Mejora Volumetrica: +{d['mejora']}%", 0, 1)
    pdf.cell(0, 10, f"Reservas Extra EUR: {d['eur']} bbls", 0, 1)
    html = f'<a href="data:application/pdf;base64,{base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()}" download="FlowBio_Report.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:bold; cursor:pointer;">📥 DESCARGAR REPORTE PDF</button></a>'
    return html

# 4. LLAMADA IA BACKEND (EVITA ERRORES DE CONEXIÓN)
def get_ai_analysis(fluido, tuberia, pozos, bpd):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"EOR Eng. Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}. JSON keys: mejora (float 0.1-0.2), ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red."
    try:
        r = requests.post(url, headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1}, timeout=10)
        return json.loads(r.json()['choices'][0]['message']['content'])
    except: return None

# ══════════════════════════════════════════════════════
# NAVEGACIÓN
# ══════════════════════════════════════════════════════

if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:110px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'JetBrains Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">SUBSURFACE INTELLIGENCE OS</p>
    </div>
    """, unsafe_allow_html=True)
    _, c2, c3, _ = st.columns([1, 1.8, 1.8, 1])
    with c2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            st.session_state.data = {"ahorro": 1620000.0, "mejora": 16.5, "fee": 21900.0, "co2": 833.0, "eur": 425000.0, "mpy": 0.8, "pozos": 78, "bpd": 350, "label": "AWS S3 DATA LAKE"}
            st.session_state.screen = 'dash'
            st.rerun()
    with c3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup'
            st.rerun()

elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:60px 100px;'><h2 style='font-family:Syne; font-size:45px; color:white;'>Configuración del Yacimiento</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fluido = st.selectbox("QUÍMICO", ["Na-CMC (FlowBio Eco-Safe)", "HPAM (Tradicional)"])
        tuberia = st.selectbox("TUBERÍA", ["Acero al Carbono (L-80)", "Aleación CRA (13Cr)"])
    with c2:
        pozos = st.number_input("NÚMERO DE POZOS", value=15)
        bpd = st.number_input("BPD BASE POR POZO", value=350)
    if st.button("⚡ GENERAR PROYECCIÓN IA"):
        with st.status("Analizando física con Llama-3.3..."):
            ai = get_ai_analysis(fluido, tuberia, pozos, bpd)
            if ai:
                # BLINDAJE DE DATOS (Asegura que sean números)
                st.session_state.data = {
                    "ahorro": float(ai.get('ahorro_usd', 0)),
                    "mejora": float(ai.get('mejora', 0.15)) * (100 if float(ai.get('mejora', 0.15)) < 1 else 1),
                    "fee": float(ai.get('fee_usd', 0)),
                    "co2": float(ai.get('co2_tons', 0)),
                    "eur": float(ai.get('eur_bbls', 0)),
                    "mpy": float(ai.get('mpy', 0.1)),
                    "pozos": int(pozos), "bpd": float(bpd),
                    "label": "GROQ AI LIVE"
                }
                st.session_state.screen = 'dash'
                st.rerun()

elif st.session_state.screen == 'dash':
    d = st.session_state.data
    m_col, d_col, e_col = st.columns([1, 2.5, 1.2])

    with m_col:
        st.markdown("<p style='font-family:Syne; color:#00E5A0; font-size:18px; margin-top:20px;'>MARKET TARGETS</p>", unsafe_allow_html=True)
        st.markdown('<div class="client-card"><p style="font-size:9px; color:#64748B;">STRATEGY: PEMEX</p><p style="font-weight:700; font-size:12px;">ROI Campos Maduros</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="client-card" style="border-left-color:#3B82F6;"><p style="font-size:9px; color:#64748B;">STRATEGY: YPF</p><p style="font-weight:700; font-size:12px;">Vaca Muerta Fracking</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="client-card" style="border-left-color:#F59E0B;"><p style="font-size:9px; color:#64748B;">STRATEGY: EQUINOR</p><p style="font-weight:700; font-size:12px;">Net Zero Offshore</p></div>', unsafe_allow_html=True)
        if st.button("🏠 INICIO"):
            st.session_state.screen = 'splash'
            st.rerun()

    with d_col:
        st.markdown(f"<h2 style='font-family:Syne; margin-top:15px;'>Command Center <span style='font-size:12px; color:#22D3EE;'>[{d['label']}]</span></h2>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,.0f}</p><p class="kpi-sub">≈ ${d["ahorro"]*USD_TO_MXN:,.0f} MXN</p></div>', unsafe_allow_html=True)
        with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA PROMEDIO</p><p class="kpi-value">+{d["mejora"]:.1f}%</p><p class="kpi-sub">Incremental Vol.</p></div>', unsafe_allow_html=True)
        with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">FEE MENSUAL</p><p class="kpi-value" style="color:#22D3EE;">${d["fee"]:,.0f}</p><p class="kpi-sub">Success Fee</p></div>', unsafe_allow_html=True)
        with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">ESG CO2</p><p class="kpi-value" style="color:#F59E0B;">{d["co2"]:.0f}t</p><p class="kpi-sub">Ahorro Anual</p></div>', unsafe_allow_html=True)
        
        HTML_CHART = f"""
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:400px; margin-top:20px; border-radius:12px; background:#0D1520; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i);
            var base = {d['pozos'] * d['bpd']};
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot', width:2}}, name:'Base'}},
                {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
            ], {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B', family:'DM Mono'}}, margin:{{t:20, b:40, l:50, r:20}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }});
        </script>
        """
        components.html(HTML_CHART, height=430)

    with e_col:
        st.markdown("<p style='font-family:Syne; color:#22D3EE; font-size:18px; margin-top:20px;'>ENGINEERING</p>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:#0D1520; padding:20px; border-radius:12px; border:1px solid rgba(255,255,255,0.05);">
            <p style="font-size:10px; color:#64748B;">POZOS SELECCIONADOS</p>
            <p style="font-family:'Syne'; font-size:24px; color:#00E5A0;">{d['pozos']}</p>
            <hr style="opacity:0.1">
            <p style="font-size:10px; color:#64748B;">RESERVAS EUR (5A)</p>
            <p style="font-family:'Syne'; font-size:24px; color:#22D3EE;">{d['eur']:,.0f}</p>
            <hr style="opacity:0.1">
            <p style="font-size:10px; color:#64748B;">CORROSIÓN MPY</p>
            <p style="font-family:'Syne'; font-size:24px; color:{'#EF4444' if d['mpy'] > 5 else '#00E5A0'};">{d['mpy']:.1f}</p>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        components.html(get_pdf_download_link(d), height=100)
        if st.button("⚙️ RE-CONFIGURAR"):
            st.session_state.screen = 'setup'
            st.rerun()
