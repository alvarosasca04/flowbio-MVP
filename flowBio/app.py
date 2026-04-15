import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS (DeepTech UX)
# ==========================================
st.set_page_config(
    page_title="FlowBio EOR Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS para Dark Mode premium, tipografía y acentos
st.markdown("""
    <style>
    /* Fondo principal y acentos */
    .stApp {
        background-color: #0B0E14;
    }
    
    /* Personalización de métricas */
    div[data-testid="stMetricValue"] {
        color: #39FF14 !important; /* Verde Neón para números clave */
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricDelta"] {
        color: #00E5FF !important; /* Cyan para los deltas */
    }
    
    /* Botón principal */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00E5FF 0%, #0088FF 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        height: 3rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #39FF14 0%, #00E5FF 100%);
        box-shadow: 0px 0px 15px rgba(57, 255, 20, 0.5);
        transform: translateY(-2px);
    }
    
    /* Títulos y separadores */
    h1, h2, h3 {
        color: #F8F9FA !important;
        font-family: 'Inter', sans-serif;
    }
    hr {
        border-color: #1F2937;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PANEL DE CONTROL LATERAL (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00E5FF;'>FlowBio Intelligence</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #6B7280; margin-top: -15px;'>EOR Agentic OS</h4>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 🗄️ Ingesta de Datos")
    uploaded_file = st.file_uploader("Cargar historial de producción (CSV)", type=['csv'])
    
    st.markdown("### ⚙️ Parámetros de Yacimiento")
    perm = st.slider("Permeabilidad (mD)", min_value=1, max_value=1000, value=250, step=10)
    visc = st.slider("Viscosidad del crudo (cP)", min_value=1.0, max_value=150.0, value=45.5, step=0.5)
    sw = st.slider("Saturación de Agua (Sw)", min_value=0.1, max_value=0.9, value=0.6, step=0.05)
    
    st.divider()
    deploy_clicked = st.button("🚀 DESPLEGAR AGENTES EOR")

# ==========================================
# 3. INTERFAZ PRINCIPAL (Main Area)
# ==========================================
st.title("Centro de Comando EOR")
st.markdown("Plataforma de orquestación de agentes de IA para Recuperación Secundaria Optimizada.")
st.divider()

if not deploy_clicked:
    st.info("👈 Configure los parámetros del yacimiento y despliegue los agentes para iniciar la simulación PIML (Physics-Informed Machine Learning).")
else:
    # --- SIMULACIÓN DE AGENTES (Terminal Visual) ---
    with st.status("Iniciando Enjambre de Agentes FlowBio...", expanded=True) as status:
        time.sleep(1)
        st.write("⏳ **Data Agent:** Limpiando y estructurando historial del CSV... `[OK]`")
        time.sleep(1.2)
        st.write("⏳ **Physics Agent:** Aplicando Ley de Darcy y restricciones termodinámicas para M=1... `[OK]`")
        time.sleep(1.5)
        st.write("⏳ **Skin Factor Agent:** Optimizando concentración para evitar taponamiento físico... `[OK]`")
        time.sleep(1.2)
        st.write("⏳ **Financial Agent:** Proyectando Línea Base (DCA) y calculando ROI... `[OK]`")
        time.sleep(0.5)
        status.update(label="Flujo de Trabajo Agentic Completado", state="complete", expanded=False)

    st.success("✅ Modelado finalizado. Mostrando proyecciones financieras y operativas.")
    
    # --- RESULTADOS FINANCIEROS (Métricas) ---
    st.markdown("### 💰 Impacto Financiero y Operativo Proyectado (36 Meses)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Crudo Incremental Proyectado", value="+22,500 bbls", delta="↑ Alta certidumbre")
    with col2:
        st.metric(label="Ganancia Operativa Adicional", value="+$1.5M USD", delta="Neto de Capex/Opex")
    with col3:
        # Usamos HTML para forzar el color Cyan en el Success Fee para distinguirlo
        st.markdown(f"""
            <div style='background-color: #111827; padding: 1rem; border-radius: 0.5rem; border: 1px solid #1F2937;'>
                <p style='color: #9CA3AF; margin-bottom: 0;'>Tarifa FlowBio (Success Fee)</p>
                <h2 style='color: #00E5FF; margin-top: 0;'>$67,500 USD</h2>
                <p style='color: #6B7280; font-size: 0.8rem; margin-bottom: 0;'>* Solo facturable sobre extracción exitosa</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- VISUALIZACIÓN GRÁFICA (Plotly) ---
    st.markdown("### 📈 Curva de Declinación (DCA) vs Intervención FlowBio")
    
    # Generación de datos dummy matemáticamente coherentes
    meses = np.arange(1, 37)
    intervencion_mes = 12
    
    # Baseline: Declinación exponencial
    baseline = 3000 * np.exp(-0.06 * meses)
    
    # Optimized: Empuje por inyección de polímeros (a partir del mes de intervención)
    optimized = np.copy(baseline)
    optimized[intervencion_mes:] = baseline[intervencion_mes:] + 1200 * np.exp(-0.03 * (meses[intervencion_mes:] - intervencion_mes))
    
    # Creación del gráfico Plotly
    fig = go.Figure()

    # Trazo 1: Línea Base (Status Quo)
    fig.add_trace(go.Scatter(
        x=meses, y=baseline,
        mode='lines',
        name='Status Quo (Declinación Base)',
        line=dict(color='#FF3366', width=3, dash='dash') # Rojo oscuro
    ))

    # Trazo 2: Proyección FlowBio con área sombreada
    fig.add_trace(go.Scatter(
        x=meses, y=optimized,
        mode='lines',
        name='Proyección Optimizada FlowBio',
        line=dict(color='#39FF14', width=4), # Verde Neón
        fill='tonexty', # Sombrear hasta la línea anterior (Baseline)
        fillcolor='rgba(57, 255, 20, 0.15)' # Verde Neón translúcido
    ))
    
    # Punto de Intervención
    fig.add_vline(x=intervencion_mes, line_width=1, line_dash="dot", line_color="#00E5FF")
    fig.add_annotation(
        x=intervencion_mes, y=2800,
        text="Inicio Inyección Na-CMC",
        showarrow=True, arrowhead=1, arrowcolor="#00E5FF",
        font=dict(color="#00E5FF", size=12),
        ax=40, ay=-40
    )

    # Diseño del Layout (Dark Mode puro)
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Meses Operativos",
        yaxis_title="Producción (bbls/mes)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Etiqueta explicativa
    st.caption("🟢 **Área de Barriles Incrementales:** Volumen adicional recuperado gracias a la optimización de la tasa de movilidad y la reducción del *fingering* viscoso.")
