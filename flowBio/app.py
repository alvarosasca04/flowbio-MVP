import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import math
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
    
    /* Fuentes de respaldo para evitar que cambie la tipografía */
    body, p, div { font-family: 'Inter', -apple-system, sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    
    .kpi-box { background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 0px; }
    .kpi-value { font-size: 32px; font-weight: 800; color: #fff; margin: 5px 0; }
    .kpi-desc { font-size: 10px; color: #8BA8C0; margin-top: 5px; line-height: 1.2; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES DE CORE (S3 Y PDF)
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        # Intenta ambas formas de acceder a st.secrets para mayor compatibilidad
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
        st.error(f"Error al cargar datos. Verifica credenciales o conexión a S3. ({e})")
        return None

def clean_text(text):
    """Limpia caracteres especiales antes de meterlos al PDF para evitar errores"""
    if text is None: return ""
    return str(text).replace('·', '.').replace('²', '2').encode('latin-1', errors='replace').decode('latin-1')

def generate_corporate_pdf(well, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, clean_text('FlowBio Executive Report: ' + str(well)), 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, clean_text('Fecha: ' + datetime.now().strftime("%Y-%m-%d")), 0, 1)
    pdf.ln(10)
    pdf.set_fill_color(13, 21, 32)
    
    eur_str = f"{d.get('eur', 0):,}"
    items = [
        ["PV", str(d.get('visc_p', 98.4)) + " cP"], 
        ["YP", str(d.get('yield_p', 28.9)) + " lb/ft2"], 
        ["EUR", eur_str + " bbls"], 
        ["PAYBACK", str(d.get('payback', 0)) + " Meses"]
    ]
    
    for k, v in items:
        pdf.cell(95, 12, clean_text(" " + k), 1, 0, 'L', True)
        pdf.cell(95, 12, clean_text(" " + v), 1, 1, 'R')
        
    # FIX: errors='replace' previene que la app explote con caracteres raros
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ══════════════════════════════════════════════════════
# 3. INTERFAZ DE NAVEGACIÓN Y DASHBOARD
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # PANTALLA DE ACCESO
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("SINCRONIZAR"):
            if pwd == "FlowBio2026":
                st.session_state.all_data = load_data_from_s3()
                if st.session_state.all_data:
                    st.session_state.auth = True
                    st.rerun()
else:
    # DASHBOARD PRINCIPAL
    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.markdown("## Command Center")
    with c_logout:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 CERRAR SESIÓN"):
            st.session_state.auth = False  
            st.rerun()                     

    # --- LÓGICA DINÁMICA ---
    datos_pozos = st.session_state.all_data

    # Parche de seguridad para desenvolver JSON si es necesario
    if "dashboard_data" in datos_pozos:
        datos_pozos = datos_pozos["dashboard_data"]

    # Filtro para ignorar basura en caché
    lista_pozos = [k for k in datos_pozos.keys() if "Well" in k or "Pozo" in k]

    if not lista_pozos:
        st.error("⚠️ Caché obsoleto. Por favor haz click en los 3 puntitos arriba a la derecha y selecciona 'Clear Cache'.")
        st.stop()

    # Menú desplegable de pozo
    pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis de Declinación:", lista_pozos)
    d = datos_pozos[pozo_seleccionado]

    # Cálculos financieros del pozo seleccionado (Tus cálculos exactos)
    eur_val = d.get('eur', 0)
    barriles_extra_mes = int(eur_val / 60) # EUR dividido en 60 meses
    valor_extra = barriles_extra_mes * 74.5 
    success_fee = d.get('fee', 0)
    payback_val = d.get('payback', 0)
    mejora_val = d.get('mejora', 0)

    # KPIs DINÁMICOS
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL (MES)</p><p class="kpi-value">+{barriles_extra_mes:,} <span style="font-size:16px;">bbls</span></p><p class="kpi-desc">Producción extra estimada.</p></div>', unsafe_allow_html=True)
    with k2: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA GENERADO</p><p class="kpi-value">${valor_extra:,.0f}</p><p class="kpi-desc">Ingreso adicional bruto.</p></div>', unsafe_allow_html=True)
    with k3: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${success_fee:,.0f}</p><p class="kpi-desc">Nuestra tarifa por éxito.</p></div>', unsafe_allow_html=True)
    with k4: 
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{payback_val} <span style="font-size:16px;">Meses</span></p><p class="kpi-desc">Retorno de inversión.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════════════
    # ZONA INFERIOR: GRÁFICA Y REPORTE CLÍNICO
    # ══════════════════════════════════════════════════════
    cl, cr = st.columns([2.3, 1.7])
    
    with cl:
        # Gráfica Plotly original
        script_grafica = f"""
        <script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>
        <div id='plot' style='height:400px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05);'></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i);
            var y_base = x.map(i => 350 * Math.exp(-0.06 * i)); 
            var mejora = {mejora_val} / 100;
            var y_flowbio = x.map(i => i < 5 ? y_base[i] : y_base[i] + (350 * mejora * Math.exp(-0.015 * (i-5))));
            
            var trace1 = {{x: x, y: y_base, name: 'Status Quo', line: {{color: '#EF4444', dash: 'dot'}}}};
            var trace2 = {{x: x, y: y_flowbio, name: 'FlowBio EOR', line: {{color: '#00E5A0', width: 4}}, fill: 'tonexty', fillcolor: 'rgba(0,229,160,0.1)'}};
            
            var layout = {{paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: {{color: '#64748B'}}, margin:{{t:30, b:40, l:50, r:20}} }};
            Plotly.newPlot('plot', [trace1, trace2], layout);
        </script>
        """
        components.html(script_grafica, height=420)
        
    with cr:
        # Insights Explicados leyendo S3
        html_parts = [
            "<div style='background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:415px;'>",
            "<p style='color:#00E5A0; font-weight:800; font-size:12px;'>🧠 ENGINEERING INSIGHTS</p>",
            f"<p style='font-family:\"DM Mono\"; font-size:14px; color:#22D3EE; margin-bottom:2px;'>QUÍMICO: {d.get('quimico', 'Polímero Avanzado')}</p>",
            f"<p style='font-size:11px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Concentración recomendada: {d.get('ppm', 1500)} ppm.</p>",
            f"<p style='font-family:\"DM Mono\"; font-size:14px; color:#22D3EE; margin-bottom:2px;'>CAUDAL: {d.get('bwpd', 350)} bwpd</p>",
            f"<p style='font-size:11px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Límite de fractura: Max {d.get('lim_psi', 3000)} psi.</p>",
            "<hr style='opacity:0.1; margin:15px 0;'>",
            f"<p style='color:#64748B; font-size:10px; font-weight:600;'>INCREMENTAL TOTAL (EUR):</p>",
            f"<p style='color:#00E5A0; font-size:32px; font-weight:800; margin:0;'>{d.get('eur', 0):,} <span style='font-size:14px; color:#64748B;'>bbls</span></p>",
            "</div>"
        ]
        st.markdown("".join(html_parts), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📥 DESCARGAR REPORTE PDF", data=generate_corporate_pdf(pozo_seleccionado, d), file_name=f"Reporte_FlowBio_{pozo_seleccionado}.pdf", mime="application/pdf")
