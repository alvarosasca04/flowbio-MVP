import streamlit as st
import boto3
import json
import pandas as pd

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN DE AWS S3 (Vía Streamlit Secrets)
# ══════════════════════════════════════════════════════
BUCKET = "flowbio-data-lake-v2-627807503177-us-east-2-an"
REGION = "us-east-2"
REPORT_KEY = "agentes/ultimo_reporte.json"

st.set_page_config(page_title="FlowBio | EOR Intelligence", layout="wide", page_icon="💧")

@st.cache_data(ttl=60) # Refresca los datos cada 60 segundos
def load_report():
    try:
        # Autenticación segura usando los secretos de Streamlit Cloud
        s3 = boto3.client(
            "s3",
            region_name=REGION,
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
        )
        obj = s3.get_object(Bucket=BUCKET, Key=REPORT_KEY)
        return json.loads(obj["Body"].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error conectando con el Cerebro PIML en AWS: {e}")
        return None

# ══════════════════════════════════════════════════════
# INTERFAZ DE USUARIO (DASHBOARD)
# ══════════════════════════════════════════════════════
st.title("🤖 FlowBio Intelligence — EOR Managed Agents")
st.markdown("### Cerebro Analítico PIML para Recuperación Secundaria")

data = load_report()

if data:
    meta = data["metadata"]
    resumen = data["resumen_ejecutivo"]
    esg = data.get("esg_cbam", {})

    # --- MÉTRICAS PRINCIPALES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pozos Analizados", f"{meta['total_pozos_analizados']:,}")
    col2.metric("Skin Promedio Campo", f"{resumen['skin_promedio']:.2f}")
    col3.metric("Eficiencia de Barrido", f"+{resumen['mejora_promedio_pct']}%")
    col4.metric("ROI Proyectado (Anual)", f"${resumen['ahorro_total_usd']:,.0f} USD", delta="Success Fee $5/bbl")

    st.divider()

    # --- ALERTAS Y ESG ---
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("🔔 Alertas Prioritarias (Skin Factor)")
        for alerta in data.get("alertas", []):
            color = "red" if alerta["nivel"] == "CRÍTICO" else "orange" if alerta["nivel"] == "ADVERTENCIA" else "green"
            st.markdown(f"**:{color}[{alerta['tipo']}]** Pozo: `{alerta['pozo']}` | Valor: `{alerta['valor']}`")
            st.caption(f"Acción sugerida: {alerta['accion']}")

    with right_col:
        st.subheader("🌍 Impacto ESG / CBAM")
        if esg:
            st.success(f"🍃 **{esg.get('total_ton_co2_ahorradas', 0):.1f}** tCO₂ ahorradas/año")
            st.info(f"💶 **${esg.get('total_cbam_usd_evitado', 0):,.0f}** USD en impuestos CBAM evitados")
            st.markdown("---")
            st.caption("Na-CMC local derivado de biomasa invasora. 100% biodegradable y DNSH compliant.")

    st.divider()

    # --- TABLA DE OPORTUNIDADES ---
    st.subheader("🎯 Top Oportunidades de Inyección (Na-CMC FlowBio)")
    if "top_oportunidades_eor" in data and data["top_oportunidades_eor"]:
        df_ops = pd.DataFrame(data["top_oportunidades_eor"])
        st.dataframe(df_ops, use_container_width=True)
    else:
        st.info("No se detectaron oportunidades de inyección con los parámetros actuales.")

    # --- MENSAJES EJECUTIVOS ---
    st.divider()
    st.subheader("💬 Executive Insights por Perfil")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        with st.expander("💼 Mensaje para EOR Manager (Finanzas)"):
            st.write(data["mensajes_por_perfil"]["eor_manager"])
        with st.expander("⚙️ Mensaje para Reservoir Engineer (Física)"):
            st.write(data["mensajes_por_perfil"]["reservoir_engineer"])
    with p_col2:
        with st.expander("🌱 Mensaje para ESG Manager (Sostenibilidad)"):
            st.write(data["mensajes_por_perfil"]["esg_manager"])
        st.caption(f"Última actualización de agentes: {meta['timestamp']}")

else:
    st.warning("Esperando a que los agentes en AWS SageMaker generen el primer reporte PIML...")
