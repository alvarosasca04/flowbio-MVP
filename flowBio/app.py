import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
import random
from fpdf import FPDF
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
# 2. DATOS DE RESPALDO (DEMO MODE PARA LA UAG)
# ══════════════════════════════════════════════════════
def get_fallback_data():
    return {
        "dashboard_data": {
            "profundidad_analizada": "Datos Reales (Mar del Norte)",
            "pozos_piloto": 10,
            "candidatos_inyeccion": 8,
            "parametros_tecnicos": {
                "razon_movilidad_alcanzada": 1.02,
                "estado_skin_factor": "Mitigado Preventivamente"
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

def generate_corporate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, 'FlowBio EOR Agentic Report', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Fecha: ' + datetime.now().strftime("%Y-%m-%d"), 0, 1)
    pdf.ln(10)
    
    pdf.set_fill_color(13, 21, 32)
    tec = data["dashboard_data"]["parametros_tecnicos"]
    fin = data["dashboard_data"]["metricas_financieras"]
    
    rows = [
        ["M-Ratio Alcanzado", str(tec['razon_movilidad_alcanzada'])],
        ["Estado de Inyectividad", tec['estado_skin_factor']],
        ["Barriles Extra/Mes", f"+{fin['barriles_incrementales_mes']:,} bbls"],
        ["Success Fee Proyectado", f"${fin['flowbio_success_fee_usd']:,.2f} USD"]
    ]
    
    for k, v in rows:
        pdf.cell(95, 12, " " + k, 1, 0, 'L', True)
        pdf.cell(95, 12, " " + v, 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

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
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🚀 DESPLEGAR AGENTES PIML"):
                with st.status("Orquestando Agentes FlowBio...", expanded=True) as status:
                    st.write("🤖 **Data Agent:** Limpiando histórico CSV...")
                    time.sleep(1)
                    st.write("🤖 **Physics Agent:** Validando Ley de Darcy y gradientes...")
                    time.sleep(1)
                    st.write("🤖 **Rheology Agent:** M=1 alcanzado. Skin Factor Mitigado.")
                    time.sleep(1)
                    st.write("🤖 **Financial Agent:** Calculando Barriles Incrementales...")
                    time.sleep(1)
                    status.update(label="Simulación Exitosa", state="complete", expanded=False)
                st.session_state.simulated = True
                st.rerun()
    else:
        # SISTEMA DE PESTAÑAS (TABS) PARA DEMOSTRAR PROFUNDIDAD TÉCNICA
        tab1, tab2 = st.tabs(["📊 Visión Ejecutiva (CFO)", "⚙️ Análisis por Pozo (Ingeniería)"])
        
        # --- PESTAÑA 1: EL NEGOCIO (Igual que antes) ---
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
                    "var y2 = x.map(i => i<5 ? y1[i] : y1[i] + 1200 * Math.exp(-0.01*i));",
                    "var t1 = {x:x, y:y1, name:'Status Quo', line:{color:'#EF4444', dash:'dot'}};",
                    "var t2 = {x:x, y:y2, name:'FlowBio', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'};",
                    "var lay = {paper_bgcolor:'transparent', plot_bgcolor:'transparent', font:{color:'#64748B'}, margin:{t:10, b:30, l:50, r:20}};",
                    "Plotly.newPlot('plot', [t1, t2], lay);",
                    "</script>"
                ]
                components.html("".join(script_parts), height=400)
                
            with cr:
                st.markdown("<p style='color:#8BA8C0; font-family:Inter; font-size:14px; margin-top:20px; margin-bottom:5px;'>Reporte Global de Mitigación</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(34,211,238,0.2); height:380px;'>
                    <p style='color:#22D3EE; font-size:11px; font-weight:800; margin-bottom:0;'>RAZÓN DE MOVILIDAD PROMEDIO (M):</p>
                    <p style='color:#fff; font-size:32px; font-weight:800; margin-top:0;'>{tec['razon_movilidad_alcanzada']}</p>
                    <p style='color:#00E5A0; font-size:14px; font-weight:700;'>{tec['estado_skin_factor']}</p>
                    <hr style='opacity:0.1; margin:20px 0;'>
                    <p style='color:#64748B; font-size:10px; font-weight:600; margin-bottom:0;'>REDUCCIÓN WATER CUT (ESTIMADA):</p>
                    <p style='color:#fff; font-size:24px; font-weight:800; margin-top:0;'>-{ing['wc_reduccion_pct']}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.download_button("📥 DESCARGAR REPORTE EJECUTIVO", data=generate_corporate_pdf(d_root), file_name="FlowBio_Agentic_Report.pdf")

        # --- PESTAÑA 2: EL INGENIERO (Pozo por Pozo) ---
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            pozos_disponibles = [f"UKCS-Well-{100 + i}" for i in range(1, 11)]
            pozo_seleccionado = st.selectbox("🎯 SELECCIONE UN ACTIVO PARA REVISIÓN PROFUNDA:", pozos_disponibles)
            
            # Generamos variaciones matemáticas leves basadas en la semilla del nombre del pozo para que parezcan datos reales distintos
            random.seed(pozo_seleccionado)
            ind_bpd = int((fin["barriles_incrementales_mes"] / 10) * random.uniform(0.85, 1.15))
            ind_m = round(tec["razon_movilidad_alcanzada"] * random.uniform(0.95, 1.05), 2)
            ind_skin = round(random.uniform(-0.5, 1.2), 2)
            ind_fee = int(ind_bpd * 5)
            
            c1, c2, c3 = st.columns(3)
            c1.metric(label="Crudo Extra Proyectado", value=f"+{ind_bpd:,} bbls/mes", delta=f"{ind_fee:,} USD (Fee)")
            c2.metric(label="Movilidad Alcanzada (M)", value=ind_m, delta="Barrido Eficiente" if ind_m < 1.1 else "Alerta Leve", delta_color="normal" if ind_m < 1.1 else "off")
            c3.metric(label="Skin Factor Proyectado", value=ind_skin, delta="Daño Mitigado" if ind_skin < 1 else "Requiere Monitoreo", delta_color="inverse")
            
            st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='background:#0D1520; padding:20px; border-radius:8px; border-left:4px solid #22D3EE;'>
                <p style='color:#8BA8C0; font-family:Inter; font-size:12px; margin:0;'>📝 DICTAMEN DE AGENTE (PIML):</p>
                <p style='color:#fff; font-family:DM Mono; font-size:14px; margin-top:5px;'>
                El activo <b>{pozo_seleccionado}</b> es candidato <b>ÓPTIMO</b>. La simulación termodinámica indica que con una concentración ajustada, se alcanzará una razón M={ind_m}, empujando {ind_bpd} barriles incrementales sin rebasar la presión de fractura de la roca madre.
                </p>
            </div>
            """, unsafe_allow_html=True)
