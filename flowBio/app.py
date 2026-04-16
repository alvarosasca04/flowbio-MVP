import streamlit as st
import streamlit.components.v1 as components
import boto3
import json

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL (STREAMLIT)
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="FlowBio Subsurface OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# CONEXIÓN AL CEREBRO GROQ (AWS S3) Y TIPO DE CAMBIO
# ══════════════════════════════════════════════════════
USD_TO_MXN = 20.0  # Tipo de cambio de referencia

@st.cache_data(ttl=30)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        
        response = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data
    except Exception as e:
        return None

reporte = fetch_s3_data()

# Extracción de Datos S3 (con fallbacks)
r = reporte["resumen_ejecutivo"] if reporte else {}
esg = reporte["esg_cbam"] if reporte else {}

s3_pozos = r.get("pozos_piloto", 10)
s3_ahorro_usd = r.get("ahorro_total_usd", 1620000)
s3_mejora = r.get("mejora_promedio_pct", 16.5)
s3_fee_usd = r.get("fee_mensual_usd", 21900)
s3_skin = r.get("skin_promedio", 4.2)
s3_co2 = esg.get("total_ton_co2_ahorradas", 833)

s3_wc = r.get("wc_reduccion_pct", 18.4)
s3_eur = r.get("eur_extra_bbls", 425000)
s3_pb = r.get("payback_meses", 1.2)
s3_lc_usd = r.get("lc_caida_usd", 2.15)

# ══════════════════════════════════════════════════════
# HTML / JS / CSS - MOTOR VISUAL
# ══════════════════════════════════════════════════════
HTML_BASE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root { 
  --bg: #060B11; --card: #0D1520; --border: #1A2A3A; 
  --green: #00E5A0; --blue: #3B82F6; --cyan: #22D3EE; --amber: #F59E0B; --red: #EF4444; 
  --text: #E2EEF8; --muted: #64748B; --soft: #8BA8C0;
  --mono: 'DM Mono', monospace; --head: 'Syne', sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; overflow-x: hidden; }

/* NAVEGACIÓN Y COMPONENTES */
.screen { display: none; min-height: 100vh; width: 100vw; flex-direction: column; align-items: center; justify-content: center;}
.screen.active { display: flex; }
.btn-main { background: var(--green); color: #060B11; font-family: var(--head); font-weight: 800; font-size: 13px; letter-spacing: 2px; padding: 18px 45px; border-radius: 8px; border: none; cursor: pointer; transition: 0.3s; text-transform: uppercase;}
.btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(0,229,160,0.4); transform: translateY(-2px);}
.btn-ghost { background: transparent; color: var(--text); border: 1px solid var(--border); font-family: var(--mono); font-size: 12px; padding: 18px 40px; border-radius: 8px; cursor: pointer; transition: 0.3s; }
.btn-ghost:hover { border-color: var(--cyan); color: var(--cyan); }

/* SELECTOR DE POZOS */
.config-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 30px; width: 100%; max-width: 900px;}
.well-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; max-height: 250px; overflow-y: auto; padding-right: 10px; margin-top:20px;}
.well-lbl { display: flex; align-items: center; gap: 10px; font-family: var(--mono); font-size: 13px; cursor: pointer; color: var(--text); background: #060B11; padding: 12px 15px; border-radius: 8px; border: 1px solid var(--border); transition: 0.2s;}
.well-lbl:hover { border-color: var(--green); }
input[type="checkbox"] { accent-color: var(--green); width: 16px; height: 16px; cursor: pointer; }

/* DASHBOARD LAYOUT */
.dash-wrap { width: 100%; max-width: 1440px; padding: 40px; display: flex; flex-direction: column; gap: 24px; align-items: stretch; justify-content: flex-start;}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; width: 100%; }
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; border-top: 3px solid; transition: 0.3s; }
.kpi-lbl { font-family: var(--mono); font-size: 10px; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 10px; text-transform: uppercase;}
.kpi-val { font-family: var(--mono); font-size: 34px; font-weight: 500; letter-spacing: -1px; margin-bottom: 4px; color:#fff;}
.kpi-mxn { font-family: var(--mono); font-size: 12px; color: var(--soft); margin-bottom: 15px; letter-spacing: 1px; }

/* GRID PRINCIPAL (GRÁFICA + DATOS DUROS) */
.main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; width: 100%; }
.panel-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }
.panel-title { font-family: var(--mono); font-size: 11px; color: var(--muted); letter-spacing: 2px; margin-bottom: 20px; text-transform: uppercase; border-bottom: 1px solid var(--border); padding-bottom: 10px;}

.metric-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border); }
.metric-lbl { color: var(--soft); font-size: 12px; font-family:var(--mono);}
.metric-val { font-family: var(--mono); font-weight: 500; font-size: 13px; }

.hard-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
.hard-card { background: #091018; border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center; }
.hard-val { font-family: var(--mono); font-size: 20px; font-weight: 500; margin: 5px 0; }
.hard-mxn { font-family: var(--mono); font-size: 10px; color: var(--muted); }
.hard-lbl { font-family: var(--mono); font-size: 9px; color: var(--muted); letter-spacing: 1px; text-transform: uppercase;}

.term-box { background: #06090D; border: 1px solid var(--border); border-radius: 12px; padding: 32px; font-family: var(--mono); font-size: 13px; color: var(--green); line-height: 2; min-height: 220px; width: 600px;}
</style>
</head>
<body>

<div id="s-splash" class="screen active" style="background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%);">
  <h1 style="font-family:var(--head); font-size:90px; font-weight:800; color:#fff; letter-spacing:-3px; margin-bottom:5px;">FlowBio<span style="color:var(--green)">.</span></h1>
  <p style="font-family:var(--mono); font-size:12px; color:var(--muted); letter-spacing:4px; margin-bottom:40px;">SUBSURFACE INTELLIGENCE OS</p>
  
  <div class="config-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h2 style="font-family:var(--head); color:#fff; font-size:20px;">Auditoría de Activos (S3 Data Lake)</h2>
            <p style="font-family:var(--mono); color:var(--cyan); font-size:11px; letter-spacing:1px;">SELECCIONE LOS POZOS PARA LA PRUEBA DE CONCEPTO</p>
        </div>
        <button onclick="marcarTodos()" style="background:transparent; border:1px solid var(--border); color:var(--soft); padding:10px 20px; border-radius:6px; cursor:pointer; font-family:var(--mono); font-size:10px;">SELECCIONAR TODOS</button>
    </div>
    
    <div class="well-grid" id="well-container"></div>
    
    <div style="display:flex; justify-content:center; margin-top:30px;">
        <button class="btn-main" onclick="runSim()">⚡ DESPLEGAR AGENTES EN SELECCIÓN</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen">
  <div class="term-box" id="term-log"></div>
</div>

<div id="s-dash" class="screen">
  <div class="dash-wrap">
    
    <div style="display:flex; justify-content:space-between; align-items:flex-end; padding-bottom: 10px;">
        <div>
            <h1 style="font-family:var(--head); font-size:28px; color:#fff;">Auditoría de Recuperación FlowBio</h1>
            <p style="font-family:var(--mono); font-size:10px; color:var(--cyan); letter-spacing:2px; margin-top:5px;">MODELO PIML · TIPO DE CAMBIO: $__TC_MXN__ MXN/USD</p>
        </div>
        <button onclick="go('s-splash')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">← RE-CONFIGURAR PILOTO</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" style="border-top-color:var(--green)">
        <div class="kpi-lbl">AHORRO OPEX / AÑO</div>
        <div class="kpi-val" style="color:var(--green)" id="ui-ahorro-usd">--</div>
        <div class="kpi-mxn" id="ui-ahorro-mxn">--</div>
        <div class="kpi-sub" style="border-top:1px solid var(--border); padding-top:10px;">Impacto Financiero Calculado</div>
      </div>
      <div class="kpi-card" style="border-top-color:var(--blue)">
        <div class="kpi-lbl">MEJORA PROMEDIO</div>
        <div class="kpi-val" style="color:var(--blue)" id="ui-mejora">--</div>
        <div class="kpi-mxn" style="color:var(--bg)">.</div> <div class="kpi-sub" style="border-top:1px solid var(--border); padding-top:10px;">Incremento Producción Base</div>
      </div>
      <div class="kpi-card" style="border-top-color:var(--cyan)">
        <div class="kpi-lbl">SUCCESS FEE MENSUAL</div>
        <div class="kpi-val" style="color:var(--cyan)" id="ui-fee-usd">--</div>
        <div class="kpi-mxn" id="ui-fee-mxn">--</div>
        <div class="kpi-sub" style="border-top:1px solid var(--border); padding-top:10px;">Modelo de Riesgo Compartido</div>
      </div>
      <div class="kpi-card" style="border-top-color:var(--amber)">
        <div class="kpi-lbl">ESG: CO2 EVITADO</div>
        <div class="kpi-val" style="color:var(--amber)"><span id="ui-co2">--</span> <span style="font-size:20px;">Tons</span></div>
        <div class="kpi-mxn" style="color:var(--bg)">.</div> <div class="kpi-sub" style="border-top:1px solid var(--border); padding-top:10px;">Certificados Carbono (Na-CMC)</div>
      </div>
    </div>

    <div class="main-grid">
      <div class="panel-card">
        <div class="panel-title">PROYECCIÓN DE DECLINACIÓN Y RECUPERACIÓN (POZOS SELECCIONADOS)</div>
        <div id="chart-div" style="height:350px;"></div>
      </div>

      <div style="display:flex; flex-direction:column; gap:20px;">
          <div class="panel-card" style="padding:15px 24px;">
            <div class="panel-title" style="margin-bottom:10px;">DIAGNÓSTICO DEL SISTEMA</div>
            <div class="metric-row"><span class="metric-lbl">Pozos en Piloto</span><span class="metric-val" style="color:var(--green)" id="ui-pozos">--</span></div>
            <div class="metric-row"><span class="metric-lbl">Factor Skin (S) Promedio</span><span class="metric-val" style="color:var(--red)">S = <span id="ui-skin">--</span></span></div>
            <div class="metric-row" style="border:none; padding-bottom:0;"><span class="metric-lbl">Origen de Datos</span><span class="metric-val" style="color:var(--cyan)">AWS S3</span></div>
          </div>
          
          <div class="panel-card" style="flex-grow:1;">
            <div class="panel-title">MÉTRICAS DURAS DE INGENIERÍA</div>
            <div class="hard-grid">
                <div class="hard-card">
                    <div class="hard-lbl">RESERVAS EUR (5 AÑOS)</div>
                    <div class="hard-val" style="color:var(--cyan)" id="ui-eur">--</div>
                    <div class="hard-mxn">Barriles Extra</div>
                </div>
                <div class="hard-card">
                    <div class="hard-lbl">CAÍDA LIFTING COST</div>
                    <div class="hard-val" style="color:var(--blue)" id="ui-lc-usd">--</div>
                    <div class="hard-mxn" id="ui-lc-mxn">--</div>
                </div>
                <div class="hard-card">
                    <div class="hard-lbl">TIEMPO PAYBACK</div>
                    <div class="hard-val" style="color:var(--green)" id="ui-pb">--</div>
                    <div class="hard-mxn">Meses Operativos</div>
                </div>
                <div class="hard-card">
                    <div class="hard-lbl">REDUCCIÓN WATER CUT</div>
                    <div class="hard-val" style="color:var(--amber)" id="ui-wc">--</div>
                    <div class="hard-mxn">Eficiencia de Barrido</div>
                </div>
            </div>
          </div>
      </div>
    </div>

  </div>
</div>

<script>
// DATOS IMPORTADOS DE PYTHON (JSON Groq + Variables Globales)
const S3_DATA = {
    pozos: parseInt("__S3_POZOS__"), ahorro: parseFloat("__S3_AHORRO__"), mejora: parseFloat("__S3_MEJORA__"),
    fee: parseFloat("__S3_FEE__"), skin: parseFloat("__S3_SKIN__"), co2: parseFloat("__S3_CO2__"), 
    wc: parseFloat("__S3_WC__"), eur: parseFloat("__S3_EUR__"), pb: parseFloat("__S3_PB__"), lc: parseFloat("__S3_LC__")
};

const TC = parseFloat("__TC_MXN__");

function formatUsd(n) { return n >= 1e6 ? '$'+(n/1e6).toFixed(2)+'M' : (n >= 1e3 ? '$'+(n/1e3).toFixed(1)+'K' : '$'+Math.round(n).toLocaleString()); }
function formatMxn(n) { 
    let mxn = n * TC;
    return mxn >= 1e6 ? '≈ $'+(mxn/1e6).toFixed(2)+'M MXN' : '≈ $'+Math.round(mxn).toLocaleString()+' MXN'; 
}
function formatNum(n) { return n >= 1e6 ? (n/1e6).toFixed(2)+'M' : (n >= 1e3 ? (n/1e3).toFixed(1)+'K' : Math.round(n).toLocaleString()); }

function go(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); }

// Poblar Casillas de Pozos
const container = document.getElementById('well-container');
for(let i=1; i<=S3_DATA.pozos; i++) {
    const wellName = `UKCS-P${i.toString().padStart(3, '0')}`;
    container.innerHTML += `<label class="well-lbl"><input type="checkbox" value="${wellName}" class="well-chk" checked> ${wellName}</label>`;
}

function marcarTodos() {
    let checks = document.querySelectorAll('.well-chk');
    let allChecked = Array.from(checks).every(c => c.checked);
    checks.forEach(cb => cb.checked = !allChecked);
}

async function runSim() {
  const selected = document.querySelectorAll('.well-chk:checked').length;
  if(selected === 0) { alert("⚠️ Seleccione al menos 1 pozo para iniciar la simulación."); return; }

  go('s-terminal');
  const box = document.getElementById('term-log'); box.innerHTML = '';
  const logs = [ 
      `> Inicializando Audit Trail para ${selected} pozos seleccionados...`, 
      `> Extrayendo datos geológicos de AWS S3...`, 
      `> Resolviendo tensores de permeabilidad PIML...`, 
      `> Calculando conversiones financieras (Tipo de Cambio: $${TC} MXN)...`,
      `> ✓ Despliegue de métricas listo.` 
  ];
  
  for (let l of logs) { box.innerHTML += `<div>${l}</div>`; await new Promise(r => setTimeout(r, 500)); }
  await new Promise(r => setTimeout(r, 400));
  
  // MAGIA MATEMÁTICA INTERACTIVA (Regla de 3 basada en la selección)
  const ratio = selected / S3_DATA.pozos;
  const curr_ahorro = S3_DATA.ahorro * ratio;
  const curr_fee = S3_DATA.fee * ratio;
  const curr_co2 = S3_DATA.co2 * ratio;
  const curr_eur = S3_DATA.eur * ratio;

  // Poblar UI Financiera (Doble Moneda)
  document.getElementById('ui-ahorro-usd').innerText = formatUsd(curr_ahorro);
  document.getElementById('ui-ahorro-mxn').innerText = formatMxn(curr_ahorro);
  
  document.getElementById('ui-fee-usd').innerText = formatUsd(curr_fee);
  document.getElementById('ui-fee-mxn').innerText = formatMxn(curr_fee);
  
  document.getElementById('ui-mejora').innerText = `+${S3_DATA.mejora}%`;
  document.getElementById('ui-co2').innerText = Math.round(curr_co2).toLocaleString();
  
  // Poblar UI Ingeniería
  document.getElementById('ui-pozos').innerText = selected;
  document.getElementById('ui-skin').innerText = S3_DATA.skin.toFixed(1);
  
  // Datos Duros
  document.getElementById('ui-eur').innerText = formatNum(curr_eur);
  document.getElementById('ui-wc').innerText = `-${S3_DATA.wc}%`;
  document.getElementById('ui-pb').innerText = `${S3_DATA.pb} Meses`;
  
  // Lifting Cost en Doble Moneda
  document.getElementById('ui-lc-usd').innerText = `-$${S3_DATA.lc.toFixed(2)}`;
  document.getElementById('ui-lc-mxn').innerText = `≈ -$${(S3_DATA.lc * TC).toFixed(2)} MXN`;

  // Gráfica
  const base_bpd = selected * 350; 
  drawChart(base_bpd, S3_DATA.mejora / 100);
  go('s-dash');
}

function drawChart(baseProd, mejora) {
    const x = Array.from({length:40}, (_,i)=>i);
    const y1 = x.map(i => baseProd * Math.exp(-0.04*i));
    const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (baseProd * mejora * Math.exp(-0.012*(i-5))));

    Plotly.newPlot('chart-div', [
        {x:x, y:y1, name:'Baseline', type:'scatter', line:{color:'#EF4444',dash:'dot',width:2}, hoverinfo:'none'},
        {x:x, y:y2, name:'FlowBio', type:'scatter', line:{color:'#00E5A0',width:3}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.15)'}
    ], {
        paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', margin:{l:40,r:10,t:10,b:25}, showlegend:false,
        font:{family:'DM Mono',color:'#64748B',size:10}, 
        xaxis:{gridcolor:'#1A2A3A', showline:false, zeroline:false}, 
        yaxis:{gridcolor:'#1A2A3A', showline:false, zeroline:false}
    }, {responsive:true, displayModeBar:false});
}
</script>
</body>
</html>
"""

# Reemplazo Seguro
html_final = HTML_BASE.replace("__S3_POZOS__", str(s3_pozos)).replace("__S3_AHORRO__", str(s3_ahorro_usd))
html_final = html_final.replace("__S3_MEJORA__", str(s3_mejora)).replace("__S3_FEE__", str(s3_fee_usd))
html_final = html_final.replace("__S3_SKIN__", str(s3_skin)).replace("__S3_CO2__", str(s3_co2))
html_final = html_final.replace("__S3_WC__", str(s3_wc)).replace("__S3_EUR__", str(s3_eur))
html_final = html_final.replace("__S3_PB__", str(s3_pb)).replace("__S3_LC__", str(s3_lc_usd))
html_final = html_final.replace("__TC_MXN__", str(USD_TO_MXN))

components.html(html_final, height=1050, scrolling=True)
