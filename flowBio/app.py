import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import math
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL Y CSS DE ALTA SEGURIDAD
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    
    /* Centrado de Pantalla de Acceso */
    .auth-container {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; height: 70vh; text-align: center;
    }

    /* Estilo Premium para Inputs y Botones */
    .stTextInput > div > div > input {
        background-color: #0D1520 !important; color: white !important;
        border: 1px solid #00E5A0 !important; border-radius: 8px !important;
        text-align: center; font-family: 'DM Mono';
    }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 40px !important;
        width: 100%; border: none !important; transition: 0.3s all ease;
    }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(0, 229, 160, 0.3); }

    /* KPIs */
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; margin-bottom: 20px;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 32px; font-weight: 800; color: #fff; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. FUNCIONES DE CORE (S3 Y PDF)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=1)
def load_data_from_s3():
    try:
        s3 = boto3.client('s3', 
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        response = s3.get_object(Bucket=bucket, Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

def create_corporate_pdf(well, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, 'FlowBio Report', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Activo: {well} | Fecha: {datetime.now().strftime("%Y-%m-%d")}', 0, 1)
    pdf.ln(10)
    # Datos en tabla
    pdf.set_fill_color(13, 21, 32)
    for k, v in [["PV", f"{d['visc_p']} cP"], ["YP", f"{d['yield_p']} lb/ft2"], ["EUR", f"{d['eur']:,} bbls"], ["PAYBACK", f"{d['payback']} Meses"]]:
        pdf.cell(95, 12, f" {k}", 1, 0, 'L', True)
        pdf.cell(95, 12, f" {v}", 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════
# 3. INTERFAZ DE ACCESO Y SEGURIDAD
# ══════════════════════════════════════════════════════
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <div class="auth-container">
            <h1 style='font-family:Syne; font-size:100px; color:white; margin-bottom:0;'>FlowBio<span style='color:#00E5A0'>.</span></h1>
            <p style='color:#64748B; letter-spacing:8px; font-size:12px; margin-bottom:40px;'>SECURE ACCESS GATEWAY</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_auth, _ = st.columns([1, 0.8, 1])
    with col_auth:
        key = st.text_input("PASSWORD DE OPERACIONES:", type="password")
        if st.button("AUTENTICAR Y SINCRONIZAR"):
            if key == "FlowBio2026": # CAMBIA TU CONTRASEÑA AQUÍ
                data = load_data_from_s3()
                if data:
                    st.session_state.all_data = data
                    st.session_state.authenticated = True
                    st.rerun()
            else:
                st.error("Credencial Inválida")

# ══════════════════════════════════════════════════════
# 4. COMMAND CENTER (DASHBOARD)
# ══════════════════════════════════════════════════════
else:
    st.markdown("<div style='padding: 2rem 3rem;'><h2 style='font-family:Syne; color:white;'>Command Center</h2>", unsafe_allow_html=True)
    wells = list(st.session_state.all_data.keys())
    selected = st.selectbox("Seleccione Pozo Analizado:", wells)
    d = st.session_state.all_data[selected]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX</p><p class="kpi-value">${d["ahorro"]:,}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box"><p class="kpi-label">MEJORA BARRIDO</p><p class="kpi-value">+{d["mejora"]}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${d["fee"]:,}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{d["payback"]} Meses</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([2.3, 1.7])
    with cl:
        # Gráfica Dinámica Plotly
        chart_html = f"""<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script><div id="plot" style="height:450px; background:#0D1520; border-radius:12px;"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i); var y1 = x.map(i => 350 * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (350 * {d['mejora']}/100 * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [{{x:x, y:y1, name:'Base', line:{{color:'#EF4444', dash:'dot'}}}},{{x:x, y:y2, name:'FlowBio AI', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'}}], 
            {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B'}}, margin:{{t:20, b:40, l:50, r:20}} }});
        </script>"""
        components.html(chart_html, height=470)

    with cr:
        # Insights y Reporte PDF
        st.markdown(f"""
        <div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); min-height:380px;">
            <p style="color:#00E5A0; font-weight:800; font-size:12px;">🧠 ENGINEERING INSIGHTS</p>
            <p style="font-family: 'DM Mono'; font-size: 14px; color: #22D3EE;">VISCOSIDAD (PV): {d['visc_p']} cP</p>
            <p style="font-family: 'DM Mono'; font-size: 14px; color: #22D3EE;">YIELD POINT (YP): {d['yield_p']} lb/100ft2</p>
            <hr style="opacity:0.1">
            <p style="color:#64748B; font-size:10px; text-transform: uppercase;">INCREMENTAL PROYECTADO:</p>
            <p style="color:#00E5A0; font-size:42px; font-weight:800; margin:0;">{d['eur']:,} <span style="font-size:14px; color:#64748B;">bbls</span></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # Botón PDF Corregido
        pdf_data = create_corporate_pdf(selected, d)
        st.download_button("📥 EXPORTAR REPORTE PDF OPERACIONAL", data=pdf_data, file_name=f"FlowBio_{selected}.pdf", mime="application/pdf")
