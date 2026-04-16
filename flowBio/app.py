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

# CSS para mantener el estilo Premium
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-weight: 800 !important; border-radius: 8px !important;
        padding: 15px !important; border: none !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 1. CREDENCIALES SEGURAS
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
USD_TO_MXN = 20.0

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'ai_result' not in st.session_state: st.session_state.ai_result = None

# ══════════════════════════════════════════════════════
# 2. MOTOR DE IA (EJECUTADO EN EL SERVIDOR - SEGURO)
# ══════════════════════════════════════════════════════
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""Act as EOR engineering simulator. JSON ONLY output. 
    Params: Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}. 
    Rules: Na-CMC has ~16.5% improvement, low corrosion. HPAM has ~11% improvement, high corrosion on carbon steel. 
    Calculate: mejora, ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red."""
    
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

# ══════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════

# --- PANTALLA INICIAL ---
if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; font-family:sans-serif;">
        <h1 style="font-size:90px; font-weight:800; margin-bottom:10px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="letter-spacing:4px; color:#64748B; margin-bottom:50px;">SUBSURFACE INTELLIGENCE OS</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown("<div style='padding:50px 100px;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:white;'>Configuración Técnica (IA Engine)</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fluido = st.selectbox("Químico", ["Na-CMC (FlowBio)", "HPAM (Sintético)"])
        tuberia = st.selectbox("Metalurgia", ["Acero al Carbono", "Aleación CRA"])
    with col2:
        pozos = st.number_input("Pozos", value=15)
        bpd = st.number_input("BPD/Pozo", value=350)
    
    fee = st.slider("Success Fee ($/bbl)", 1.0, 15.0, 5.0)
    
    if st.button("⚡ GENERAR ANÁLISIS IA"):
        with st.status("Consultando a Llama-3.3 en tiempo real..."):
            res = get_ai_analysis(fluido, tuberia, pozos, bpd, fee)
            st.session_state.ai_result = json.loads(res)
            st.session_state.inputs = {"pozos": pozos, "bpd": bpd, "fluido": fluido, "tuberia": tuberia}
            st.session_state.screen = 'dash'
            st.rerun()
    if st.button("← Volver"):
        st.session_state.screen = 'splash'
        st.rerun()

# --- DASHBOARD FINAL ---
elif st.session_state.screen in ['dash', 'demo']:
    if st.session_state.screen == 'demo':
        rep = fetch_s3_data()
        r_s3 = rep["resumen_ejecutivo"] if rep else {}
        d = {
            "ahorro": r_s3.get("ahorro_total_usd", 0), "mejora": r_s3.get("mejora_promedio_pct", 16.5),
            "fee": r_s3.get("fee_mensual_usd", 0), "co2": 833, "eur": 425000, 
            "wc": 18.4, "pb": 1.2, "mpy": 0.8, "pozos": 10, "bpd": 350, "label": "AWS S3 DATA"
        }
    else:
        ai = st.session_state.ai_result
        inp = st.session_state.inputs
        d = {
            "ahorro": ai['ahorro_usd'], "mejora": ai['mejora']*100, "fee": ai['fee_usd'],
            "co2": ai['co2_tons'], "eur": ai['eur_bbls'], "wc": ai['wc_red'],
            "pb": ai['payback'], "mpy": ai['mpy'], "pozos": inp['pozos'], "bpd": inp['bpd'], "label": "GROQ AI LIVE"
        }

    # Dashboard Visual
    HTML_DASH = f"""
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div style="background:#060B11; color:white; font-family:sans-serif; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <h2 style="margin:0;">FlowBio Insight <span style="font-size:12px; color:#22D3EE;">[{d['label']}]</span></h2>
            <button onclick="window.location.reload()" style="background:transparent; border:1px solid #1A2A3A; color:white; padding:10px; cursor:pointer;">REINICIAR</button>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-bottom:20px;">
            <div style="background:#0D1520; padding:20px; border-top:3px solid #00E5A0;">
                <div style="font-size:10px; color:#64748B;">AHORRO OPEX / AÑO (USD)</div>
                <div style="font-size:32px; color:#00E5A0;">${d['ahorro']:,.0f}</div>
                <div style="font-size:12px; color:#8BA8C0;">≈ ${d['ahorro']*USD_TO_MXN:,.0f} MXN</div>
            </div>
            <div style="background:#0D1520; padding:20px; border-top:3px solid #3B82F6;">
                <div style="font-size:10px; color:#64748B;">MEJORA PROMEDIO</div>
                <div style="font-size:32px;">+{d['mejora']:.1f}%</div>
            </div>
            <div style="background:#0D1520; padding:20px; border-top:3px solid #22D3EE;">
                <div style="font-size:10px; color:#64748B;">FEE MENSUAL</div>
                <div style="font-size:32px; color:#22D3EE;">${d['fee']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:20px; border-top:3px solid #F59E0B;">
                <div style="font-size:10px; color:#64748B;">ESG: CO2 EVITADO</div>
                <div style="font-size:32px; color:#F59E0B;">{d['co2']:,.0f} T</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px;">
            <div id="chart" style="background:#0D1520; height:350px; border-radius:12px;"></div>
            <div style="background:#0D1520; padding:20px; border-radius:12px;">
                <div style="color:#64748B; font-size:12px; margin-bottom:15px;">MÉTRICAS DURAS</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div style="text-align:center; background:#060B11; padding:15px; border-radius:8px;">
                        <div style="color:#22D3EE; font-size:20px;">{d['eur']:,.0f}</div>
                        <div style="font-size:8px; color:#64748B;">RESERVAS EUR (5A)</div>
                    </div>
                    <div style="text-align:center; background:#060B11; padding:15px; border-radius:8px;">
                        <div style="color:#EF4444; font-size:20px;">{d['mpy']:.1f}</div>
                        <div style="font-size:8px; color:#64748B;">CORROSIÓN MPY</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        var x = Array.from({{length:40}}, (_,i)=>i);
        var base = {d['pozos']*d['bpd']};
        var y1 = x.map(i => base * Math.exp(-0.06*i));
        var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
        Plotly.newPlot('chart', [
            {{x:x, y:y1, type:'scatter', line:{{color:'#64748B', dash:'dot'}}, name:'Base'}},
            {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:3}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'EOR'}}
        ], {{paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:10, b:40, l:50, r:10}}}});
    </script>
    """
    components.html(HTML_DASH, height=1000)
