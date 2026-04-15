import streamlit as st
import boto3
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="FlowBio Intelligence — EOR Managed Agents",
    page_icon="🤖",
    layout="wide"
)

# --- CONEXIÓN A AWS S3 ---
def get_s3_client():
    # Usa los secrets configurados en Streamlit Cloud
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
        st.error(f"Error conectando con el Cerebro PIML en AWS: {e}")
        return None

# --- LÓGICA PRINCIPAL ---
data = load_report_from_s3()

if data:
    meta = data["metadata"]
    resumen = data["resumen_ejecutivo"]
    esg = data.get("esg_cbam", {})
    
    # --- ENCABEZADO ---
    st.title("🤖 FlowBio Intelligence — EOR Managed Agents")
    st.markdown(f"**Cerebro Analítico PIML para Recuperación Secundaria** | Actualizado: {meta['timestamp'][:16]}")
    st.divider()

    # --- MÉTRICAS PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pozos Analizados", f"{meta['total_pozos_analizados']}")
    with col2:
        st.metric("Candidatos Na-CMC", f"{resumen['candidatos_inyeccion']}")
    with col3:
        st.metric("Mejora Promedio EOR", f"{resumen['mejora_promedio_pct']}%", delta="+5.2%")
    with col4:
        st.metric("Ahorro OPEX Proyectado", f"${resumen['ahorro_total_usd']:,} USD")

    st.divider()

    # --- CUERPO DEL DASHBOARD ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Análisis de Yacimiento y ESG")
        
        tab1, tab2 = st.tabs(["Distribución de Daño (Skin)", "Impacto Ambiental (CO2)"])
        
        with tab1:
            # Gráfico de barras para niveles de Skin
            skin_data = pd.DataFrame({
                "Nivel": ["Crítico (S>15)", "Alto (8-15)", "Moderado (3-8)"],
                "Cantidad": [resumen['pozos_criticos'], resumen['pozos_altos'], resumen['pozos_moderados']]
            })
            fig_skin = px.bar(skin_data, x='Nivel', y='Cantidad', color='Nivel', 
                             color_discrete_map={"Crítico (S>15)": "#ef553b", "Alto (8-15)": "#fecb52", "Moderado (3-8)": "#636efa"})
            st.plotly_chart(fig_skin, use_container_width=True)

        with tab2:
            if esg:
                st.info(f"🍀 **Ahorro Total de Carbono:** {esg['total_ton_co2_ahorradas']} tCO2/año")
                st.success(f"💶 **Evitado en Impuestos CBAM (EU):** ${esg['total_cbam_usd_evitado']:,} USD/año")
                
                # Gráfico circular de pozos ESG
                fig_esg = px.pie(values=[esg['pozos_esg_alto'], resumen['candidatos_inyeccion'] - esg['pozos_esg_alto']], 
                                names=['Impacto Alto', 'Impacto Medio'], hole=0.4, title="Pozos con Alto Potencial ESG")
                st.plotly_chart(fig_esg, use_container_width=True)

    with col_right:
        st.subheader("🔔 Alertas Prioritarias")
        for alerta in data.get("alertas", []):
            with st.expander(f"{alerta['nivel']} - {alerta['pozo']}"):
                st.write(f"**Tipo:** {alerta['tipo']}")
                st.write(f"**Valor:** {alerta['valor']}")
                st.write(f"**Acción:** {alerta['accion']}")
                if alerta['impacto_usd'] > 0:
                    st.caption(f"Impacto económico: ${alerta['impacto_usd']:,} USD")

    st.divider()

    # --- TABLA DE OPORTUNIDADES ---
    st.subheader("🎯 Top Oportunidades de Inyección (Na-CMC FlowBio)")
    df_ops = pd.DataFrame(data["top_oportunidades_eor"])
    st.dataframe(df_ops.style.highlight_max(axis=0, subset=['mejora_pct'], color='#2e7d32'), use_container_width=True)

    # --- MENSAJES POR PERFIL ---
    st.divider()
    st.subheader("💬 Recomendaciones de los Agentes")
    perfiles = data.get("mensajes_por_perfil", {})
    p1, p2, p3 = st.columns(3)
    p1.info(f"**EOR Manager:**\n\n{perfiles.get('eor_manager', 'Sin datos')}")
    p2.warning(f"**Reservoir Engineer:**\n\n{perfiles.get('reservoir_engineer', 'Sin datos')}")
    p3.success(f"**ESG Manager:**\n\n{perfiles.get('esg_manager', 'Sin datos')}")

else:
    st.warning("Esperando a que los agentes en AWS SageMaker generen el primer reporte PIML...")
