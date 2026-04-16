import streamlit as st
import streamlit.components.v1 as components
import boto3
import json
import os
import requests

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN Y ESTILO FLOWBIO (RESTAURADO)
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px !important; border: none !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 1. VARIABLES Y CREDENCIALES
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
USD_TO_MXN = 20.0

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'final_data' not in st.session_state: st.session_state.final_data = None

# ══════════════════════════════════════════════════════
# 2. CONEXIÓN REAL CON LOS DATOS DE TU JUPYTER (S3)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=10)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        response = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        
        # Mapeo exacto de lo que genera tu Jupyter
        res = data["resumen_ejecutivo"]
        esg = data["esg_cbam"]
        
        return {
            "ahorro": res.get("ahorro_total_usd", 0),
            "mejora": res.get("mejora_promedio_pct", 0),
            "fee": res.get("fee_mensual_usd", 0),
            "co2": esg.get("total_ton_co2_ahorradas", 0),
            "eur": res.get("eur_extra_bbls", 0),
            "wc": res.get("wc_reduccion_pct", 0),
            "pb": res.get("payback_meses", 0),
            "lc": res.get("lc_caida_usd", 0),
            "pozos": res.get("pozos_piloto", 10),
            "label": "AWS S3 DATA LAKE (VALORES REALES AGENTES)"
        }
    except Exception as e:
        return None

# 3. MOTOR DE IA (Para el modo manual)
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Act as EOR eng. Return JSON. Params: Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}."
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1}
    try:
        r = requests.post(url, headers=headers, json=data)
        ai = json.loads(r.json()['choices'][0]['message']['content'])
        return {
            "ahorro": ai['ahorro_usd'], "mejora": ai['mejora']*100, "fee": ai['fee_usd'],
            "co2": ai['co2_tons'], "eur": ai['eur_bbls'], "wc": ai['wc_red'],
            "pb": ai['payback'], "lc": ai.get('lc_drop', 2.1), "mpy": ai['mpy'],
            "pozos": pozos, "bpd": bpd, "label": "GROQ IA LIVE PROJECTION"
        }
    except: return None

# ══════════════════════════════════════════════════════
# PANTALLAS
# ══════════════════════════════════════════════════════

if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:100px; font-weight:800; margin:0;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Sans'; letter-spacing:6px; color:#64748B; font-size:14px;">SUBSURFACE INTELLIGENCE OS</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.2, 1.8, 1.8, 1.2])
    with c2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            with st.spinner("Sincronizando con Agentes de IA en S3..."):
                real_data = fetch_s3_data()
                if real_data:
                    st.session_state.final_data = real_data
                    st.session_state.screen = 'dash'
                    st.rerun()
                else: st.error("No se pudo leer el archivo de S3. Verifica Jupyter.")
    with c3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup'
            st.rerun()

elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:60px 100px;'><h2 style='color:white; font-family:Syne;'>Configuración IA Engine</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fluido = st.selectbox("Químico", ["Na-CMC (FlowBio)", "HPAM (Tradicional)"])
        tuberia = st.selectbox("Metalurgia", ["Acero al Carbono", "Aleacion CRA"])
    with col2:
        pozos = st.number_input("Pozos", value=15)
        bpd = st.number_input("Prod. Base (BPD)", value=350)
    fee = st.slider("Success Fee ($/bbl)", 1.0, 15.0, 5.0)
    if st.button("🧠 GENERAR ANÁLISIS"):
        with st.status("Consultando IA..."):
            ai_data = get_ai_analysis(fluido, tuberia, pozos, bpd, fee)
            if ai_data:
                st.session_state.final_data = ai_data
                st.session_state.screen = 'dash'
                st.rerun()

elif st.session_state.screen == 'dash':
    d = st.session_state.final_data
    HTML_DASH = f"""
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div style="background:#060B11; color:white; font-family:'DM Sans'; padding:25px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px; border-bottom:1px solid #1A2A3A; padding-bottom:15px;">
            <h1 style="font-family:'Syne'; font-size:26px; margin:0;">FlowBio Insight <span style="color:#22D3EE; font-size:12px; font-family:'DM Mono';">[{d['label']}]</span></h1>
            <button onclick="parent.window.location.reload()" style="background:transparent; border:1px solid #ffffff20; color:white; padding:8px 15px; border-radius:5px; cursor:pointer;">REINICIAR</button>
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-bottom:25px;">
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #00E5A0;">
                <div style="font-size:10px; color:#64748B;">AHORRO OPEX / AÑO</div>
                <div style="font-size:36px; color:#00E5A0; font-family:'DM Mono';">${d['ahorro']:,.0f}</div>
                <div style="font-size:11px; color:#8BA8C0;">≈ ${d['ahorro']*USD_TO_MXN:,.0f} MXN</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #3B82F6;">
                <div style="font-size:10px; color:#64748B;">MEJORA PROMEDIO</div>
                <div style="font-size:36px; font-family:'DM Mono';">+{d['mejora']:.1f}%</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #22D3EE;">
                <div style="font-size:10px; color:#64748B;">FEE MENSUAL USD</div>
                <div style="font-size:36px; color:#22D3EE; font-family:'DM Mono';">${d['fee']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #F59E0B;">
                <div style="font-size:10px; color:#64748B;">ESG: CO2 EVITADO</div>
                <div style="font-size:36px; color:#F59E0B; font-family:'DM Mono';">{d['co2']:.0f} t</div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px;">
            <div style="background:#0D1520; border-radius:12px; padding:25px; border:1px solid #1A2A3A;">
                <div id="chart" style="height:380px;"></div>
            </div>
            <div style="background:#0D1520; border-radius:12px; padding:25px; border:1px solid #1A2A3A;">
                <div style="font-size:11px; color:#64748B; margin-bottom:20px;">MÉTRICAS DEL MOTOR PIML</div>
                <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #1A2A3A;">
                    <span style="color:#8BA8C0">Pozos Seleccionados</span><span style="color:#00E5A0; font-family:'DM Mono'; font-weight:bold;">{d['pozos']}</span>
                </div>
                <div style="margin-top:30px; display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#22D3EE; font-size:20px; font-family:'DM Mono';">{d['eur']:,.0f}</div>
                        <div style="font-size:8px; color:#64748B;">RESERVAS EUR</div>
                    </div>
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#00E5A0; font-size:20px; font-family:'DM Mono';">{d['pb']:.1f}</div>
                        <div style="font-size:8px; color:#64748B;">PAYBACK (MESES)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        var x = Array.from({{length:40}}, (_,i)=>i);
        var base = {d['pozos'] * 350};
        var y1 = x.map(i => base * Math.exp(-0.06*i));
        var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
        Plotly.newPlot('chart', [
            {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot', width:2}}, name:'Base'}},
            {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
        ], {{paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B', family:'DM Sans'}}, margin:{{t:10, b:40, l:50, r:10}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }});
    </script>
    """
    components.html(HTML_DASH, height=1000)
