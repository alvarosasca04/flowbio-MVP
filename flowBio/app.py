import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y ESTILOS
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    
    /* Fuentes de respaldo */
    body, p, div { font-family: 'Inter', -apple-system, sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 0px; }
    .kpi-value { font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-desc { font-size: 10px; color: #8BA8C0; margin-top: 5px; line-height: 1.2; }
    
    /* Estilos de botones */
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; transition: all 0.3s ease; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0, 229, 160, 0.4); }
    
    /* Estilo para la consola de la fase 2 */
    .console-box { background: #0D1520; border: 1px solid rgba(0,229,160,0.3); border-radius: 8px; padding: 20px; font-family: 'DM Mono', monospace; color: #22D3EE; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES DE CORE (S3 Y PDF MEJORADO)
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        try:
            aws_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
        except:
            aws_key = st.secrets["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["AWS_SECRET_ACCESS_KEY"]
            
        s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_sec, region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error al cargar datos desde S3. Verifica tus credenciales. ({e})")
        return None

def clean_text(text):
    if text is None: return ""
    return str(text).replace('·', '.').replace('²', '2').encode('latin-1', errors='replace').decode('latin-1')

def generate_corporate_pdf(well, d):
    # Cálculos necesarios para el PDF
    eur_val = d.get('eur', 0)
    barriles_extra_mes = int(eur_val / 60)
    valor_extra = barriles_extra_mes * 74.5 
    
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Fondo Corporativo Oscuro
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # 2. Encabezado Principal
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, clean_text('FlowBio Executive Report'), 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 229, 160) # Verde FlowBio
    pdf.cell(0, 10, clean_text(f'Pozo Analizado: {well}'), 0, 1, 'L')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(139, 168, 192) # Gris claro
    pdf.cell(0, 8, clean_text(f'Fecha de Simulación: {datetime.now().strftime("%Y-%m-%d %H:%M")}'), 0, 1, 'L')
    
    # Línea divisoria elegante
    pdf.set_draw_color(0, 229, 160)
    pdf.set_line_width(0.5)
    pdf.line(10, 45, 200, 45)
    pdf.ln(12)
    
    # --- SECCIÓN 1: IMPACTO FINANCIERO ---
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(34, 211, 238) # Cyan FlowBio
    pdf.cell(0, 10, clean_text('1. IMPACTO FINANCIERO PROYECTADO'), 0, 1, 'L')
    pdf.ln(2)
    
    fin_data = [
        ["Crudo Incremental (Mensual):", f"+{barriles_extra_mes:,} bbls"],
        ["Valor Extra Generado (Mensual):", f"${valor_extra:,.0f} USD"],
        ["Tarifa por Exito (Success Fee):", f"${d.get('fee', 0):,.0f} USD"],
        ["Retorno de Inversion (Payback):", f"{d.get('payback', 0)} Meses"],
        ["Recuperacion Total a 5 anos (EUR):", f"{eur_val:,} bbls"]
    ]
    
    pdf.set_fill_color(13, 21, 32)
    pdf.set_draw_color(30, 41, 59) # Color de borde muy sutil
    pdf.set_line_width(0.2)
    
    for k, v in fin_data:
        pdf.set_text_color(200, 200, 200)
        pdf.set_font('Arial', '', 11)
        pdf.cell(100, 10, clean_text(" " + k), border='B', fill=True)
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(90, 10, clean_text(" " + v), border='B', ln=1, align='R', fill=True)
        
    pdf.ln(10)
    
    # --- SECCIÓN 2: INGENIERÍA Y QUÍMICA ---
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(34, 211, 238) # Cyan FlowBio
    pdf.cell(0, 10, clean_text('2. DIAGNOSTICO Y PRESCRIPCION PIML'), 0, 1, 'L')
    pdf.ln(2)
    
    eng_data = [
        ["Sistema Quimico Recomendado:", str(d.get('quimico', 'Polimero Avanzado')).upper()],
        ["Dosificacion Optima:", f"{d.get('ppm', 1500)} ppm"],
        ["Volumen Poroso de Inyeccion (PV):", str(d.get('vol_pv', 0.29))],
        ["Caudal de Bombeo Objetivo:", f"{d.get('bwpd', 350)} BWPD"],
        ["Limite de Presion (Riesgo de Fractura):", f"{d.get('lim_psi', 3000):,} psi"],
        ["Viscosidad Plastica del Fluido (PV):", f"{d.get('visc_p', 98.4)} cP"],
        ["Punto de Cedencia (Yield Point):", f"{d.get('yield_p', 28.9)} lb/ft2"]
    ]
    
    for k, v in eng_data:
        pdf.set_text_color(200, 200, 200)
        pdf.set_font('Arial', '', 11)
        pdf.cell(100, 10, clean_text(" " + k), border='B', fill=True)
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(90, 10, clean_text(" " + v), border='B', ln=1, align='R', fill=True)

    # Footer
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 10, clean_text('FlowBio Subsurface OS . Simulacion IA PIML . Documento Confidencial . www.flowbio.ai'), 0, 0, 'C')
        
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ══════════════════════════════════════════════════════
# 3. CONTROLADOR DE ESTADOS (STATE MACHINE)
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'simulated' not in st.session_state:
    st.session_state.simulated = False


# 🟢 FASE 1: PANTALLA DE ACCESO
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("ACCEDER AL SISTEMA"):
            if pwd == "FlowBio2026":
                st.session_state.auth = True
                st.rerun()
            elif pwd != "":
                st.error("Contraseña incorrecta")

# 🟡 FASE 2: PANTALLA INTERMEDIA DE SIMULACIÓN DE AGENTES
elif st.session_state.auth and not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>Orquestador de Agentes IA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8BA8C0;'>Inicia el pipeline para extraer, analizar y simular los datos del repositorio S3.</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR SIMULACIÓN Y ANÁLISIS"):
            
            # Caja visual de consola
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            pasos_agentes = [
                "📡 Conectando con AWS S3 (raw-datak-repository)...",
                "📊 Agente 1 (Ing. Datos): Extrayendo y limpiando archivos Excel...",
                "🧪 Agente 2 (Químico): Evaluando salinidad y perfil térmico...",
                "⚙️ Agente 3 (PIML): Simulando curvas de declinación y daño de formación (Skin)...",
                "🌱 Agente 4 (ESG): Calculando huella de carbono y ahorros CBAM...",
                "📈 Agente 5 (Consultor): Generando Gemelo Digital Financiero..."
            ]
            
            # Animación de los agentes trabajando
            consola_texto = ""
            for i, paso in enumerate(pasos_agentes):
                consola_texto += f"> {paso}<br>"
                status_box.markdown(f"<div class='console-box'>{consola_texto}</div>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 16)
                time.sleep(1.2) # Pausa dramática para simular el proceso
            
            # Al terminar la animación, cargamos los datos reales
            consola_texto += "<br><span style='color:#00E5A0;'>✅ Sincronización exitosa. Abriendo Command Center...</span>"
            status_box.markdown(f"<div class='console-box'>{consola_texto}</div>", unsafe_allow_html=True)
            progress_bar.progress(100)
            
            st.session_state.all_data = load_data_from_s3()
            
            if st.session_state.all_data:
                time.sleep(1.5)
                st.session_state.simulated = True
                st.rerun()
            else:
                st.error("No se pudo cargar la base de datos de S3.")

# 🔵 FASE 3: DASHBOARD PRINCIPAL (COMMAND CENTER)
elif st.session_state.auth and st.session_state.simulated:
    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.markdown("## Command Center")
    with c_logout:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 CERRAR SESIÓN"):
            st.session_state.auth = False
            st.session_state.simulated = False
            st.rerun()                     

    # --- LÓGICA DINÁMICA ---
    datos_pozos = st.session_state.all_data

    if "dashboard_data" in datos_pozos:
        datos_pozos = datos_pozos["dashboard_data"]

    lista_pozos = [k for k in datos_pozos.keys() if "Well" in k or "Pozo" in k]

    if not lista_pozos:
        st.error("⚠️ Caché obsoleto. Sincroniza desde Jupyter nuevamente.")
        st.stop()

    pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis de Declinación:", lista_pozos)
    d = datos_pozos[pozo_seleccionado]

    eur_val = d.get('eur', 0)
    barriles_extra_mes = int(eur_val / 60)
    valor_extra = barriles_extra_mes * 74.5 
    success_fee = d.get('fee', 0)
    payback_val = d.get('payback', 0)
    mejora
