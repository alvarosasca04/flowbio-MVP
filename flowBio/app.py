import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA (ESTILO AGENTIC OS)
# ==========================================
st.set_page_config(
    page_title="FlowBio EOR Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INYECCIÓN DE CSS (DARK MODE PREMIUM & UI)
# ==========================================
st.markdown("""
    <style>
    /* Estética General */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tarjetas de Métricas SaaS */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    .metric-title { color: #8b949e; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px;}
    .metric-value { color: #39FF14; font-size: 2.5rem; font-weight: 800; margin: 0; }
    .metric-value.cyan { color: #00E5FF; }
    .metric-delta { color: #58a6ff; font-size: 0.8rem; margin-top: 6px; font-family: 'Inter', sans-serif;}

    /* Terminal Console Style */
    .terminal-container {
        background-color: #010409;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        color: #39FF14;
        margin-bottom: 25px;
        line-height: 1.6;
    }
    .terminal-header { display: flex; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid #1f242b; padding-bottom: 10px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; }
    .dot-red { background-color: #ff5f56; }
    .dot-yellow { background-color: #ffbd2e; }
    .dot-green { background-color: #27c93f; }

    /* Botón Desplegar */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
        color: white; font-weight: 700; border: none; border-radius: 8px;
        height: 3.5rem; width: 100%; transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.4);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR: PANEL DE CONTROL DATA LAKE
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #00E5FF; text-align: center; margin-bottom:0;'>FlowBio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; text-align: center; letter-spacing: 2px; font-size: 0.8rem;'>AGENTIC WORKFLOWS</p>", unsafe_allow_html=True)
    st.divider()
    
    # Cambio: Ahora jala de S3 en lugar de subir archivo
    st.markdown("### ☁️ AWS S3 Data Lake")
    active_assets = [
        "S3://flowbio-lake/Field_UKCS_01.csv",
        "S3://flowbio-lake/Veracruz_Norte_Asset.csv",
        "S3://flowbio-lake/Sim_Test_Scenario_B.csv"
    ]
    selected_asset = st.selectbox("Seleccionar Activo para Optimización", active_assets)
    st.success(f"Vínculo establecido: {selected_asset.split('/')[-1]}")
    
    st.divider()
    st.markdown("### ⚙️ Parámetros Físicos (Override)")
    perm = st.slider("Permeabilidad (mD)", 1, 1000, 250)
    visc = st.slider("Viscosidad Crudo (cP)", 1.0, 150.0, 45.5)
    sw = st.slider("Saturación de Agua (Sw)", 0.1, 0.9, 0.6)
    
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    deploy_clicked = st.button("🚀 INICIAR ENJAMBRE DE AGENTES")

# ==========================================
# 4. MAIN INTERFACE: CENTRO DE COMANDO
# ==========================================
st.markdown("<h2 style='color: white; font-weight: 300; margin-bottom:0;'>EOR <span style='color: #00E5FF; font-weight: 800;'>Command Center</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #8b949e; font-size: 1.1rem;'>Orquestación PIML (Physics-Informed Machine Learning) en tiempo real.</p>", unsafe_allow_html=True)
st.divider()

if not deploy_clicked:
    st.info("📡 **Status:** Sistema en espera. Seleccione un activo del Data Lake y despliegue los agentes para iniciar el análisis.")
else:
    # --- TERMINAL DE AGENTES (Simulación de Procesamiento Real) ---
    terminal_placeholder = st.empty()
    
    def update_console(lines):
        html_lines = "".join([f"<div>{line}</div>" for line in lines])
        terminal_html = f"""
        <div class="terminal-container">
            <div class="terminal-header">
                <div class="dot dot-red"></div><div class="dot dot-yellow"></div><div class="dot dot-green"></div>
                <span style="color: #444d56; font-size: 0.75rem; margin-left: 15px;">root@flowbio-agent-node-01:~#</span>
            </div>
            {html_lines}
        </div>
        """
        terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)

    console_log = ["> Accediendo a S3 Bucket... <span style='color: white;'>[SECURE_AUTH_GRANTED]</span>"]
    update_console(console_log)
    time.sleep(1)
    
    console_log.append(f"> 🤖 **Data Agent:** Extrayendo {selected_asset.split('/')[-1]}... <span style='color: white;'>[OK]</span>")
    update_console(console_log)
    time.sleep(1.2)
    
    console_log.append("> 🤖 **Physics Agent:** Validando restricciones termodinámicas (Ley de Darcy)... <span style='color: white;'>[OK]</span>")
    update_console(console_log)
    time.sleep(1.5)
    
    console_log.append("> 🤖 **Skin Agent:** Calculando viscosidad óptima para evitar daño de formación... <span style='color: white;'>[OK]</span>")
    update_console(console_log)
    time.sleep(1.2)
    
    console_log.append("> 🤖 **Financial Agent:** Ejecutando proyecciones de ROI y Success Fee... <span style='color: white;'>[OK]</span>")
    console_log.append("> <b>Análisis completado. Sincronizando resultados con Dashboard...</b>")
    update_console(console_log)
    time.sleep(0.5)

    # --- MÉTRICAS FINANCIERAS (HTML SaaS CARDS) ---
    st.markdown("### 📊 Proyección de Impacto Económico")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Crudo Incremental Proyectado</div>
            <div class="metric-value">+22,500 <span style="font-size: 1rem; color:#8b949e;">bbls</span></div>
            <div class="metric-delta">↑ Basado en simulación 36 meses</div></div>""", unsafe_allow_html=True)
            
    with m2:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Flujo de Caja Adicional (NPV)</div>
            <div class="metric-value">+$1.5M <span style="font-size: 1rem; color:#8b949e;">USD</span></div>
            <div class="metric-delta">Neto de Costos Operativos</div></div>""", unsafe_allow_html=True)
            
    with m3:
        st.markdown(f"""<div class="metric-card" style="border-color: #00E5FF; background-color: #0d1520;">
            <div class="metric-title" style="color:#00E5FF;">Tarifa FlowBio (Success Fee)</div>
            <div class="metric-value cyan">$67,500 <span style="font-size: 1rem; color:#8b949e;">USD</span></div>
            <div class="metric-delta">Costo 100% Variable por Barril Extra</div></div>""", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # --- VISUALIZACIÓN DE CURVA DE DECLINACIÓN (Plotly Dark) ---
    meses = np.arange(1, 37)
    intervencion = 12
    # Lógica matemática de declinación
    baseline = 3000 * np.exp(-0.06 * meses)
    optimized = np.copy(baseline)
    optimized[intervencion:] = baseline[intervencion:] + 1200 * np.exp(-0.03 * (meses[intervencion:] - intervencion))
    
    fig = go.Figure()
    # Status Quo
    fig.add_trace(go.Scatter(x=meses, y=baseline, mode='lines', name='Baseline (Status Quo)', line=dict(color='#ff5f56', width=3, dash='dash')))
    # FlowBio Project
    fig.add_trace(go.Scatter(x=meses, y=optimized, mode='lines', name='FlowBio Optimized', line=dict(color='#39FF14', width=4), fill='tonexty', fillcolor='rgba(57, 255, 20, 0.1)'))
    
    fig.update_layout(
        template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Meses", yaxis_title="Producción (bbls/mes)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0), hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<p style='color: #8b949e; text-align: center; font-size: 0.9rem;'>Área sombreada representa el volumen total de recuperación incremental mediante inyección de polímeros FlowBio.</p>", unsafe_allow_html=True)
