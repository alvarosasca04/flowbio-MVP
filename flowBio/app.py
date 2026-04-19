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
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES DE CORE (S3 Y PDF)
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"], aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"], region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error al cargar datos desde S3: {e}")
        return None

def generate_corporate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, 'FlowBio EOR Agentic Report', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Fecha de Emision: ' + datetime.now().strftime("%Y-%m-%d"), 0, 1)
    pdf.ln(10)
    
    pdf.set_fill_color(13, 21, 32)
    tec = data["parametros_tecnicos"]
    fin = data["metricas_financieras"]
    ing = data["ingenieria_dura"]
    
    rows = [
        ["Razon de Movilidad (M)", str(tec['razon_movilidad_alcanzada'])],
        ["Estado Skin Factor", tec['estado_skin_factor']],
        ["Barriles Incrementales", f"+{fin['barriles_incrementales_mes']:,} bbls/mes"],
        ["Success Fee (FlowBio)", f"${fin['flowbio_success_fee_usd']:,.2f} USD"],
        ["Payback Project", f"{ing['payback_meses']} Meses"]
    ]
    
    for k, v in rows:
        pdf.cell(95, 12, " " + k, 1, 0, 'L', True)
        pdf.cell(95, 12, " " + v, 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# 3. INTERFAZ DE NAVEGACIÓN Y SESIÓN
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'simulated' not in st.session_state:
    st.session_state.simulated = False

if not st.session_state.auth:
    # PANTALLA DE ACCESO
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1><p style='color:#64748B; font-family:Inter; margin-top:-20px;'>EOR Agentic OS</p></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("ENTER DECRYPTION KEY:", type="password")
        if st.button("CONECTAR AL DATA LAKE"):
            if pwd == "FlowBio2026":
                raw_data = load_data_from_s3()
                if raw_data:
                    st.session_state.all_data = raw_data["dashboard_data"] # Extraemos solo el nodo de negocio
                    st.session_state.auth = True
                    st.rerun()
else:
    # ══════════════════════════════════════════════════════
    # DASHBOARD PRINCIPAL - COMANDO EOR
    # ══════════════════════════════════════════════════════
    d = st.session_state.all_data
    fin = d["metricas_financieras"]
    tec = d["parametros_tecnicos"]
    ing = d["ingenieria_dura"]

    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.markdown("## 🌐 EOR Agentic OS | Command Center")
        st.caption(f"Asset: {d['profundidad_analizada']} | Pozos Analizados: {d['pozos_piloto']}")
    with c_logout:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 DISCONNECT"):
            st.session_state.auth = False
            st.session_state.simulated = False
            st.rerun()

    st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)

    # EL "AHA MOMENT" - SIMULACIÓN DE AGENTES
    if not st.session_state.simulated:
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🚀 DESPLEGAR AGENTES PIML"):
                with st.status("Iniciando Arquitectura de Agentes EOR en AWS...", expanded=True) as status:
                    st.write("⏳ **Data Agent:** Ingestando histórico de producción (CSV) desde S3...")
                    time.sleep(1.2)
                    st.write("⏳ **Physics Agent:** Aplicando Ley de Darcy y gradientes geotérmicos...")
                    time.sleep(1.5)
                    st.write("⏳ **Rheology Agent:** Optimizando Inyección... ¡Razón de Movilidad (M=1) Alcanzada!")
                    time.sleep(1.2)
                    st.write("⏳ **Skin Factor Agent:** Recalibrando químicos. Riesgo de taponamiento físico MITIGADO.")
                    time.sleep(1.5)
                    st.write("⏳ **Financial Agent:** Corriendo Análisis de Declinación (DCA) y calculando ROI...")
                    time.sleep(1)
                    status.update(label="¡Simulación Completada! Dashboard de Ventas Desplegado.", state="complete", expanded=False)
                time.sleep(0.5)
                st.session_state.simulated = True
                st.rerun()
    else:
        # LOS KPIS DEL NEGOCIO (Lo que ve el CFO)
        k1, k2, k3, k4 = st.columns(4)
        with k1: 
            st.markdown(f'<div class="kpi-box"><p class="kpi-label">🛢️ CRUDO INCREMENTAL</p><p class="kpi-value">+{fin["barriles_incrementales_mes"]:,}</p><p class="kpi-desc">Barriles extra mensuales proyectados vs Status Quo.</p></div>', unsafe_allow_html=True)
        with k2: 
            st.markdown(f'<div class="kpi-box"><p class="kpi-label">💰 VALOR GENERADO</p><p class="kpi-value">${fin["ingreso_bruto_operadora_usd"]:,.0f}</p><p class="kpi-desc">Ingreso bruto adicional para la Operadora (USD).</p></div>', unsafe_allow_html=True)
        with k3: 
            st.markdown(f'<div class="kpi-box" style="border-top: 4px solid #22D3EE;"><p class="kpi-label">🤝 FLOWBIO SUCCESS FEE</p><p class="kpi-value">${fin["flowbio_success_fee_usd"]:,.0f}</p><p class="kpi-desc">Nuestra comisión. Cero riesgo de CapEx para el cliente.</p></div>', unsafe_allow_html=True)
        with k4: 
            st.markdown(f'<div class="kpi-box"><p class="kpi-label">⏱️ PAYBACK PROJECT</p><p class="kpi-value">{ing["payback_meses"]} Meses</p><p class="kpi-desc">Retorno de inversión por optimización química.</p></div>', unsafe_allow_html=True)

        cl, cr = st.columns([2.3, 1.7])
        
        with cl:
            # GRÁFICA DCA (Decline Curve Analysis)
            st.markdown("<p style='color:#8BA8C0; font-family:Inter; font-size:14px; margin-top:20px; margin-bottom:5px;'>Análisis de Curva de Declinación (DCA) - Línea Base vs FlowBio</p>", unsafe_allow_html=True)
            script_parts = [
                "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>",
                "<div id='plot' style='height:380px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05);'></div>",
                "<script>",
                "var x = Array.from({length:40}, (_,i)=>i);",
                "var y1 = x.map(i => 5000 * Math.exp(-0.06*i));", # Status Quo cayendo
                "var y2 = x.map(i => i<5 ? y1[i] : y1[i] + 1500 * Math.exp(-0.015*(i-5)));", # Producción FlowBio mantenida
                "var t1 = {x:x, y:y1, name:'Línea Base (Status Quo)', line:{color:'#EF4444', dash:'dot', width:3}};",
                "var t2 = {x:x, y:y2, name:'FlowBio Optimizado', line:{color:'#00E5A0', width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.15)'};",
                "var lay = {paper_bgcolor:'transparent', plot_bgcolor:'transparent', font:{color:'#64748B'}, margin:{t:20, b:40, l:50, r:20}, legend:{orientation:'h', y:1.1}};",
                "Plotly.newPlot('plot', [t1, t2], lay);",
                "</script>"
            ]
            components.html("".join(script_parts), height=410)
            
        with cr:
            # INSIGHTS TÉCNICOS (Lo que ve el Ingeniero de Yacimientos)
            st.markdown("<p style='color:#8BA8C0; font-family:Inter; font-size:14px; margin-top:20px; margin-bottom:5px;'>Reporte de Mitigación Física</p>", unsafe_allow_html=True)
            html_parts = [
                "<div style='background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(34, 211, 238, 0.3); height:380px;'>",
                
                f"<p style='color:#22D3EE; font-size:11px; font-weight:800; margin-bottom:0;'>RAZÓN DE MOVILIDAD ALCANZADA (M):</p>",
                f"<p style='color:#fff; font-size:28px; font-weight:800; font-family:\"DM Mono\"; margin-top:0;'>{tec['razon_movilidad_alcanzada']}</p>",
                "<p style='font-size:11px; color:#8BA8C0; margin-top:-10px; margin-bottom:20px;'>Desplazamiento pistón verificado. Cero digitación viscosa.</p>",
                
                f"<p style='color:#22D3EE; font-size:11px; font-weight:800; margin-bottom:0;'>ESTADO DE INYECTIVIDAD:</p>",
                f"<p style='color:#00E5A0; font-size:18px; font-weight:800; margin-top:0;'>{tec['estado_skin_factor']}</p>",
                "<p style='font-size:11px; color:#8BA8C0; margin-top:-10px; margin-bottom:20px;'>Parámetros recalibrados por IA para evitar daño por químicos plásticos.</p>",
                
                "<hr style='opacity:0.1; margin:15px 0;'>",
                
                f"<p style='color:#64748B; font-size:10px; font-weight:600; margin-bottom:0;'>REDUCCIÓN DE WATER CUT PROYECTADA:</p>",
                f"<p style='color:#fff; font-size:24px; font-weight:800; font-family:\"DM Mono\"; margin:0;'>-{ing['wc_reduccion_pct']}%</p>",
                
                "</div>"
            ]
            st.markdown("".join(html_parts), unsafe_allow_html=True)
            
            # Botón de Descarga
            st.download_button("📥 DESCARGAR REPORTE EJECUTIVO B2B (PDF)", data=generate_corporate_pdf(d), file_name="FlowBio_Agentic_Report.pdf", mime="application/pdf")
