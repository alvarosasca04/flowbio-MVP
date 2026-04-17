import streamlit as st
import streamlit.components.v1 as components
import json
import boto3

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y ESTILOS
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne' !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. DEFINICIÓN DE FUNCIONES (ESTO DEBE IR ANTES DEL IF)
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
        st.error(f"Error cargando datos: {e}")
        return None

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE NAVEGACIÓN Y SEGURIDAD
# ══════════════════════════════════════════════════════
PASSWORD_PROTECTION = "FlowBio2026" 

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if st.session_state.screen == 'splash':
    st.markdown("<br><br><h1 style='text-align:center; font-family:Syne; font-size:80px; color:white;'>FlowBio<span style='color:#00E5A0'>.</span></h1>", unsafe_allow_html=True)
    
    _, c_auth, _ = st.columns([1, 1, 1])
    with c_auth:
        pwd = st.text_input("Ingrese Código de Acceso:", type="password")
        if st.button("SINCRONIZAR Y ACCEDER"):
            if pwd == PASSWORD_PROTECTION:
                data = load_data_from_s3() # Ahora la función ya está definida arriba
                if data:
                    st.session_state.all_data = data
                    st.session_state.authenticated = True
                    st.session_state.screen = 'dash'
                    st.rerun()
            else:
                st.error("❌ Código incorrecto.")

elif st.session_state.screen == 'dash' and st.session_state.authenticated:
    st.header("Command Center")
    # Tu dashboard aquí...
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.screen = 'splash'
        st.rerun()
