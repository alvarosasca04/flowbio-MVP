import streamlit as st
import boto3
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (Debe ser la primera línea) ---
st.set_page_config(
    page_title="FlowBio | EOR Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS (Para darle un toque más pro) ---
st.markdown("""
    <style>
    .big-font {font-size:24px !important; font-weight: bold;}
    .status-online {color: #28a745; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A AWS S3 ---
@st.cache_data(ttl=60) # Actualiza los datos cada 60 segundos automáticamente
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )

def load_report_from_s3():
    bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
    key = "agentes/ultimo_reporte.json"
    try:
        s3 = get_s3_client()
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        return None

# --- CARGA DE DATOS ---
data = load_report_from_s3()

if data:
    meta = data["metadata"]
    resumen = data["resumen_ejecutivo"]
    esg = data.get("esg_cbam", {})
    
    # ==========================================
    # 📱 BARRA LATERAL (SIDEBAR)
    # ==========================================
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1998/1998342.png", width=80) # Icono genérico (puedes cambiarlo)
        st.title("FlowBio OS")
        st.markdown("<span class='status-online'>● Sistema Online</span>", unsafe_allow_html=True)
        st.divider()
        st.caption("Última ejecución PIML:")
        st.write(f"⏱️ **{meta['timestamp'][:16].replace('T', ' ')}**")
        st.write(f"🧠 **Motor:** `{meta['llm']}`")
        st.divider()
        st.info("💡 **Tip:** Los datos se recargan automáticamente cada minuto si hay nuevas ejecuciones en AWS.")

    # ==========================================
    # 🖥️ PANTALLA PRINCIPAL
    # ==========================================
    st.title("⚡ EOR Managed Agents Dashboard")
    st.markdown("Análisis impulsado por IA para inyección de **Na-CMC FlowBio**.")
    st.write("") # Espacio
    
    # --- 1. KPIs GLOBALES ---
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pozos Analizados", f"{meta.get('total_pozos_analizados', 500)}")
        c2.metric("Candidatos Ideales", f"{resumen['candidatos_inyeccion']}", "Aptos para Na-CMC")
        c3.metric("Mejora Promedio (EOR)", f"{resumen['mejora_promedio_pct']}%", "+ Eficiencia", delta_color="normal")
        c4.metric("Ahorro OPEX Anual", f"${resumen['ahorro_total_usd']:,}", "USD Proyectados")

    st.write("") # Espacio
    
    # --- 2. GRÁFICOS Y ALERTAS (Layout 70% - 30%) ---
    col_charts, col_alerts = st.columns([2.5, 1])

    with col_charts:
        st.subheader("📊 Análisis de Yacimiento y Descarbonización")
        tab1, tab2 = st.tabs(["🔴 Factor de Daño (Skin)", "🍀 Impacto ESG (CBAM)"])
        
        with tab1:
            skin_data = pd.DataFrame({
                "Severidad": ["Crítico (S>15)", "Alto (8-15)", "Moderado (3-8)"],
                "Pozos": [resumen['pozos_criticos'], resumen['pozos_altos'], resumen['pozos_moderados']]
            })
            fig_skin = px.bar(skin_data, x='Severidad', y='Pozos', color='Severidad', 
                             color_discrete_map={"Crítico (S>15)": "#ff4b4b", "Alto (8-15)": "#ffa421", "Moderado (3-8)": "#29b5e8"})
            fig_skin.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_skin, use_container_width=True)

        with tab2:
            if esg:
                e1, e2 = st.columns(2)
                e1.success(f"**{esg['total_ton_co2_ahorradas']} tCO₂**\nAhorro Anual de Carbono")
                e2.info(f"**${esg['total_cbam_usd_evitado']:,} USD**\nImpuesto CBAM Evitado")
                
                fig_esg = px.pie(values=[esg['pozos_esg_alto'], resumen['candidatos_inyeccion'] - esg['pozos_esg_alto']], 
                                names=['Alto Potencial ESG', 'Potencial Estándar'], hole=0.5)
                fig_esg.update_traces(marker=dict(colors=['#00cc96', '#636efa']))
                fig_esg.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300)
                st.plotly_chart(fig_esg, use_container_width=True)

    with col_alerts:
        st.subheader("🚨 Alertas de Campo")
        with st.container(border=True, height=400): # Contenedor con scroll para no deformar la pantalla
            for alerta in data.get("alertas", []):
                color = "red" if alerta['nivel'] == "CRÍTICO" else "orange" if alerta['nivel'] == "ADVERTENCIA" else "green"
                st.markdown(f"**:{color}[{alerta['nivel']}]** | {alerta['pozo']}")
                st.write(f"*{alerta['tipo']} ({alerta['valor']})*")
                if alerta.get('impacto_usd', 0) > 0:
                    st.caption(f"💰 Riesgo/Oportunidad: ${alerta['impacto_usd']:,} USD")
                st.divider()

    # --- 3. DATA FRAME DE OPORTUNIDADES ---
    st.subheader("🎯 Top Oportunidades de Inyección")
    df_ops = pd.DataFrame(data.get("top_oportunidades_eor", []))
    if not df_ops.empty:
        # Formatear la tabla para que se vea más limpia
        st.dataframe(
            df_ops,
            column_config={
                "pozo": "Nombre del Pozo",
                "mejora_pct": st.column_config.ProgressColumn("Mejora %", format="%.1f%%", min_value=0, max_value=30),
                "ahorro_anual_usd": st.column_config.NumberColumn("Ahorro (USD/año)", format="$%d"),
                "skin": st.column_config.NumberColumn("Factor Skin", format="%.2f"),
                "ds_optimo": "DS Recomendado",
                "conc_optima": "Concentración"
            },
            hide_index=True,
            use_container_width=True
        )

    # --- 4. CONSOLA DE AGENTES ---
    st.write("")
    with st.expander("🤖 Ver conclusiones directas de los Agentes de IA", expanded=False):
        perfiles = data.get("mensajes_por_perfil", {})
        p1, p2, p3 = st.columns(3)
        p1.markdown(f"💼 **EOR Manager**\n> {perfiles.get('eor_manager', '')}")
        p2.markdown(f"🔧 **Reservoir Engineer**\n> {perfiles.get('reservoir_engineer', '')}")
        p3.markdown(f"🌱 **ESG Manager**\n> {perfiles.get('esg_manager', '')}")

else:
    # Pantalla de error más amigable
    st.error("🔌 No se pudo conectar con el Cerebro PIML en AWS.")
    st.info("Asegúrate de que los agentes en tu servidor EC2 hayan ejecutado el script `app.py` para generar el archivo `ultimo_reporte.json`.")
