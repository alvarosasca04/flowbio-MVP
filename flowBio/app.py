import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE ESCENA ---
st.set_page_config(
    page_title="FlowBio | Agentic OS High-Fidelity",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENGINE DE DISEÑO ULTRA-HIFI (CSS INYECTADO) ---
st.markdown("""
    <style>
    /* Importar fuente técnica */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');

    .stApp { 
        background-color: #05070a; 
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }

    /* Hero Section High-Definition */
    .hero-section {
        text-align: center;
        padding: 100px 20px;
        background: radial-gradient(circle at center, #111827 0%, #05070a 100%);
        border-radius: 30px;
        margin-bottom: 50px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 5rem;
        font-weight: 900;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #00E5FF 0%, #39FF14 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* Glassmorphism de Alta Definición */
    .glass-card {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 25px;
        transition: all 0.4s ease;
    }
    .glass-card:hover {
        border-color: rgba(0, 229, 255, 0.4);
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.1);
        transform: translateY(-5px);
    }

    /* Métricas Neón */
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3.2rem;
        font-weight: 700;
        line-height: 1;
        background: linear-gradient(180deg, #39FF14 0%, #1db954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .cyan-text {
        background: linear-gradient(180deg, #00E5FF 0%, #00a8cc 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    /* Terminal Hacker-Pro */
    .terminal-window {
        background-color: #010409;
        border: 1px solid #30363d;
        border-radius: 15px;
        padding: 25px;
        font-family: 'JetBrains Mono', monospace;
        color: #39FF14;
        font-size: 0.9rem;
        height: 280px;
        overflow-y: auto;
        box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.05);
    }

    /* Botones Estilo Cyberpunk */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00E5FF, #0077FF);
        border: none; color: white; font-weight: 800;
        border-radius: 15px; padding: 15px 30px; width: 100%;
        text-transform: uppercase; letter-spacing: 2px;
        box-shadow: 0 10px 20px rgba(0, 119, 255, 0.2);
        transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 0 30px #00E5FF;
        letter-spacing: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = 'inicio'

# ==========================================
# 🏠 PÁGINA DE INICIO (EXPERIENCIA CINEMÁTICA)
# ==========================================
if st.session_state.page == 'inicio':
    st.markdown(f"""
        <div class="hero-section">
            <p style="color: #00E5FF; font-weight: 700; letter-spacing: 5px; margin-bottom: 0;">PIML AGENTIC FRAMEWORK</p>
            <h1 class="hero-title">FLOWBIO</h1>
            <p style="font-size: 1.8rem; color: #9CA3AF; font-weight: 300;">Elevando la Recuperación Secundaria a la Era de la Autonomía</p>
            <div style="max-width: 700px; margin: 30px auto; height: 2px; background: linear-gradient(90deg, transparent, #30363d, transparent);"></div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="glass-card"><h4 style="color:#00E5FF;">01. INGESTIÓN</h4><p style="color:#9CA3AF;">Sincronización en tiempo real con Data Lakes S3 mediante encriptación TLS 1.3.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="glass-card"><h4 style="color:#00E5FF;">02. AGENTES</h4><p style="color:#9CA3AF;">Redes neuronales informadas por la física resolviendo Ley de Darcy en milisegundos.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="glass-card"><h4 style="color:#00E5FF;">03. RESULTADOS</h4><p style="color:#9CA3AF;">Visualización ejecutiva de ROI y curvas DCA de alta fidelidad para CFOs.</p></div>', unsafe_allow_html=True)

    st.write("<br>"*2, unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1.2, 2, 1.2])
    with col_btn2:
        if st.button("🔌 INICIAR SISTEMA OPERATIVO EOR"):
            st.session_state.page = 'dashboard'
            st.rerun()

# ==========================================
# 📊 DASHBOARD (ALTA DEFINICIÓN)
# ==========================================
elif st.session_state.page == 'dashboard':
    with st.sidebar:
        st.markdown("<h2 style='color: #00E5FF; letter-spacing: -1px;'>🧬 FlowBio OS</h2>", unsafe_allow_html=True)
        if st.button("⬅️ LOGOUT"):
            st.session_state.page = 'inicio'
            st.rerun()
        st.divider()
        st.markdown("### 🛰️ TRANSMISIÓN S3")
        asset = st.selectbox("Data Stream", ["Offshore_UKCS_Field_A", "Veracruz_Complex_B"])
        st.divider()
        st.markdown("### 🎚️ PARÁMETROS FÍSICOS")
        p_visc = st.slider("Viscosidad (cP)", 1.0, 200.0, 85.0)
        p_perm = st.slider("Permeabilidad (mD)", 10, 800, 350)
        st.divider()
        deploy = st.button("🚀 BOOT AGENTS")

    st.markdown(f"<h1 style='letter-spacing:-2px; margin-bottom:0;'>Control <span style='color:#00E5FF;'>Center</span></h1>", unsafe_allow_html=True)
    st.caption(f"Connected to: {asset} | Status: Operational")

    if not deploy:
        st.write("<br>"*5, unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;'><h1 style='opacity:0.1; font-size:8rem;'>📡</h1><h3 style='color:#30363d;'>SISTEMA EN STANDBY</h3></div>", unsafe_allow_html=True)
    else:
        # 1. TERMINAL PRO
        terminal_placeholder = st.empty()
        log_lines = [
            "Handshake secure...", "S3 Data Stream: Connected.",
            "Agent_01 (Physics): Darcy constraints loaded.",
            "Agent_02 (Data): Noise filtering complete.",
            "Agent_03 (Skin): Damage mapping initialized.",
            "Pipeline stable. Rendering High-Fidelity Dashboard."
        ]
        curr = ""
        for l in log_lines:
            curr += f"<div style='margin-bottom:5px;'><span style='color:#30363d;'>[{datetime.now().strftime('%H:%M:%S')}]</span> > {l}</div>"
            terminal_placeholder.markdown(f'<div class="terminal-window">{curr}</div>', unsafe_allow_html=True)
            time.sleep(0.3)

        # 2. MÉTRICAS HIFI
        incremental = int(22500 * (p_perm/350) * (p_visc/85))
        revenue = incremental * 65
        fee = revenue * 0.05

        st.write("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><p style="color:#8b949e; letter-spacing:2px; font-size:0.8rem;">INCREMENTAL BBLS</p><p class="metric-value">+{incremental:,}</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><p style="color:#8b949e; letter-spacing:2px; font-size:0.8rem;">NPV (USD)</p><p class="metric-value">${revenue/1e6:.1f}M</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card" style="border-color:#00E5FF; box-shadow: 0 0 20px rgba(0,229,255,0.05);"><p style="color:#00E5FF; letter-spacing:2px; font-size:0.8rem;">SUCCESS FEE</p><p class="metric-value cyan-text">${fee:,.0f}</p></div>', unsafe_allow_html=True)

        # 3. MAPA Y GRÁFICO EN COLUMNAS
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.markdown("### 🗺️ GIS Mapping")
            df_wells = pd.DataFrame({
                'lat': [18.85 + np.random.uniform(-0.02, 0.02) for _ in range(10)],
                'lon': [-97.10 + np.random.uniform(-0.02, 0.02) for _ in range(10)],
                'Health': np.random.uniform(0, 100, 10)
            })
            fig_map = px.scatter_mapbox(df_wells, lat="lat", lon="lon", color="Health", size="Health",
                                       color_continuous_scale="Viridis", zoom=12, height=400)
            fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_map, use_container_width=True)

        with col_b:
            st.markdown("### 📈 Production Forecast")
            meses = np.arange(1, 37)
            base = 4000 * np.exp(-0.07 * meses)
            opt = np.copy(base)
            opt[12:] = base[12:] + (incremental/15) * np.exp(-0.04 * (meses[12:] - 12))
            
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=meses, y=base, name='Base', line=dict(color='#ff5f56', width=1, dash='dot')))
            fig_p.add_trace(go.Scatter(x=meses, y=opt, name='FlowBio', line=dict(color='#39FF14', width=4), fill='tonexty', fillcolor='rgba(57, 255, 20, 0.05)'))
            fig_p.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                               margin=dict(l=0,r=0,t=10,b=0), height=400, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
            st.plotly_chart(fig_p, use_container_width=True)
