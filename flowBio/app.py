import streamlit as st
import boto3
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="FlowBio | EOR Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    div[data-testid="stExpander"] { border: 1px solid #31333f; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN AWS S3 ---
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
        return json.loads(response['Body'].read().decode('utf-8'))
    except:
        return None

# --- CARGA DE DATOS ---
data = load_report_from_s3()

if data:
    meta = data["metadata"]
    resumen = data["resumen_ejecutivo"]
    esg = data.get("esg_cbam", {})

    # ==========================================
    # 📱 BARRA LATERAL (CONTROL DE SISTEMA)
    # ==========================================
    with st.sidebar:
        st.title("🛡️ FlowBio OS")
        st.status("Conexión S3 Activa", state="complete")
        st.divider()
        st.write(f"**Motor:** `{meta.get('llm', 'Llama 3.3')}`")
        st.write(f"**Sincronización:** {meta['timestamp'][:16].replace('T', ' ')}")
        st.divider()
        st.caption("FlowBio Intelligence v3.5 | Orizaba, Veracruz")

    # ==========================================
    # 🖥️ DASHBOARD PRINCIPAL
    # ==========================================
    st.title("⚡ Centro de Inteligencia EOR")
    st.markdown("Optimización de recuperación secundaria mediante **Na-CMC Biopolymers**.")
    
    # --- KPIs SUPERIORES ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Pozos en Análisis", f"{meta.get('total_pozos_analizados', 500)}", "Campo UKCS")
    with c2: st.metric("Oportunidades EOR", f"{resumen['candidatos_inyeccion']}", "Aptos Na-CMC")
    with c3: st.metric("Mejora de Barrido", f"{resumen['mejora_promedio_pct']}%", delta="PIML Opt.", delta_color="normal")
    with c4: st.metric("ROI Proyectado (Anual)", f"${resumen['ahorro_total_usd']:,}", "USD OPEX")

    st.write("")
    
    # --- FILA 2: ANÁLISIS VISUAL ---
    col_main, col_alerts = st.columns([2, 1])

    with col_main:
        with st.container(border=True):
            tab_skin, tab_esg = st.tabs(["📊 Distribución de Daño", "🌱 Impacto Ambiental"])
            
            with tab_skin:
                skin_df = pd.DataFrame({
                    "Gravedad": ["Crítico (S>15)", "Alto (8-15)", "Moderado (3-8)"],
                    "Conteo": [resumen['pozos_criticos'], resumen['pozos_altos'], resumen['pozos_moderados']]
                })
                fig = px.bar(skin_df, x='Gravedad', y='Conteo', color='Gravedad',
                             color_discrete_map={"Crítico (S>15)": "#ff4b4b", "Alto (8-15)": "#ffa421", "Moderado (3-8)": "#00d4ff"})
                fig.update_layout(showlegend=False, height=350, margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            
            with tab_esg:
                st.write(f"🍀 **Ahorro de Carbono:** {esg.get('total_ton_co2_ahorradas', 0)} tCO2/año")
                st.write(f"💶 **Beneficio CBAM:** ${esg.get('total_cbam_usd_evitado', 0):,} USD/año")
                fig_esg = px.pie(values=[esg.get('pozos_esg_alto', 0), 100], names=['ESG Alto', 'Otros'], hole=0.6)
                fig_esg.update_layout(height=300, margin=dict(t=10, b=10))
                st.plotly_chart(fig_esg, use_container_width=True)

    with col_alerts:
        st.subheader("⚠️ Acciones Prioritarias")
        for a in data.get("alertas", []):
            color = "red" if a['nivel'] == "CRÍTICO" else "orange" if a['nivel'] == "ADVERTENCIA" else "blue"
            with st.expander(f":{color}[{a['nivel']}] - {a['pozo']}"):
                st.write(f"**{a['tipo']}:** {a['valor']}")
                st.caption(f"Acción sugerida: {a['accion']}")

    # --- FILA 3: TABLA DE OPERACIONES ---
    st.subheader("🎯 Pozos Candidatos para Intervención")
    df_ops = pd.DataFrame(data["top_oportunidades_eor"])
    st.dataframe(
        df_ops,
        column_config={
            "pozo": "Pozo ID",
            "mejora_pct": st.column_config.ProgressColumn("Mejora Barrido", format="%.1f%%", min_value=0, max_value=25),
            "ahorro_anual_usd": st.column_config.NumberColumn("Ahorro Anual", format="$%d"),
            "skin": "Factor Skin",
            "ds_optimo": "DS Na-CMC"
        },
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("🔄 Sincronizando con los Agentes en AWS... Por favor, espere.")
