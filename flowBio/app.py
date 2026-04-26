import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
from fpdf import FPDF
from datetime import datetime

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
    .stButton > button { background: #00E5A0 !important; color: #060B11 !important; font-family: 'Syne', font-weight: 800 !important; border-radius: 8px !important; padding: 15px 30px !important; width: 100%; transition: all 0.3s ease; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0,229,160,0.4); }
    .console-box { background: #0D1520; border: 1px solid rgba(0,229,160,0.3); border-radius: 8px; padding: 20px; font-family: 'DM Mono', monospace; color: #22D3EE; }
</style>
""", unsafe_allow_html=True)

def load_data_from_s3():
    try:
        aws_key = st.secrets.get("aws", {}).get("AWS_ACCESS_KEY_ID", st.secrets.get("AWS_ACCESS_KEY_ID"))
        aws_sec = st.secrets.get("aws", {}).get("AWS_SECRET_ACCESS_KEY", st.secrets.get("AWS_SECRET_ACCESS_KEY"))
        s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_sec, region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error AWS S3: {e}"); return None

def calcular_kpis_desde_grafica(proyeccion):
    if not proyeccion: return {'eur_val': 0, 'barriles_extra_mes': 0, 'valor_extra': 0, 'success_fee': 0, 'payback_val': 0.0}
    p10_promedio = sum(r.get('P10', 0) for r in proyeccion) / len(proyeccion)
    p50_promedio = sum(r.get('P50', 0) for r in proyeccion) / len(proyeccion)
    bopd_extra = max(0, p50_promedio - p10_promedio)
    barriles_extra_mes = bopd_extra * 30
    valor_extra = barriles_extra_mes * 74.5
    success_fee = valor_extra * 0.15
    eur_incremental = sum(max(0, r.get('P50', 0) - r.get('P10', 0)) for r in proyeccion) * 30
    payback_val = 3.2 if barriles_extra_mes > 0 else 0.0
    return {'eur_val': round(eur_incremental, 0), 'barriles_extra_mes': round(barriles_extra_mes, 0), 'valor_extra': round(valor_extra, 0), 'success_fee': round(success_fee, 0), 'payback_val': payback_val}

def clean_text(text):
    return str(text).replace('·','.').replace('²','2').encode('latin-1', errors='replace').decode('latin-1') if text else ""

def generate_corporate_pdf(well, kpis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6,11,17); pdf.rect(0,0,210,297,'F')
    pdf.set_font('Arial','B',24); pdf.set_text_color(255,255,255)
    pdf.cell(0,10,clean_text('FlowBio Executive Report'),0,1,'L')
    pdf.set_font('Arial','B',16); pdf.set_text_color(0,229,160)
    pdf.cell(0,10,clean_text(f'Pozo Analizado: {well}'),0,1,'L')
    pdf.set_draw_color(0,229,160); pdf.set_line_width(0.5); pdf.line(10,35,200,35); pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(34, 211, 238)
    pdf.cell(0, 10, clean_text('IMPACTO FINANCIERO Y TECNICO'), 0, 1, 'L'); pdf.ln(2)
    
    fin_data = [
        ["Crudo Incremental (Mensual):", f"+{int(kpis['barriles_extra_mes']):,} bbls"],
        ["Valor Extra Generado (Mensual):", f"${kpis['valor_extra']:,.0f} USD"],
        ["Tarifa por Exito (Success Fee):", f"${kpis['success_fee']:,.0f} USD"],
        ["Recuperacion Total Incremental (EUR):", f"{int(kpis['eur_val']):,} bbls"]
    ]
    pdf.set_fill_color(13, 21, 32); pdf.set_draw_color(30, 41, 59); pdf.set_line_width(0.2)
    for k, v in fin_data:
        pdf.set_text_color(200, 200, 200); pdf.set_font('Arial', '', 11)
        pdf.cell(100, 10, clean_text(" " + k), border='B', fill=True)
        pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 11)
        pdf.cell(90, 10, clean_text(" " + v), border='B', ln=1, align='R', fill=True)
        
    return pdf.output(dest='S').encode('latin-1', errors='replace')

if 'auth' not in st.session_state: st.session_state.auth = False
if 'simulated' not in st.session_state: st.session_state.simulated = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:20vh;'><h1 style='color:white; font-family:Syne; font-size:80px;'>FlowBio<span style='color:#00E5A0'>.</span></h1></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 0.8, 1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("ACCEDER AL SISTEMA") and pwd == "FlowBio2026": st.session_state.auth = True; st.rerun()

elif st.session_state.auth and not st.session_state.simulated:
    st.markdown("<h2 style='text-align:center; color:white; font-family:Syne;'>FlowBio EORIA</h2>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        if st.button("🚀 INICIAR LECTURA DE S3"):
            status_box = st.empty(); progress_bar = st.progress(0)
            for i, p in enumerate(["Conectando a S3...", "Procesando JSON...", "Listando pozos reales..."]):
                status_box.markdown(f"<div class='console-box'>> {p}</div>", unsafe_allow_html=True)
                progress_bar.progress((i+1)*33); time.sleep(0.5)
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
    if not lista_pozos: st.error("⚠️ Carpeta vacía en S3."); st.stop()

    pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis:", lista_pozos)
    d = datos_pozos[pozo_seleccionado]

    proyeccion = d.get('proyeccion', [])
    kpis = calcular_kpis_desde_grafica(proyeccion)

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL (MES)</p><p class="kpi-value">+{int(kpis["barriles_extra_mes"]):,}</p><p class="kpi-sub">bbls / mes</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA GENERADO</p><p class="kpi-value">${kpis["valor_extra"]:,.0f}</p><p class="kpi-sub">USD / mes</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${kpis["success_fee"]:,.0f}</p><p class="kpi-sub">USD / mes · 15%</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{kpis["payback_val"]}</p><p class="kpi-sub">Meses</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([2.3, 1.7])

    with cl:
        x_vals = [r.get('mes', i+1) for i, r in enumerate(proyeccion)]
        chart_json = json.dumps({"x": x_vals, "p50": [r.get('P50',0) for r in proyeccion], "p10": [r.get('P10',0) for r in proyeccion], "p90": [r.get('P90',0) for r in proyeccion]})
        script_grafica = (
            "<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>"
            "<div id='plot' style='height:420px; background:#0D1520; border-radius:12px; border:1px solid rgba(255,255,255,0.05); box-shadow:0 8px 16px rgba(0,0,0,0.4);'></div>"
            "<script> var pd = " + chart_json + ";"
            "  var t_p90 = { x:pd.x, y:pd.p90, type:'scatter', mode:'lines', name:'P90', line:{color:'rgba(0,229,160,0.3)', width:1}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.08)' };"
            "  var t_p50 = { x:pd.x, y:pd.p50, type:'scatter', mode:'lines+markers', name:'P50 (Tratamiento)', line:{color:'#00E5A0', width:3}, marker:{size:4, color:'#00E5A0'} };"
            "  var t_p10 = { x:pd.x, y:pd.p10, type:'scatter', mode:'lines', name:'P10 (Status Quo)', line:{color:'rgba(100,116,139,0.8)', width:2, dash:'dot'} };"
            "  var layout = { paper_bgcolor:'#0D1520', plot_bgcolor:'#0D1520', font:{color:'#8BA8C0'}, title:{text:'Curva de Declinación y Recuperación', font:{color:'#fff'}}, xaxis:{title:'Meses'}, yaxis:{title:'BOPD'}, legend:{orientation:'h', y:-0.15}, margin:{t:40, b:50, l:50, r:20} };"
            "  Plotly.newPlot('plot', [t_p10, t_p90, t_p50], layout, {responsive:true});"
            "</script>"
        )
        components.html(script_grafica, height=450)

    with cr:
        # ¡AQUI RESTAURAMOS EL DISEÑO ORIGINAL EXACTO!
        quimico = d.get('quimico', 'Na-CMC FlowBio')
        ppm = d.get('ppm', 1500)
        vol_pv = d.get('vol_pv', 0.29)
        bwpd = d.get('bwpd', 350)
        lim_psi = d.get('lim_psi', 3000)

        html_parts = [
            "<div style='background:#0D1520; padding:28px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:420px; display:flex; flex-direction:column; justify-content:space-between;'>",
            "<div>",
            "<p style='color:#00E5A0; font-family:\"DM Mono\"; font-weight:800; font-size:11px; letter-spacing:1.5px; margin-bottom:20px;'>⚡ DIAGNÓSTICO DE INYECCIÓN</p>",
            f"<p style='font-family:\"Syne\"; font-size:16px; font-weight:700; color:#22D3EE; margin-bottom:2px;'>🧪 {str(quimico).upper()}</p>",
            f"<p style='font-family:\"Inter\"; font-size:12px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Dosificación óptima: <b style='color:#E2E8F0'>{ppm} ppm</b> &nbsp;|&nbsp; PV: <b style='color:#E2E8F0'>{vol_pv}</b></p>",
            f"<p style='font-family:\"Syne\"; font-size:16px; font-weight:700; color:#22D3EE; margin-bottom:2px;'>🌊 PARÁMETROS DE BOMBEO</p>",
            f"<p style='font-family:\"Inter\"; font-size:12px; color:#8BA8C0; margin-top:0px; margin-bottom:15px;'>Caudal objetivo: <b style='color:#E2E8F0'>{bwpd} BWPD</b><br>Presión máxima (Fractura): <b style='color:#EF4444'>{lim_psi:,} psi</b></p>",
            "</div><div><hr style='border:none; border-top:1px dashed rgba(255,255,255,0.1); margin:15px 0;'>",
            f"<p style='color:#64748B; font-family:\"DM Mono\"; font-size:10px; font-weight:600; letter-spacing:1px;'>IMPACTO TOTAL ACUMULADO (EUR):</p>",
            f"<p style='color:#00E5A0; font-family:\"Syne\"; font-size:36px; font-weight:800; margin:0; line-height:1;'>{int(kpis['eur_val']):,} <span style='font-size:14px; color:#64748B; font-family:\"DM Mono\";'>bbls</span></p>",
            "</div></div>"
        ]
        st.markdown("".join(html_parts), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.download_button(
            label="📄 DESCARGAR REPORTE PDF", 
            data=generate_corporate_pdf(pozo_seleccionado, kpis), 
            file_name=f"FlowBio_Report_{pozo_seleccionado}.pdf", 
            mime="application/pdf"
        )
