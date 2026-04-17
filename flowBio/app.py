import streamlit as st
import streamlit.components.v1 as components
import json
import boto3

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y SEGURIDAD
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

PASSWORD_PROTECTION = "FlowBio2026" 

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne' !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIÓN DE CONEXIÓN A AWS S3
# ══════════════════════════════════════════════════════
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
    except Exception as e:
        st.error(f"Error de conexión S3: {e}")
        return None

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE NAVEGACIÓN Y SEGURIDAD
# ══════════════════════════════════════════════════════
if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if st.session_state.screen == 'splash':
    st.markdown("<br><br><h1 style='text-align:center; font-family:Syne; font-size:80px; color:white;'>FlowBio<span style='color:#00E5A0'>.</span></h1>", unsafe_allow_html=True)
    _, c_auth, _ = st.columns([1, 1, 1])
    with c_auth:
        pwd = st.text_input("Ingrese Código de Acceso Corporativo:", type="password")
        if st.button("SINCRONIZAR Y ACCEDER"):
            if pwd == PASSWORD_PROTECTION:
                st.session_state.authenticated = True
                data = load_data_from_s3()
                if data:
                    st.session_state.all_data = data
                    st.session_state.screen = 'dash'
                    st.rerun()
            else:
                st.error("❌ Acceso denegado: Código incorrecto.")

elif st.session_state.screen == 'dash' and st.session_state.authenticated:
    st.markdown("<h2 style='font-family:Syne; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    
    # Aquí iría el resto de tu Dashboard (selección de pozos, KPIs, gráficas)
    wells = list(st.session_state.all_data.keys())
    selected_well = st.selectbox("Seleccione activo analizado:", wells)
    d = st.session_state.all_data[selected_well]
    
    # Ejemplo de despliegue de KPIs
    k1, k2 = st.columns(2)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box"><p class="kpi-label">MEJORA</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)

    if st.button("🏠 SALIR"):
        st.session_state.authenticated = False
        st.session_state.screen = 'splash'
        st.rerun()
