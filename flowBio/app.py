import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import plotly.express as px
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

    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00E5FF, #0077FF);
        border: none; color: white; font-weight: bold;
        border-radius: 10px; padding: 10px 25px; width: 100%;
    }
    
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
        st.markdown('<div class="glass-card"><h3>🚀 Agentes Autónomos</h3><p>Workflow que limpia datos, valida física y calcula ROI sin intervención humana.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h3>🧬 Motor PIML</h3><p>Modelado de fluidos no newtonianos integrado con leyes fundamentales termodinámicas.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card"><h3>💰 Success Fee</h3><p>Modelo de bajo riesgo. Solo facturamos sobre la producción incremental real.</p></div>', unsafe_allow_html=True)

    st.write("<br>"*2, unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        if st.button("✨ ENTRAR AL DASHBOARD DE COMANDO", key="btn_entrar"):
            change_page('dashboard')
            st.rerun()

# ==========================================
# 📊 DASHBOARD DE COMANDO
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
        
        # --- GENERACIÓN DE REPORTE ---
        st.write("<br>"*5, unsafe_allow_html=True)
        if st.button("📄 GENERAR REPORTE TÉCNICO"):
            with st.spinner("Compilando reporte PIML..."):
                time.sleep(2)
                st.success("Reporte generado exitosamente.")
                st.download_button(
                    label="⬇️ DESCARGAR PDF",
                    data=f"REPORTE TÉCNICO FLOWBIO\nActivo: {asset}\nFecha: {datetime.now()}\nIncremental: Proyectado",
                    file_name=f"FlowBio_Report_{asset}.pdf",
                    mime="application/pdf"
                )

    st.markdown(f"<h2>Command Center <span style='color:#00E5FF;'>{asset}</span></h2>", unsafe_allow_html=True)

    if not deploy:
        st.write("<br>"*5, unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; opacity: 0.4;'>
                <h1 style='font-size: 4rem;'>🖥️</h1>
                <h3>CONSOLA EN STANDBY</h3>
                <p>Presione 'Desplegar Agentes' para iniciar el análisis geoespacial y físico</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # 1. TERMINAL
        terminal_placeholder = st.empty()
        log_lines = [
            "> Handshake con AWS S3 finalizado...",
            f"> Extrayendo logs geoespaciales de {asset}...",
            "> Data Agent: Estructurando series de tiempo... [OK]",
            "> Physics Agent: Resolviendo ecuación de transporte... [OK]",
            "> Skin Agent: Mapeando daño de formación... [OK]",
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

        # 3. MAPA DE POZOS (NUEVO)
        st.markdown("### 🗺️ Inteligencia Geoespacial: Mapa de Salud del Yacimiento")
        
        # Datos simulados basados en el activo seleccionado
        lat_base = 57.15 if "UKCS" in asset else 18.85
        lon_base = 2.15 if "UKCS" in asset else -97.10
        
        df_wells = pd.DataFrame({
            'Pozo': [f'Pozo-{i}' for i in range(15)],
            'lat': lat_base + np.random.uniform(-0.05, 0.05, 15),
            'lon': lon_base + np.random.uniform(-0.05, 0.05, 15),
            'Skin_Factor': np.random.uniform(2, 22, 15),
            'Status': np.random.choice(['Óptimo', 'Moderado', 'Crítico'], 15)
        })

        fig_map = px.scatter_mapbox(
            df_wells, lat="lat", lon="lon", color="Status", size="Skin_Factor",
            hover_name="Pozo", zoom=11, height=450,
            color_discrete_map={"Óptimo": "#39FF14", "Moderado": "#ffbd2e", "Crítico": "#ff5f56"}
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # 4. GRÁFICO DE PRODUCCIÓN
        st.markdown("### 📈 Análisis Predictivo de Producción")
        meses = np.arange(1, 37)
        baseline = 3500 * np.exp(-0.06 * meses)
        optimized = np.copy(baseline)
        optimized[12:] = baseline[12:] + (incremental/15) * np.exp(-0.04 * (meses[12:] - 12))

        fig_prod = go.Figure()
        fig_prod.add_trace(go.Scatter(x=meses, y=baseline, name='Status Quo', line=dict(color='#ff5f56', dash='dot')))
        fig_prod.add_trace(go.Scatter(x=meses, y=optimized, name='FlowBio EOR', line=dict(color='#39FF14', width=4), fill='tonexty', fillcolor='rgba(57, 255, 20, 0.1)'))
        fig_prod.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig_prod, use_container_width=True)
