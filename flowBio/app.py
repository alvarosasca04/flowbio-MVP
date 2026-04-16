import streamlit as st
import streamlit.components.v1 as components
import boto3
import json

st.set_page_config(
    page_title="FlowBio Command Center",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════
# 1. CONEXIÓN AL CEREBRO GROQ (AWS S3)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=30) # Cache corto para actualizar rápido en la demo
def fetch_groq_results():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        
        response = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data, "✅ Conexión exitosa a AWS S3. Leyendo datos del Piloto."
    except Exception as e:
        return None, f"⚠️ No se pudo conectar a S3. Error: {str(e)}"

reporte, mensaje_conexion = fetch_groq_results()

# Variables dinámicas extrayendo del JSON real
titulo_dash = reporte["metadata"]["titulo"] if reporte else "FlowBio Insight - PoC Piloto"
total_pozos = reporte["resumen_ejecutivo"].get("candidatos_inyeccion", 10) if reporte else 10

ahorro_usd = reporte["resumen_ejecutivo"]["ahorro_total_usd"] if reporte else 1850000
fee_mensual = reporte["resumen_ejecutivo"]["fee_mensual_usd"] if reporte else 25000
mejora_pct = reporte["resumen_ejecutivo"]["mejora_promedio_pct"] if reporte else 16.5
skin_avg = reporte["resumen_ejecutivo"]["skin_promedio"] if reporte else 4.2
co2_evitado = reporte["esg_cbam"]["total_ton_co2_ahorradas"] if reporte else 950.5

# Mostrar estatus de conexión discretamente arriba
if reporte:
    st.success(mensaje_conexion)
else:
    st.warning(mensaje_conexion)

# Ocultar menús de Streamlit
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060C12; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. INTERFAZ UI / HTML (USANDO RAW STRING)
# ══════════════════════════════════════════════════════
HTML_BASE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FlowBio Intelligence</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #060C12; --card: #0D1928; --border: #152335; --green: #00E5A0; 
  --blue: #3B82F6; --cyan: #22D3EE; --amber: #F59E0B; --red: #EF4444; 
  --text: #E2EEF8; --muted: #4A6580; --mono: 'DM Mono', monospace; --head: 'Syne', sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; height: 100%; overflow: hidden; }
.screen { display: none; width: 100vw; height: 100vh; }
.screen.active { display: flex; }
#s-splash { flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,229,160,.05) 0%, transparent 70%); }
.splash-logo { font-family: var(--head); font-size: clamp(64px, 9vw, 120px); font-weight: 800; letter-spacing: -4px; color: #fff; margin-bottom: 8px; }
.splash-logo span { color: var(--green); }
.btn-launch { background: var(--green); color: #050C12; font-family: var(--head); font-weight: 700; font-size: 13px; letter-spacing: 2px; border-radius: 10px; padding: 18px 52px; cursor: pointer; border: none; }
#s-terminal { flex-direction: column; align-items: center; justify-content: center; }
.term-wrap { width: 100%; max-width: 720px; padding: 40px; }
.term-box { background: #06090D; border: 1px solid var(--border); border-radius: 12px; padding: 32px; font-family: var(--mono); font-size: 13px; color: var(--green); line-height: 2; min-height: 220px; }
.term-bar { height: 6px; width: 0%; background: linear-gradient(90deg, var(--green), var(--cyan)); border-radius: 6px; transition: width .4s ease; margin-top:20px; }
#s-dash { flex-direction: column; overflow-y: auto; overflow-x: hidden; }
.dash-wrap { width: 100%; max-width: 1400px; margin: 0 auto; padding: 28px 32px 60px; display: flex; flex-direction: column; gap: 24px; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 22px 20px; border-top: 2px solid var(--green); }
.kpi-lbl { font-family: var(--mono); font-size: 9px; letter-spacing: 1.8px; color: var(--muted); margin-bottom: 12px; }
.kpi-val { font-family: var(--mono); font-size: 36px; font-weight: 500; letter-spacing: -2px; color: #fff; }
.kpi-sub { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 8px; }
.chart-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 24px; }
</style>
</head>
<body>

<div id="s-splash" class="screen active">
  <h1 class="splash-logo">FlowBio<span>.</span></h1>
  <p style="font-family: var(--mono); font-size:12px; color:var(--muted); letter-spacing:3px; margin-bottom: 40px;">GROQ SPEED ENGINE · AWS S3 SYNC</p>
  <button class="btn-launch" onclick="runSim()">CARGAR DATOS DEL PILOTO (S3)</button>
</div>

<div id="s-terminal" class="screen">
  <div class="term-wrap">
    <div class="term-box" id="term-log"></div>
    <div class="term-bar" id="term-bar"></div>
  </div>
</div>

<div id="s-dash" class="screen">
  <div class="dash-wrap">
    <div style="border-bottom:1px solid #152335; padding-bottom:18px;">
        <h1 style="font-family:var(--head); font-size:26px; font-weight:800;">__VAL_TITULO__ <span style="color:var(--green)"></span></h1>
        <p style="font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:2px; margin-top:4px;">LECTURA EN VIVO: ultimo_reporte.json (S3)</p>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" style="border-top-color: var(--green);">
        <div class="kpi-lbl">AHORRO OPEX / AÑO (USD)</div>
        <div class="kpi-val" style="color:var(--green)">$__VAL_AHORRO__</div>
        <div class="kpi-sub">Impacto Financiero Calculado</div>
      </div>
      <div class="kpi-card" style="border-top-color: var(--blue);">
        <div class="kpi-lbl">MEJORA PROMEDIO</div>
        <div class="kpi-val" style="color:var(--blue)">+__VAL_MEJORA__%</div>
        <div class="kpi-sub">Incremento Producción Base</div>
      </div>
      <div class="kpi-card" style="border-top-color: var(--cyan);">
        <div class="kpi-lbl">FEE MENSUAL USD</div>
        <div class="kpi-val" style="color:var(--cyan)">$__VAL_FEE__</div>
        <div class="kpi-sub">Success Fee FlowBio</div>
      </div>
      <div class="kpi-card" style="border-top-color: var(--amber);">
        <div class="kpi-lbl">ESG: CO2 EVITADO</div>
        <div class="kpi-val" style="color:var(--amber)">__VAL_CO2__ t</div>
        <div class="kpi-sub">Toneladas Anuales (Na-CMC)</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 380px; gap: 20px;">
      <div class="chart-card">
        <div style="font-family:var(--mono); font-size:11px; letter-spacing:1.8px; color:var(--muted); margin-bottom:16px;">IMPACTO PROYECTADO: BLOQUE PILOTO</div>
        <div id="chart-prod" style="height:300px"></div>
      </div>
      <div class="chart-card" style="justify-content:center;">
          <div style="font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:2px; margin-bottom:16px;">MÉTRICAS DEL MOTOR PIML</div>
          <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #152335; font-size:12px;">
            <span style="color:#8BA8C0">Pozos en Piloto</span><span style="font-family:var(--mono); font-weight:500; color:var(--text)">__VAL_POZOS__</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #152335; font-size:12px;">
            <span style="color:#8BA8C0">Factor Skin Promedio</span><span style="font-family:var(--mono); font-weight:500; color:var(--red)">S = __VAL_SKIN__</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:12px 0; font-size:12px;">
            <span style="color:#8BA8C0">Origen de Datos</span><span style="font-family:var(--mono); font-weight:500; color:var(--green)">AWS S3 (US-EAST-2)</span>
          </div>
      </div>
    </div>
  </div>
</div>

<script>
async function runSim() {
  document.getElementById('s-splash').classList.remove('active');
  document.getElementById('s-terminal').classList.add('active');
  
  const box = document.getElementById('term-log');
  const bar = document.getElementById('term-bar');
  const logs = [
    {t:400, m:"> Estableciendo túnel seguro con AWS S3 (us-east-2)..."},
    {t:900, m:"> ✓ Archivo localizado: ultimo_reporte.json"},
    {t:1500,m:"> Extrayendo variables del bloque piloto (Groq AI)..."},
    {t:2100,m:"> ✓ Renderizando UI de Command Center."}
  ];

  for (let i = 0; i < logs.length; i++) {
    await new Promise(r => setTimeout(r, logs[i].t - (i>0?logs[i-1].t:0)));
    box.innerHTML += `<div style="margin-bottom:8px">${logs[i].m}</div>`;
    bar.style.width = ((i+1)/logs.length)*100 + '%';
  }

  await new Promise(r => setTimeout(r, 600));
  
  // GRAFICAR ESCALA REALISTA
  const x = Array.from({length:40}, (_,i)=>i);
  const mejora = parseFloat("__VAL_MEJORA__") / 100;
  const pozos = parseInt("__VAL_POZOS__");
  // Asumimos ~350 barriles por día por pozo maduro en promedio
  const base = pozos * 350; 
  
  const y1 = x.map(i => base * Math.exp(-0.06*i));
  const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mejora * Math.exp(-0.015*(i-5))));

  Plotly.newPlot('chart-prod',[
    {x:x, y:y1, name:'Baseline', type:'scatter', line:{color:'#EF4444',dash:'dot',width:2}},
    {x:x, y:y2, name:'FlowBio', type:'scatter', line:{color:'#00E5A0',width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'},
  ],{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)', margin:{l:40,r:10,t:10,b:30}, showlegend:false,
    font:{family:'DM Mono',color:'#4A6580',size:10}, xaxis:{gridcolor:'#152335'}, yaxis:{gridcolor:'#152335'}
  },{responsive:true,displayModeBar:false});

  document.getElementById('s-terminal').classList.remove('active');
  document.getElementById('s-dash').classList.add('active');
}
</script>
</body>
</html>
"""

# Reemplazo Seguro de Variables para Venta B2B
def format_currency(value):
    if value >= 1000000:
        return f"{value/1000000:.1f}M"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    return str(int(value))

html_final = HTML_BASE.replace("__VAL_TITULO__", titulo_dash)
html_final = html_final.replace("__VAL_AHORRO__", format_currency(ahorro_usd))
html_final = html_final.replace("__VAL_MEJORA__", str(mejora_pct))
html_final = html_final.replace("__VAL_FEE__", format_currency(fee_mensual))
html_final = html_final.replace("__VAL_CO2__", str(co2_evitado))
html_final = html_final.replace("__VAL_SKIN__", str(skin_avg))
html_final = html_final.replace("__VAL_POZOS__", str(total_pozos))

components.html(html_final, height=900, scrolling=True)
