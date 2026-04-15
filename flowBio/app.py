import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE ESCENA ---
st.set_page_config(
    page_title="FlowBio | Agentic EOR Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SISTEMA DE ESTILOS "ENTERPRISE DARK" ---
st.markdown("""
    <style>
    .stApp { background: #0d1117; color: #e6edf3; }
    
    /* Hero Section Página de Inicio */
    .hero-section {
        text-align: center;
        padding: 80px 20px;
        background: radial-gradient(circle at center, #1a1f2e 0%, #0d1117 100%);
        border-radius: 20px;
        margin-bottom: 40px;
        border: 1px solid #30363d;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00E5FF, #39FF14);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Tarjetas Glassmorphism */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    /* Botones Premium */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00E5FF, #0077FF);
        border: none; color: white; font-weight: bold;
        border-radius: 10px; padding: 10px 25px; width: 100%;
    }
    
    /* Terminal Console */
    .terminal-window {
        background-color: #010409;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        color: #39FF14;
        height: 250px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = 'inicio'

def change_page(page_name):
    st.session_state.page = page_name

# ==========================================
# 🏠 PÁGINA DE INICIO (HOME)
# ==========================================
if st.session_state.page == 'inicio':
    st.markdown(f"""
        <div class="hero-section">
            <h1 class="hero-title">FlowBio Intelligence</h1>
            <p style="font-size: 1.5rem; color: #8b949e;">La primera plataforma de Agentes de IA para Optimización EOR</p>
            <p style="max-width: 800px; margin: 20px auto; color: #8b949e;">
                Reduzca el factor de daño, optimice la movilidad de fluidos y maximice su recuperación incremental 
                mediante flujos de trabajo autónomos PIML.
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="glass-card"><h3>🚀 Agentes Autónomos</h3><p>Workflow de agentes que limpian datos, validan física y calculan ROI sin intervención humana.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h3>🧬 Motor PIML</h3><p>Modelado de fluidos no newtonianos integrado con leyes fundamentales de la termodinámica.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card"><h3>💰 Success Fee</h3><p>Modelo de negocio de bajo riesgo. Solo facturamos sobre la producción incremental real.</p></div>', unsafe_allow_html=True)

    st.write("<br>"*2, unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        if st.button("✨ ENTRAR AL DASHBOARD DE COMANDO", key="btn_entrar"):
            change_page('dashboard')
            st.rerun()

# ==========================================
# 📊 DASHBOARD DE COMANDO (CON REPORTE PDF)
# ==========================================
elif st.session_state.page == 'dashboard':
    with st.sidebar:
        st.markdown("<h1 style='color: #00E5FF;'>🧬 FlowBio</h1>", unsafe_allow_html=True)
        if st.button("🏠 Regresar al Inicio"):
            change_page('inicio')
            st.rerun()
        st.divider()
        st.markdown("### ☁️ S3 Data Lake Source")
        asset = st.selectbox("Activo S3", ["UKCS_North_Sea_Asset_01", "Veracruz_South_Project"])
        st.divider()
        st.markdown("### ⚙️ Parámetros del Pozo")
        p_visc = st.slider("Viscosidad (cP)", 1.0, 200.0, 85.0)
        p_perm = st.slider("Permeabilidad (mD)", 10, 800, 350)
        st.divider()
        deploy = st.button("🚀 DESPLEGAR AGENTES")
        
        # --- GENERACIÓN DE PDF (Simulación) ---
        st.write("<br>"*5, unsafe_allow_html=True)
        if st.button("📄 GENERAR REPORTE PDF"):
            with st.spinner("Compilando reporte técnico..."):
                time.sleep(2)
                st.success("Reporte Técnico PDF generado con éxito.")
                st.download_button(
                    label="⬇️ DESCARGAR REPORTE",
                    data="Simulación de contenido PDF técnico para FlowBio Intelligence",
                    file_name=f"Reporte_EOR_{asset}.pdf",
                    mime="application/pdf"
                )

    st.markdown("<h2>Centro de Comando <span style='color:#00E5FF;'>EOR</span></h2>", unsafe_allow_html=True)

    if not deploy:
        st.write("<br>"*5, unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; opacity: 0.4;'>
                <h1 style='font-size: 4rem;'>🖥️</h1>
                <h3>CONSOLA EN STANDBY</h3>
                <p>Presione 'Desplegar Agentes' en el panel lateral para iniciar el análisis PIML</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # 1. TERMINAL
        terminal_placeholder = st.empty()
        log_lines = [
            "> Iniciando handshake con AWS S3...",
            f"> Extrayendo logs de {asset}...",
            "> Data Agent: Estructurando series de tiempo... [OK]",
            "> Physics Agent: Resolviendo ecuación de transporte... [OK]",
            "> Skin Agent: Calculando daño de formación... [OK]",
            "> Agentes sincronizados. Renderizando UI..."
        ]
        current_log = ""
        for line in log_lines:
            current_log += f"<div>> {line}</div>"
            terminal_placeholder.markdown(f'<div class="terminal-window">{current_log}</div>', unsafe_allow_html=True)
            time.sleep(0.3)

        # 2. MÉTRICAS DINÁMICAS
        incremental = int(22500 * (p_perm/350) * (p_visc/85))
        revenue = incremental * 65
        fee = revenue * 0.05

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><p style="color:#8b949e;">CRUDO INCREMENTAL</p><h2 style="color:#39FF14;">+{incremental:,} bbls</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><p style="color:#8b949e;">GANANCIA OPERATIVA</p><h2 style="color:#39FF14;">${revenue/1e6:.1f}M USD</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card" style="border-color:#00E5FF;"><p style="color:#00E5FF;">SUCCESS FEE</p><h2 style="color:#00E5FF;">${fee:,.0f} USD</h2></div>', unsafe_allow_html=True)

        # 3. GRÁFICO PLOTLY
        meses = np.arange(1, 37)
        baseline = 3500 * np.exp(-0.06 * meses)
        optimized = np.copy(baseline)
        optimized[12:] = baseline[12:] + (incremental/15) * np.exp(-0.04 * (meses[12:] - 12))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=meses, y=baseline, name='Status Quo', line=dict(color='#ff5f56', dash='dot')))
        fig.add_trace(go.Scatter(x=meses, y=optimized, name='FlowBio EOR', line=dict(color='#39FF14', width=4), fill='tonexty', fillcolor='rgba(57, 255, 20, 0.1)'))
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
