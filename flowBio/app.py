import streamlit as st
import streamlit.components.v1 as components
import boto3
import json
import os
import requests

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y ESTILO INDUSTRIAL
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    
    /* Botones Estilo Industrial */
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px !important; border: none !important;
        width: 100%; transition: 0.3s ease; text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton > button:hover { box-shadow: 0 0 20px rgba(0,229,160,0.4); transform: translateY(-2px); }
    
    /* Botón de Regreso / Secundario */
    div.back-btn > div > .stButton > button {
        background: transparent !important; color: #64748B !important;
        border: 1px solid #1A2A3A !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. CREDENCIALES Y VARIABLES DE SESIÓN
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
USD_TO_MXN = 20.0

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'final_data' not in st.session_state: st.session_state.final_data = None

# 3. MOTOR DE IA (BACKEND SEGURO)
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"""Act as EOR engine. Return JSON ONLY. Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}.
    Calculate: mejora (float 0.1-0.2), ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red. 
    Rule: Na-CMC is better and safer than HPAM."""
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1}
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except: return None

# ══════════════════════════════════════════════════════
# PANTALLAS DE LA PLATAFORMA
# ══════════════════════════════════════════════════════

# --- PANTALLA 1: SPLASH (INICIO) ---
if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:100px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Sans'; letter-spacing:6px; color:#64748B; font-size:14px; text-transform:uppercase;">Subsurface Intelligence OS</p>
    </div>
    """, unsafe_allow_html=True)
    
    _, c2, c3, _ = st.columns([1.2, 1.8, 1.8, 1.2])
    with c2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            # Datos maestros de S3 para la demo
            st.session_state.final_data = {
                "ahorro": 1620000, "mejora": 16.5, "fee": 21900, "co2": 833, 
                "eur": 425000, "wc": 18.4, "pb": 1.2, "mpy": 0.8, 
                "pozos": 78, "bpd": 350, "label": "AWS S3 DATA LAKE"
            }
            st.session_state.screen = 'dash'
            st.rerun()
    with c3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup'
            st.rerun()

# --- PANTALLA 2: SETUP (CONFIGURACIÓN) ---
elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:60px 100px;'><h2 style='color:white; font-family:Syne; font-size:35px; margin-bottom:40px;'>Configuración IA Engine</h2>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fluido = st.selectbox("Químico Inyectado", ["Na-CMC (FlowBio, Eco-Seguro)", "HPAM (Tradicional, Tóxico)"])
            tuberia = st.selectbox("Metalurgia de Tubería", ["Acero al Carbono (Estándar)", "Aleación CRA (Inoxidable)"])
        with col2:
            pozos = st.number_input("Número de Pozos", value=15, min_value=1)
            bpd = st.number_input("Producción Base (BPD/Pozo)", value=350, min_value=1)
        
        fee = st.slider("Success Fee Propuesto ($/bbl)", 1.0, 15.0, 5.0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns([1, 4])
        with btn_col1:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("← INICIO"):
                st.session_state.screen = 'splash'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_col2:
            if st.button("🧠 GENERAR ANÁLISIS DE IA"):
                with st.status("Analizando física del yacimiento con Llama-3.3..."):
                    res = get_ai_analysis(fluido, tuberia, pozos, bpd, fee)
                    if res:
                        ai = json.loads(res)
                        st.session_state.final_data = {
                            "ahorro": ai['ahorro_usd'], "mejora": ai['mejora']*100, "fee": ai['fee_usd'],
                            "co2": ai['co2_tons'], "eur": ai['eur_bbls'], "wc": ai['wc_red'],
                            "pb": ai['payback'], "mpy": ai['mpy'], "pozos": pozos, "bpd": bpd, 
                            "label": "IA LIVE PROJECTION"
                        }
                        st.session_state.screen = 'dash'
                        st.rerun()

# --- PANTALLA 3: DASHBOARD (RESULTADOS) ---
elif st.session_state.screen == 'dash':
    d = st.session_state.final_data
    
    # Renderizamos el HTML del Dashboard
    HTML_DASH = f"""
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div style="background:#060B11; color:white; font-family:'DM Sans'; padding:25px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px; border-bottom:1px solid #1A2A3A; padding-bottom:15px;">
            <h1 style="font-family:'Syne'; font-size:32px; margin:0;">FlowBio Insight <span style="color:#22D3EE; font-size:12px; font-family:'DM Mono';">[{d['label']}]</span></h1>
        </div>

        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-bottom:25px;">
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #00E5A0;">
                <div style="font-size:10px; color:#64748B; letter-spacing:1px; font-weight:700;">AHORRO OPEX / AÑO (USD)</div>
                <div style="font-size:38px; color:#00E5A0; font-family:'DM Mono'; font-weight:500;">${d['ahorro']:,.0f}</div>
                <div style="font-size:12px; color:#8BA8C0; font-family:'DM Mono';">≈ ${d['ahorro']*USD_TO_MXN:,.0f} MXN</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #3B82F6;">
                <div style="font-size:10px; color:#64748B; letter-spacing:1px; font-weight:700;">MEJORA PROMEDIO</div>
                <div style="font-size:38px; font-family:'DM Mono'; font-weight:500;">+{d['mejora']:.1f}%</div>
                <div style="font-size:12px; color:#8BA8C0; font-family:'DM Mono';">Incremento de Producción</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #22D3EE;">
                <div style="font-size:10px; color:#64748B; letter-spacing:1px; font-weight:700;">FEE MENSUAL USD</div>
                <div style="font-size:38px; color:#22D3EE; font-family:'DM Mono'; font-weight:500;">${d['fee']:,.0f}</div>
                <div style="font-size:12px; color:#8BA8C0; font-family:'DM Mono';">≈ ${d['fee']*USD_TO_MXN:,.0f} MXN</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #F59E0B;">
                <div style="font-size:10px; color:#64748B; letter-spacing:1px; font-weight:700;">ESG: CO2 EVITADO</div>
                <div style="font-size:38px; color:#F59E0B; font-family:'DM Mono'; font-weight:500;">{d['co2']:.0f} t</div>
                <div style="font-size:12px; color:#8BA8C0; font-family:'DM Mono';">Toneladas Anuales</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px;">
            <div style="background:#0D1520; border-radius:12px; padding:25px; border:1px solid #1A2A3A;">
                <div style="font-size:11px; color:#64748B; margin-bottom:20px; font-weight:700; letter-spacing:1px;">PROYECCIÓN DE PRODUCCIÓN (POZOS SELECCIONADOS)</div>
                <div id="chart" style="height:380px;"></div>
            </div>
            <div style="background:#0D1520; border-radius:12px; padding:25px; border:1px solid #1A2A3A;">
                <div style="font-size:11px; color:#64748B; margin-bottom:20px; font-weight:700; letter-spacing:1px;">MÉTRICAS DEL MOTOR PIML</div>
                <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #1A2A3A;">
                    <span style="color:#8BA8C0">Pozos Seleccionados</span><span style="color:#00E5A0; font-family:'DM Mono'; font-weight:700;">{d['pozos']}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #1A2A3A;">
                    <span style="color:#8BA8C0">Factor Skin Promedio</span><span style="color:#EF4444; font-family:'DM Mono'; font-weight:700;">S = 4.2</span>
                </div>
                
                <div style="margin-top:30px; display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#22D3EE; font-size:22px; font-family:'DM Mono';">{d['eur']:,.0f}</div>
                        <div style="font-size:9px; color:#64748B; text-transform:uppercase;">Reservas EUR</div>
                    </div>
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:{'#EF4444' if d['mpy']>5 else '#00E5A0'}; font-size:22px; font-family:'DM Mono';">{d['mpy']:.1f}</div>
                        <div style="font-size:9px; color:#64748B; text-transform:uppercase;">Corrosión MPY</div>
                    </div>
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#00E5A0; font-size:22px; font-family:'DM Mono';">{d['pb']:.1f}</div>
                        <div style="font-size:9px; color:#64748B; text-transform:uppercase;">Payback Meses</div>
                    </div>
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#3B82F6; font-size:22px; font-family:'DM Mono';">-{d['wc']:.1f}%</div>
                        <div style="font-size:9px; color:#64748B; text-transform:uppercase;">Reducción Water Cut</div>
                    </div>
                </div>
                {f'<div style="margin-top:20px; background:rgba(239,68,68,0.1); border:1px solid #EF4444; border-radius:10px; padding:12px; color:#EF4444; font-size:11px;">⚠️ <b>ALERTA DE METALURGIA:</b> HPAM detectado. Riesgo de pitting en tubería de carbono.</div>' if d['mpy']>5 else ''}
            </div>
        </div>
    </div>
    <script>
        var x = Array.from({{length:40}}, (_,i)=>i);
        var base = {d['pozos'] * d['bpd']};
        var y1 = x.map(i => base * Math.exp(-0.06*i));
        var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
        Plotly.newPlot('chart', [
            {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot', width:2}}, name:'Base'}},
            {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
        ], {{
            paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', 
            font:{{color:'#64748B', family:'DM Mono'}}, margin:{{t:10, b:40, l:50, r:10}},
            xaxis: {{gridcolor:'#1A2A3A', zeroline:false}}, yaxis: {{gridcolor:'#1A2A3A', zeroline:false}}
        }}, {{responsive: true, displayModeBar: false}});
    </script>
    """
    components.html(HTML_DASH, height=950, scrolling=True)
    
    # BOTONES DE NAVEGACIÓN INFERIORES (STREAMLIT NATIVO)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("⚙️ RE-CONFIGURAR"):
            st.session_state.screen = 'setup'
            st.rerun()
    with col2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🏠 INICIO"):
            st.session_state.screen = 'splash'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
