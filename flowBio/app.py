import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import base64

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL Y ESTILOS MEJORADOS
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    
    /* Eliminar elementos por defecto de Streamlit */
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }

    /* Contenedor de la Splash Screen */
    .splash-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        height: 60vh; /* Ajuste para centrar verticalmente */
    }

    /* KPIs del Dashboard */
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }

    /* BOTÓN CENTRADO Y PREMIUM */
    .stButton > button {
        background: #00E5A0 !important;
        color: #060B11 !important;
        font-family: 'Syne' !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        padding: 18px 45px !important;
        border: none !important;
        transition: 0.3s all ease;
        text-transform: uppercase;
        letter-spacing: 2px;
        display: block;
        margin: 0 auto !important; /* CENTRADO TOTAL */
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 40px rgba(0, 229, 160, 0.4);
    }

    /* Selectores de pozo */
    div[data-baseweb="select"] > div {
        background-color: #0D1520; border: 1px solid #00E5A0; color: white; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. CONEXIÓN REAL A S3 (DATOS DE AGENTES)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=1)
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', 
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/dashboard_data.json"
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except:
        return None

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE NAVEGACIÓN
# ══════════════════════════════════════════════════════
if 'screen' not in st.session_state: st.session_state.screen = 'splash'

# --- PANTALLA DE INICIO (SPLASH) ---
if st.session_state.screen == 'splash':
    st.markdown("""
        <div class="splash-container">
            <h1 style='font-family:Syne; font-size:120px; color:white; margin-bottom:0;'>FlowBio<span style='color:#00E5A0'>.</span></h1>
            <p style='color:#64748B; letter-spacing:10px; font-size:14px; margin-bottom:40px;'>AGENT INTELLIGENCE OS</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("SINCROZINAR CON NUBE S3"):
        data = load_data_from_s3()
        if data:
            st.session_state.all_data = data
            st.session_state.screen = 'dash'
            st.rerun()

# --- PANTALLA DE DASHBOARD (COMMAND CENTER) ---
elif st.session_state.screen == 'dash':
    st.markdown("<h2 style='font-family:Syne; color:white; margin-bottom:20px;'>Command Center</h2>", unsafe_allow_html=True)
    
    wells = list(st.session_state.all_data.keys())
    selected_well = st.selectbox("Seleccione pozo analizado por IA:", wells)
    d = st.session_state.all_data[selected_well]
    
    # --- KPIs SUPERIORES ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${d["fee"]:,}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">CO2 EVITADO</p><p class="kpi-value">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    # --- CONTENIDO TÉCNICO ---
    cl, cr = st.columns([2.3, 1.7])
    
    with cl:
        # Gráfica Dinámica (Plotly)
        chart_html = f"""<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script><div id="plot" style="height:500px; border-radius:12px; background:#0D1520; margin-top:20px; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i); var base = 350; var mej = {d['mejora']} / 100;
            var y1 = x.map(i => base * Math.exp(-0.06*i)); var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mej * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [{{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot'}}, name:'Base (HPAM)'}},{{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio AI'}}], 
            {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:40, b:40, l:50, r:20}} }});
        </script>"""
        components.html(chart_html, height=530)
        
    with cr:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        # 🧪 EXPLICACIÓN TÉCNICA DE DATOS DUROS 🧪
        pv_val = d.get('visc_p', '95.49')
        yp_val = d.get('yield_p', '28.1')
        pb_val = d.get('payback', '1.0')
        eur_val = f"{d.get('eur', 0):,}"

        insight_html = f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:500px; overflow-y:auto;">
<p style="color:#00E5A0; font-weight:800; font-size:12px; margin-bottom:15px;">🧠 ENGINEERING INSIGHTS (5-AGENT CONSENSUS)</p>
<div style="background: rgba(26, 42, 58, 0.4); border-left: 3px solid #22D3EE; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
<p style="font-family: 'DM Mono'; font-size: 10px; color: #22D3EE; margin: 0; text-transform: uppercase;">VISCOSIDAD PLÁSTICA (PV): {pv_val} cP</p>
<p style="font-family: 'Inter'; font-size: 12px; color: #8BA8C0; line-height: 1.4; margin-top: 5px;"><b>¿Por qué importa?</b> Una viscosidad alta garantiza que el fluido empuje el crudo sin "dedear" el agua, maximizando el barrido areal.</p>
</div>
<div style="background: rgba(26, 42, 58, 0.4); border-left: 3px solid #22D3EE; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
<p style="font-family: 'DM Mono'; font-size: 10px; color: #22D3EE; margin: 0; text-transform: uppercase;">YIELD POINT (YP): {yp_val} lb/100ft²</p>
<p style="font-family: 'Inter'; font-size: 12px; color: #8BA8C0; line-height: 1.4; margin-top: 5px;"><b>¿Por qué importa?</b> Indica la estabilidad bajo presión. Un YP balanceado evita la degradación mecánica del polímero en el fondo.</p>
</div>
<div style="background: rgba(26, 42, 58, 0.4); border-left: 3px solid #22D3EE; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
<p style="font-family: 'DM Mono'; font-size: 10px; color: #22D3EE; margin: 0; text-transform: uppercase;">PAYBACK: {pb_val} MESES</p>
<p style="font-family: 'Inter'; font-size: 12px; color: #8BA8C0; line-height: 1.4; margin-top: 5px;"><b>¿Por qué importa?</b> Retorno casi inmediato. El crudo extra cubre el costo tecnológico en tiempo récord.</p>
</div>
<p style="color:#64748B; font-size:10px; margin-top:15px; text-transform: uppercase;">INCREMENTAL PROYECTADO (EUR):</p>
<p style="color:#00E5A0; font-size:32px; font-weight:800; margin:0;">{eur_val} <span style="font-size:12px; color:#64748B;">bbls</span></p>
</div>"""
        st.write(insight_html, unsafe_allow_html=True)

    # --- BOTÓN DE SALIDA ---
    st.markdown("<br><hr style='opacity:0.1;'><br>", unsafe_allow_html=True)
    if st.button("🏠 CERRAR SESIÓN"):
        st.session_state.screen = 'splash'
        st.rerun()
