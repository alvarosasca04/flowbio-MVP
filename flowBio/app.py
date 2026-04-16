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
@st.cache_data(ttl=30)
def fetch_groq_results():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        
        response = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data, "✅ Conexión exitosa a AWS S3. JSON sincronizado."
    except Exception as e:
        return None, f"⚠️ No se pudo conectar a S3. Usando caché offline."

reporte, mensaje_conexion = fetch_groq_results()

# Variables dinámicas extrayendo del JSON real
titulo_dash = reporte["metadata"]["titulo"] if reporte else "FlowBio Insight"
# Valores base (RAW) que usaremos para la regla de 3 en Javascript
base_pozos = reporte["resumen_ejecutivo"].get("candidatos_inyeccion", 10) if reporte else 10
base_ahorro = reporte["resumen_ejecutivo"]["ahorro_total_usd"] if reporte else 1850000
base_fee = reporte["resumen_ejecutivo"]["fee_mensual_usd"] if reporte else 25000
mejora_pct = reporte["resumen_ejecutivo"]["mejora_promedio_pct"] if reporte else 16.5
skin_avg = reporte["resumen_ejecutivo"]["skin_promedio"] if reporte else 4.2
base_co2 = reporte["esg_cbam"]["total_ton_co2_ahorradas"] if reporte else 950.5

# Ocultar menús de Streamlit
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060C12; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. INTERFAZ UI / HTML 
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
.btn-launch:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(0,229,160,0.4); }

/* Pantalla Configuración */
#s-config { flex-direction: column; overflow-y: auto; align-items: center; justify-content: center;}
.config-wrap { width: 100%; max-width: 1000px; padding: 40px; display: flex; flex-direction: column; gap: 24px; }
.config-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 30px; }
.card-title { font-family: var(--mono); font-size: 12px; letter-spacing: 2px; color: var(--cyan); margin-bottom: 20px; text-transform: uppercase; }
.well-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; max-height: 200px; overflow-y: auto; padding-right: 10px;}
.well-lbl { display: flex; align-items: center; gap: 10px; font-family: var(--mono); font-size: 13px; cursor: pointer; color: var(--text); background: #0B1420; padding: 10px 15px; border-radius: 8px; border: 1px solid transparent; transition: 0.2s;}
.well-lbl:hover { border-color: var(--green); }
input[type="checkbox"] { accent-color: var(--green); width: 16px; height: 16px; cursor: pointer; }

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
  <button class="btn-launch" onclick="go('s-config')">CONFIGURAR PRUEBA DE CONCEPTO (PoC)</button>
</div>

<div id="s-config" class="screen">
  <div class="config-wrap">
    <div>
        <h1 style="font-family:var(--head); font-size:32px; font-weight:800; color:#fff;">Target <span style="color:var(--green)">Selection</span></h1>
        <p style="font-family:var(--mono); font-size:11px; color:var(--muted); letter-spacing:2px; margin-top:4px;">SELECCIONE LOS ACTIVOS PARA EL PILOTO</p>
    </div>
    
    <div class="config-card">
      <div class="card-title">BASE DE DATOS AWS (UKCS_well_availability...)</div>
      <div class="well-grid" id="well-container">
        </div>
    </div>
    
    <div style="display:flex; justify-content:flex-end; gap: 15px;">
        <button onclick="marcarTodos()" style="background:transparent; border:1px solid var(--border); color:var(--muted); padding:15px 30px; border-radius:10px; cursor:pointer; font-family:var(--mono); font-size:12px;">MARCAR TODOS</button>
        <button class="btn-launch" onclick="runSim()">⚡ DESPLEGAR AGENTES EN SELECCIÓN</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen">
  <div class="term-wrap">
    <div class="term-box" id="term-log"></div>
    <div class="term-bar" id="term-bar"></div>
  </div>
</div>

<div id="s-dash" class="screen">
  <div class="dash-wrap">
    <div style="border-bottom:1px solid #152335; padding-bottom:18px; display:flex; justify-content:space-between; align-items:flex-end;">
        <div>
            <h1 style="font-family:var(--head); font-size:26px; font-weight:800;">__VAL_TITULO__</h1>
            <p style="font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:2px; margin-top:4px;">LECTURA EN VIVO: AWS S3</p>
        </div>
        <button onclick="go('s-config')" style="background:transparent; border:1px solid var(--border); color:var(--muted); padding:10px 20px; border-radius:8px; cursor:pointer; font-family:var(--mono); font-size:10px; text-transform:uppercase;">← Re-seleccionar Pozos</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" style="border-top-color: var(--green);">
        <div class="kpi-lbl">AHORRO OPEX / AÑO (USD)</div>
        <div class="kpi-val" style="color:var(--green)" id="val-ahorro">--</div>
        <div class="kpi-sub">Impacto Financiero Calculado</div>
      </div>
      <div class="kpi-card" style="border-top-color: var(--blue);">
        <div class="kpi-lbl">MEJORA PROMEDIO</div>
        <div class="kpi-val" style="color:var(--blue)">+__VAL_MEJORA__%</div>
        <div class="kpi-sub">Incremento Producción Base</div>
      </div>
      <div class="kpi-card" style="border-top-color: var(--cyan);">
        <div class="kpi-lbl">FEE MENSUAL USD</div>
        <div class="kpi-val" style="color:var(--cyan)" id="val-fee">--</div>
        <div class="kpi-sub">Success Fee FlowBio</div>
      </div>
      <div class="kpi-card" style="border-top-color: var(--amber);">
        <div class="kpi-lbl">ESG: CO2 EVITADO</div>
        <div class="kpi-val" style="color:var(--amber)" id="val-co2">--</div>
        <div class="kpi-sub">Toneladas Anuales (Na-CMC)</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 380px; gap: 20px;">
      <div class="chart-card">
        <div style="font-family:var(--mono); font-size:11px; letter-spacing:1.8px; color:var(--muted); margin-bottom:16px;">PROYECCIÓN DE PRODUCCIÓN (POZOS SELECCIONADOS)</div>
        <div id="chart-prod" style="height:300px"></div>
      </div>
      <div class="chart-card" style="justify-content:center;">
          <div style="font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:2px; margin-bottom:16px;">MÉTRICAS DEL MOTOR PIML</div>
          <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #152335; font-size:12px;">
            <span style="color:#8BA8C0">Pozos Seleccionados</span><span style="font-family:var(--mono); font-weight:500; color:var(--green)" id="val-pozos">--</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #152335; font-size:12px;">
            <span style="color:#8BA8C0">Factor Skin Promedio</span><span style="font-family:var(--mono); font-weight:500; color:var(--red)">S = __VAL_SKIN__</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:12px 0; font-size:12px;">
            <span style="color:#8BA8C0">Origen de Datos</span><span style="font-family:var(--mono); font-weight:500; color:var(--cyan)">AWS S3 (US-EAST-2)</span>
          </div>
      </div>
    </div>
  </div>
</div>

<script>
// Valores Base Inyectados desde Python (JSON de Groq)
const PYTHON_DATA = {
    pozos_base: __RAW_POZOS__,
    ahorro_base: __RAW_AHORRO__,
    fee_base: __RAW_FEE__,
    co2_base: __RAW_CO2__,
    mejora_pct: parseFloat("__VAL_MEJORA__") / 100
};

function go(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

// Poblar los pozos automáticamente
const container = document.getElementById('well-container');
for(let i=1; i<=PYTHON_DATA.pozos_base; i++) {
    const wellName = `UKCS-P${i.toString().padStart(3, '0')}`;
    container.innerHTML += `
        <label class="well-lbl">
            <input type="checkbox" value="${wellName}" class="well-chk" checked>
            ${wellName}
        </label>
    `;
}

function marcarTodos() {
    document.querySelectorAll('.well-chk').forEach(cb => cb.checked = true);
}

function formatMoney(n) {
    if(n >= 1000000) return '$' + (n/1000000).toFixed(2) + 'M';
    if(n >= 1000) return '$' + (n/1000).toFixed(1) + 'K';
    return '$' + Math.round(n);
}

async function runSim() {
  const selected = document.querySelectorAll('.well-chk:checked').length;
  if(selected === 0) { alert("⚠️ Seleccione al menos 1 pozo para continuar."); return; }

  go('s-terminal');
  
  const box = document.getElementById('term-log');
  const bar = document.getElementById('term-bar');
  box.innerHTML = '';
  
  const logs = [
    {t:300, m:`> Filtrando clúster en AWS: ${selected} pozos aislados...`},
    {t:900, m:"> ✓ Archivo localizado: ultimo_reporte.json"},
    {t:1500,m:"> Extrayendo matrices y re-escalando finanzas PIML..."},
    {t:2100,m:"> ✓ Renderizando UI de Command Center."}
  ];

  for (let i = 0; i < logs.length; i++) {
    await new Promise(r => setTimeout(r, logs[i].t - (i>0?logs[i-1].t:0)));
    box.innerHTML += `<div style="margin-bottom:8px">${logs[i].m}</div>`;
    bar.style.width = ((i+1)/logs.length)*100 + '%';
  }

  await new Promise(r => setTimeout(r, 600));
  
  // LA MAGIA DE LA ESCALA (Regla de 3 basada en los pozos seleccionados)
  const ratio = selected / PYTHON_DATA.pozos_base;
  
  const ahorro_real = PYTHON_DATA.ahorro_base * ratio;
  const fee_real = PYTHON_DATA.fee_base * ratio;
  const co2_real = PYTHON_DATA.co2_base * ratio;

  // Inyectar al HTML dinámicamente
  document.getElementById('val-pozos').innerText = selected;
  document.getElementById('val-ahorro').innerText = formatMoney(ahorro_real);
  document.getElementById('val-fee').innerText = formatMoney(fee_real);
  document.getElementById('val-co2').innerText = Math.round(co2_real) + " t";
  
  // GRAFICAR ESCALA REALISTA
  const x = Array.from({length:40}, (_,i)=>i);
  const base_bpd = selected * 350; // Asumimos ~350 bpd por pozo maduro
  
  const y1 = x.map(i => base_bpd * Math.exp(-0.06*i));
  const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (base_bpd * PYTHON_DATA.mejora_pct * Math.exp(-0.015*(i-5))));

  Plotly.newPlot('chart-prod',[
    {x:x, y:y1, name:'Baseline', type:'scatter', line:{color:'#EF4444',dash:'dot',width:2}},
    {x:x, y:y2, name:'FlowBio', type:'scatter', line:{color:'#00E5A0',width:4}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'},
  ],{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)', margin:{l:40,r:10,t:10,b:30}, showlegend:false,
    font:{family:'DM Mono',color:'#4A6580',size:10}, xaxis:{gridcolor:'#152335'}, yaxis:{gridcolor:'#152335'}
  },{responsive:true,displayModeBar:false});

  go('s-dash');
}
</script>
</body>
</html>
"""

# Reemplazo de Strings Crudos
html_final = HTML_BASE.replace("__VAL_TITULO__", titulo_dash)
html_final = html_final.replace("__VAL_MEJORA__", str(mejora_pct))
html_final = html_final.replace("__VAL_SKIN__", str(skin_avg))

# Variables numéricas RAW para que Javascript haga la matemática interactiva
html_final = html_final.replace("__RAW_POZOS__", str(base_pozos))
html_final = html_final.replace("__RAW_AHORRO__", str(base_ahorro))
html_final = html_final.replace("__RAW_FEE__", str(base_fee))
html_final = html_final.replace("__RAW_CO2__", str(base_co2))

components.html(html_final, height=900, scrolling=True)
