import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px !important; width: 100%;
    }
    div[data-baseweb="select"] > div {
        background-color: #0D1520; border: 1px solid #00E5A0; color: white; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. CONEXIÓN REAL A LOS AGENTES (AWS S3)
# ══════════════════════════════════════════════════════
def load_data_from_agents():
    """Lee el JSON generado por los agentes en Jupyter desde S3"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-2"
        )
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/dashboard_data.json" # Archivo que genera tu Jupyter
        
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error: No se pudo conectar con los Agentes. Asegúrate de que Jupyter haya subido el archivo dashboard_data.json a S3.")
        return None

# ══════════════════════════════════════════════════════
# 3. NAVEGACIÓN
# ══════════════════════════════════════════════════════
if 'screen' not in st.session_state: st.session_state.screen = 'splash'

if st.session_state.screen == 'splash':
    st.markdown("<br><br><br><h1 style='text-align:center; font-family:Syne; font-size:100px; color:white;'>FlowBio.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; letter-spacing:5px;'>AGENT INTELLIGENCE OS</p><br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    if col_btn.button("SINCRONIZAR CON AGENTES"):
        data = load_data_from_agents()
        if data:
            st.session_state.all_data = data
            st.session_state.screen = 'dash'
            st.rerun()

elif st.session_state.screen == 'dash':
    st.markdown("<h2 style='font-family:Syne; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    
    # BUSCADOR REAL: Solo muestra pozos que los agentes analizaron
    wells = list(st.session_state.all_data.keys())
    selected_well = st.selectbox("🔍 Buscar pozo analizado por IA:", wells)
    d = st.session_state.all_data[selected_well]
    
    # Mostrar KPIs analizados por los agentes
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box"><p class="kpi-label">RATIO MOVILIDAD (M)</p><p class="kpi-value">{d["m_ratio"]}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box"><p class="kpi-label">CO2 EVITADO</p><p class="kpi-value">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    # Gráfica Dinámica (JavaScript) centrada en el pozo
    cl, cr = st.columns([2.5, 1.5])
    with cl:
        HTML_CHART = """
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:450px; border-radius:12px; background:#0D1520; margin-top:20px;"></div>
        <script>
            var base = __BPD__;
            var mej = __MEJ__ / 100;
            var x = Array.from({length:40}, (_,i)=>i);
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mej * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {x:x, y:y1, type:'scatter', line:{color:'#EF4444', dash:'dot'}, name:'Base (HPAM)'},
                {x:x, y:y2, type:'scatter', line:{color:'#00E5A0', width:4}, name:'FlowBio AI'}
            ], { paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{color:'#64748B'}, margin:{t:20, b:40, l:50, r:20} });
        </script>
        """.replace("__BPD__", str(d['bpd'])).replace("__MEJ__", str(d['mejora']))
        components.html(HTML_CHART, height=480)
        
    with cr:
        st.markdown(f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); margin-top:20px; height:450px;">
            <p style="color:#00E5A0; font-weight:800; font-size:12px;">🧠 INSIGHTS DE AGENTE IA</p>
            <p style="color:#64748B; font-size:10px; margin-top:20px;">RECOMENDACIÓN TÉCNICA</p>
            <p style="color:white; font-size:14px;">{d['recomendacion']}</p>
            <p style="color:#64748B; font-size:10px; margin-top:20px;">INCREMENTAL PROYECTADO (EUR)</p>
            <p style="color:#00E5A0; font-size:28px; font-weight:800;">{d['eur']:,} <span style="font-size:12px;">bbls</span></p>
        </div>""", unsafe_allow_html=True)

    # Botones de Acción centrados
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        st.write("")
        if st.button("🏠 VOLVER AL INICIO / DESCONECTAR"):
            st.session_state.screen = 'splash'; st.rerun()
