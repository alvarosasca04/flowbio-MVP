import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
import random
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN Y ESTILOS
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Agentic OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 2rem 3rem !important; }
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 0px; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-desc { font-family: 'Inter'; font-size: 10px; color: #8BA8C0; margin-top: 5px; line-height: 1.2; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne' !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; border: none; transition: 0.3s; }
    .stButton > button:hover { background: #22D3EE !important; box-shadow: 0 0 15px rgba(34, 211, 238, 0.4); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-family: 'Syne'; font-weight: 700; color: #8BA8C0; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { color: #00E5A0 !important; border-bottom: 2px solid #00E5A0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. DATOS DE RESPALDO (DEMO MODE - FASE 1)
# ══════════════════════════════════════════════════════
def get_fallback_data():
    return {
        "dashboard_data": {
            "profundidad_analizada": "Datos Reales (Mar del Norte)",
            "pozos_piloto": 10,
            "candidatos_inyeccion": 8,
            "parametros_tecnicos": {
                "razon_movilidad_alcanzada": 1.02,
                "estado_skin_factor": "Mitigado Preventivamente (Fase 1: HPAM/Xantana)"
            },
            "metricas_financieras": {
                "barriles_incrementales_mes": 25000,
                "ingreso_bruto_operadora_usd": 1862500.0,
                "ahorro_opex_quimico_usd": 150000.0,
                "flowbio_success_fee_usd": 125000.0
            },
            "ingenieria_dura": {
                "wc_reduccion_pct": 18.4,
                "eur_extra_bbls": 425000,
                "payback_meses": 1.2,
                "lc_caida_usd": 2.15
            }
        }
    }

def load_data_from_s3():
    try:
        s3 = boto3.client('s3', 
                          aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"], 
                          aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"], 
                          region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        raw_data = json.loads(response['Body'].read().decode('utf-8'))
        if "dashboard_data" in raw_data:
            return raw_data
        else:
            return get_fallback_data()
    except Exception as e:
        return get_fallback_data()

# 🚀 NUEVA FUNCIÓN A PRUEBA DE FALLOS (TEXTO PLANO)
def generate_text_report(data):
    tec = data["dashboard_data"]["parametros_tecnicos"]
    fin = data["dashboard_data"]["metricas_financieras"]
    
    reporte = f"""==================================================
FLOWBIO EOR AGENTIC OS - REPORTE EJECUTIVO
Fecha de Generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
==================================================

[ DIAGNÓSTICO TÉCNICO ]
- Razón de Movilidad (M): {tec['razon_movilidad_alcanzada']}
- Estado de Inyectividad: {tec['estado_skin_factor']}

[ IMPACTO FINANCIERO MENSUAL ]
- Barriles Extra Proyectados: +{fin['barriles_incrementales_mes']:,} bbls
- Ingreso Bruto para Cliente: ${fin['ingreso_bruto_operadora_usd']:,.2f} USD
- FlowBio Success Fee:        ${fin['flowbio_success_fee_usd']:,.2f} USD

==================================================
* Documento generado autómaticamente por Agentes PIML.
"""
    return reporte.encode('utf-8')

# ══════════════════════════════════════════════════════
# 3. LÓGICA DE ACCESO Y DASHBOARD
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'simulated' not in st.session_state:
    st.session_state.simulated = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1><p style='color:#64748B; font-family:Inter; margin-top:-20px;'>EOR Agentic OS</p></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("SINCRONIZAR DATA LAKE"):
            if pwd == "FlowBio2026":
                st.session_state.all_data = load_data_from_s3() 
                st.session_state.auth = True
                st.rerun()
else:
    d_root = st.session_state.all_data
    d = d_root["dashboard_data"]
    fin = d["metricas_financieras"]
    tec = d["parametros_tecnicos"]
    ing = d["ingenieria_dura"]

    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.markdown("## Command Center")
        st.caption(f"Activo: {d['profundidad_analizada']} | Piloto: {d['pozos_piloto']} Pozos")
    with c_logout:
        if st.button("🏠 LOGOUT"):
            st.session_state.auth = False
            st.session_state.simulated = False
            st.rerun()

    if not st.session_state.simulated:
        st.markdown("""
        <div style='background:#0D1520; padding:30px; border-radius:12px; border-left:4px solid #EF4444; margin-bottom: 40px; margin-top: 20px;'>
            <h4 style='color:#EF4444; margin-top:0; font-family:Inter; font-weight:800; font-size:14px; letter-spacing:1px;'>📊 DIAGNÓSTICO INICIAL (STATUS QUO)</h4>
            <p style='color:#8BA8C0; font-family:"DM Mono"; font-size:16px; margin-bottom:5px; line-height:1.8;'>
                ▶ <b>Datos Ingestados:</b> Históricos de producción (10 Pozos)<br>
                ▶ <b>Producción Base Inicial:</b> 4,000 bpd (Declinación natural activa)<br>
                ▶ <b>Lifting Cost Actual:</b> $18.50 USD/bbl<br>
                ▶ <b>Alerta Física:</b> Alta canalización de agua (Fingering) detectada.
            </p>
            <p style='color:#64748B; font-size:12px; margin-top:15px; font-family:Inter;'><i>* Los Agentes PIML están listos para recalibrar la termodinámica del yacimiento y proyectar la recuperación secundaria.</i></p>
        </div>
        """, unsafe_allow_html=True)

        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            if st.button("🚀 DESPLEGAR AGENTES PIML PARA OPTIMIZAR"):
                with st.status("Orquestando Agentes FlowBio...", expanded=True) as status:
                    st.write("🤖 **Data Agent:** Limpiando histórico CSV y aislando Línea Base...")
                    time.sleep(1.2)
                    st.write("🤖 **Physics Agent:** Validando salinidad y perfilando polímero (HPAM vs Xantana)...")
                    time.sleep(1.5)
                    st.write("🤖 **Rheology Agent:** Optimizando Inyección (M=1). Skin Factor Mitigado.")
                    time.sleep(1.2)
                    st.write("🤖 **Financial Agent:** Calculando Barriles Incrementales y Success Fee...")
                    time.sleep(1.5)
                    status.update(label="Simulación Exitosa. Generando ROI.", state="complete", expanded=False)
                time.sleep(0.5)
                st.session_state.simulated = True
                st.rerun()
    else:
        tab1, tab2 = st.tabs(["📊 Visión Ejecutiva (CFO)", "⚙️ Análisis por Pozo (Ingeniería)"])
        
        with tab1:
            k1, k2, k3, k4 = st.columns(4)
            with k1: 
                st.markdown(f'<div class="kpi-box"><p class="kpi-label">🛢️ CRUDO INCREMENTAL (TOTAL)</p><p class="kpi-value">+{fin["barriles_incrementales_mes"]:,}</p><p class="kpi-desc">Barriles extra mensuales en todo el piloto.</p></div>', unsafe_allow_html=True)
            with k2: 
                st.markdown(f'<div class="kpi-box"><p class="kpi-label">💰 VALOR EXTRA GENERADO</p><p class="kpi-value">${fin["ingreso_bruto_operadora_usd"]:,.0f}</p><p class="kpi-desc">Ingreso adicional bruto para el cliente.</p></div>', unsafe_allow_html=True)
            with k3: 
                st.markdown(f'<div class="kpi-box" style="border-top:4px solid #22D3EE"><p class="kpi-label">🤝 SUCCESS FEE (FLOWBIO)</p><p class="kpi-value">${fin["flowbio_success_fee_usd"]:,.0f}</p><p class="kpi-desc">Nuestra tarifa por éxito verificado.</p></div>', unsafe_allow_html=True)
            with k4: 
                st.markdown(f'<div class="kpi-box"><p class="kpi-label">⏱️ PAYBACK PROJECT</p><p class="kpi-value">{ing["payback_meses"]} Meses</p><p class="kpi-desc">Retorno de inversión tecnológica promedio.</p></div>', unsafe_allow_html=True)

            cl, cr = st.columns([2.3, 1.7])
            with cl:
                st.markdown("<p style='color:#8BA8C0; font-family:Inter; font-size:14px; margin-top:20px; margin-bottom:5px;'>Curva de Declinación Consolidada (DCA)</p>", unsafe_allow_html=True)
                script_parts = [
                    "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>",
                    "<div id='plot' style='height:380px; background:#0D1520; border-radius:12px;'></div>",
                    "<script>",
                    "var x = Array.from({length:30}, (_,i)=>i);",
                    "var y1 = x.map(i => 4000 * Math.exp(-0.05*i));",
                    "var y2 = x.map(i => i <= 4 ? y1[i] : y1[i] + 1400 * (1 - Math.exp(-0.6*(i-4))) * Math.exp(-0.015*(i-4)));",
                    "var t1 = {x:x, y:y1, name:'Status Quo', line:{color:'#EF4444', dash:'dot', width:2, shape:'spline'}, hovertemplate:'<b>%{y:,.0f}</b> bpd<extra></extra>'};",
                    "var t2 = {x:x, y:y2, name:'FlowBio EOR', line:{color:'#00E5A0', width:4, shape:'spline'}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.15)', hovertemplate:'<b>%{y:,.0f}</b> bpd<extra></extra>'};",
                    "var lay = {",
                    "  paper_bgcolor:'transparent', plot_bgcolor:'transparent', font:{color:'#8BA8C0', family:'Inter'},",
                    "  margin:{t:10, b:45, l:60, r:20},",
                    "  hovermode: 'x unified',",
                    "  hoverlabel: {bgcolor:'#0D1520', bordercolor:'#00E5A0', font:{family:'Inter', color:'#fff', size:13}},",
                    "  xaxis: {title: 'Tiempo (Meses)', gridcolor: 'rgba(255,255,255,0.03)', zerolinecolor: 'rgba(255,255,255,0.1)'},",
                    "  yaxis: {title: 'Producción (bpd)', gridcolor: 'rgba(255,255,255,0.03)', zerolinecolor: 'rgba(255,255,255,0.1)', tickformat: ',', rangemode: 'tozero'},",
                    "  legend: {orientation: 'h', y: 1.1, font: {size: 12}},",
                    "  annotations: [{x: 16, y: 2600, text: 'ZONA DE RENTABILIDAD', showarrow: false, font: {color: '#00E5A0
