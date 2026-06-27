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
    .kpi-box-cyan { border-top-color: #22D3EE !important; }
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
    .resumen-bar {
        background: rgba(0,229,160,0.05);
        border: 1px solid rgba(0,229,160,0.15);
        border-radius: 10px; padding: 14px 20px;
        margin-bottom: 20px;
        display: flex; gap: 40px; flex-wrap: wrap;
    }
    .resumen-item { display: flex; flex-direction: column; }
    .resumen-label { font-size: 10px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .resumen-val   { font-size: 18px; font-weight: 800; color: #00E5A0; font-family: 'Syne', sans-serif; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. CARGA DESDE S3
# ══════════════════════════════════════════════════════
def load_data_from_s3():
    try:
        try:
            aws_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
        except Exception:
            aws_key = st.secrets["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["AWS_SECRET_ACCESS_KEY"]
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_sec,
            region_name="us-east-2"
        )
        response = s3.get_object(
            Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an",
            Key="agentes/dashboard_data.json"
        )
        return json.loads(response["Body"].read().decode("utf-8"))
    except Exception as e:
        st.error(f"Error al cargar datos desde S3: {e}")
        return None

# ══════════════════════════════════════════════════════
# 3. ADAPTADOR DE ESTRUCTURA JSON
#    Soporta tanto el formato nuevo (flowbio_pipeline.py)
#    como el formato viejo (main.py)
# ══════════════════════════════════════════════════════
def extraer_pozos(raw: dict):
    """
    Nuevo formato (flowbio_pipeline.py):
      { "_resumen": {...}, "Pozo X (#1)": { "proyeccion": [...], "kpis": {...} } }

    Formato viejo (main.py / Jupyter):
      { "dashboard_data": { "pozo": { "proyeccion": [...], "ahorro": {...} } } }
      o directamente { "pozo": { "proyeccion": [...], "ahorro": {...} } }
    """
    # Desenvolver wrapper legacy
    if "dashboard_data" in raw:
        raw = raw["dashboard_data"]

    resumen = raw.get("_resumen", {})
    pozos = {k: v for k, v in raw.items() if k != "_resumen"}
    return pozos, resumen


def extraer_kpis_pozo(d: dict):
    """
    Extrae KPIs del pozo independientemente del formato del JSON.
    Nuevo: d["kpis"] con claves valor_extra_usd, fee_usd, barriles_mes, payback_meses, eur_bbls
    Viejo: d["ahorro"] con claves valor_extra, fee, barriles, payback, eur
    """
    proyeccion = d.get("proyeccion", [])

    # Intentar formato nuevo primero
    kpis_raw = d.get("kpis", d.get("ahorro", {}))

    # Mapeo flexible de nombres de campos
    def get(keys, default=0):
        for k in keys:
            if k in kpis_raw:
                return float(kpis_raw[k])
        return default

    barriles  = get(["barriles_mes", "barriles"], 0)
    valor     = get(["valor_extra_usd", "valor_extra"], 0)
    fee       = get(["fee_usd", "fee"], 0)
    payback   = get(["payback_meses", "payback"], 3.0)
    eur       = get(["eur_bbls", "eur", "EUR"], 0)
    m_ratio   = get(["M_ratio"], 0)

    # Si no hay kpis precalculados, calcular desde proyeccion
    if barriles == 0 and proyeccion:
        p50_prom = sum(r.get("P50", 0) for r in proyeccion) / len(proyeccion)
        p10_prom = sum(r.get("P10", 0) for r in proyeccion) / len(proyeccion)
        barriles = max(0, p50_prom - p10_prom)
        valor    = barriles * 74.5
        fee      = valor * 0.15
        eur      = sum(r.get("P50", 0) for r in proyeccion)

    return {
        "barriles_mes": round(barriles, 0),
        "valor_extra":  round(valor, 0),
        "success_fee":  round(fee, 0),
        "payback_val":  round(payback, 1),
        "eur_val":      round(eur, 0),
        "M_ratio":      round(m_ratio, 3),
        "proyeccion":   proyeccion,
    }

# ══════════════════════════════════════════════════════
# 4. PDF
# ══════════════════════════════════════════════════════
def clean_text(text):
    if text is None: return ""
    return str(text).replace("·", ".").replace("²", "2").encode("latin-1", errors="replace").decode("latin-1")

def generate_pdf(well, kpis, proyeccion):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17); pdf.rect(0, 0, 210, 297, "F")
    pdf.set_font("Arial", "B", 24); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, clean_text("FlowBio Executive Report"), 0, 1, "L")
    pdf.set_font("Arial", "B", 16); pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 10, clean_text(f"Pozo: {well}"), 0, 1, "L")
    pdf.set_font("Arial", "", 10); pdf.set_text_color(139, 168, 192)
    pdf.cell(0, 8, clean_text(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), 0, 1, "L")
    pdf.set_draw_color(0, 229, 160); pdf.line(10, 45, 200, 45); pdf.ln(12)

    pdf.set_font("Arial", "B", 14); pdf.set_text_color(34, 211, 238)
    pdf.cell(0, 10, "IMPACTO FINANCIERO PROYECTADO", 0, 1, "L"); pdf.ln(2)
    for k, v in [
        ("Crudo Incremental (Mensual):",   f"+{int(kpis['barriles_mes']):,} bbls"),
        ("Valor Extra Generado:",           f"${kpis['valor_extra']:,.0f} USD"),
        ("Success Fee FlowBio:",            f"${kpis['success_fee']:,.0f} USD"),
        ("Payback:",                        f"{kpis['payback_val']} Meses"),
        ("EUR Total (P50):",               f"{int(kpis['eur_val']):,} bbls"),
    ]:
        pdf.set_text_color(200, 200, 200); pdf.set_font("Arial", "", 11)
        pdf.cell(100, 10, clean_text(" " + k), border="B", fill=False)
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 11)
        pdf.cell(90, 10, clean_text(" " + v), border="B", ln=1, align="R")

    pdf.ln(10); pdf.set_font("Arial", "B", 14); pdf.set_text_color(34, 211, 238)
    pdf.cell(0, 10, "PROYECCION DE PRODUCCION (12 meses)", 0, 1, "L"); pdf.ln(2)
    pdf.set_font("Arial", "B", 10); pdf.set_text_color(0, 229, 160)
    for col, w in [("Mes", 20), ("P10", 45), ("P50", 45), ("P90", 45), ("Mob", 35)]:
        pdf.cell(w, 8, col, border="B")
    pdf.ln()
    pdf.set_font("Arial", "", 10); pdf.set_text_color(200, 200, 200)
    for row in proyeccion[:12]:
        pdf.cell(20, 8, clean_text(str(row.get("mes", ""))), border="B")
        pdf.cell(45, 8, clean_text(f"{row.get('P10', 0):,.1f}"), border="B")
        pdf.cell(45, 8, clean_text(f"{row.get('P50', 0):,.1f}"), border="B")
        pdf.cell(45, 8, clean_text(f"{row.get('P90', 0):,.1f}"), border="B")
        pdf.cell(35, 8, clean_text(str(row.get("mob", ""))), border="B", ln=1)

    pdf.set_y(-30); pdf.set_font("Arial", "I", 9); pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 10, clean_text("FlowBio Subsurface OS · Simulacion IA PIML · Confidencial"), 0, 0, "C")
    return pdf.output(dest="S").encode("latin-1", errors="replace")

# ══════════════════════════════════════════════════════
# 5. STATE MACHINE
# ══════════════════════════════════════════════════════
if "auth"      not in st.session_state: st.session_state.auth      = False
if "simulated" not in st.session_state: st.session_state.simulated = False

# ── FASE 1: LOGIN ────────────────────────────────────
if not st.session_state.auth:
    st.markdown(
        "<div style='text-align:center; margin-top:20vh;'>"
        "<h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1>"
        "<p style='color:#64748B; font-family:Inter; margin-top:-20px;'>EOR Agentic OS</p>"
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
elif not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8BA8C0;'>Pipeline de agentes IA conectado al Data Lake S3.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR SIMULACIÓN Y ANÁLISIS"):
            status_box = st.empty(); progress_bar = st.progress(0)
            pasos = [
                "📡 Conectando con AWS S3...",
                "📊 Agente 1: Extrayendo y limpiando datos de pozos...",
                "🧪 Agente 2: Evaluando salinidad y perfil térmico...",
                "⚙️  Agente 3 (PIML): Simulando curvas de declinación...",
                "🌱 Agente 4 (ESG): Calculando huella de carbono...",
                "📈 Agente 5: Generando Gemelo Digital Financiero...",
            ]
            consola = ""
            for i, paso in enumerate(pasos):
                consola += f"> {paso}<br>"
                status_box.markdown(f"<div class='console-box'>{consola}</div>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 16); time.sleep(1.2)
            consola += "<br><span style='color:#00E5A0;'>✅ Sincronización exitosa. Abriendo Command Center...</span>"
            status_box.markdown(f"<div class='console-box'>{consola}</div>", unsafe_allow_html=True)
            progress_bar.progress(100)
            st.session_state.all_data = load_data_from_s3()
            if st.session_state.all_data:
                time.sleep(1.5); st.session_state.simulated = True; st.rerun()
            else:
                st.error("No se pudo cargar la base de datos de S3.")

# ── FASE 3: COMMAND CENTER ───────────────────────────
else:
    c_title, c_logout = st.columns([4, 1])
    with c_title: st.markdown("## Command Center")
    with c_logout:
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 CERRAR SESIÓN"):
            st.session_state.auth = False; st.session_state.simulated = False; st.rerun()

    # Adaptar estructura al formato nuevo o viejo
    pozos, resumen = extraer_pozos(st.session_state.all_data)
    lista_pozos = list(pozos.keys())
    if not lista_pozos:
        st.error("La base de datos está vacía."); st.stop()

    # Barra de resumen global (solo si viene del pipeline nuevo)
    if resumen:
        st.markdown(
            f"<div class='resumen-bar'>"
            f"<div class='resumen-item'><span class='resumen-label'>Pozos analizados</span><span class='resumen-val'>{resumen.get('pozos_analizados','—')}</span></div>"
            f"<div class='resumen-item'><span class='resumen-label'>Crudo extra total / mes</span><span class='resumen-val'>+{int(resumen.get('total_bbls_extra_mes',0)):,} bbls</span></div>"
            f"<div class='resumen-item'><span class='resumen-label'>Ingreso operadora</span><span class='resumen-val'>${resumen.get('ingreso_operadora_usd',0):,.0f}</span></div>"
            f"<div class='resumen-item'><span class='resumen-label'>FlowBio Fee</span><span class='resumen-val'>${resumen.get('flowbio_fee_usd',0):,.0f}</span></div>"
            f"<div class='resumen-item'><span class='resumen-label'>Movilidad promedio (M)</span><span class='resumen-val'>{resumen.get('M_promedio','—')}</span></div>"
            f"</div>",
            unsafe_allow_html=True
        )

    pozo_sel = st.selectbox("📍 Seleccione un pozo para análisis:", lista_pozos)
    kpis = extraer_kpis_pozo(pozos[pozo_sel])
    proyeccion = kpis["proyeccion"]

    if not proyeccion:
        st.error("No se encontró proyección para este pozo."); st.stop()

    # KPI Cards
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL (MES)</p><p class="kpi-value">+{int(kpis["barriles_mes"]):,}</p><p class="kpi-sub">bbls / mes</p><p class="kpi-desc">Diferencial P50 – P10 promedio.</p></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA GENERADO</p><p class="kpi-value">${kpis["valor_extra"]:,.0f}</p><p class="kpi-sub">USD / mes · @$74.5/bbl</p><p class="kpi-desc">Ingreso incremental bruto mensual.</p></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-box kpi-box-cyan"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${kpis["success_fee"]:,.0f}</p><p class="kpi-sub">USD / mes</p><p class="kpi-desc">Tarifa FlowBio sobre valor incremental.</p></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{kpis["payback_val"]}</p><p class="kpi-sub">Meses</p><p class="kpi-desc">Retorno de inversión estimado.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([2.3, 1.7])

    with cl:
        x_vals   = [r.get("mes", i+1)  for i, r in enumerate(proyeccion)]
        p50_vals = [r.get("P50", 0)    for r in proyeccion]
        p10_vals = [r.get("P10", 0)    for r in proyeccion]
        p90_vals = [r.get("P90", 0)    for r in proyeccion]
        mob_vals = [r.get("mob", 0)    for r in proyeccion]
        chart_json = json.dumps({"x": x_vals, "p50": p50_vals, "p10": p10_vals, "p90": p90_vals, "mob": mob_vals})
        components.html(
            "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>"
            "<div id='plot' style='height:430px;background:#0D1520;border-radius:12px;border:1px solid rgba(255,255,255,0.05);'></div>"
            "<script>"
            "var pd=" + chart_json + ";"
            "Plotly.newPlot('plot',["
            "{x:pd.x,y:pd.p10,name:'P10 (Conservador)',mode:'lines',line:{color:'rgba(100,116,139,0.6)',width:1,dash:'dot'}},"
            "{x:pd.x,y:pd.p90,name:'P90 (Optimista)',mode:'lines',line:{color:'rgba(0,229,160,0.3)',width:1},fill:'tonexty',fillcolor:'rgba(0,229,160,0.08)'},"
            "{x:pd.x,y:pd.p50,name:'P50 — FlowBio',mode:'lines+markers',line:{color:'#00E5A0',width:3},marker:{size:4}},"
            "{x:pd.x,y:pd.mob,name:'Movilidad',mode:'lines',line:{color:'#F59E0B',width:2,dash:'dash'},yaxis:'y2'}"
            "],{paper_bgcolor:'#0D1520',plot_bgcolor:'#0D1520',font:{color:'#8BA8C0',family:'Inter'},"
            "title:{text:'Curva de Declinación PIML — " + str(len(proyeccion)) + " meses',font:{color:'#fff',size:14}},"
            "xaxis:{title:'Mes',gridcolor:'rgba(255,255,255,0.05)',zeroline:false},"
            "yaxis:{title:'Producción (BOPD)',gridcolor:'rgba(255,255,255,0.05)',zeroline:false},"
            "yaxis2:{title:'Movilidad',overlaying:'y',side:'right',color:'#F59E0B',showgrid:false},"
            "legend:{orientation:'h',y:-0.15},margin:{t:50,b:70,l:65,r:65}},"
            "{responsive:true});</script>",
            height=450
        )

    with cr:
        st.markdown("<h4 style='color:#22D3EE; font-family:Syne; margin-bottom:16px;'>🧪 Diagnóstico de Inyección CEOR</h4>", unsafe_allow_html=True)
        d = pozos[pozo_sel]
        diag = [
            ("Escenario Base",          "<span style='color:#EF4444;'>Polímero HPAM Tradicional</span>"),
            ("Impacto ESG (HPAM)",      "Alta Huella de Carbono"),
            ("Escenario FlowBio",       "<span style='color:#00E5A0;font-weight:800;'>Biopolímero Avanzado (Na-CMC)</span>"),
            ("Dosificación Óptima",     f"{int(d.get('ppm', 1200))} ppm"),
            ("Caudal de Inyección",     f"{int(d.get('bwpd', 350))} BWPD"),
            ("Presión Fractura Límite", f"{int(d.get('lim_psi', 2800)):,} psi"),
            ("Volumen Poroso (PV)",     "0.29 PV"),
            ("Movilidad (M)",           f"{kpis['M_ratio']}"),
            ("Estado de Compatibilidad","Óptimo (Resistente a Salinidad)"),
        ]
        rows = "".join(f"<div class='diag-row'><span class='diag-key'>{k}</span><span class='diag-val'>{v}</span></div>" for k, v in diag)
        st.markdown(f"<div style='background:#0D1520;border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px;'>{rows}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generate_pdf(pozo_sel, kpis, proyeccion)
        st.download_button(
            label="📄 DESCARGAR REPORTE PDF",
            data=pdf_bytes,
            file_name=f"FlowBio_{pozo_sel}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
