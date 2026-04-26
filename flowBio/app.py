import streamlit as st
import streamlit.components.v1 as components
import json
import boto3
import time
from datetime import datetime

st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide")

# Estilos CSS intactos
st.markdown("""
<style>
    .stApp { background: #060B11; }
    .kpi-box { background: rgba(13,21,32,0.8); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 22px; border-top: 4px solid #00E5A0; height: 100%; }
    .kpi-label { font-size:11px; color:#64748B; font-weight:600; text-transform:uppercase; }
    .kpi-value { font-size:32px; font-weight:800; color:#fff; margin:5px 0; }
    .kpi-sub { font-size:13px; font-weight:600; color:#00E5A0; margin:0; }
    .diag-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .diag-key { color:#64748B; font-size:12px; }
    .diag-val { color:#fff; font-size:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

def load_data_from_s3():
    try:
        s3 = boto3.client('s3', region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/dashboard_data.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        st.error(f"Error cargando datos: {e}"); return None

# ── KPI CALCULATOR ROBUSTO ──
def get_kpis(d):
    # Intentamos leer el diccionario 'ahorro' si existe, si no, calculamos en vivo
    ahorro = d.get('ahorro', {})
    proyeccion = d.get('proyeccion', [])
    
    # Si ahorro está en el JSON, lo usamos, si no, lo derivamos de la proyección (protección)
    barriles = float(ahorro.get('barriles', 0)) if isinstance(ahorro, dict) else 0
    valor = float(ahorro.get('valor_extra', 0)) if isinstance(ahorro, dict) else 0
    fee = float(ahorro.get('fee', 0)) if isinstance(ahorro, dict) else 0
    pb = float(ahorro.get('payback', 0)) if isinstance(ahorro, dict) else 0
    eur = float(ahorro.get('eur', 0)) if isinstance(ahorro, dict) else sum(r.get('P50',0) for r in proyeccion)
    
    return {'eur': eur, 'barriles': barriles, 'valor': valor, 'fee': fee, 'pb': pb}

# ── LOGICA DE UI ──
if 'all_data' not in st.session_state: st.session_state.all_data = load_data_from_s3()
datos = st.session_state.all_data

if datos:
    # Aseguramos que lista_pozos tenga TODO el contenido del JSON
    lista_pozos = sorted(list(datos.keys()))
    
    pozo = st.sidebar.selectbox("📍 Selecciona Pozo:", lista_pozos)
    d = datos[pozo]
    kpis = get_kpis(d)

    st.title(f"Command Center: {pozo}")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL (MES)</p><p class="kpi-value">+{int(kpis["barriles"]):,}</p><p class="kpi-sub">bbls / mes</p></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA GENERADO</p><p class="kpi-value">${kpis["valor"]:,.0f}</p><p class="kpi-sub">USD / mes</p></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${kpis["fee"]:,.0f}</p><p class="kpi-sub">15%</p></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{kpis["pb"]}</p><p class="kpi-sub">Meses</p></div>', unsafe_allow_html=True)

    # Gráfica
    proyeccion = d.get('proyeccion', [])
    x = [r.get('mes', i) for i, r in enumerate(proyeccion)]
    p50 = [r.get('P50', 0) for r in proyeccion]
    p10 = [r.get('P10', 0) for r in proyeccion]
    
    chart_data = json.dumps({"x": x, "p50": p50, "p10": p10})
    script = f"""
    <script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>
    <div id='plot' style='height:400px; background:#0D1520;'></div>
    <script>
        var pd = {chart_data};
        Plotly.newPlot('plot', [
            {{x:pd.x, y:pd.p10, name:'Status Quo', line:{{dash:'dot', color:'gray'}}, type:'scatter'}},
            {{x:pd.x, y:pd.p50, name:'FlowBio EOR', line:{{color:'#00E5A0', width:3}}, type:'scatter'}}
        ], {{paper_bgcolor:'#0D1520', plot_bgcolor:'#0D1520', font:{{color:'white'}}, margin:{{t:30, b:40, l:50, r:20}}}}, {{responsive:true}});
    </script>
    """
    components.html(script, height=430)
else:
    st.error("No hay datos en S3. Por favor ejecuta el Jupyter Notebook.")
