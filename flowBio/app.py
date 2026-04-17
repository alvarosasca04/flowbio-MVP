import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import base64
from fpdf import FPDF

# ══════════════════════════════════════════════════════
# 1. IDENTIDAD VISUAL PREMIUM
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    .kpi-box {
        background: rgba(13, 21, 32, 0.8); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0;
    }
    .kpi-label { font-family: 'Inter'; font-size: 11px; color: #64748B; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-family: 'Syne'; font-size: 38px; font-weight: 800; color: #fff; margin: 5px 0; }
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne' !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        width: 100%; transition: 0.3s; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'data' not in st.session_state: st.session_state.data = None

# ══════════════════════════════════════════════════════
# 2. CONEXIÓN REAL A AWS S3 (EL CEREBRO DE TUS AGENTES)
# ══════════════════════════════════════════════════════
def fetch_agents_data_from_s3():
    try:
        # Conecta a S3 usando los Secrets de Streamlit
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY"),
            region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-2")
        )
        
        # Lee el archivo exacto que genera tu Jupyter
        bucket_name = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        file_key = "agentes/ultimo_reporte.json"
        
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        data_json = json.loads(content)
        
        resumen = data_json.get("resumen_ejecutivo", {})
        esg = data_json.get("esg_cbam", {})
        
        # Mapeamos los datos del JSON a las variables del Dashboard
        return {
            "ahorro": resumen.get("ahorro_total_usd", 0),
            "mejora": resumen.get("mejora_promedio_pct", 0),
            "fee": resumen.get("fee_mensual_usd", 0),
            "eur": resumen.get("eur_extra_bbls", 0),
            "co2": esg.get("total_ton_co2_ahorradas", 0),
            "pozos": resumen.get("pozos_piloto", 10),
            "n": 0.569, # Fijo para Na-CMC según tu PDF
            "k": 151.4, # Fijo para Na-CMC según tu PDF
            "m_ratio": 0.28, # Fijo para Na-CMC según tu PDF
            "bpd": 350 # Base asumida
        }
    except Exception as e:
        return {"error": str(e)}

# ══════════════════════════════════════════════════════
# 3. MOTOR DE REPORTE PDF (INTACTO Y PERFECTO)
# ══════════════════════════════════════════════════════
class FlowBioReport(FPDF):
    def header(self):
        self.set_fill_color(6, 11, 17); self.rect(0, 0, 210, 40, 'F')
        self.set_xy(10, 12)
        self.set_font('Arial', 'B', 22); self.set_text_color(0, 229, 160)
        self.cell(0, 10, 'FlowBio AI Engine', 0, 1, 'L')
        self.set_font('Arial', '', 10); self.set_text_color(255, 255, 255)
        self.cell(0, 5, 'Reporte Ejecutivo de Agentes - PIML', 0, 1, 'L')
        self.ln(10)

    def draw_section_header(self, title):
        self.ln(5)
        self.set_font('Arial', 'B', 12); self.set_text_color(60, 60, 60)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.set_draw_color(0, 229, 160); self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y()); self.ln(5)

    def draw_metric_card(self, label, value, x, y):
        self.set_fill_color(250, 250, 250); self.set_draw_color(230, 230, 230)
        self.rect(x, y, 45, 22, 'FD')
        self.set_xy(x, y + 4)
        self.set_font('Arial', 'B', 14); self.set_text_color(0, 120, 80)
        self.cell(45, 8, str(value), border=0, ln=0, align='C')
        self.set_xy(x, y + 13)
        self.set_font('Arial', '', 8); self.set_text_color(120, 120, 120)
        self.cell(45, 5, str(label), border=0, ln=0, align='C')

def generate_pdf_base64(d):
    pdf = FlowBioReport()
    pdf.add_page()
    pdf.draw_section_header('Impacto Economico Anual Proyectado')
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(0, 150, 100)
    pdf.cell(0, 18, f"${d['ahorro']:,.0f} USD/año", 0, 1, 'L')
    pdf.draw_metric_card("ROI Estimado", "15%", 10, 85)
    pdf.draw_metric_card("Ahorro/bbl", "$2.57", 58, 85)
    pdf.draw_metric_card("OPEX Actual", "$19.80", 106, 85)
    pdf.draw_metric_card("OPEX FlowBio", "$17.23", 154, 85)
    
    pdf.set_xy(10, 115); pdf.draw_section_header('Analisis Reologico - Motor PIML')
    pdf.draw_metric_card("Indice flujo (n)", str(d['n']), 10, 132)
    pdf.draw_metric_card("Consistencia K", f"{d['k']} mPas", 58, 132)
    pdf.draw_metric_card("Ratio movilidad", str(d['m_ratio']), 106, 132)
    pdf.draw_metric_card("Ef. barrido", f"{d['mejora']}%", 154, 132)
    
    pdf.set_xy(10, 165); pdf.draw_section_header('Resolucion de Agentes de IA')
    pdf.set_font('Arial', '', 10.5); pdf.set_text_color(50, 50, 50)
    conclu = (f"El orquestador de Groq determino la inyeccion viable en {d['pozos']} pozos extrayendo datos de S3. "
              f"Se estima una recuperacion EUR adicional de {d['eur']:,.0f} barriles, con un Success Fee "
              f"estimado de ${d['fee']:,.0f} USD. La reduccion de la huella de carbono asciende a {d['co2']} toneladas.")
    pdf.multi_cell(0, 7, conclu)
    return base64.b64encode(pdf.output(dest="S").encode("latin-1")).decode()

# ══════════════════════════════════════════════════════
# 4. DASHBOARD UI
# ══════════════════════════════════════════════════════
if st.session_state.screen == 'splash':
    st.markdown("""<div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:110px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Mono'; letter-spacing:8px; color:#64748B; font-size:14px;">AGENT INTELLIGENCE OS</p></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("OBTENER DATOS DE AGENTES (AWS S3)"):
            with st.status("Conectando con Data Lake en AWS..."):
                s3_data = fetch_agents_data_from_s3()
                if "error" in s3_data:
                    st.error(f"Error de conexión S3. ¿Configuraste las llaves de AWS en Streamlit Secrets? Error: {s3_data['error']}")
                else:
                    st.session_state.data = s3_data
                    st.session_state.screen = 'dash'
                    st.rerun()

elif st.session_state.screen == 'dash':
    d = st.session_state.data
    st.markdown(f"<h2 style='font-family:Syne; margin:20px; color:white;'>Command Center <span style='font-size:12px; color:#22D3EE;'>[DATA SOURCED FROM JUPYTER AGENTS]</span></h2>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-box"><p class="kpi-label">AHORRO OPEX / AÑO</p><p class="kpi-value" style="color:#00E5A0;">${d["ahorro"]:,.0f}</p></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-box" style="border-top-color:#3B82F6;"><p class="kpi-label">MEJORA PROMEDIO</p><p class="kpi-value">+{d["mejora"]:.1f}%</p></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-box" style="border-top-color:#22D3EE;"><p class="kpi-label">RATIO MOVILIDAD</p><p class="kpi-value" style="color:#22D3EE;">{d["m_ratio"]}</p></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-box" style="border-top-color:#F59E0B;"><p class="kpi-label">ESG CO2 EVITADO</p><p class="kpi-value" style="color:#F59E0B;">{d["co2"]}t</p></div>', unsafe_allow_html=True)

    cl, cr = st.columns([3, 1])
    with cl:
        HTML_CHART = f"""
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="plot" style="height:480px; border-radius:12px; background:#0D1520; border:1px solid rgba(255,255,255,0.05);"></div>
        <script>
            var x = Array.from({{length:40}}, (_,i)=>i);
            var base = {d['pozos'] * d['bpd']};
            var y1 = x.map(i => base * Math.exp(-0.06*i));
            var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
            Plotly.newPlot('plot', [
                {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot', width:2}}, name:'Base'}},
                {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
            ], {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B', family:'DM Mono'}}, margin:{{t:20, b:40, l:50, r:20}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }}, {{responsive: true, displayModeBar: false}});
        </script>
        """
        components.html(HTML_CHART, height=500)
    with cr:
        st.markdown(f"""<div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid #1A2A3A;">
            <p style="font-size:10px; color:#64748B; font-weight:700;">DATOS TECNICOS</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">RESERVAS EUR (5A)</p><p style="font-family:'Syne'; font-size:26px; color:#22D3EE; margin:0;">{d['eur']:,.0f}</p>
            <p style="font-size:9px; color:#475569; margin-top:15px;">FEE MENSUAL</p><p style="font-family:'Syne'; font-size:26px; color:#00E5A0; margin:0;">${d['fee']:,.0f}</p></div>""", unsafe_allow_html=True)
        
        pdf_b64 = generate_pdf_base64(d)
        st.markdown(f'<br><a href="data:application/pdf;base64,{pdf_b64}" download="FlowBio_Agent_Report.pdf" style="text-decoration:none;"><button style="background:#00E5A0; border:none; padding:15px; border-radius:8px; width:100%; color:#060B11; font-weight:800; cursor:pointer;">📥 DESCARGAR REPORTE OFICIAL</button></a>', unsafe_allow_html=True)
        if st.button("🏠 VOLVER A CONECTAR"): st.session_state.screen = 'splash'; st.rerun()
