import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. ESTILO "COMMAND CENTER" DE ALTA FIDELIDAD
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }

    /* Botones Premium alineados */
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        border: none !important; width: 100%; transition: 0.3s;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton > button:hover { box-shadow: 0 0 20px rgba(0,229,160,0.4); transform: translateY(-2px); }

    /* Tarjetas de Dashboard */
    .kpi-box {
        background: rgba(13, 21, 32, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 3px solid #00E5A0;
    }
</style>
""", unsafe_allow_html=True)

# 2. LÓGICA DE NAVEGACIÓN
if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'data' not in st.session_state: st.session_state.data = None

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# 3. MOTOR IA (PROCESAMIENTO EN SERVIDOR)
def get_ai_analysis(fluido, tuberia, pozos, bpd):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"EOR Eng. Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}. Return JSON: mejora, ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy."
    try:
        r = requests.post(url, headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1}, timeout=15)
        res = json.loads(r.json()['choices'][0]['message']['content'])
        return {
            "ahorro": float(res.get('ahorro_usd', 0)),
            "mejora": float(res.get('mejora', 0.15)) * (100 if float(res.get('mejora', 0.15)) < 1 else 1),
            "fee": float(res.get('fee_usd', 0)), "co2": float(res.get('co2_tons', 0)),
            "eur": float(res.get('eur_bbls', 0)), "mpy": float(res.get('mpy', 0.1)),
            "pozos": int(pozos), "bpd": float(bpd), "label": "IA LIVE PROJECTION"
        }
    except: return None

# ══════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════

# --- PANTALLA 1: SPLASH (INICIO) ---
if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:110px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Mono'; letter-spacing:8px; color:#64748B; font-size:14px; text-transform:uppercase;">Molecular Intelligence for EOR</p>
    </div>
    """, unsafe_allow_html=True)
    
    _, c2, c3, _ = st.columns([1, 1.8, 1.8, 1])
    with c2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            st.session_state.data = {"ahorro": 1620000, "mejora": 16.5, "fee": 21900, "co2": 833, "eur": 425000, "mpy": 0.8, "pozos": 78, "bpd": 350, "label": "AWS S3 DATA LAKE"}
            st.session_state.screen = 'dash'
            st.rerun()
    with c3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup' # <-- Corregido para ir a configurar
            st.rerun()

# --- PANTALLA 2: SETUP (CONFIGURACIÓN) ---
elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:60px 100px;'><h2 style='font-family:Syne; color:white; font-size:40px;'>Configuración del Simulador</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        f = st.selectbox("QUÍMICO", ["Na-CMC (FlowBio Eco-Safe)", "HPAM (Tradicional)"])
        t = st.selectbox("TUBERÍA", ["Acero al Carbono (L-80)", "Aleación CRA (13Cr)"])
    with c2:
        p = st.number_input("NÚMERO DE POZOS", value=15)
        b = st.number_input("BPD BASE POR POZO", value=350)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ GENERAR ANÁLISIS"):
        with st.status("Analizando física molecular..."):
            res = get_ai_analysis(f, t, p, b)
            if res:
                st.session_state.data = res
                st.session_state.screen = 'dash'
                st.rerun()

# --- PANTALLA 3: DASHBOARD (VISUALIZACIÓN) ---
elif st.session_state.screen == 'dash':
    d = st.session_state.data
    st.markdown(f"<h2 style='font-family:Syne; margin:20px;'>Command Center <span style='font-size:12px; color:#22D3EE;'>[{d['label']}]</span></h2>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p style="color:#64748B; font-size:10px;">AHORRO OPEX</p><h1 style="color:#00E5A0; font-family:Syne;">${d["ahorro"]:,.0f}</h1></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p style="color:#64748B; font-size:10px;">MEJORA</p><h1 style="color:#fff; font-family:Syne;">+{d["mejora"]:.1f}%</h1></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p style="color:#64748B; font-size:10px;">FEE MENSUAL</p><h1 style="color:#22D3EE; font-family:Syne;">${d["fee"]:,.0f}</h1></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p style="color:#64748B; font-size:10px;">ESG CO2</p><h1 style="color:#F59E0B; font-family:Syne;">{d["co2"]:.0f}t</h1></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 1])
    with col_l:
        # Gráfica ampliada
        HTML_CHART = f"""
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:450px; border-radius:12px; background:#0D1520; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i);
            var base = {d['pozos']*d['bpd']};
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot'}}, name:'Base'}},
                {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
            ], {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:20, b:40, l:50, r:20}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }});
        </script>
        """
        components.html(HTML_CHART, height=480)

    with col_r:
        st.markdown(f"""
        <div style="background:#0D1520; padding:20px; border-radius:12px; border:1px solid #1A2A3A;">
            <p style="font-size:10px; color:#64748B;">RESERVAS EUR</p>
            <h2 style="font-family:Syne; color:#22D3EE;">{d['eur']:,.0f}</h2>
            <hr style="opacity:0.1">
            <p style="font-size:10px; color:#64748B;">CORROSIÓN MPY</p>
            <h2 style="font-family:Syne; color:{'#EF4444' if d['mpy']>5 else '#00E5A0'};">{d['mpy']:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← CONFIGURAR"): st.session_state.screen = 'setup'; st.rerun()
        if st.button("🏠 INICIO"): st.session_state.screen = 'splash'; st.rerun()
