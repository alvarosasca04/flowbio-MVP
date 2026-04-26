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
    body, p, div { font-family: 'Inter', -apple-system, sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    .kpi-box { background: rgba(13,21,32,0.8); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; margin-bottom:0px; }
    .kpi-value { font-size:32px; font-weight:800; color:#fff; margin:5px 0; }
    .kpi-sub   { font-size:13px; font-weight:600; color:#00E5A0; margin:0; }
    .kpi-desc  { font-size:10px; color:#8BA8C0; margin-top:5px; line-height:1.2; }
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; transition: all 0.3s ease; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0,229,160,0.4); }
    .console-box { background: #0D1520; border: 1px solid rgba(0,229,160,0.3); border-radius: 8px; padding: 20px; font-family: 'DM Mono', monospace; color: #22D3EE; }
    .diag-row { display: flex; justify-content: space-between; align-items: center; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .diag-key { color:#64748B; font-size:12px; }
    .diag-val { color:#fff; font-size:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES CORE
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        try:
            aws_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
        except Exception:
            aws_key = st.secrets["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["AWS_SECRET_ACCESS_KEY"]
        s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_sec, region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error al cargar datos desde S3. ({e})")
        return None

def calcular_kpis(proyeccion: list, ahorro: dict):
    # Valores extraídos desde el backend en Jupyter (mensuales y reales)
    if isinstance(ahorro, dict) and 'barriles' in ahorro:
        barriles_extra_mes = float(ahorro['barriles'])
        valor_extra = float(ahorro['valor_extra'])
        success_fee = float(ahorro['fee'])
        payback_val = float(ahorro['payback'])
        eur_val = float(ahorro['eur'])
    else:
        # Fallback de emergencia si el dict llega vacío
        prod_base = sum(r.get('P10',0) for r in proyeccion)/len(proyeccion) if proyeccion else 0
        prod_fb = sum(r.get('P50',0) for r in proyeccion)/len(proyeccion) if proyeccion else 0
        barriles_extra_mes = max(0, prod_fb - prod_base) * 30  # FIX: Multiplicado por 30 días
        valor_extra = barriles_extra_mes * 74.5
        success_fee = valor_extra * 0.15
        payback_val = 2.5
        eur_val = sum(r.get('P50',0)*30 for r in proyeccion)

    return {
        'eur_val': round(eur_val, 0),
        'barriles_extra_mes': round(barriles_extra_mes, 0),
        'valor_extra': round(valor_extra, 0),
        'success_fee': round(success_fee, 0),
        'payback_val': round(payback_val, 1)
    }

def clean_text(text):
    if text is None: return ""
    return str(text).replace('·','.').replace('²','2').encode('latin-1', errors='replace').decode('latin-1')

def generate_corporate_pdf(well, kpis, proyeccion):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6,11,17); pdf.rect(0,0,210,297,'F')
    pdf.set_font('Arial','B',24); pdf.set_text_color(255,255,255)
    pdf.cell(0,10,clean_text('FlowBio Executive Report'),0,1,'L')
    pdf.set_font('Arial','B',16); pdf.set_text_color(0,229,160)
    pdf.cell(0,10,clean_text(f'Pozo Analizado: {well}'),0,1,'L')
    pdf.set_draw_color(0,229,160); pdf.set_line_width(0.5); pdf.line(10,35,200,35); pdf.ln(10)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ══════════════════════════════════════════════════════
# 3. STATE MACHINE Y DASHBOARD
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state: st.session_state.auth = False
if 'simulated' not in st.session_state: st.session_state.simulated = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("ACCEDER AL SISTEMA"):
            if pwd == "FlowBio2026": st.session_state.auth = True; st.rerun()

elif st.session_state.auth and not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR SIMULACIÓN Y ANÁLISIS"):
            status_box = st.empty(); progress_bar = st.progress(0)
            pasos = ["📡 Conectando con AWS S3...", "📊 Extrayendo archivos Excel...", "🧪 Evaluando perfiles...", "⚙️ Simulando declinación...", "📈 Generando Gemelo Digital..."]
            consola = ""
            for i, paso in enumerate(pasos):
                consola += f"> {paso}<br>"
                status_box.markdown("<div class='console-box'>" + consola + "</div>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 20); time.sleep(1)
            st.session_state.all_data = load_data_from_s3()
            if st.session_state.all_data: st.session_state.simulated = True; st.rerun()

elif st.session_state.auth and st.session_state.simulated:
    c_title, c_logout = st.columns([4, 1])
    with c_title: st.markdown("## Command Center")
    with c_logout:
        if st.button("🏠 CERRAR SESIÓN"): st.session_state.auth = False; st.session_state.simulated = False; st.rerun()

    datos_pozos = st.session_state.all_data
    if "dashboard_data" in datos_pozos: datos_pozos = datos_pozos["dashboard_data"]
    lista_pozos = list(datos_pozos.keys())
    
    if not lista_pozos: st.error("⚠️ La base de datos está vacía."); st.stop()

    pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis de Declinación:", lista_pozos)
    d = datos_pozos[pozo_seleccionado]

    proyeccion = d.get('proyeccion', [])
    ahorro = d.get('ahorro', {})
    kpis = calcular_kpis(proyeccion, ahorro)

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL (MES)</p><p class="kpi-value">+{int(kpis["barriles_extra_mes"]):,}</p><p class="kpi-sub">bbls / mes</p><p class="kpi-desc">Producción incremental.</p></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA GENERADO</p><p class="kpi-value">${kpis["valor_extra"]:,.0f}</p><p class="kpi-sub">USD / mes · @$74.5/bbl</p><p class="kpi-desc">Ingreso incremental bruto.</p></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${kpis["success_fee"]:,.0f}</p><p class="kpi-sub">USD / mes · 15%</p><p class="kpi-desc">Tarifa FlowBio sobre valor incremental.</p></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{kpis["payback_val"]}</p><p class="kpi-sub">Meses</p><p class="kpi-desc">Retorno de inversión estimado.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([2.3, 1.7])

    with cl:
        x_vals = [r.get('mes', i+1) for i, r in enumerate(proyeccion)]
        chart_json = json.dumps({"x": x_vals, "p50": [r.get('P50',0) for r in proyeccion], "p10": [r.get('P10',0) for r in proyeccion], "p90": [r.get('P90',0) for r in proyeccion], "mob": [r.get('mob',0) for r in proyeccion]})
        script_grafica = (
            "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>"
            "<div id='plot' style='height:430px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05); box-shadow:0 8px 16px rgba(0,0,0,0.4);'></div>"
            "<script> var pd = " + chart_json + ";"
            "  var t_p90 = { x:pd.x, y:pd.p90, type:'scatter', mode:'lines', name:'P90 (Optimista)', line:{color:'rgba(0,229,160,0.3)', width:1}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.08)' };"
            "  var t_p50 = { x:pd.x, y:pd.p50, type:'scatter', mode:'lines+markers', name:'P50 — FlowBio', line:{color:'#00E5A0', width:3}, marker:{size:4, color:'#00E5A0'} };"
            "  var t_p10 = { x:pd.x, y:pd.p10, type:'scatter', mode:'lines', name:'P10 (Conservador)', line:{color:'rgba(100,116,139,0.6)', width:1, dash:'dot'}, fill:'tonexty', fillcolor:'rgba(100,116,139,0.05)' };"
            "  var t_mob = { x:pd.x, y:pd.mob, type:'scatter', mode:'lines', name:'Movilidad', line:{color:'#F59E0B', width:2, dash:'dash'}, yaxis:'y2' };"
            "  var layout = { paper_bgcolor:'#0D1520', plot_bgcolor:'#0D1520', font:{color:'#8BA8C0'}, title:{text:'Curva de Declinación PIML', font:{color:'#fff'}}, xaxis:{title:'Mes', gridcolor:'rgba(255,255,255,0.05)'}, yaxis:{title:'BOPD', gridcolor:'rgba(255,255,255,0.05)'}, yaxis2:{overlaying:'y', side:'right', showgrid:false}, legend:{orientation:'h', y:-0.15}, margin:{t:50, b:70, l:65, r:65} };"
            "  Plotly.newPlot('plot', [t_p10, t_p90, t_p50, t_mob], layout, {responsive:true});"
            "</script>"
        )
        components.html(script_grafica, height=450)

    with cr:
        st.markdown("<h4 style='color:#22D3EE; font-family:Syne; margin-bottom:16px;'>📊 Resumen Estadístico</h4>", unsafe_allow_html=True)
        diag_data = [
            ("Meses proyectados", f"{len(proyeccion)} meses"),
            ("P50 inicial (mes 1)", f"{proyeccion[0].get('P50',0):,.1f} BOPD" if proyeccion else "—"),
            ("P50 final", f"{proyeccion[-1].get('P50',0):,.1f} BOPD" if proyeccion else "—"),
            ("Movilidad final", f"{proyeccion[-1].get('mob',0):.3f}" if proyeccion else "—"),
            ("EUR total P50", f"{int(kpis['eur_val']):,} bbls"),
        ]
        rows_html = "".join(f"<div class='diag-row'><span class='diag-key'>{k}</span><span class='diag-val'>{v}</span></div>" for k, v in diag_data)
        st.markdown("<div style='background:#0D1520; border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:20px;'>" + rows_html + "</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(label="📄 DESCARGAR REPORTE PDF", data=generate_corporate_pdf(pozo_seleccionado, kpis, proyeccion), file_name=f"FlowBio_Report.pdf", mime="application/pdf")
