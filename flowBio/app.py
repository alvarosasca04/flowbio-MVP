"""
FlowBio Intelligence — Subsurface Diagnostic Console v3.1 (Agent-Linked)
UX diseñado para: EOR Manager · Reservoir Engineer · ESG Manager
Sincronizado con: CrewAI Managed Agents + AWS S3 Data Lake
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math, io, warnings, json
from datetime import datetime
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CONFIGURACIÓN GLOBAL ---
BUCKET = "flowbio-data-lake-v2-627807503177-us-east-2-an"
# Colores del Branding FlowBio
BG="#0D1B2A"; BG2="#0A1520"; BG3="#071018"; BRD="#1E3A60"
TX="#D0E4F8"; GR="#4BAE6E"; BL="#4A9FD4"; RD="#E05A5A"
AM="#E8A030"; PU="#9B7FD4"; GR2="#3A7D44"; TEAL="#00C9B1"

# ═══════════════════════════════════════════
# ESTILOS CSS (Figma to Streamlit)
# ═══════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');
*{{box-sizing:border-box}}
html,body,.stApp{{background:{BG};color:{TX};font-family:'Outfit',sans-serif}}
section[data-testid="stSidebar"]{{background:{BG2};border-right:1px solid {BRD}}}
.stTabs [aria-selected="true"]{{color:{GR}!important;border-bottom:2px solid {GR}!important}}
.stTabs [data-baseweb="tab"]{{color:#6A8AAA;font-family:'Outfit',sans-serif;font-size:13px}}

/* KPIS */
.kcard{{background:{BG2};border:1px solid {BRD};border-radius:14px;padding:20px 14px;text-align:center;position:relative;overflow:hidden}}
.kcard-eor::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{BL},{GR})}}
.kcard-res::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{PU},{BL})}}
.kcard-esg::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{GR},{TEAL})}}
.klbl{{font-size:9px;letter-spacing:2px;color:#6A8AAA;font-weight:700;text-transform:uppercase;margin-bottom:6px}}
.kval{{font-size:30px;font-weight:900;font-family:'Space Mono',monospace;line-height:1.1}}
.ksub{{font-size:10px;color:#4A7AAA;margin-top:5px}}

/* AGENT CARDS */
.agent-card{{background:{BG2};border:1px solid {BRD};border-radius:12px;padding:16px;position:relative;overflow:hidden;height:100%}}
.agent-card.done{{border-color:{GR}}}
.agent-card.idle{{border-color:{BRD}}}
.agent-badge{{font-size:9px;font-family:'Space Mono',monospace;padding:3px 10px;border-radius:20px;font-weight:700;display:inline-block;margin-bottom:10px}}
.agent-badge.done{{background:rgba(75,174,110,.15);color:{GR};border:1px solid {GR}}}
.agent-badge.idle{{background:rgba(30,58,96,.4);color:#6A8AAA;border:1px solid {BRD}}}
.agent-name{{font-size:14px;font-weight:700;margin-bottom:4px}}
.agent-output{{font-size:10px;font-family:'Space Mono',monospace;color:{GR};margin-top:10px;background:{BG3};border-radius:6px;padding:8px;border:1px solid rgba(75,174,110,0.2)}}

/* ALERT BOXES */
.alert-crit{{background:rgba(224,90,90,.08);border:1px solid rgba(224,90,90,.3);border-left:4px solid {RD};border-radius:8px;padding:12px 14px;margin-bottom:8px}}
.alert-ok{{background:rgba(75,174,110,.08);border:1px solid rgba(75,174,110,.3);border-left:4px solid {GR};border-radius:8px;padding:12px 14px;margin-bottom:8px}}
.sh{{font-size:10px;letter-spacing:2.5px;color:#6A8AAA;font-weight:700;text-transform:uppercase;border-bottom:1px solid {BRD};padding-bottom:8px;margin:24px 0 14px}}
.box-g{{background:rgba(75,174,110,.1);border:1px solid rgba(75,174,110,.4);border-radius:10px;padding:14px;font-size:12px;color:#7ABF8A}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# S3 CONEXIÓN Y CARGA DE DATOS
# ═══════════════════════════════════════════
@st.cache_resource(ttl=300)
def get_s3():
    try:
        import boto3
        c = boto3.client("s3",
            aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["aws"].get("AWS_DEFAULT_REGION", "us-east-2"))
        return c, True
    except: return None, False

@st.cache_data(ttl=60)
def cargar_reporte_agentes():
    """
    Sincronización con SageMaker: Carga el JSON generado por el Agente 3.
    """
    s3, ok = get_s3()
    if not ok: return _reporte_demo(), "Modo Demo (S3 desconectado)", False
    try:
        # Buscamos el reporte real disparado por CrewAI
        obj = s3.get_object(Bucket=BUCKET, Key="agentes/ultimo_reporte.json")
        rep = json.loads(obj["Body"].read())
        ts = rep.get("metadata", {}).get("timestamp", "—")
        return rep, f"LIVE · Agente 3 ({ts[11:16]})", True
    except:
        return _reporte_demo(), "Modo Demo (Sin reporte en S3)", False

def _reporte_demo():
    return {
        "metadata": {"timestamp": datetime.now().isoformat(), "total_pozos_analizados": 15},
        "resumen_ejecutivo": {
            "skin_promedio": 7.4, "pozos_criticos": 2, "candidatos_inyeccion": 8,
            "mejora_promedio_pct": 14.2, "ahorro_total_anual_usd": 847000
        },
        "alertas": [
            {"nivel": "CRÍTICO", "tipo": "Skin Damage Severo", "pozo": "49/9-1", "valor": "S = 18.42", "accion": "Inyección Na-CMC prioritaria."},
            {"nivel": "ADVERTENCIA", "tipo": "Riesgo FPI", "pozo": "211/18-1", "valor": "FPI = 0.62", "accion": "Evaluar salinidad."}
        ],
        "top_oportunidades_eor": [
            {"pozo": "29/10-1", "mejora_pct": 18.4, "ahorro_anual_usd": 124000, "skin": 6.2, "recomendacion": "INYECTAR Na-CMC"}
        ]
    }

def trigger_agentes_sagemaker():
    """Dispara el archivo trigger.json para que los agentes en SageMaker inicien."""
    s3, ok = get_s3()
    if not ok: return False
    try:
        s3.put_object(
            Bucket=BUCKET,
            Key="agentes/trigger.json",
            Body=json.dumps({"trigger": True, "timestamp": datetime.now().isoformat()})
        )
        return True
    except: return False

# ═══════════════════════════════════════════
# DASHBOARD UI
# ═══════════════════════════════════════════
st.title("🛢️ FlowBio Intelligence")
st.markdown("### Subsurface Diagnostic Console · AI Managed Agents")

# --- TAB DE AGENTES (EL CORAZÓN DEL SISTEMA) ---
rep_ag, fuente_ag, es_real = cargar_reporte_agentes()

st.markdown(f"<div class='sh'>🤖 MANAGED AGENTS STATUS — {fuente_ag}</div>", unsafe_allow_html=True)

if st.button("▶ DISPARAR AGENTES EN SAGEMAKER", type="primary"):
    if trigger_agentes_sagemaker():
        st.success("✅ ¡Trigger enviado! Los agentes están iniciando la simulación en SageMaker.")
    else: st.error("❌ Error de conexión con S3.")

col1, col2, col3 = st.columns(3)
status = "done" if es_real else "idle"
meta = rep_ag.get("metadata", {})
res = rep_ag.get("resumen_ejecutivo", {})

with col1:
    st.markdown(f"""
    <div class='agent-card {status}'>
      <div class='agent-badge {status}'>{'✓ FINALIZADO' if status=='done' else '⏸ EN ESPERA'}</div>
      <div class='agent-name'>Agente 1: Ingeniero de Datos</div>
      <div class='agent-desc'>Carga y limpieza de CSVs desde S3 Data Lake.</div>
      <div class='agent-output'>Input: UKCS_Wells.csv<br>Status: Aterrizado en S3</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='agent-card {status}'>
      <div class='agent-badge {status}'>{'✓ FINALIZADO' if status=='done' else '⏸ EN ESPERA'}</div>
      <div class='agent-name'>Agente 2: Simulador PIML</div>
      <div class='agent-desc'>Cálculo de Skin Factor y Reología Na-CMC.</div>
      <div class='agent-output'>Skin Promedio: {res.get('skin_promedio',0):.2f}<br>Mejora EOR: +{res.get('mejora_promedio_pct',0):.1f}%</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='agent-card {status}'>
      <div class='agent-badge {status}'>{'✓ FINALIZADO' if status=='done' else '⏸ EN ESPERA'}</div>
      <div class='agent-name'>Agente 3: Monitor de Alertas</div>
      <div class='agent-desc'>Generación de reporte ejecutivo y alertas.</div>
      <div class='agent-output'>Ahorro Total: ${res.get('ahorro_total_anual_usd',0):,.0f}<br>Reporte: ultimo_reporte.json</div>
    </div>""", unsafe_allow_html=True)

# --- KPIs DEL REPORTE ---
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Pozos Analizados", f"{meta.get('total_pozos_analizados', 0)}")
k2.metric("Candidatos EOR", f"{res.get('candidatos_inyeccion', 0)}", delta="Na-CMC Ready", delta_color="normal")
k3.metric("Skin Promedio", f"{res.get('skin_promedio', 0):.2f}")
k4.metric("Ahorro Proyectado", f"${res.get('ahorro_total_anual_usd', 0)/1000:.0f}K USD/año")

# --- ALERTAS DEL AGENTE 3 ---
st.markdown("<div class='sh'>🔔 ALERTAS GENERADAS POR IA</div>", unsafe_allow_html=True)
ca, cb = st.columns(2)

with ca:
    for a in rep_ag.get("alertas", []):
        cls = "alert-crit" if a["nivel"] == "CRÍTICO" else "alert-ok"
        st.markdown(f"""<div class='{cls}'><b>{a['tipo']}</b> — Pozo {a['pozo']}<br><small>{a['accion']}</small></div>""", unsafe_allow_html=True)

with cb:
    st.markdown("<div class='box-g'><b>📋 Recomendación de Campo:</b><br>" + rep_ag.get("recomendacion_campo", "Simulación pendiente.") + "</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center><small>FlowBio Intelligence v3.1 · Orizaba, Veracruz · 2026</small></center>", unsafe_allow_html=True)
