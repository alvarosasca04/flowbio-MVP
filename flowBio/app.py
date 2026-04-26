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
    .kpi-box {
        background: rgba(13,21,32,0.8);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px; padding: 22px;
        border-top: 4px solid #00E5A0; height: 100%;
    }
    .kpi-label { font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; margin-bottom:0px; }
    .kpi-value { font-size:32px; font-weight:800; color:#fff; margin:5px 0; }
    .kpi-sub   { font-size:13px; font-weight:600; color:#00E5A0; margin:0; }
    .kpi-desc  { font-size:10px; color:#8BA8C0; margin-top:5px; line-height:1.2; }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        width: 100%; transition: all 0.3s ease;
    }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0,229,160,0.4); }
    .console-box {
        background: #0D1520; border: 1px solid rgba(0,229,160,0.3);
        border-radius: 8px; padding: 20px;
        font-family: 'DM Mono', monospace; color: #22D3EE;
    }
    .diag-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
    }
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
        response = s3.get_object(
            Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an",
            Key="agentes/dashboard_data.json"
        )
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error al cargar datos desde S3. ({e})")
        return None


def clean_text(text):
    if text is None: return ""
    return str(text).replace('·','.').replace('²','2').encode('latin-1', errors='replace').decode('latin-1')


def calcular_kpis(proyeccion: list, ahorro: dict):
    """
    Calcula KPIs reales desde la estructura JSON real:
    proyeccion: lista de {mes, P50, P10, P90, mob}
    ahorro: dict con datos financieros
    """
    PRECIO_BARRIL = 74.5   # USD/bbl
    SUCCESS_FEE_PCT = 0.15  # 15% del valor generado

    # EUR = suma total de P50 durante todos los meses de proyección
    eur_val = sum(row.get('P50', 0) for row in proyeccion)

    # Producción base estimada = promedio P10 (escenario conservador sin tratamiento)
    prod_base_promedio = sum(row.get('P10', 0) for row in proyeccion) / len(proyeccion) if proyeccion else 0

    # Producción con FlowBio = promedio P50
    prod_fb_promedio = sum(row.get('P50', 0) for row in proyeccion) / len(proyeccion) if proyeccion else 0

    # Barriles incrementales por mes = diferencia entre P50 y P10
    barriles_extra_mes = max(0, prod_fb_promedio - prod_base_promedio)

    # Valor extra mensual
    valor_extra = barriles_extra_mes * PRECIO_BARRIL

    # Success fee mensual estimado
    success_fee = valor_extra * SUCCESS_FEE_PCT

    # Payback: asumiendo costo de implementación = 3 meses de success fee
    costo_impl = success_fee * 3
    payback_val = round(costo_impl / success_fee, 1) if success_fee > 0 else 0

    # Si el dict ahorro tiene overrides, los usamos
    if isinstance(ahorro, dict):
        if 'fee' in ahorro:       success_fee  = float(ahorro['fee'])
        if 'payback' in ahorro:   payback_val  = float(ahorro['payback'])
        if 'eur' in ahorro:       eur_val      = float(ahorro['eur'])
        if 'EUR' in ahorro:       eur_val      = float(ahorro['EUR'])
        if 'valor_extra' in ahorro: valor_extra = float(ahorro['valor_extra'])
        if 'barriles' in ahorro:  barriles_extra_mes = float(ahorro['barriles'])

    return {
        'eur_val':            round(eur_val, 0),
        'barriles_extra_mes': round(barriles_extra_mes, 0),
        'valor_extra':        round(valor_extra, 0),
        'success_fee':        round(success_fee, 0),
        'payback_val':        round(payback_val, 1),
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
    pdf.set_font('Arial','',10); pdf.set_text_color(139,168,192)
    pdf.cell(0,8,clean_text(f'Fecha de Simulacion: {datetime.now().strftime("%Y-%m-%d %H:%M")}'),0,1,'L')
    pdf.set_draw_color(0,229,160); pdf.set_line_width(0.5); pdf.line(10,45,200,45); pdf.ln(12)

    # Sección financiera
    pdf.set_font('Arial','B',14); pdf.set_text_color(34,211,238)
    pdf.cell(0,10,clean_text('1. IMPACTO FINANCIERO PROYECTADO'),0,1,'L'); pdf.ln(2)
    fin_data = [
        ["Crudo Incremental (Mensual):",      f"+{int(kpis['barriles_extra_mes']):,} bbls"],
        ["Valor Extra Generado (Mensual):",    f"${kpis['valor_extra']:,.0f} USD"],
        ["Tarifa por Exito (Success Fee):",    f"${kpis['success_fee']:,.0f} USD"],
        ["Retorno de Inversion (Payback):",    f"{kpis['payback_val']} Meses"],
        ["Recuperacion Total EUR (P50):",      f"{int(kpis['eur_val']):,} bbls"],
    ]
    pdf.set_fill_color(13,21,32); pdf.set_draw_color(30,41,59); pdf.set_line_width(0.2)
    for k, v in fin_data:
        pdf.set_text_color(200,200,200); pdf.set_font('Arial','',11)
        pdf.cell(100,10,clean_text(" "+k),border='B',fill=True)
        pdf.set_text_color(255,255,255); pdf.set_font('Arial','B',11)
        pdf.cell(90,10,clean_text(" "+v),border='B',ln=1,align='R',fill=True)

    pdf.ln(10)
    # Sección proyección (primeros 12 meses)
    pdf.set_font('Arial','B',14); pdf.set_text_color(34,211,238)
    pdf.cell(0,10,clean_text('2. PROYECCION DE PRODUCCION (P10 / P50 / P90)'),0,1,'L'); pdf.ln(2)
    pdf.set_font('Arial','B',10); pdf.set_text_color(0,229,160)
    for col, w in [("Mes",20),("P10 (bbls)",45),("P50 (bbls)",45),("P90 (bbls)",45),("Mob",35)]:
        pdf.cell(w,8,clean_text(col),border='B',fill=False)
    pdf.ln()
    pdf.set_font('Arial','',10)
    for row in proyeccion[:12]:
        pdf.set_text_color(200,200,200)
        pdf.cell(20,8,clean_text(str(row.get('mes',''))),border='B',fill=False)
        pdf.cell(45,8,clean_text(f"{row.get('P10',0):,.1f}"),border='B',fill=False)
        pdf.cell(45,8,clean_text(f"{row.get('P50',0):,.1f}"),border='B',fill=False)
        pdf.cell(45,8,clean_text(f"{row.get('P90',0):,.1f}"),border='B',fill=False)
        pdf.cell(35,8,clean_text(str(row.get('mob',''))),border='B',ln=1,fill=False)

    pdf.set_y(-30); pdf.set_font('Arial','I',9); pdf.set_text_color(100,116,139)
    pdf.cell(0,10,clean_text('FlowBio Subsurface OS . Simulacion IA PIML . Documento Confidencial . www.flowbio.ai'),0,0,'C')
    return pdf.output(dest='S').encode('latin-1', errors='replace')


# ══════════════════════════════════════════════════════
# 3. STATE MACHINE
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state: st.session_state.auth = False
if 'simulated' not in st.session_state: st.session_state.simulated = False

# ── FASE 1: ACCESO ───────────────────────────────────
if not st.session_state.auth:
    st.markdown(
        "<div style='text-align:center; margin-top:20vh;'>"
        "<h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1>"
        "</div>", unsafe_allow_html=True
    )
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("ACCEDER AL SISTEMA"):
            if pwd == "FlowBio2026":
                st.session_state.auth = True; st.rerun()
            elif pwd != "":
                st.error("Contraseña incorrecta")

# ── FASE 2: SIMULACIÓN ──────────────────────────────
elif st.session_state.auth and not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8BA8C0;'>Inicia el pipeline para extraer, analizar y simular los datos del repositorio S3.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR SIMULACIÓN Y ANÁLISIS"):
            status_box = st.empty(); progress_bar = st.progress(0)
            pasos = [
                "📡 Conectando con AWS S3 (raw-datak-repository)...",
                "📊 Agente 1 (Ing. Datos): Extrayendo y limpiando archivos Excel...",
                "🧪 Agente 2 (Químico): Evaluando salinidad y perfil térmico...",
                "⚙️ Agente 3 (PIML): Simulando curvas de declinación y daño de formación (Skin)...",
                "🌱 Agente 4 (ESG): Calculando huella de carbono y ahorros CBAM...",
                "📈 Agente 5 (Consultor): Generando Gemelo Digital Financiero..."
            ]
            consola = ""
            for i, paso in enumerate(pasos):
                consola += f"> {paso}<br>"
                status_box.markdown("<div class='console-box'>" + consola + "</div>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 16); time.sleep(1.2)
            consola += "<br><span style='color:#00E5A0;'>✅ Sincronización exitosa. Abriendo Command Center...</span>"
            status_box.markdown("<div class='console-box'>" + consola + "</div>", unsafe_allow_html=True)
            progress_bar.progress(100)
            st.session_state.all_data = load_data_from_s3()
            if st.session_state.all_data:
                time.sleep(1.5); st.session_state.simulated = True; st.rerun()
            else:
                st.error("No se pudo cargar la base de datos de S3.")

# ── FASE 3: COMMAND CENTER ───────────────────────────
elif st.session_state.auth and st.session_state.simulated:
    c_title, c_logout = st.columns([4, 1])
    with c_title: st.markdown("## Command Center")
    with c_logout:
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 CERRAR SESIÓN"):
            st.session_state.auth = False; st.session_state.simulated = False; st.rerun()

    datos_pozos = st.session_state.all_data
    if "dashboard_data" in datos_pozos: datos_pozos = datos_pozos["dashboard_data"]
    lista_pozos = list(datos_pozos.keys())
    if not lista_pozos: st.error("⚠️ La base de datos está vacía."); st.stop()

    pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis de Declinación:", lista_pozos)
    d = datos_pozos[pozo_seleccionado]

    # ── Extraer datos reales del JSON ──
    proyeccion = d.get('proyeccion', d.get('PROYECCION', []))
    ahorro     = d.get('ahorro', d.get('AHORRO', {}))

    if not proyeccion:
        st.error("⚠️ No se encontró la lista 'proyeccion' para este pozo.")
        st.stop()

    # ── Calcular KPIs desde datos reales ──
    kpis = calcular_kpis(proyeccion, ahorro)
    eur_val            = kpis['eur_val']
    barriles_extra_mes = kpis['barriles_extra_mes']
    valor_extra        = kpis['valor_extra']
    success_fee        = kpis['success_fee']
    payback_val        = kpis['payback_val']

    # ── KPI Cards ──
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div class="kpi-box">'
            f'<p class="kpi-label">CRUDO INCREMENTAL (MES)</p>'
            f'<p class="kpi-value">+{int(barriles_extra_mes):,}</p>'
            f'<p class="kpi-sub">bbls / mes</p>'
            f'<p class="kpi-desc">Diferencial P50 – P10 promedio.</p>'
            f'</div>', unsafe_allow_html=True)
    with k2:
        st.markdown(
            f'<div class="kpi-box">'
            f'<p class="kpi-label">VALOR EXTRA GENERADO</p>'
            f'<p class="kpi-value">${valor_extra:,.0f}</p>'
            f'<p class="kpi-sub">USD / mes · @$74.5/bbl</p>'
            f'<p class="kpi-desc">Ingreso incremental bruto mensual.</p>'
            f'</div>', unsafe_allow_html=True)
    with k3:
        st.markdown(
            f'<div class="kpi-box">'
            f'<p class="kpi-label">SUCCESS FEE</p>'
            f'<p class="kpi-value">${success_fee:,.0f}</p>'
            f'<p class="kpi-sub">USD / mes · 15%</p>'
            f'<p class="kpi-desc">Tarifa FlowBio sobre valor incremental.</p>'
            f'</div>', unsafe_allow_html=True)
    with k4:
        st.markdown(
            f'<div class="kpi-box">'
            f'<p class="kpi-label">PAYBACK</p>'
            f'<p class="kpi-value">{payback_val}</p>'
            f'<p class="kpi-sub">Meses</p>'
            f'<p class="kpi-desc">Retorno de inversión estimado.</p>'
            f'</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfica + Panel derecho (Diagnóstico) ──
    cl, cr = st.columns([2.3, 1.7])

    with cl:
        # Construir arrays para Plotly
        x_vals   = [row.get('mes', i+1) for i, row in enumerate(proyeccion)]
        p50_vals = [row.get('P50', 0)   for row in proyeccion]
        p10_vals = [row.get('P10', 0)   for row in proyeccion]
        p90_vals = [row.get('P90', 0)   for row in proyeccion]
        mob_vals = [row.get('mob', 0)   for row in proyeccion]

        chart_json = json.dumps({"x": x_vals, "p50": p50_vals, "p10": p10_vals, "p90": p90_vals, "mob": mob_vals})

        script_grafica = (
            "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>"
            "<div id='plot' style='height:430px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05); box-shadow:0 8px 16px rgba(0,0,0,0.4);'></div>"
            "<script>"
            "  var pd = " + chart_json + ";"
            "  var t_p90 = { x:pd.x, y:pd.p90, type:'scatter', mode:'lines', name:'P90 (Optimista)', line:{color:'rgba(0,229,160,0.3)', width:1}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.08)' };"
            "  var t_p50 = { x:pd.x, y:pd.p50, type:'scatter', mode:'lines+markers', name:'P50 — FlowBio', line:{color:'#00E5A0', width:3}, marker:{size:4, color:'#00E5A0'} };"
            "  var t_p10 = { x:pd.x, y:pd.p10, type:'scatter', mode:'lines', name:'P10 (Conservador)', line:{color:'rgba(100,116,139,0.6)', width:1, dash:'dot'}, fill:'tonexty', fillcolor:'rgba(100,116,139,0.05)' };"
            "  var t_mob = { x:pd.x, y:pd.mob, type:'scatter', mode:'lines', name:'Movilidad (mob)', line:{color:'#F59E0B', width:2, dash:'dash'}, yaxis:'y2' };"
            "  var layout = { paper_bgcolor:'#0D1520', plot_bgcolor:'#0D1520', font:{color:'#8BA8C0', family:'Inter'}, title:{text:'Curva de Declinación PIML — Proyección ' + pd.x.length + ' meses', font:{color:'#fff', size:14}}, xaxis:{title:'Mes', gridcolor:'rgba(255,255,255,0.05)', color:'#8BA8C0', zeroline:false}, yaxis:{title:'Producción (BOPD)', gridcolor:'rgba(255,255,255,0.05)', color:'#8BA8C0', zeroline:false}, yaxis2:{title:'Movilidad', overlaying:'y', side:'right', color:'#F59E0B', gridcolor:'rgba(245,158,11,0.1)', showgrid:false}, legend:{font:{color:'#8BA8C0'}, orientation:'h', y:-0.15}, margin:{t:50, b:70, l:65, r:65} };"
            "  Plotly.newPlot('plot', [t_p10, t_p90, t_p50, t_mob], layout, {responsive:true});"
            "</script>"
        )
        components.html(script_grafica, height=450)

    with cr:
        # ── NUEVA SECCIÓN: RECOMENDACIÓN DE INYECCIÓN QUÍMICA ──
        st.markdown("<h4 style='color:#22D3EE; font-family:Syne; margin-bottom:16px;'>🧪 Diagnóstico de Inyección CEOR</h4>", unsafe_allow_html=True)
        
        # Datos dinámicos para el diagnóstico
        ppm_optimo = int(d.get('ppm', 1200))
        lim_psi = int(d.get('lim_psi', 2800))
        bwpd = int(d.get('bwpd', 350))
        
        # Comparativa: Industria vs FlowBio
        diag_data = [
            ("Escenario Base", "<span style='color:#EF4444;'>Polímero HPAM Tradicional</span>"),
            ("Impacto ESG (HPAM)", "Alta Huella de Carbono"),
            ("Escenario FlowBio", "<span style='color:#00E5A0; font-weight:800;'>Biopolímero Avanzado (Na-CMC)</span>"),
            ("Dosificación Óptima", f"{ppm_optimo} ppm"),
            ("Caudal de Inyección", f"{bwpd} BWPD"),
            ("Presión Fractura Límite", f"{lim_psi:,} psi"),
            ("Volumen Poroso (PV)", "0.29 PV"),
            ("Estado de Compatibilidad", "Óptimo (Resistente a Salinidad)")
        ]

        rows_html = "".join(f"<div class='diag-row'><span class='diag-key'>{k}</span><span class='diag-val'>{v}</span></div>" for k, v in diag_data)
        
        st.markdown(
            f"<div style='background:#0D1520; border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:20px;'>{rows_html}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generate_corporate_pdf(pozo_seleccionado, kpis, proyeccion)
        st.download_button(
            label="📄 DESCARGAR REPORTE PDF",
            data=pdf_bytes,
            file_name=f"FlowBio_Report_{pozo_seleccionado}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
