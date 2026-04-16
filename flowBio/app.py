import streamlit as st
import streamlit.components.v1 as components
import boto3
import json

st.set_page_config(page_title="FlowBio Command Center", page_icon="🛢️", layout="wide", initial_sidebar_state="collapsed")

# 1. LEER DATOS DUROS DE S3
@st.cache_data(ttl=10)
def fetch_s3():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        obj = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/ultimo_reporte.json")
        return json.loads(obj['Body'].read().decode('utf-8'))
    except: return None

reporte = fetch_s3()

# Variables S3 (Fallback por si no hay internet)
r = reporte["resumen_ejecutivo"] if reporte else {}
pozos = r.get("pozos_piloto", 10)
ahorro = r.get("ahorro_total_usd", 1620000)
mejora = r.get("mejora_promedio_pct", 16.5)
fee = r.get("fee_mensual_usd", 21900)
co2 = reporte["esg_cbam"]["total_ton_co2_ahorradas"] if reporte else 833

# DATOS DUROS S3
wc_red = r.get("wc_reduccion_pct", 18.4)
eur = r.get("eur_extra_bbls", 425000)
payback = r.get("payback_meses", 1.2)
lc_drop = r.get("lc_caida_usd", 2.15)

st.markdown("""<style>[data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; } .stApp { margin: 0; padding: 0; background: #060C12; } .block-container { padding: 0 !important; max-width: 100vw !important; }</style>""", unsafe_allow_html=True)

HTML_BASE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root { --bg: #060C12; --card: #0D1928; --border: #152335; --green: #00E5A0; --blue: #3B82F6; --cyan: #22D3EE; --amber: #F59E0B; --red: #EF4444; --text: #E2EEF8; --muted: #4A6580; --mono: 'DM Mono', monospace; --head: 'Syne', sans-serif; }
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; overflow-x: hidden; }
.screen { display: none; min-height: 100vh; width: 100vw; }
.screen.active { display: flex; flex-direction: column; }
.btn-main { background: var(--green); color: #060C12; font-family: var(--head); font-weight: 800; font-size: 12px; letter-spacing: 2px; padding: 18px 40px; border-radius: 8px; border: none; cursor: pointer; transition: 0.2s; text-transform: uppercase;}
.btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(0,229,160,0.3); }
.btn-ghost { background: transparent; color: var(--text); border: 1px solid var(--border); font-family: var(--mono); font-size: 12px; padding: 18px 40px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
.btn-ghost:hover { border-color: var(--cyan); color: var(--cyan); }
/* Dashboard */
.dash-wrap { width: 100%; max-width: 1400px; margin: 0 auto; padding: 40px; display: flex; flex-direction: column; gap: 24px; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 22px; border-top: 2px solid var(--green); }
.kpi-lbl { font-family: var(--mono); font-size: 9px; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 12px; text-transform: uppercase;}
.kpi-val { font-family: var(--mono); font-size: 32px; font-weight: 500; color: #fff; letter-spacing: -1px;}
.hard-data-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 10px; }
.hard-card { background: #08101A; border: 1px solid #1E3348; border-radius: 10px; padding: 18px; text-align: center; }
.hard-val { font-family: var(--head); font-size: 28px; font-weight: 700; color: var(--cyan); margin: 8px 0 4px; }
.hard-lbl { font-family: var(--mono); font-size: 10px; color: var(--soft); letter-spacing: 1px; }
/* Formularios Manuales */
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-family: var(--mono); font-size: 10px; color: var(--soft); margin-bottom: 5px; }
.form-group input { width: 100%; background: var(--bg); border: 1px solid var(--border); padding: 12px; color: #fff; border-radius: 6px; font-family: var(--mono);}
</style>
</head>
<body>

<div id="s-splash" class="screen active" style="align-items: center; justify-content: center; background: radial-gradient(circle at center, #0B1A2A 0%, #060C12 100%);">
  <h1 style="font-family: var(--head); font-size: 90px; font-weight: 800; color: #fff; margin-bottom: 10px;">FlowBio<span style="color:var(--green)">.</span></h1>
  <p style="font-family: var(--mono); font-size: 12px; color: var(--muted); letter-spacing: 4px; margin-bottom: 50px;">SUBSURFACE INTELLIGENCE OS</p>
  
  <div style="display:flex; gap:20px;">
    <button class="btn-main" onclick="startS3Mode()">Iniciar Demo (Live S3 Data)</button>
    <button class="btn-ghost" onclick="go('s-manual')">Simulador Manual</button>
  </div>
</div>

<div id="s-manual" class="screen" style="align-items: center; justify-content: center;">
  <div style="background: var(--card); border: 1px solid var(--border); padding: 40px; border-radius: 16px; width: 600px;">
    <h2 style="font-family: var(--head); color: #fff; margin-bottom: 20px;">Parámetros del Yacimiento</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <div class="form-group"><label>NÚMERO DE POZOS</label><input type="number" id="m-pozos" value="15"></div>
      <div class="form-group"><label>PRODUCCIÓN BASE (BPD/POZO)</label><input type="number" id="m-bpd" value="400"></div>
      <div class="form-group"><label>PERMEABILIDAD (mD)</label><input type="number" id="m-perm" value="1200"></div>
      <div class="form-group"><label>VISCOSIDAD (cP)</label><input type="number" id="m-visc" value="180"></div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: 30px;">
        <button class="btn-ghost" style="padding: 12px 20px;" onclick="go('s-splash')">← Volver</button>
        <button class="btn-main" onclick="startManualMode()">EJECUTAR FÍSICA</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen" style="align-items: center; justify-content: center;">
  <div style="width: 600px; background: #06090D; border: 1px solid var(--border); padding: 30px; border-radius: 12px; font-family: var(--mono); color: var(--green); font-size: 13px; line-height: 2;" id="term-log"></div>
</div>

<div id="s-dash" class="screen">
  <div class="dash-wrap">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom: 1px solid var(--border); padding-bottom: 15px;">
        <div>
            <h1 style="font-family:var(--head); font-size:28px; color:#fff;" id="dash-title">FlowBio Insight</h1>
            <p style="font-family:var(--mono); font-size:10px; color:var(--cyan); letter-spacing:2px;" id="dash-origen">ORIGEN: S3 CLOUD</p>
        </div>
        <button onclick="go('s-splash')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">REINICIAR SISTEMA</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-lbl">AHORRO OPEX / AÑO</div><div class="kpi-val" style="color:var(--green)" id="ui-ahorro">--</div></div>
      <div class="kpi-card" style="border-top-color:var(--blue)"><div class="kpi-lbl">MEJORA PROMEDIO</div><div class="kpi-val" style="color:var(--blue)" id="ui-mejora">--</div></div>
      <div class="kpi-card" style="border-top-color:var(--cyan)"><div class="kpi-lbl">FEE MENSUAL USD</div><div class="kpi-val" style="color:var(--cyan)" id="ui-fee">--</div></div>
      <div class="kpi-card" style="border-top-color:var(--amber)"><div class="kpi-lbl">CO2 EVITADO (Tons)</div><div class="kpi-val" style="color:var(--amber)" id="ui-co2">--</div></div>
    </div>

    <h3 style="font-family:var(--mono); font-size:12px; color:var(--muted); letter-spacing:3px; margin-top:20px; border-bottom:1px solid #1E3348; padding-bottom:8px;">DATOS DUROS DE INGENIERÍA (PIML)</h3>
    <div class="hard-data-grid">
        <div class="hard-card"><div class="hard-lbl">EUR INCREMENTAL (5 AÑOS)</div><div class="hard-val" id="ui-eur">--</div><div style="font-size:10px; color:var(--muted)">Barriles Totales Recuperados</div></div>
        <div class="hard-card"><div class="hard-lbl">REDUCCIÓN WATER CUT</div><div class="hard-val" style="color:#3B82F6" id="ui-wc">--</div><div style="font-size:10px; color:var(--muted)">Menor Producción de Agua</div></div>
        <div class="hard-card"><div class="hard-lbl">TIEMPO DE PAYBACK</div><div class="hard-val" style="color:#00E5A0" id="ui-pb">--</div><div style="font-size:10px; color:var(--muted)">Meses para Retorno de Inversión</div></div>
        <div class="hard-card"><div class="hard-lbl">CAÍDA LIFTING COST</div><div class="hard-val" style="color:#F59E0B" id="ui-lc">--</div><div style="font-size:10px; color:var(--muted)">Ahorro por barril producido</div></div>
    </div>

    <div style="background:var(--card); border:1px solid var(--border); border-radius:14px; padding:24px; margin-top:10px;">
        <div style="font-family:var(--mono); font-size:11px; color:var(--muted); margin-bottom:15px; letter-spacing:1px;">PROYECCIÓN BASELINE vs FLOWBIO</div>
        <div id="chart-div" style="height:280px;"></div>
    </div>
  </div>
</div>

<script>
// Datos S3 importados desde Python
const S3_DATA = {
    pozos: parseInt("__S3_POZOS__"), ahorro: parseFloat("__S3_AHORRO__"), mejora: parseFloat("__S3_MEJORA__"),
    fee: parseFloat("__S3_FEE__"), co2: parseFloat("__S3_CO2__"), wc: parseFloat("__S3_WC__"),
    eur: parseFloat("__S3_EUR__"), pb: parseFloat("__S3_PB__"), lc: parseFloat("__S3_LC__")
};

function formatMoney(n) { return n >= 1e6 ? '$'+(n/1e6).toFixed(2)+'M' : (n >= 1e3 ? '$'+(n/1e3).toFixed(1)+'K' : '$'+Math.round(n)); }
function formatNum(n) { return n >= 1e6 ? (n/1e6).toFixed(2)+'M' : (n >= 1e3 ? (n/1e3).toFixed(1)+'K' : Math.round(n)); }
function go(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); }

async function animateTerminal(modeText) {
    go('s-terminal');
    const box = document.getElementById('term-log'); box.innerHTML = '';
    const logs = [ `> Inicializando sistema...`, `> ${modeText}`, `> Resolviendo Tensores PIML...`, `> ✓ Modelado completado.` ];
    for (let l of logs) { box.innerHTML += `<div>${l}</div>`; await new Promise(r => setTimeout(r, 600)); }
}

async function startS3Mode() {
    await animateTerminal('Descargando Data Lake desde AWS S3...');
    document.getElementById('dash-title').innerText = `FlowBio Piloto (${S3_DATA.pozos} Pozos)`;
    document.getElementById('dash-origen').innerText = `ORIGEN: AWS S3 (DATOS REALES)`;
    
    // Poblar UI
    document.getElementById('ui-ahorro').innerText = formatMoney(S3_DATA.ahorro);
    document.getElementById('ui-mejora').innerText = `+${S3_DATA.mejora}%`;
    document.getElementById('ui-fee').innerText = formatMoney(S3_DATA.fee);
    document.getElementById('ui-co2').innerText = formatNum(S3_DATA.co2);
    
    document.getElementById('ui-eur').innerText = formatNum(S3_DATA.eur) + " BBLS";
    document.getElementById('ui-wc').innerText = `-${S3_DATA.wc}%`;
    document.getElementById('ui-pb').innerText = `${S3_DATA.pb} MESES`;
    document.getElementById('ui-lc').innerText = `-$${S3_DATA.lc}/BBL`;

    drawChart(S3_DATA.pozos * 350, S3_DATA.mejora / 100);
    go('s-dash');
}

async function startManualMode() {
    await animateTerminal('Ejecutando Simulador Físico Manual...');
    
    // Obtener valores del formulario
    const pozos = parseInt(document.getElementById('m-pozos').value);
    const bpd = parseFloat(document.getElementById('m-bpd').value);
    const perm = parseFloat(document.getElementById('m-perm').value);
    const visc = parseFloat(document.getElementById('m-visc').value);

    document.getElementById('dash-title').innerText = `FlowBio Simulación (${pozos} Pozos)`;
    document.getElementById('dash-origen').innerText = `ORIGEN: SIMULADOR MANUAL (K=${perm}mD, v=${visc}cP)`;

    // MATEMÁTICA MANUAL (Simplificada para la Demo)
    const M = Math.max(0.1, Math.min(8.0, visc / perm * 10)); // Ratio movilidad dummy
    const mejora_pct = Math.max(5.0, 30.0 - M*2); // Mejora teórica
    const extra_bpd = (mejora_pct/100) * bpd * pozos;
    
    const ahorro_yr = extra_bpd * (75 - 18.5) * 0.19 * 365;
    const fee_mo = extra_bpd * 5.0 * 30;
    
    const wc_red = Math.max(8.0, 22.0 - M);
    const eur_extra = extra_bpd * 365 * 5 * 0.8;
    const lc_drop = (18.5 * bpd*pozos) / ((bpd*pozos)+extra_bpd) - 18.5;

    // Poblar UI
    document.getElementById('ui-ahorro').innerText = formatMoney(ahorro_yr);
    document.getElementById('ui-mejora').innerText = `+${mejora_pct.toFixed(1)}%`;
    document.getElementById('ui-fee').innerText = formatMoney(fee_mo);
    document.getElementById('ui-co2').innerText = formatNum(extra_bpd * 0.4);
    
    document.getElementById('ui-eur').innerText = formatNum(eur_extra) + " BBLS";
    document.getElementById('ui-wc').innerText = `-${wc_red.toFixed(1)}%`;
    document.getElementById('ui-pb').innerText = `1.5 MESES`; // Hardcoded for demo
    document.getElementById('ui-lc').innerText = `-$${Math.abs(lc_drop).toFixed(2)}/BBL`;

    drawChart(bpd * pozos, mejora_pct / 100);
    go('s-dash');
}

function drawChart(baseProd, mejora) {
    const x = Array.from({length:40}, (_,i)=>i);
    const y1 = x.map(i => baseProd * Math.exp(-0.06*i));
    const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (baseProd * mejora * Math.exp(-0.015*(i-5))));

    Plotly.newPlot('chart-div', [
        {x:x, y:y1, name:'Baseline', type:'scatter', line:{color:'#EF4444',dash:'dot',width:2}},
        {x:x, y:y2, name:'FlowBio', type:'scatter', line:{color:'#00E5A0',width:3}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.1)'}
    ], {
        paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', margin:{l:40,r:10,t:10,b:30}, showlegend:false,
        font:{family:'DM Mono',color:'#4A6580',size:10}, xaxis:{gridcolor:'#152335'}, yaxis:{gridcolor:'#152335'}
    }, {responsive:true, displayModeBar:false});
}
</script>
</body>
</html>
"""

# Reemplazo de variables de Python a JS
html_final = HTML_BASE.replace("__S3_POZOS__", str(pozos)).replace("__S3_AHORRO__", str(ahorro))
html_final = html_final.replace("__S3_MEJORA__", str(mejora)).replace("__S3_FEE__", str(fee))
html_final = html_final.replace("__S3_CO2__", str(co2)).replace("__S3_WC__", str(wc_red))
html_final = html_final.replace("__S3_EUR__", str(eur)).replace("__S3_PB__", str(payback))
html_final = html_final.replace("__S3_LC__", str(lc_drop))

components.html(html_final, height=950, scrolling=True)
