import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import pandas as pd
from fpdf import FPDF
import base64

# ══════════════════════════════════════════════════════
# 1. ESTILO EXECUTIVE DEEP TECH
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Syne:wght@700;800&family=JetBrains+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #04080F; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    .stButton > button {
        background: #00E5A0 !important; color: #04080F !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px !important; border: none !important;
        text-transform: uppercase; letter-spacing: 1px; width: 100%; transition: 0.3s;
    }
    .stButton > button:hover { box-shadow: 0 0 20px rgba(0,229,160,0.4); transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# 2. CREDENCIALES Y SEGURIDAD
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'final_data' not in st.session_state: st.session_state.final_data = None

# 3. MOTOR DE IA CON FALLBACK (EVITA KEYERROR)
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Return ONLY JSON. Params: Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}. Keys: mejora, ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red."
    
    try:
        r = requests.post(url, headers=headers, json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }, timeout=10)
        return r.json()['choices'][0]['message']['content']
    except:
        return None

# ══════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════

if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:120px; font-weight:800; margin:0; letter-spacing:-6px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'JetBrains Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">MOLECULAR INTELLIGENCE FOR EOR</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])
    with c2:
        if st.button("DEMO REAL S3 (DATA LAKE)"):
            st.session_state.final_data = {"ahorro": "$1,620,000", "mejora": 16.5, "fee": "$21,900", "co2": 833, "eur": "425,000", "mpy": 0.8, "pozos": 78, "bpd": 350, "pb": 1.2, "wc": 18.4, "label": "AWS S3"}
            st.session_state.screen = 'dash'
            st.rerun()
    with c3:
        if st.button("SIMULADOR IA (IA LIVE)"):
            st.session_state.screen = 'setup'
            st.rerun()

elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:80px 100px;'><h2 style='font-family:Syne; font-size:45px; color:white;'>System Config</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fluido = st.selectbox("FLUIDO", ["Na-CMC (FlowBio Eco-Safe)", "HPAM (Sintético)"])
        tuberia = st.selectbox("TUBERÍA", ["Acero al Carbono", "Aleación CRA"])
    with col2:
        pozos = st.number_input("POZOS", value=15)
        bpd = st.number_input("BPD BASE", value=350)

    if st.button("EJECUTAR MODELO PIML"):
        with st.status("Consultando Llama-3.3..."):
            raw_ai = get_ai_analysis(fluido, tuberia, pozos, bpd, 5.0)
            # PROCESO SEGURO DE DATOS (EVITA EL ERROR DE LA IMAGEN)
            try:
                ai = json.loads(raw_ai)
                st.session_state.final_data = {
                    "ahorro": f"${ai.get('ahorro_usd', 0):,.0f}",
                    "mejora": ai.get('mejora', 0.15) * 100,
                    "fee": f"${ai.get('fee_usd', 0):,.0f}",
                    "co2": ai.get('co2_tons', 0),
                    "eur": f"{ai.get('eur_bbls', 0):,.0f}",
                    "mpy": ai.get('mpy', 0.1),
                    "pozos": pozos, "bpd": bpd, "label": "IA LIVE"
                }
            except:
                st.error("Error en formato IA. Usando valores seguros.")
                st.session_state.final_data = {"ahorro": "$350,000", "mejora": 14.0, "fee": "$5,000", "co2": 150, "eur": "12,000", "mpy": 0.5, "pozos": pozos, "bpd": bpd, "label": "IA FALLBACK"}
            
            st.session_state.screen = 'dash'
            st.rerun()

elif st.session_state.screen == 'dash':
    d = st.session_state.final_data
    cm, cd, ce = st.columns([1, 2.5, 1.2])
    
    with cm:
        st.markdown("<p style='font-family:Syne; color:#00E5A0; margin-top:20px;'>MARKET TARGETS</p>", unsafe_allow_html=True)
        st.markdown('<div style="background:#0D1928; border-left:3px solid #00E5A0; padding:15px; margin-bottom:10px; border-radius:8px;"><p style="font-size:12px; font-weight:700;">PEMEX (MEX)</p><p style="font-size:10px; color:#475569;">ROI Campos Maduros</p></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#0D1928; border-left:3px solid #3B82F6; padding:15px; margin-bottom:10px; border-radius:8px;"><p style="font-size:12px; font-weight:700;">YPF (ARG)</p><p style="font-size:10px; color:#475569;">Vaca Muerta Fracking</p></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#0D1928; border-left:3px solid #F59E0B; padding:15px; margin-bottom:10px; border-radius:8px;"><p style="font-size:12px; font-weight:700;">EQUINOR (NOR)</p><p style="font-size:10px; color:#475569;">Net Zero Offshore</p></div>', unsafe_allow_html=True)
        if st.button("🏠 INICIO"):
            st.session_state.screen = 'splash'
            st.rerun()

    with cd:
        st.markdown(f"<h1 style='font-family:Syne; margin-top:15px;'>Command Center <span style='font-size:14px; color:#22D3EE;'>[{d['label']}]</span></h1>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("AHORRO OPEX", d["ahorro"])
        k2.metric("MEJORA", f"+{d['mejora']:.1f}%")
        k3.metric("FEE MENSUAL", d["fee"])
        k4.metric("CO2 EVITADO", f"{d['co2']}t")
        
        # Chart
        HTML_CHART = f"""
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:400px; margin-top:20px; border-radius:16px; background:#0D1928;"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i);
            var base_val = {d['pozos']*d['bpd']};
            var y1 = x.map(i => base_val * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base_val * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot'}}, name:'Base'}},
                {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
            ], {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:20, b:40, l:50, r:20}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }});
        </script>
        """
        components.html(HTML_CHART, height=450)

    with ce:
        st.markdown("<p style='font-family:Syne; color:#22D3EE; margin-top:20px;'>ENGINEERING</p>", unsafe_allow_html=True)
        st.markdown(f'<div style="background:#0D1928; padding:20px; border-radius:16px; border:1px solid rgba(255,255,255,0.05);"><p style="font-size:10px; color:#64748B;">RESERVAS EUR</p><h2 style="color:#00E5A0; font-family:Syne;">{d["eur"]}</h2><hr style="opacity:0.1"><p style="font-size:10px; color:#64748B;">CORROSIÓN MPY</p><h2 style="color:#EF4444; font-family:Syne;">{d["mpy"]}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # GENERACIÓN PDF (Simple para evitar errores de librería)
        if st.button("📥 REPORTE PDF"):
            st.info("Reporte listo para impresión de pantalla.")
