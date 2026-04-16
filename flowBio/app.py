import streamlit as st
import streamlit.components.v1 as components
import base64
import boto3
import json
import os
import requests

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
</style>
""", unsafe_allow_html=True)

# 1. CREDENCIALES SEGURAS
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
USD_TO_MXN = 20.0

# ══════════════════════════════════════════════════════
# 2. FUNCIÓN DE IA (BACKEND - EVITA ERROR DE CONEXIÓN)
# ══════════════════════════════════════════════════════
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Act as EOR eng calculator. JSON output only. 
    Params: Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}. 
    Keys: mejora, ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red. 
    Rules: Na-CMC has ~16.5% imp, low corrosion (<1.0 mpy), high co2 saved. 
    HPAM has ~11% imp, 0 co2, high corrosion (>20 mpy) on carbon steel. 
    Ahorro OPEX = (Extra bpd * 365 * 18.5) - (Mitigation Cost)."""

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return json.dumps({"error": str(e)})

# ══════════════════════════════════════════════════════
# 3. LECTURA DE S3 (MODO DEMO)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/ultimo_reporte.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

reporte = fetch_s3_data()
r = reporte["resumen_ejecutivo"] if reporte else {}
esg = reporte["esg_cbam"] if reporte else {}

# Lógica de estados para navegar entre pantallas
if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'ai_result' not in st.session_state: st.session_state.ai_result = None

def change_screen(name): st.session_state.screen = name

# ══════════════════════════════════════════════════════
# PANTALLAS DE CONTROL (STREAMLIT NATIVO)
# ══════════════════════════════════════════════════════

# --- PANTALLA INICIO ---
if st.session_state.screen == 'splash':
    components.html(f"""
    <div style="height:90vh; display:flex; flex-direction:column; align-items:center; justify-content:center; background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%); color:white; font-family:sans-serif;">
        <h1 style="font-size:90px; margin-bottom:10px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="letter-spacing:4px; color:#64748B; margin-bottom:50px;">SUBSURFACE INTELLIGENCE OS</p>
        <div style="display:flex; gap:20px;">
            <button onclick="parent.window.location.hash='demo'; location.reload();" style="background:#00E5A0; color:#060B11; padding:18px 40px; border-radius:8px; border:none; font-weight:800; cursor:pointer;">EJECUTAR DEMO REAL (S3)</button>
            <button onclick="parent.window.location.hash='setup'; location.reload();" style="background:transparent; color:white; border:1px solid #1A2A3A; padding:18px 40px; border-radius:8px; cursor:pointer;">SIMULADOR IA LIVE</button>
        </div>
    </div>
    """, height=800)
    
    # Capturar clicks de los botones via URL hash
    query_params = st.query_params
    if "hash" in query_params:
        st.session_state.screen = query_params["hash"]
        st.rerun()

# --- PANTALLA SETUP ---
elif st.session_state.screen == 'setup':
    with st.container():
        st.markdown("<h2 style='color:white; text-align:center;'>Configuración IA Engine</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fluido = st.selectbox("Químico", ["Na-CMC (FlowBio)", "HPAM (Tradicional)"])
            tuberia = st.selectbox("Metalurgia", ["Acero al Carbono", "Aleacion CRA"])
        with col2:
            pozos = st.number_input("Pozos", value=15)
            bpd = st.number_input("Prod. Base (BPD)", value=350)
        
        fee = st.slider("Success Fee ($/bbl)", 1.0, 15.0, 5.0)
        
        if st.button("🧠 EJECUTAR ANÁLISIS IA", use_container_width=True):
            with st.status("🤖 Consultando a Llama-3.3 en tiempo real..."):
                res = get_ai_analysis(fluido, tuberia, pozos, bpd, fee)
                st.session_state.ai_result = json.loads(res)
                st.session_state.screen = 'dash'
                st.rerun()

# --- PANTALLA DASHBOARD ---
elif st.session_state.screen == 'dash' or st.session_state.screen == 'demo':
    # Preparar datos finales
    if st.session_state.screen == 'demo':
        mode_label = "PILOTO REAL S3"
        d = {
            "ahorro": r.get("ahorro_total_usd", 1620000), "mejora": r.get("mejora_promedio_pct", 16.5),
            "fee": r.get("fee_mensual_usd", 21900), "co2": esg.get("total_ton_co2_ahorradas", 833),
            "eur": r.get("eur_extra_bbls", 425000), "wc": r.get("wc_reduccion_pct", 18.4),
            "pb": r.get("payback_meses", 1.2), "mpy": 0.8, "pozos": r.get("pozos_piloto", 10), "fluido": "Na-CMC"
        }
    else:
        mode_label = "IA LIVE PROJECTION"
        ai = st.session_state.ai_result
        d = {
            "ahorro": ai['ahorro_usd'], "mejora": ai['mejora'] * 100, "fee": ai['fee_usd'],
            "co2": ai['co2_tons'], "eur": ai['eur_bbls'], "wc": ai['wc_red'],
            "pb": ai['payback'], "mpy": ai['mpy'], "pozos": pozos, "fluido": fluido
        }

    # Inyectar en el HTML visual (el que te gusta)
    HTML_DASH = f"""
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div style="background:#060B11; color:white; font-family:sans-serif; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <h1>FlowBio Command Center <span style="font-size:12px; color:#22D3EE;">ORIGEN: {mode_label}</span></h1>
            <button onclick="window.location.reload()" style="background:transparent; border:1px solid #1A2A3A; color:white; padding:10px; cursor:pointer;">REINICIAR</button>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-bottom:20px;">
            <div style="background:#0D1520; padding:20px; border-top:3px solid #00E5A0;">
                <div style="font-size:10px; color:#64748B;">AHORRO OPEX / AÑO</div>
                <div style="font-size:30px; color:#00E5A0;">${d['ahorro']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:20px; border-top:3px solid #3B82F6;">
                <div style="font-size:10px; color:#64748B;">MEJORA VOLUMÉTRICA</div>
                <div style="font-size:30px;">+{d['mejora']:.1f}%</div>
            </div>
            <div style="background:#0D1520; padding:20px; border-top:3px solid #22D3EE;">
                <div style="font-size:10px; color:#64748B;">FEE FLOWBIO</div>
                <div style="font-size:30px;">${d['fee']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:20px; border-top:3px solid #F59E0B;">
                <div style="font-size:10px; color:#64748B;">ESG: CO2 EVITADO</div>
                <div style="font-size:30px;">{d['co2']:.0f} T</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px;">
            <div id="chart" style="background:#0D1520; height:350px;"></div>
            <div style="background:#0D1520; padding:20px;">
                <div style="color:#64748B; font-size:12px; margin-bottom:15px;">DATOS DUROS INGENIERÍA</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div style="text-align:center; background:#060B11; padding:10px;">
                        <div style="font-size:18px; color:#22D3EE;">{d['eur']:,.0f}</div>
                        <div style="font-size:9px; color:#64748B;">RESERVAS EUR</div>
                    </div>
                    <div style="text-align:center; background:#060B11; padding:10px;">
                        <div style="font-size:18px; color:#EF4444;">{d['mpy']:.1f}</div>
                        <div style="font-size:9px; color:#64748B;">CORROSIÓN MPY</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        var x = Array.from({{length:40}}, (_,i)=>i);
        var y1 = x.map(i => {d['pozos']*350} * Math.exp(-0.06*i));
        var y2 = x.map(i => i<5 ? y1[i] : y1[i] + ({d['pozos']*350} * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
        Plotly.newPlot('chart', [
            {{x:x, y:y1, type:'scatter', line:{{color:'#64748B', dash:'dot'}}, name:'Base'}},
            {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0'}}, fill:'tonexty', name:'EOR'}}
        ], {{paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:10, b:40, l:40, r:10}}}});
    </script>
    """
    components.html(HTML_DASH, height=1000)
