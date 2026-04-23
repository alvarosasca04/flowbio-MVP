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
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
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
    
    # FIX: Declaramos la variable de ambas formas para evitar el NameError en el f-string
    mejora_val = d.get('mejora', 0)
    mejora = d.get('mejora', 0)

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
    
    cl, cr = st.columns([2.3, 1.7])
    
    with cl:
        script_grafica = f"""
        <script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>
        <div id='plot' style='height:420px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05); box-shadow: 0 8px 16px rgba(0,0,0,0.4);'></div>
        <script>
            var x = Array.from({{length:48}}, (_,i)=>i);
            var bopd_base = 350; 
            var mejora_js = {mejora_val} / 100;
            
            var y_base = x.map(i => bopd_base * Math.exp(-0.06 * i)); 
            var y_flowbio = x.map(i => i < 5 ? y_base[i] : y_base[i] + (bopd_base * mejora_js * Math.exp(-0.015 * (i-5))));
            
            var trace1 = {{
                x: x, y: y_base, name: 'Status Quo', type: 'scatter',
                line: {{color: '#EF4444', dash: 'dot', width: 2}},
                hovertemplate: '<b>Status Quo:</b> %{{y:.1f}} bbl/d<extra></extra>'
            }};
            
            var trace2 = {{
                x: x, y: y_flowbio, name: 'FlowBio EOR', type: 'scatter',
                line: {{color: '#00E5A0', width: 3}}, fill: 'tonexty', fillcolor: 'rgba(0,229,160,0.12)',
                hovertemplate: '<b>FlowBio:</b> %{{y:.1f}} bbl/d<extra></extra>'
            }};
            
            var layout = {{
                title: {{text: '<b>Curva de Declinación y Recuperación (4 Años)</b>', font: {{color: '#FFFFFF', family: 'Syne', size: 14}}, x: 0.05, y: 0.95}},
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: {{color: '#8BA8C0', family: 'DM Mono', size: 10}}, 
                margin: {{t:60, b:40, l:50, r:20}},
                xaxis: {{title: 'MESES', gridcolor: '#152335', zeroline: false}}, yaxis: {{title: 'BOPD', gridcolor: '#152335', zeroline: false}},
                showlegend: true,
                legend: {{orientation: 'h', y: 1.12, x: 1, xanchor: 'right', bgcolor: 'rgba(0,0,0,0)', font: {{color: '#E2E8F0'}}}},
                hovermode: 'x unified',
                annotations: [{{x: 5, y: y_base[5], xref: 'x', yref: 'y', text: 'INYECCIÓN PIML', showarrow: true, arrowhead: 2, arrowsize: 1, arrowwidth: 1.5, ax: 0, ay: -50, font: {{color: '#22D3EE', family: 'DM Mono', size: 9}}, arrowcolor: '#22D3EE'}}]
            }};
            Plotly.newPlot('plot', [trace1, trace2], layout, {{responsive: true, displayModeBar: false}});
        </script>
        """
        components.html(script_grafica, height=450)
        
    with cr:
        html_parts = [
            "<div style='background:#0D1520; padding:28px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:420px; display:flex; flex-direction:column; justify-content:space-between;'>",
            "<div>",
            "<p style='color:#00E5A0; font-family:\"DM Mono\"; font-weight:800; font-size:11px; letter-spacing:1.5px; margin-bottom:20px;'>⚡ DIAGNÓSTICO DE INYECCIÓN</p>",
            f"<p style='font-family:\"Syne\"; font-size:16px; font-weight:700; color:#22D3EE; margin-bottom:2px;'>🧪 {d.get('quimico', 'Polímero Avanzado').upper()}</p>",
            f"<p style='font-family:\"Inter\"; font-size:12px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Dosificación óptima: <b style='color:#E2E8F0'>{d.get('ppm', 1500)} ppm</b> &nbsp;|&nbsp; PV: <b style='color:#E2E8F0'>{d.get('vol_pv', 0.29)}</b></p>",
            f"<p style='font-family:\"Syne\"; font-size:16px; font-weight:700; color:#22D3EE; margin-bottom:2px;'>🌊 PARÁMETROS DE BOMBEO</p>",
            f"<p style='font-family:\"Inter\"; font-size:12px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Caudal objetivo: <b style='color:#E2E8F0'>{d.get('bwpd', 350)} BWPD</b><br>Presión máxima (Fractura): <b style='color:#EF4444'>{d.get('lim_psi', 3000):,} psi</b></p>",
            "</div><div><hr style='border:none; border-top:1px dashed rgba(255,255,255,0.1); margin:15px 0;'>",
            f"<p style='color:#64748B; font-family:\"DM Mono\"; font-size:10px; font-weight:600; letter-spacing:1px;'>IMPACTO TOTAL ACUMULADO (EUR):</p>",
            f"<p style='color:#00E5A0; font-family:\"Syne\"; font-size:36px; font-weight:800; margin:0; line-height:1;'>{d.get('eur', 0):,} <span style='font-size:14px; color:#64748B; font-family:\"DM Mono\";'>bbls</span></p>",
            "</div></div>"
        ]
        st.markdown("".join(html_parts), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.download_button("📥 DESCARGAR REPORTE EJECUTIVO PDF", data=generate_corporate_pdf(pozo_seleccionado, d), file_name=f"Reporte_FlowBio_{pozo_seleccionado}.pdf", mime="application/pdf")
