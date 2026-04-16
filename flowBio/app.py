import streamlit as st
import streamlit.components.v1 as components
import json
import os
import requests
import pandas as pd
from fpdf import FPDF
import base64

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN VISUAL Y ESTILO FLOWBIO
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    
    /* Botones Premium Estilo Screenshot */
    .stButton > button {
        background: #00E5A0 !important; color: #060B11 !important;
        font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
        border-radius: 8px !important; padding: 15px 30px !important;
        border: none !important; width: 100%; transition: 0.3s ease;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton > button:hover { box-shadow: 0 0 20px rgba(0,229,160,0.4); transform: translateY(-2px); }
    
    /* Botón Secundario / Regreso */
    div.back-btn > div > .stButton > button {
        background: transparent !important; color: #64748B !important;
        border: 1px solid #1A2A3A !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. SEGURIDAD Y VARIABLES
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
USD_TO_MXN = 20.0

if 'screen' not in st.session_state: st.session_state.screen = 'splash'
if 'final_data' not in st.session_state: st.session_state.final_data = None

# 2. GENERADOR DE PDF PROFESIONAL
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 11, 17)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(0, 229, 160)
    pdf.cell(0, 20, 'FlowBio Insight Report', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'Generado el: {pd.Timestamp.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.ln(10)
    
    # KPIs
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Resumen Ejecutivo:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"- Ahorro Estimado: ${data['ahorro']:,.2f} USD / Año", 0, 1)
    pdf.cell(0, 10, f"- Mejora de Produccion: +{data['mejora']:.1f}%", 0, 1)
    pdf.cell(0, 10, f"- CO2 Evitado Anual: {data['co2']:.0f} Toneladas", 0, 1)
    pdf.cell(0, 10, f"- Reservas EUR (5A): {data['eur']:,.0f} bbls", 0, 1)
    pdf.cell(0, 10, f"- Tiempo de Payback: {data['pb']:.1f} Meses", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# 3. MOTOR IA (BACKEND)
def get_ai_analysis(fluido, tuberia, pozos, bpd, fee):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Act as EOR eng. Fluid={fluido}, Tubing={tuberia}, Wells={pozos}, BPD={bpd}, Fee={fee}. Return JSON: mejora (0.1-0.2), ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red."
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1}
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except: return None

# ══════════════════════════════════════════════════════
# NAVEGACIÓN DE PANTALLAS
# ══════════════════════════════════════════════════════

# --- PANTALLA INICIO ---
if st.session_state.screen == 'splash':
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; color:white; padding-bottom:40px;">
        <h1 style="font-family:'Syne'; font-size:100px; font-weight:800; margin:0; letter-spacing:-4px;">FlowBio<span style="color:#00E5A0">.</span></h1>
        <p style="font-family:'DM Sans'; letter-spacing:6px; color:#64748B; font-size:14px; text-transform:uppercase;">Subsurface Intelligence OS</p>
    </div>
    """, unsafe_allow_html=True)
    _, c2, c3, _ = st.columns([1.2, 1.8, 1.8, 1.2])
    with c2:
        if st.button("EJECUTAR DEMO REAL (S3)"):
            st.session_state.final_data = {"ahorro": 1620000, "mejora": 16.5, "fee": 21900, "co2": 833, "eur": 425000, "wc": 18.4, "pb": 1.2, "mpy": 0.8, "pozos": 78, "bpd": 350, "label": "AWS S3 DATA LAKE"}
            st.session_state.screen = 'dash'
            st.rerun()
    with c3:
        if st.button("SIMULADOR IA LIVE"):
            st.session_state.screen = 'setup'
            st.rerun()

# --- PANTALLA CONFIGURACIÓN ---
elif st.session_state.screen == 'setup':
    st.markdown("<div style='padding:60px 100px;'><h2 style='color:white; font-family:Syne; font-size:35px;'>Configuración IA Engine</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fluido = st.selectbox("Químico", ["Na-CMC (FlowBio)", "HPAM (Sintético)"])
            tuberia = st.selectbox("Metalurgia", ["Acero al Carbono", "Aleación CRA"])
        with col2:
            pozos = st.number_input("Pozos", value=15)
            bpd = st.number_input("BPD Base", value=350)
        fee = st.slider("Success Fee ($/bbl)", 1.0, 15.0, 5.0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        bc1, bc2 = st.columns([1, 4])
        with bc1:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("← INICIO"):
                st.session_state.screen = 'splash'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with bc2:
            if st.button("🧠 GENERAR ANÁLISIS"):
                with st.status("Consultando IA Llama-3.3..."):
                    res = get_ai_analysis(fluido, tuberia, pozos, bpd, fee)
                    if res:
                        ai = json.loads(res)
                        st.session_state.final_data = {
                            "ahorro": ai['ahorro_usd'], "mejora": ai['mejora']*100, "fee": ai['fee_usd'],
                            "co2": ai['co2_tons'], "eur": ai['eur_bbls'], "wc": ai['wc_red'],
                            "pb": ai['payback'], "mpy": ai['mpy'], "pozos": pozos, "bpd": bpd, 
                            "label": "IA LIVE PROJECTION"
                        }
                        st.session_state.screen = 'dash'
                        st.rerun()

# --- DASHBOARD ---
elif st.session_state.screen == 'dash':
    d = st.session_state.final_data
    
    # HTML Visual Premium
    HTML_DASH = f"""
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div style="background:#060B11; color:white; font-family:'DM Sans'; padding:25px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px; border-bottom:1px solid #1A2A3A; padding-bottom:15px;">
            <h1 style="font-family:'Syne'; font-size:32px; margin:0;">FlowBio Insight <span style="color:#22D3EE; font-size:12px; font-family:'DM Mono';">[{d['label']}]</span></h1>
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-bottom:25px;">
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #00E5A0;">
                <div style="font-size:10px; color:#64748B;">AHORRO OPEX / AÑO</div>
                <div style="font-size:36px; color:#00E5A0; font-family:'DM Mono';">${d['ahorro']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #3B82F6;">
                <div style="font-size:10px; color:#64748B;">MEJORA PROMEDIO</div>
                <div style="font-size:36px; font-family:'DM Mono';">+{d['mejora']:.1f}%</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #22D3EE;">
                <div style="font-size:10px; color:#64748B;">FEE MENSUAL USD</div>
                <div style="font-size:36px; color:#22D3EE; font-family:'DM Mono';">${d['fee']:,.0f}</div>
            </div>
            <div style="background:#0D1520; padding:25px; border-radius:12px; border-top:3px solid #F59E0B;">
                <div style="font-size:10px; color:#64748B;">ESG: CO2 EVITADO</div>
                <div style="font-size:36px; color:#F59E0B; font-family:'DM Mono';">{d['co2']:.0f} t</div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px;">
            <div style="background:#0D1520; border-radius:12px; padding:25px; border:1px solid #1A2A3A;">
                <div id="chart" style="height:380px;"></div>
            </div>
            <div style="background:#0D1520; border-radius:12px; padding:25px; border:1px solid #1A2A3A;">
                <div style="font-size:11px; color:#64748B; margin-bottom:20px;">MÉTRICAS PIML</div>
                <div style="display:flex; justify-content:space-between; padding:15px 0; border-bottom:1px solid #1A2A3A;">
                    <span>Pozos</span><span style="color:#00E5A0; font-family:'DM Mono'; font-weight:bold;">{d['pozos']}</span>
                </div>
                <div style="margin-top:30px; display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#22D3EE; font-size:22px; font-family:'DM Mono';">{d['eur']:,.0f}</div>
                        <div style="font-size:8px; color:#64748B;">RESERVAS EUR</div>
                    </div>
                    <div style="background:#060B11; padding:15px; border-radius:8px; text-align:center;">
                        <div style="color:#EF4444; font-size:22px; font-family:'DM Mono';">{d['mpy']:.1f}</div>
                        <div style="font-size:8px; color:#64748B;">MPY CORROSIÓN</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        var x = Array.from({{length:40}}, (_,i)=>i);
        var base = {d['pozos'] * d['bpd']};
        var y1 = x.map(i => base * Math.exp(-0.06*i));
        var y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * {d['mejora']/100} * Math.exp(-0.015*(i-5))));
        Plotly.newPlot('chart', [
            {{x:x, y:y1, type:'scatter', line:{{color:'#EF4444', dash:'dot', width:2}}, name:'Base'}},
            {{x:x, y:y2, type:'scatter', line:{{color:'#00E5A0', width:4}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)', name:'FlowBio'}}
        ], {{paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{{color:'#64748B', family:'DM Sans'}}, margin:{{t:10, b:40, l:50, r:10}}, xaxis:{{gridcolor:'#1A2A3A'}}, yaxis:{{gridcolor:'#1A2A3A'}} }});
    </script>
    """
    components.html(HTML_DASH, height=950, scrolling=True)
    
    # BOTONES DE ACCIÓN
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        if st.button("⚙️ RE-CONFIGURAR"):
            st.session_state.screen = 'setup'
            st.rerun()
    with c2:
        pdf_data = create_pdf(d)
        st.download_button("📥 DESCARGAR REPORTE PDF", data=pdf_data, file_name="flowbio_insight.pdf", mime="application/pdf")
    with c3:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🏠 INICIO"):
            st.session_state.screen = 'splash'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
