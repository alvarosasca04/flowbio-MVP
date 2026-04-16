import streamlit as st
import streamlit.components.v1 as components
import boto3
import json
import os
import requests

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

# CSS para ocultar todo lo innecesario y dar el look FlowBio
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    
    /* Estilo para los botones nativos de Streamlit para que parezcan los de la imagen */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 20px;
        font-family: sans-serif;
        font-weight: 800;
        letter-spacing: 1px;
        transition: 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# 1. CREDENCIALES
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

# 2. LÓGICA DE NAVEGACIÓN
if 'screen' not in st.session_state:
    st.session_state.screen = 'splash'

# 3. LECTURA DE S3 (MANTENEMOS TU BACKEND)
@st.cache_data(ttl=30)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/ultimo_reporte.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

# 4. LLAMADA A IA
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Act as EOR eng. JSON only. Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}. Return: mejora, ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red."
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except: return "{}"

# ══════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════

# --- PANTALLA INICIO (SPLASH) ---
if st.session_state.screen == 'splash':
    # El diseño visual en HTML (sin botones funcionales, solo estética)
    st.markdown("""
    <div style="height:50vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; background: #060B11; color:white; font-family:sans-serif;">
        <h1 style="font-size:90px; margin-bottom:10px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="letter-spacing:4px; color:#64748B; margin-bottom:50px;">SUBSURFACE INTELLIGENCE OS</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones funcionales de Streamlit centrados
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            st.session_state.screen = 'demo'
            st.rerun()
    with col3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup'
            st.rerun()

# --- PANTALLA SETUP ---
elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:40px;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:white; text-align:center; font-family:sans-serif;'>IA Engine Setup</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fluido = st.selectbox("Fluido", ["Na-CMC (FlowBio)", "HPAM (Tradicional)"])
            tuberia = st.selectbox("Tuberia", ["Acero al Carbono", "Aleacion CRA"])
        with col2:
            pozos = st.number_input("Pozos", value=15)
            bpd = st.number_input("BPD Base", value=350)
        
        fee = st.slider("Success Fee ($/bbl)", 1.0, 15.0, 5.0)
        
        if st.button("🧠 GENERAR PROYECCIÓN CON LLAMA-3.3"):
            with st.status("Conectando con Groq IA..."):
                res = get_ai_analysis(fluido, tuberia, pozos, bpd, fee)
                st.session_state.ai_result = json.loads(res)
                st.session_state.screen = 'dash'
                st.rerun()
    if st.button("← Volver"):
        st.session_state.screen = 'splash'
        st.rerun()

# --- DASHBOARD (DEMO O IA) ---
elif st.session_state.screen in ['dash', 'demo']:
    # Decidir qué datos mostrar
    if st.session_state.screen == 'demo':
        rep = fetch_s3_data()
        r = rep["resumen_ejecutivo"] if rep else {}
        d = {
            "ahorro": r.get("ahorro_total_usd", 1620000), "mejora": r.get("mejora_promedio_pct", 16.5),
            "fee": r.get("fee_mensual_usd", 21900), "co2": 833, "pozos": 10, "label": "DATA LAKE S3"
        }
    else:
        ai = st.session_state.ai_result
        d = {
            "ahorro": ai.get('ahorro_usd', 0), "mejora": ai.get('mejora', 0)*100,
            "fee": ai.get('fee_usd', 0), "co2": ai.get('co2_tons', 0), "pozos": 15, "label": "IA LIVE"
        }

    # Renderizar el Dashboard (HTML Visual)
    HTML_DASH = f"""
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div style="background:#060B11; color:white; font-family:sans-serif; padding:30px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:30px;">
            <h2 style="margin:0;">Command Center <span style="color:#22D3EE; font-size:14px;">[{d['label']}]</span></h2>
            <button onclick="window.location.reload()" style="background:transparent; border:1px solid #1A2A3A; color:white; padding:10px 20px; border-radius:5px; cursor:pointer;">REINICIAR</button>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:20px; margin-bottom:30px;">
            <div style="background:#0D1520; padding:25px; border-top:3px solid #00E5A0; border-radius:8px;">
                <div style="font-size:11px; color:#64748B; margin-bottom:10px;">AHORRO OPEX / AÑO</div>
                <div style="font-size:32px; font-weight:bold; color:#00E5A0;">${d['ahorro']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-top:3px solid #3B82F6; border-radius:8px;">
                <div style="font-size:11px; color:#64748B; margin-bottom:10px;">MEJORA PRODUCTIVA</div>
                <div style="font-size:32px; font-weight:bold;">+{d['mejora']:.1f}%</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-top:3px solid #22D3EE; border-radius:8px;">
                <div style="font-size:11px; color:#64748B; margin-bottom:10px;">FEE FLOWBIO</div>
                <div style="font-size:32px; font-weight:bold;">${d['fee']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-top:3px solid #F59E0B; border-radius:8px;">
                <div style="font-size:11px; color:#64748B; margin-bottom:10px;">CO2 EVITADO</div>
                <div style="font-size:32px; font-weight:bold; color:#F59E0B;">{d['co2']:.0f} T</div>
            </div>
        </div>

        <div id="chart" style="background:#0D1520; height:400px; border-radius:8px; padding:20px;"></div>
    </div>
    <script>
        var x = Array.from({{length:40}}, (_,i)=>i);
        var y1 = x.map(i => {d['pozos']*350} * Math.exp(-0.05*i));
        var y2 = x.map(i => i<5 ? y1[i] : y1[i] + ({d['pozos']*350} * {d['mejora']/100} * Math.exp(-0.01*(i-5))));
        Plotly.newPlot('chart', [
            {{x:x, y:y1, type:'scatter', line:{{color:'#64748B', dash:'dot'}}, name:'Base'}},
            {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:3}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'EOR'}}
        ], {{
            paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', 
            font:{{color:'#64748B'}}, margin:{{t:10, b:40, l:50, r:10}},
            xaxis: {{gridcolor:'#1A2A3A'}}, yaxis: {{gridcolor:'#1A2A3A'}}
        }}, {{responsive: true}});
    </script>
    """
    components.html(HTML_DASH, height=1000)
