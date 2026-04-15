import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="FlowBio EOR Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INYECCIÓN DE CSS AVANZADO (Diseño HTML/SaaS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo oscuro profundo */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Ocultar elementos predeterminados de Streamlit para más limpieza */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tarjetas de Métricas (Estilo Dashboard Web) */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
        box-shadow: 0 8px 15px rgba(88, 166, 255, 0.1);
    }
    .metric-title {
        color: #8b949e;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .metric-value {
        color: #39FF14; /* Verde Neón */
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
    }
    .metric-value.cyan { color: #00E5FF; /* Cyan para la tarifa */ }
    .metric-delta {
        color: #58a6ff;
        font-size: 0.85rem;
        margin-top: 5px;
    }

    /* Terminal de Agentes */
    .terminal-container {
        background-color: #010409;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #39FF14;
        margin-bottom: 20px;
    }
    .terminal-header {
        display: flex;
        gap: 8px;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #30363d;
    }
    .dot { width: 12px; height: 12px; border-radius: 50%; }
    .dot-red { background-color: #ff5f56; }
    .dot-yellow { background-color: #ffbd2e; }
    .dot-green { background-color: #27c93f; }

    /* Botón Principal */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        height: 3.5rem;
        width: 100%;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. PANEL DE CONTROL LATERAL (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='color: #00E5FF; margin-bottom: 0; font-size: 2rem;'>FlowBio</h1>
            <p style='color: #8b949e; letter-spacing: 2px; margin-top: -10px;'>AGENTIC OS</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🗄️ Ingesta de Datos")
    uploaded_file = st.file_uploader("Historial de producción (CSV)", type=['csv'])
    
    st.markdown("### ⚙️ Parámetros Físicos")
    perm = st.slider("Permeabilidad (mD)", 1, 1000, 250, 10)
    visc = st.slider("Viscosidad (cP)", 1.0, 150.0, 45.5, 0.5)
    sw = st.slider("Saturación de Agua (Sw)", 0.1, 0.9, 0.6, 0.05)
    
    st.markdown("<br>", unsafe_allow_html=True)
    deploy_clicked = st.button("🚀 DESPLEGAR AGENTES")

# ==========================================
# 4. INTERFAZ PRINCIPAL (Main Area)
# ==========================================
st.markdown("<h2 style='color: white; font-weight: 300;'>Centro de Comando <span style='color: #00E5FF; font-weight: 700;'>EOR</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #8b949e;'>Orquestación de Agentes PIML para Recuperación Secundaria Avanzada.</p>", unsafe_allow_html=True)
st.divider()

if not deploy_clicked:
    st.info("💡 Esperando configuración. Ajuste los parámetros en el panel izquierdo y despliegue los agentes.")
else:
    # --- TERMINAL VISUAL (Simulación HTML) ---
    terminal_placeholder = st.empty()
    
    def render_terminal(lines):
        html = f"""
        <div class="terminal-container">
            <div class="terminal-header">
                <div class="dot dot-red"></div>
                <div class="dot dot-yellow"></div>
                <div class="dot dot-green"></div>
                <span style="color: #8b949e; font-size: 0.8rem; margin-left: 10px;">flowbio-agents@cluster ~ %</span>
            </div>
            {"<br>".join(lines)}
        </div>
        """
        terminal_placeholder.markdown(html, unsafe_allow_html=True)

    # Simulación de agentes en tiempo real
    lines = ["> Iniciando Enjambre de Agentes FlowBio..."]
    render_terminal(lines)
    time.sleep(1)
    
    lines.append("> [Agente Datos] Limpiando y estructurando dataset... <span style='color: #58a6ff;'>[OK]</span>")
    render_terminal(lines)
    time.sleep(1.2)
    
    lines.append("> [Agente Física] Aplicando Ley de Darcy y PIML (M=1)... <span style='color: #58a6ff;'>[OK]</span>")
    render_terminal(lines)
    time.sleep(1.5)
    
    lines.append("> [Agente Químico] Optimizando concentración (Skin Factor)... <span style='color: #58a6ff;'>[OK]</span>")
    render_terminal(lines)
    time.sleep(1.2)
    
    lines.append("> [Agente Finanzas] Proyectando DCA y calculando ROI... <span style='color: #58a6ff;'>[OK]</span>")
    lines.append("> <b>Ejecución Completada.</b> Modelos exportados a consola UI.")
    render_terminal(lines)
    time.sleep(0.5)
    
    # --- RESULTADOS FINANCIEROS (Tarjetas HTML Personalizadas) ---
    st.markdown("### 📊 Proyección Financiera a 36 Meses")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Crudo Incremental Proyectado</div>
            <div class="metric-value">+22,500 <span style="font-size: 1.2rem;">bbls</span></div>
            <div class="metric-delta">↑ Con base en simulación térmica</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Ganancia Operativa Neta</div>
            <div class="metric-value">+$1.5M <span style="font-size: 1.2rem;">USD</span></div>
            <div class="metric-delta">Neto de Capex/Opex y Polímero</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-card" style="border-color: #00E5FF; background-color: #0d1520;">
            <div class="metric-title">Tarifa FlowBio (Success Fee)</div>
            <div class="metric-value cyan">$67,500 <span style="font-size: 1.2rem;">USD</span></div>
            <div class="metric-delta" style="color: #8b949e;">* 100% ligada al éxito de extracción</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # --- VISUALIZACIÓN GRÁFICA (Plotly) ---
    # Generación de datos dummy matemáticos (Sin cambiar tu lógica)
    meses = np.arange(1, 37)
    intervencion_mes = 12
    baseline = 3000 * np.exp(-0.06 * meses)
    optimized = np.copy(baseline)
    optimized[intervencion_mes:] = baseline[intervencion_mes:] + 1200 * np.exp(-0.03 * (meses[intervencion_mes:] - intervencion_mes))
    
    fig = go.Figure()

    # Línea Base
    fig.add_trace(go.Scatter(
        x=meses, y=baseline,
        mode='lines',
        name='Status Quo (DCA)',
        line=dict(color='#ff5f56', width=3, dash='dash') 
    ))

    # Línea FlowBio
    fig.add_trace(go.Scatter(
        x=meses, y=optimized,
        mode='lines',
        name='FlowBio Optimizada',
        line=dict(color='#39FF14', width=4), 
        fill='tonexty', 
        fillcolor='rgba(57, 255, 20, 0.1)' 
    ))
    
    # Línea de intervención
    fig.add_vline(x=intervencion_mes, line_width=1, line_dash="dot", line_color="#00E5FF")
    fig.add_annotation(
        x=intervencion_mes, y=max(optimized)*0.9,
        text="Inyección Na-CMC",
        showarrow=True, arrowhead=2, arrowcolor="#00E5FF",
        font=dict(color="#00E5FF", size=12),
        ax=40, ay=-30
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Meses Operativos",
        yaxis_title="Producción (bbls/mes)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0),
        hovermode="x unified",
        font=dict(family="Courier New, monospace")
    )

    st.plotly_chart(fig, use_container_width=True)
