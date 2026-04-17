import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import base64

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM Y CSS PERSONALIZADO
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    
    /* Cajas de Datos Principales */
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    
    /* Cajas de Datos Duros (Técnicas) */
    .tech-box {
        background: rgba(26, 42, 58, 0.4); border-left: 3px solid #22D3EE;
        border-radius: 8px; padding: 15px; margin-bottom: 10px;
    }
    
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .tech-label { font-family: 'DM Mono'; font-size: 10px; color: #22D3EE; margin: 0; }
    .tech-value { font-family: 'Inter'; font-size: 18px; font-weight: 600; color: white; margin: 0; }

    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 18px 30px !important; width: 100%;
        border: none !important; transition: 0.3s; text-transform: uppercase;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 0 20px rgba(0,229,160,0.4); }
    
    div[data-baseweb="select"] > div {
        background-color: #0D1520; border: 1px solid #00E5A0; color: white; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. MOTOR DE CONEXIÓN A S3
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-2"
        )
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/dashboard_data.json"
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error("Error: Los agentes aún están procesando o el archivo no existe en S3.")
        return None

# ══════════════════════════════════════════════════════
# 3. INTERFAZ DE NAVEGACIÓN
# ══════════════════════════════════════════════════════
if 'screen' not in st.session_state: st.session_state.screen = 'splash'

if st.session_state.screen == 'splash':
    st.markdown("<br><br><br><br><h1 style='text-align:center; font-family:Syne; font-size:110px; color:white; margin-bottom:0;'>FlowBio<span style='color:#00E5A0'>.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; letter-spacing:8px; font-size:14px; margin-top:0;'>SUBSURFACE INTELLIGENCE OS</p><br>", unsafe_allow_html=True)
    
    _, col_btn, _ = st.columns([1, 1.2, 1])
    if col_btn.button("Sincronizar Datos de Ingeniería"):
        data = load_data_from_s3()
        if data:
            st.session_state.all_data = data
            st.session_state.screen = 'dash'
            st.rerun()

elif st.session_state.screen == 'dash':
    # Cabecera de Control
    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.markdown("<h2 style='font-family:Syne; color:white; margin-bottom:0;'>Command Center</h2>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔌 Desconectar"):
            st.session_state.screen = 'splash'
            st.rerun()

    # Buscador Centralizado
    selected_well = st.selectbox("Seleccione el activo analizado por el Agente PIML:", list(st.session_state.all_data.keys()))
    d = st.session_state.all_data[selected_well]
    
    st.markdown(f"<p style='color:#00E5A0; font-family:DM Mono; font-size:12px;'>STATUS: {d['label']}</p>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # 4. DASHBOARD DE MÉTRICAS (KPIs)
    # ══════════════════════════════════════════════════════
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">Ahorro OPEX Proyectado</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">Mejora de Barrido</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">FlowBio Success Fee</p><p class="kpi-value">${d["fee"]:,}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">Ton CO2 Evitadas</p><p class="kpi-value">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # 5. GRÁFICA Y DATOS DUROS LATERALES
    # ══════════════════════════════════════════════════════
    cl, cr = st.columns([2.3, 1.7])
    
    with cl:
        # Gráfica Plotly con Hoverlabel Premium
        HTML_CHART = """
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:500px; border-radius:12px; background:#0D1520; margin-top:20px; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({length:40}, (_,i)=>i);
            var base = __BPD__;
            var mej = __MEJ__ / 100;
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mej * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {x:x, y:y1, type:'scatter', line:{color:'#EF4444', dash:'dot', width:2}, name:'Base (HPAM)'},
                {x:x, y:y2, type:'scatter', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio AI'}
            ], { 
                paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', 
                font:{color:'#64748B', family:'Inter'}, margin:{t:40, b:40, l:50, r:20},
                xaxis:{gridcolor:'#1A2A3A'}, yaxis:{gridcolor:'#1A2A3A'},
                hoverlabel: {bgcolor: '#060B11', font: {color: '#00E5A0'}}
            });
        </script>
        """.replace("__BPD__", str(d['bpd'])).replace("__MEJ__", str(d['mejora']))
        components.html(HTML_CHART, height=530)
        
    with cr:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        # Sección de Datos Duros Extraída de Jupyter
        st.markdown(f"""
        <div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:500px;">
            <p style="color:#00E5A0; font-weight:800; font-size:12px; margin-bottom:20px;">🧠 ENGINEERING INSIGHTS (AGENTE PIML)</p>
            
            <div class="tech-box">
                <p class="tech-label">VISCOSIDAD PLÁSTICA (PV)</p>
                <p class="tech-value">{d.get('visc_p', 'N/A')} cP</p>
            </div>
            <div class="tech-box">
                <p class="tech-label">YIELD POINT (YP)</p>
                <p class="tech-value">{d.get('yield_p', 'N/A')} lb/100ft²</p>
            </div>
            <div class="tech-box">
                <p class="tech-label">TEMP. FONDO (BHT)</p>
                <p class="tech-value">{d.get('temp', '85')} °C</p>
            </div>
            
            <p style="color:#64748B; font-size:10px; margin-top:20px;">INCREMENTAL PROYECTADO (EUR)</p>
            <p style="color:#00E5A0; font-size:32px; font-weight:800; margin:0;">{d['eur']:,} <span style="font-size:12px; color:#64748B;">bbls</span></p>
            
            <p style="color:#64748B; font-size:10px; margin-top:15px;">PAYBACK INVERSIÓN</p>
            <p style="color:white; font-size:22px; font-weight:700; margin:0;">{d['payback']} Meses</p>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # 6. BOTONES DE ACCIÓN CENTRADOS
    # ══════════════════════════════════════════════════════
    st.markdown("<br><hr style='opacity:0.1;'><br>", unsafe_allow_html=True)
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        st.button("📄 GENERAR REPORTE PDF (PRÓXIMAMENTE)")
        st.write("")
        if st.button("🏠 VOLVER AL INICIO"):
            st.session_state.screen = 'splash'
            st.rerun()
