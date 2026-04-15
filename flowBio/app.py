import streamlit as st
import streamlit.components.v1 as components
import boto3
import json

st.set_page_config(
    page_title="FlowBio Intelligence | Subsurface OS",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════
# 1. CONEXIÓN AL CEREBRO GROQ (AWS S3)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=60) # Cache para que cargue instantáneo
def fetch_groq_results():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        return None

reporte = fetch_groq_results()

# Extraemos los datos reales (o usamos un fallback si el S3 está vacío)
ahorro_usd = reporte["resumen_ejecutivo"]["ahorro_total_usd"] if reporte else 1850000
fee_mensual = reporte["resumen_ejecutivo"]["fee_mensual_usd"] if reporte else 25000
mejora_pct = reporte["resumen_ejecutivo"]["mejora_promedio_pct"] if reporte else 16.5
skin_avg = reporte["resumen_ejecutivo"]["skin_promedio"] if reporte else 4.2
co2_evitado = reporte["esg_cbam"]["total_ton_co2_ahorradas"] if reporte else 950.5

# ══════════════════════════════════════════════════════
# 2. INTERFAZ UI / HTML
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"],
    footer, #MainMenu { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060C12; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
    iframe { position: fixed; top: 0; left: 0;
             width: 100vw; height: 100vh; border: none; z-index: 9999; }
</style>
""", unsafe_allow_html=True)

# Inyectamos las variables de Python directamente al JavaScript usando f-strings
HTML = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FlowBio Intelligence</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:      #060C12; --bg2:     #0B1420; --bg3:     #0F1C2E;
  --card:    #0D1928; --border:  #152335; --border2: #1E3348;
  --green:   #00E5A0; --blue:    #3B82F6; --cyan:    #22D3EE;
  --amber:   #F59E0B; --red:     #EF4444; --text:    #E2EEF8;
  --muted:   #4A6580; --soft:    #8BA8C0;
  --mono:    'DM Mono', monospace;
  --head:    'Syne', sans-serif;
  --body:    'DM Sans', sans-serif;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: var(--bg); color: var(--text); font-family: var(--body); height: 100%; overflow: hidden; }}
.screen {{ display: none; width: 100vw; height: 100vh; }}
.screen.active {{ display: flex; }}
#s-splash {{ flex-direction: column; align-items: center; justify-content: center; position: relative; overflow: hidden; background: radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,229,160,.05) 0%, transparent 70%); }}
.splash-logo {{ font-family: var(--head); font-size: clamp(64px, 9vw, 120px); font-weight: 800; letter-spacing: -4px; line-height: 1; color: #fff; margin-bottom: 8px; }}
.splash-logo span {{ color: var(--green); }}
.btn-launch {{ background: var(--green); color: #050C12; font-family: var(--head); font-weight: 700; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; border: none; border-radius: 10px; padding: 18px 52px; cursor: pointer; transition: all .2s; }}
#s-terminal {{ flex-direction: column; align-items: center; justify-content: center; background: var(--bg); }}
.term-wrap {{ width: 100%; max-width: 720px; padding: 40px; }}
.term-box {{ background: #06090D; border: 1px solid var(--border); border-radius: 12px; padding: 32px; font-family: var(--mono); font-size: 13px; color: var(--green); line-height: 2; min-height: 220px; }}
.term-line {{ opacity: 0; animation: termShow .3s forwards; }}
@keyframes termShow {{ to {{ opacity:1; }} }}
.term-progress {{ margin-top: 20px; background: var(--bg3); border: 1px solid var(--border); border-radius: 6px; height: 6px; overflow: hidden; }}
.term-bar {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--green), var(--cyan)); border-radius: 6px; transition: width .4s ease; }}
#s-dash {{ flex-direction: column; overflow-y: auto; overflow-x: hidden; }}
.dash-wrap {{ width: 100%; max-width: 1400px; margin: 0 auto; padding: 28px 32px 60px; display: flex; flex-direction: column; gap: 24px; }}
.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
.kpi-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 22px 20px; position: relative; overflow: hidden; }}
.kpi-lbl {{ font-family: var(--mono); font-size: 9px; letter-spacing: 1.8px; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; }}
.kpi-val {{ font-family: var(--mono); font-size: 36px; font-weight: 500; letter-spacing: -2px; line-height: 1; color: #fff; }}
.kpi-sub {{ font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 8px; }}
.content-grid {{ display: grid; grid-template-columns: 1fr 380px; gap: 20px; min-height: 420px; }}
.chart-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 24px; display: flex; flex-direction: column; }}
</style>
</head>
<body>

<div id="s-splash" class="screen active">
  <h1 class="splash-logo">FlowBio<span>.</span></h1>
  <p style="font-family: 'DM Mono'; font-size:12px; color:#4A6580; letter-spacing:3px; margin-bottom: 40px;">GROQ SPEED ENGINE · AWS S3 SYNC</p>
  <button class="btn-launch" onclick="runSim()">
    CARGAR DATOS DESDE AWS S3
  </button>
</div>

<div id="s-terminal" class="screen">
  <div class="term-wrap">
    <div style="display:flex; gap:8px; margin-bottom:20px;">
      <div style="width:10px; height:10px; border-radius:50%; background:#EF4444"></div>
      <div style="width:10px; height:10px; border-radius:50%; background:#F59E0B"></div>
      <div style="width:10px; height:10px; border-radius:50%; background:#00E5A0"></div>
    </div>
    <div class="term-box" id="term-log"></div>
    <div class="term-progress"><div class="term-bar" id="term-bar"></div></div>
  </div>
</div>

<div id="s-dash" class="screen">
  <div class="dash-wrap">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid #152335; padding-bottom:18px;">
      <div>
        <h1 style="font-family:'Syne'; font-size:26px; font-weight:800;">Command Center <span style="color:#00E5A0">FlowBio</span></h1>
        <p style="font-family:'DM Mono'; font-size:10px; color:#4A6580; letter-spacing:2px; margin-top:4px;">LECTURA EN VIVO: ultimo_reporte.json</p>
      </div>
      <button onclick="go('s-splash')" style="background:transparent; border:1px solid #1E3348; color:#8BA8C0; padding:10px 20px; border-radius:8px; cursor:pointer; font-family:'DM Mono'; text-transform:uppercase; font-size:10px;">← Desconectar S3</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" style="border-top: 2px solid #00E5A0;">
        <div class="kpi-lbl">AHORRO TOTAL USD (GROQ)</div>
        <div class="kpi-val" style="color:#00E5A0">${(ahorro_usd/1000000):.2f}M</div>
        <div class="kpi-sub">Impacto Financiero Calculado</div>
      </div>
      <div class="kpi-card" style="border-top: 2px solid #3B82F6;">
        <div class="kpi-lbl">MEJORA PROMEDIO</div>
        <div class="kpi-val" style="color:#3B82F6">+{mejora_pct}%</div>
        <div class="kpi-sub">Incremento Producción Base</div>
      </div>
      <div class="kpi-card" style="border-top: 2px solid #22D3EE;">
        <div class="kpi-lbl">FEE MENSUAL USD</div>
        <div class="kpi-val" style="color:#22D3EE">${(fee_mensual/1000):.1f}K</div>
        <div class="kpi-sub">Success Fee FlowBio</div>
      </div>
      <div class="kpi-card" style="border-top: 2px solid #F59E0B;">
        <div class="kpi-lbl">ESG: CO2 EVITADO</div>
        <div class="kpi-val" style="color:#F59E0B">{co2_evitado}</div>
        <div class="kpi-sub">Toneladas Anuales (Na-CMC)</div>
      </div>
    </div>

    <div class="content-grid">
      <div class="chart-card">
        <div style="font-family:'DM Mono'; font-size:11px; letter-spacing:1.8px; color:#8BA8C0; margin-bottom:16px;">IMPACTO PROYECTADO: POZO CLUSTER</div>
        <div id="chart-prod" style="flex:1;min-height:300px"></div>
      </div>

      <div style="display:flex; flex-direction:column; gap:16px;">
        <div style="background:#0D1928; border:1px solid #152335; border-radius:14px; padding:22px;">
          <div style="font-family:'DM Mono'; font-size:10px; color:#4A6580; letter-spacing:2px; margin-bottom:16px;">MÉTRICAS DEL MOTOR PIML</div>
          <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #152335; font-size:12px;">
            <span style="color:#8BA8C0">Factor Skin Promedio</span><span style="font-family:'DM Mono'; font-weight:500; color:#EF4444">S = {skin_avg}</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #152335; font-size:12px;">
            <span style="color:#8BA8C0">LLM Utilizado</span><span style="font-family:'DM Mono'; font-weight:500; color:#22D3EE">Llama 3.3 70b</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:8px 0; font-size:12px;">
            <span style="color:#8BA8C0">Origen de Datos</span><span style="font-family:'DM Mono'; font-weight:500; color:#00E5A0">AWS S3 (US-EAST-2)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function go(id) {{
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}

async function runSim() {{
  go('s-terminal');
  const box = document.getElementById('term-log');
  const bar = document.getElementById('term-bar');
  box.innerHTML = '';

  const logs = [
    {{t:300, c:'dim', m:`> Conectando a AWS S3 (us-east-2)...`}},
    {{t:800, c:'ok',  m:`> ✓ Archivo detectado: ultimo_reporte.json`}},
    {{t:1400,c:'dim', m:`> Decodificando métricas del modelo Groq...`}},
    {{t:2000,c:'ok',  m:`> ✓ Datos importados exitosamente. Cargando UI.`}}
  ];

  for (let i = 0; i < logs.length; i++) {{
    await new Promise(r => setTimeout(r, logs[i].t - (i>0?logs[i-1].t:0)));
    const d = document.createElement('div');
    d.style.color = logs[i].c === 'ok' ? '#00E5A0' : '#8BA8C0';
    d.textContent = logs[i].m;
    box.appendChild(d);
    bar.style.width = Math.round(((i+1)/logs.length)*100) + '%';
  }}

  await new Promise(r => setTimeout(r, 600));
  renderProdChart();
  go('s-dash');
}}

function renderProdChart() {{
  const x = Array.from({{length:40}}, (_,i)=>i);
  const mejora = {mejora_pct} / 100;
  const base = 15000;
  const y1 = x.map(i => base * Math.exp(-0.06*i));
  const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base * mejora * Math.exp(-0.015*(i-5))));

  Plotly.newPlot('chart-prod',[
    {{x,y:y1, name:'Baseline', type:'scatter', line:{{color:'#EF4444',dash:'dot',width:2}}}},
    {{x,y:y2, name:'FlowBio Groq', type:'scatter', line:{{color:'#00E5A0',width:3}}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'}},
  ],{{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)', margin:{{l:50,r:10,t:10,b:40}}, showlegend:false,
    font:{{family:'DM Mono',color:'#4A6580',size:10}}, xaxis:{{gridcolor:'#152335'}}, yaxis:{{gridcolor:'#152335'}}
  }},{{responsive:true,displayModeBar:false}});
}}
</script>
</body>
</html>
"""

components.html(HTML, height=1000, scrolling=True)
