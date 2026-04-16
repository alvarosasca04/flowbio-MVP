import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import pandas as pd
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. ESTILO "EXECUTIVE DEEP TECH" (CSS)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Syne:wght@700;800&family=JetBrains+Mono&display=swap');
    
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #04080F; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    
    /* Tipografía General */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #E2EEF8;
    }

    /* Tarjetas Premium */
    .kpi-container {
        background: rgba(13, 25, 40, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        border-top: 4px solid;
    }
    
    .kpi-title { font-family: 'Inter'; font-size: 10px; letter-spacing: 2px; color: #64748B; font-weight: 700; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 42px; font-weight: 800; letter-spacing: -2px; margin: 10px 0; }
    .kpi-sub { font-family: 'JetBrains Mono'; font-size: 11px; color: #475569; }

    /* Market Intelligence Sidebar */
    .target-card {
        background: #0D1928;
        border-left: 3px solid #00E5A0;
        padding: 15px;
        margin-bottom: 12px;
        border-radius: 4px 12px 12px 4px;
    }

    /* Botones */
    .stButton > button {
        background: #00E5A0 !important; color: #04080F !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px !important; border: none !important;
        text-transform: uppercase; letter-spacing: 1px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 2. LOGICA DE NEGOCIO
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'final_data' not in st.session_state: st.session_state.final_data = None

def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Act as EOR engine. JSON. Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}."
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1}
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except: return None

# ══════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════

# --- PANTALLA INICIO ---
if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:120px; font-weight:800; margin:0; letter-spacing:-6px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'JetBrains Mono'; letter-spacing:8px; color:#64748B; font-size:14px; text-transform:uppercase;">Molecular Intelligence for EOR</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
    with col2:
        if st.button("DEMO REAL S3 (DATA LAKE)"):
            st.session_state.final_data = {"ahorro": 1620000, "mejora": 16.5, "fee": 21900, "co2": 833, "eur": 425000, "wc": 18.4, "pb": 1.2, "mpy": 0.8, "pozos": 78, "bpd": 350, "label": "AWS S3"}
            st.session_state.screen = 'dash'
            st.rerun()
    with col3:
        if st.button("SIMULADOR IA (CONFIGURABLE)"):
            st.session_state.screen = 'setup'
            st.rerun()

# --- PANTALLA SETUP ---
elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:80px 100px;'><h2 style='font-family:Syne; font-size:45px; color:white;'>System Config</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fluido = st.selectbox("FLUIDO", ["Na-CMC (FlowBio Eco-Safe)", "HPAM (Traditional Synthetic)"])
        tuberia = st.selectbox("TUBERÍA", ["Carbon Steel (L-80)", "CRA Alloy (13Cr)"])
    with col2:
        pozos = st.number_input("POZOS", value=15)
        bpd = st.number_input("BPD BASE", value=350)
    
    if st.button("EJECUTAR MODELO PIML"):
        with st.status("Analizando física..."):
            res = get_ai_analysis(fluido, tuberia, pozos, bpd, 5.0)
            if res:
                ai = json.loads(res)
                st.session_state.final_data = {"ahorro": ai['ahorro_usd'], "mejora": ai['mejora']*100, "fee": ai['fee_usd'], "co2": ai['co2_tons'], "eur": ai['eur_bbls'], "wc": ai['wc_red'], "pb": ai['payback'], "mpy": ai['mpy'], "pozos": pozos, "bpd": bpd, "label": "IA LIVE"}
                st.session_state.screen = 'dash'
                st.rerun()

# --- DASHBOARD ---
elif st.session_state.screen == 'dash':
    d = st.session_state.final_data
    
    # ESTRUCTURA DE 3 COLUMNAS: MARKET INTELLIGENCE | CHART | METRICS
    col_market, col_main, col_metrics = st.columns([1, 2.5, 1.2])

    with col_market:
        st.markdown("<p style='font-family:Syne; font-size:18px; color:#00E5A0; margin-top:20px;'>MARKET TARGETS</p>", unsafe_allow_html=True)
        
        # CLIENTE 1: PEMEX
        st.markdown(f"""<div class="target-card">
            <p style="color:#64748B; font-size:9px; font-weight:700;">STRATEGY: PEMEX (MEX)</p>
            <p style="font-size:13px; font-weight:700;">ROI en Campos Maduros</p>
            <p style="font-size:10px; color:#475569;">Foco: Reducción de Water Cut en Región Marina.</p>
        </div>""", unsafe_allow_html=True)
        
        # CLIENTE 2: YPF
        st.markdown(f"""<div class="target-card" style="border-left-color:#3B82F6;">
            <p style="color:#64748B; font-size:9px; font-weight:700;">STRATEGY: YPF (ARG)</p>
            <p style="font-size:13px; font-weight:700;">Vaca Muerta Fracking</p>
            <p style="font-size:10px; color:#475569;">Foco: Fluido de fricción ultra-baja Na-CMC.</p>
        </div>""", unsafe_allow_html=True)
        
        # CLIENTE 3: EQUINOR
        st.markdown(f"""<div class="target-card" style="border-left-color:#F59E0B;">
            <p style="color:#64748B; font-size:9px; font-weight:700;">STRATEGY: EQUINOR (NOR)</p>
            <p style="font-size:13px; font-weight:700;">Net Zero Offshore</p>
            <p style="font-size:10px; color:#475569;">Foco: Créditos de Carbono y Cero Toxicidad.</p>
        </div>""", unsafe_allow_html=True)
        
        if st.button("🏠 INICIO"):
            st.session_state.screen = 'splash'
            st.rerun()

    with col_main:
        st.markdown(f"<h1 style='font-family:Syne; margin-top:15px;'>Command Center <span style='font-size:14px; color:#22D3EE;'>[{d['label']}]</span></h1>", unsafe_allow_html=True)
        
        # GRID DE 4 KPIS SUPERIORES
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(f'<div class="kpi-container" style="border-top-color:#00E5A0;"><p class="kpi-title">AHORRO OPEX</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,.0f}</p><p class="kpi-sub">≈ ${(d["ahorro"]*20):,.0f} MXN</p></div>', unsafe_allow_html=True)
        with k2: st.markdown(f'<div class="kpi-container" style="border-top-color:#3B82F6;"><p class="kpi-title">MEJORA PROMEDIO</p><p class="kpi-value">+{d["mejora"]:.1f}%</p><p class="kpi-sub">Incremental Vol.</p></div>', unsafe_allow_html=True)
        with k3: st.markdown(f'<div class="kpi-container" style="border-top-color:#22D3EE;"><p class="kpi-title">FEE MENSUAL</p><p class="kpi-value" style="color:#22D3EE;">${d["fee"]:,.0f}</p><p class="kpi-sub">Success Based</p></div>', unsafe_allow_html=True)
        with k4: st.markdown(f'<div class="kpi-container" style="border-top-color:#F59E0B;"><p class="kpi-title">ESG CO2</p><p class="kpi-value" style="color:#F59E0B;">{d["co2"]:.0f}t</p><p class="kpi-sub">Saved/Year</p></div>', unsafe_allow_html=True)
        
        # CHART
        HTML_CHART = f"""
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:400px; margin-top:20px; border-radius:16px; background:#0D1928; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i);
            var b = {d['pozos']*d['bpd']};
            var y1 = x.map(i => b * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (b * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot', width:2}}, name:'Base'}},
                {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
            ], {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B', family:'JetBrains Mono'}}, margin:{{t:20, b:40, l:50, r:20}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }});
        </script>
        """
        components.html(HTML_CHART, height=450)

    with col_metrics:
        st.markdown("<p style='font-family:Syne; font-size:18px; color:#22D3EE; margin-top:20px;'>ENGINEERING</p>", unsafe_allow_html=True)
        
        # PANEL DE DATOS DUROS CON TIPOGRAFÍA SYNE
        st.markdown(f"""
        <div style="background:#0D1928; padding:20px; border-radius:16px; border:1px solid rgba(255,255,255,0.05);">
            <div style="margin-bottom:20px;">
                <p style="font-size:10px; color:#64748B; margin:0;">POZOS SELECCIONADOS</p>
                <p style="font-family:'Syne'; font-size:28px; color:#00E5A0; margin:0;">{d['pozos']}</p>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div style="background:#04080F; padding:12px; border-radius:8px; text-align:center;">
                    <p style="font-family:'Syne'; font-size:18px; color:#22D3EE; margin:0;">{d['eur']:,.0f}</p>
                    <p style="font-size:8px; color:#64748B;">RESERVAS EUR</p>
                </div>
                <div style="background:#04080F; padding:12px; border-radius:8px; text-align:center;">
                    <p style="font-family:'Syne'; font-size:18px; color:#EF4444; margin:0;">{d['mpy']:.1f}</p>
                    <p style="font-size:8px; color:#64748B;">CORROSIÓN MPY</p>
                </div>
                <div style="background:#04080F; padding:12px; border-radius:8px; text-align:center;">
                    <p style="font-family:'Syne'; font-size:18px; color:#00E5A0; margin:0;">{d['pb']:.1f}</p>
                    <p style="font-size:8px; color:#64748B;">PAYBACK (MES)</p>
                </div>
                <div style="background:#04080F; padding:12px; border-radius:8px; text-align:center;">
                    <p style="font-family:'Syne'; font-size:18px; color:#3B82F6; margin:0;">-{d['wc']:.1f}%</p>
                    <p style="font-size:8px; color:#64748B;">WATER CUT</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 REPORTE PDF"):
            st.success("Generando reporte...")
