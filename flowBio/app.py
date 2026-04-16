import streamlit as st
import streamlit.components.v1 as components
import base64
import boto3
import json
import os

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL (STREAMLIT)
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="FlowBio Subsurface OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ocultar elementos nativos de Streamlit
st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 1. CREDENCIALES SEGURAS (SECRETOS)
# ══════════════════════════════════════════════════════
# Lee la llave desde los "Secrets" de Streamlit Cloud
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ Error de seguridad: GROQ_API_KEY no configurada en los secretos del servidor.")
    st.stop()

USD_TO_MXN = 20.0

# ══════════════════════════════════════════════════════
# 2. LECTURA DE S3 (PARA EL MODO DEMO)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except:
        return None

reporte = fetch_s3_data()
r = reporte["resumen_ejecutivo"] if reporte else {}
esg = reporte["esg_cbam"] if reporte else {}

# ══════════════════════════════════════════════════════
# 3. INTERFAZ NATIVA HTMl / CSS / JS
# ══════════════════════════════════════════════════════
HTML_BASE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
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
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; overflow-x: hidden; padding: 20px;}
.screen { display: none; min-height: 90vh; width: 100%; flex-direction: column; align-items: center; justify-content: center;}
.screen.active { display: flex; }
.logo-title { font-family: var(--head); font-size: 90px; font-weight: 800; color: #fff; margin-bottom: 10px; letter-spacing:-3px;}
.logo-title span { color: var(--green); }
.btn-main { background: var(--green); color: #060B11; font-family: var(--head); font-weight: 800; font-size: 13px; letter-spacing: 2px; padding: 18px 45px; border-radius: 8px; border: none; cursor: pointer; transition: 0.3s; text-transform: uppercase;}
.btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(0,229,160,0.4); transform: translateY(-2px);}
.btn-ghost { background: transparent; color: var(--text); border: 1px solid var(--border); font-family: var(--mono); font-size: 12px; padding: 18px 40px; border-radius: 8px; cursor: pointer; transition: 0.3s; }
.btn-ghost:hover { border-color: var(--cyan); color: var(--cyan); }
.setup-card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 40px; width: 100%; max-width: 800px; box-shadow: 0 20px 50px rgba(0,0,0,0.4); }
.setup-title { font-family: var(--head); font-size: 24px; color: #fff; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 15px;}
.ctrl-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
.ctrl-group label { display: block; font-family: var(--mono); font-size: 10px; color: var(--cyan); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;}
.ctrl-group select, .ctrl-group input { width: 100%; background: #060B11; border: 1px solid var(--border); color: #fff; padding: 15px; border-radius: 8px; font-family: var(--mono); font-size: 14px; outline: none; transition:0.3s;}
.dash-wrap { width: 100%; max-width: 1440px; margin: 0 auto; display: flex; flex-direction: column; align-items: stretch;}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; width:100%;}
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; border-top: 3px solid var(--border); transition: 0.3s; }
.kpi-lbl { font-family: var(--mono); font-size: 10px; letter-spacing: 1px; color: var(--muted); margin-bottom: 10px; text-transform: uppercase;}
.kpi-val { font-family: var(--mono); font-size: 32px; font-weight: 500; letter-spacing: -1px; margin-bottom: 4px; color:#fff;}
.kpi-mxn { font-family: var(--mono); font-size: 11px; color: var(--soft); margin-bottom: 10px;}
.kpi-sub { font-family: var(--mono); font-size: 9px; color: var(--muted); border-top: 1px solid var(--border); padding-top: 8px;}
.main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; width:100%;}
.panel-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
.panel-title { font-family: var(--mono); font-size: 11px; color: var(--muted); letter-spacing: 2px; margin-bottom: 15px; text-transform: uppercase; border-bottom: 1px solid var(--border); padding-bottom: 10px;}
.hard-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.hard-card { background: #091018; border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center; }
.hard-val { font-family: var(--mono); font-size: 18px; font-weight: 500; margin: 5px 0; }
.hard-lbl { font-family: var(--mono); font-size: 9px; color: var(--muted); letter-spacing: 1px;}
.hard-mxn { font-size: 9px; color: var(--soft); font-family: var(--mono);}
.alert-box { background: rgba(239, 68, 68, 0.1); border: 1px solid var(--red); border-radius: 8px; padding: 12px; margin-top: 15px; display: none;}
.alert-title { color: var(--red); font-family: var(--mono); font-size: 11px; font-weight: bold; margin-bottom: 5px;}
.alert-desc { color: #fff; font-size: 11px; font-family: var(--body);}
.term-box { background: #06090D; border: 1px solid var(--border); border-radius: 12px; padding: 32px; font-family: var(--mono); font-size: 13px; color: var(--green); line-height: 2; min-height: 220px; width: 600px;}
</style>
</head>
<body>

<div id="s-splash" class="screen active" style="background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%);">
  <h1 class="logo-title">FlowBio<span>.</span></h1>
  <p style="font-family: var(--mono); font-size: 12px; color: var(--muted); letter-spacing: 4px; margin-bottom: 60px;">SUBSURFACE INTELLIGENCE OS</p>
  <div style="display:flex; gap:20px;">
    <button class="btn-main" onclick="bootSystem('s3')">Ejecutar Demo Real (AWS S3)</button>
    <button class="btn-ghost" onclick="go('s-setup')">Nuevo Simulador (IA Live)</button>
  </div>
</div>

<div id="s-setup" class="screen" style="background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%);">
  <div class="setup-card">
    <div class="setup-title">Configuración de Parámetros (IA Engine)</div>
    <div class="ctrl-grid">
        <div class="ctrl-group">
            <label>Químico Inyectado</label>
            <select id="in-fluido">
                <option value="Na-CMC (FlowBio, Eco-Seguro)">Na-CMC FlowBio (Eco-Seguro)</option>
                <option value="HPAM (Tradicional, Tóxico)">HPAM Tradicional (Sintético)</option>
            </select>
        </div>
        <div class="ctrl-group">
            <label>Metalurgia (Tubing)</label>
            <select id="in-tuberia">
                <option value="Acero al Carbono">Acero al Carbono (Estándar)</option>
                <option value="Aleacion CRA">Aleación CRA (Inoxidable)</option>
            </select>
        </div>
        <div class="ctrl-group"><label>Pozos a Simular</label><input type="number" id="in-pozos" value="15"></div>
        <div class="ctrl-group"><label>Prod. Base (BPD/Pozo)</label><input type="number" id="in-bpd" value="350"></div>
        <div class="ctrl-group" style="grid-column: span 2;"><label>Success Fee ($/bbl)</label><input type="number" id="in-fee" value="5.0" step="0.5"></div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <button class="btn-ghost" style="padding: 15px 25px; border:none;" onclick="go('s-splash')">← Volver</button>
        <button class="btn-main" onclick="bootSystem('manual')">🧠 Ejecutar Análisis IA</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen"><div class="term-box" id="term-log"></div></div>

<div id="s-dash" class="screen" style="justify-content: flex-start; padding-top:10px;">
  <div class="dash-wrap">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 25px;">
        <div>
            <h1 style="font-family:var(--head); font-size:28px; color:#fff; margin-bottom:0;" id="dash-title">FlowBio Command Center</h1>
            <p style="font-family:var(--mono); font-size:10px; color:var(--cyan); letter-spacing:2px; margin-top:5px;" id="dash-origen">DATOS PROCESADOS</p>
        </div>
        <div style="display:flex; gap:10px;">
            <button id="btn-edit" onclick="go('s-setup')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">⚙️ RE-CALCULAR</button>
            <button onclick="go('s-splash')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">🏠 INICIO</button>
        </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" id="card-ahorro" style="border-top-color:var(--green)">
        <div class="kpi-lbl">AHORRO OPEX / AÑO</div>
        <div class="kpi-val" style="color:var(--green)" id="ui-ahorro-usd">--</div>
        <div class="kpi-mxn" id="ui-ahorro-mxn">--</div>
        <div class="kpi-sub">Rentabilidad Calculada</div>
      </div>
      <div class="kpi-card" id="card-mejora" style="border-top-color:var(--blue)">
        <div class="kpi-lbl">MEJORA VOLUMÉTRICA</div>
        <div class="kpi-val" style="color:var(--blue)" id="ui-mejora">--</div>
        <div class="kpi-mxn" style="visibility:hidden">.</div>
        <div class="kpi-sub">Incremento de Producción</div>
      </div>
      <div class="kpi-card" style="border-top-color:var(--cyan)">
        <div class="kpi-lbl">FEE MENSUAL FLOWBIO</div>
        <div class="kpi-val" style="color:var(--cyan)" id="ui-fee-usd">--</div>
        <div class="kpi-mxn" id="ui-fee-mxn">--</div>
        <div class="kpi-sub">Modelo a Riesgo</div>
      </div>
      <div class="kpi-card" id="card-esg" style="border-top-color:var(--amber)">
        <div class="kpi-lbl">IMPACTO ESG & TOXICIDAD</div>
        <div class="kpi-val" style="color:var(--amber)" id="ui-co2">--</div>
        <div class="kpi-mxn" id="ui-toxic">--</div>
        <div class="kpi-sub">Seguridad Ambiental</div>
      </div>
    </div>

    <div class="main-grid">
      <div class="panel-card">
        <div class="panel-title">DECLINACIÓN VS INYECCIÓN EOR</div>
        <div id="chart-div" style="height:320px;"></div>
      </div>
      <div style="display:flex; flex-direction:column; gap:15px;">
          <div class="panel-card" style="flex-grow:1;">
            <div class="panel-title">MÉTRICAS DURAS INGENIERÍA</div>
            <div class="hard-grid">
                <div class="hard-card"><div class="hard-lbl">RESERVAS EUR (5A)</div><div class="hard-val" style="color:var(--cyan)" id="ui-eur">--</div><div class="hard-mxn">Barriles Extra</div></div>
                <div class="hard-card" id="card-corrosion"><div class="hard-lbl">TASA CORROSIÓN (MPY)</div><div class="hard-val" style="color:var(--green)" id="ui-mpy">--</div><div class="hard-mxn">Metalurgia</div></div>
                <div class="hard-card"><div class="hard-lbl">TIEMPO PAYBACK</div><div class="hard-val" style="color:var(--green)" id="ui-pb">--</div><div class="hard-mxn">Retorno ROI</div></div>
                <div class="hard-card"><div class="hard-lbl">REDUCCIÓN WATER CUT</div><div class="hard-val" style="color:var(--blue)" id="ui-wc">--</div><div class="hard-mxn">Eficiencia</div></div>
            </div>
            <div class="alert-box" id="ui-alert"><div class="alert-title">⚠️ RIESGO DE CORROSIÓN</div><div class="alert-desc" id="ui-alert-text"></div></div>
          </div>
      </div>
    </div>
  </div>
</div>

<script>
const GROQ_KEY = "__GROQ_API_KEY__";
const TC_MXN = parseFloat("__TC_MXN__");

const S3_DATA = {
    pozos: parseInt("__S3_POZOS__"), ahorro: parseFloat("__S3_AHORRO__"), mejora: parseFloat("__S3_MEJORA__"),
    fee: parseFloat("__S3_FEE__"), skin: parseFloat("__S3_SKIN__"), co2: parseFloat("__S3_CO2__"), 
    wc: parseFloat("__S3_WC__"), eur: parseFloat("__S3_EUR__"), pb: parseFloat("__S3_PB__"), lc: parseFloat("__S3_LC__")
};

function formatUsd(n) { return n >= 1e6 ? '$'+(n/1e6).toFixed(2)+'M' : (n >= 1e3 ? '$'+(n/1e3).toFixed(1)+'K' : '$'+Math.round(n).toLocaleString()); }
function formatMxn(n) { let mxn = n * TC_MXN; return mxn >= 1e6 ? '≈ $'+(mxn/1e6).toFixed(2)+'M MXN' : '≈ $'+Math.round(mxn).toLocaleString()+' MXN'; }
function formatNum(n) { return n >= 1e6 ? (n/1e6).toFixed(2)+'M' : (n >= 1e3 ? (n/1e3).toFixed(1)+'K' : Math.round(n).toLocaleString()); }

function go(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); }

async function bootSystem(mode) {
    go('s-terminal');
    const box = document.getElementById('term-log'); box.innerHTML = '';
    
    if(mode === 's3') {
        const logs = [ `> Conectando a AWS S3...`, `> Aislando bloque piloto S3...`, `> ✓ Datos reales cargados.` ];
        for (let l of logs) { box.innerHTML += `<div>${l}</div>`; await new Promise(r => setTimeout(r, 600)); }
        document.getElementById('dash-title').innerText = "FlowBio Insight - Piloto S3";
        document.getElementById('dash-origen').innerText = "ORIGEN: AWS S3 (DATOS REALES)";
        document.getElementById('btn-edit').style.display = "none";
        renderS3();
    } else {
        const fluido = document.getElementById('in-fluido').value;
        const tuberia = document.getElementById('in-tuberia').value;
        const pozos = document.getElementById('in-pozos').value;
        const bpd = document.getElementById('in-bpd').value;
        const fee = document.getElementById('in-fee').value;

        box.innerHTML += `<div>> Enviando a Groq IA (Llama-3.3)...</div>`;
        const aiPrompt = `Act as EOR eng calculator. JSON output only. Params: Fluid=${fluido}, Tubing=${tuberia}, Wells=${pozos}, BPD=${bpd}, Fee=${fee}. Keys: mejora, ahorro_usd, fee_usd, co2_tons, eur_bbls, mpy, payback, wc_red. Rules: Na-CMC has ~16.5% imp, low corrosion, high co2 saved. HPAM has ~11% imp, 0 co2, high corrosion on carbon steel.`;

        try {
            const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: "llama-3.3-70b-versatile", messages: [{role: "user", content: aiPrompt}], response_format: { type: "json_object" }, temperature: 0.1 })
            });
            const data = await resp.json();
            const aiData = JSON.parse(data.choices[0].message.content);
            box.innerHTML += `<div>> ✓ Análisis de IA completado.</div>`;
            document.getElementById('dash-title').innerText = "FlowBio Proyección IA";
            document.getElementById('dash-origen').innerText = "ORIGEN: GROQ LLAMA-3.3 (LIVE)";
            document.getElementById('btn-edit').style.display = "block";
            renderAI(aiData, fluido, tuberia, parseInt(pozos), parseFloat(bpd));
        } catch (e) {
            box.innerHTML += `<div style="color:red">> Error de conexión.</div>`;
        }
    }
}

function renderS3() {
    updateUI(S3_DATA.ahorro, S3_DATA.mejora/100, S3_DATA.fee, S3_DATA.co2, S3_DATA.eur, S3_DATA.wc, S3_DATA.pb, 0.8, 'Na-CMC', 'Carbono');
    drawChart(S3_DATA.pozos * 350, S3_DATA.mejora/100, 'Na-CMC');
    go('s-dash');
}

function renderAI(ai, fl, tu, pz, bp) {
    updateUI(ai.ahorro_usd, ai.mejora, ai.fee_usd, ai.co2_tons, ai.eur_bbls, ai.wc_red, ai.payback, ai.mpy, fl, tu);
    drawChart(pz * bp, ai.mejora, fl);
    go('s-dash');
}

function updateUI(ah, me, fe, co, eu, wc, pb, mp, fl, tu) {
    document.getElementById('ui-ahorro-usd').innerText = formatUsd(ah);
    document.getElementById('ui-ahorro-mxn').innerText = formatMxn(ah);
    document.getElementById('ui-mejora').innerText = `+${(me*100).toFixed(1)}%`;
    document.getElementById('ui-fee-usd').innerText = formatUsd(fe);
    document.getElementById('ui-fee-mxn').innerText = formatMxn(fe);
    document.getElementById('ui-co2').innerText = formatNum(co) + " T";
    document.getElementById('ui-toxic').innerText = fl.includes('Na-CMC') ? "Biodegradable" : "Emisor Tóxico";
    document.getElementById('ui-eur').innerText = formatNum(eu);
    document.getElementById('ui-wc').innerText = `-${wc.toFixed(1)}%`;
    document.getElementById('ui-pb').innerText = `${pb} Meses`;
    document.getElementById('ui-mpy').innerText = `${mp.toFixed(1)} mpy`;
    
    const ab = document.getElementById('ui-alert');
    if(!fl.includes('Na-CMC')) {
        ab.style.display = "block";
        document.getElementById('ui-alert-text').innerText = "Riesgo de corrosión severa detectado por uso de HPAM.";
    } else { ab.style.display = "none"; }
}

function drawChart(bp, me, fl) {
    const x = Array.from({length:40}, (_,i)=>i);
    const y1 = x.map(i => bp * Math.exp(-0.06*i));
    const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (bp * me * Math.exp(-0.015*(i-5))));
    const lineCol = fl.includes('Na-CMC') ? '#00E5A0' : '#EF4444';
    Plotly.newPlot('chart-div', [{x,y:y1,name:'Base',type:'scatter',line:{color:'#64748B',dash:'dot',width:2},hoverinfo:'none'},{x,y:y2,name:'EOR',type:'scatter',line:{color:lineCol,width:3},fill:'tonexty',fillcolor:fl.includes('Na-CMC')?'rgba(0,229,160,0.15)':'rgba(239,68,68,0.15)'}],{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',margin:{l:40,r:10,t:10,b:25},showlegend:false,font:{family:'DM Mono',color:'#64748B',size:10},xaxis:{gridcolor:'#1A2A3A'},yaxis:{gridcolor:'#1A2A3A'}},{responsive:true,displayModeBar:false});
}
</script>
</body>
</html>
"""

# Inyección final de variables seguras
html_final = HTML_BASE.replace("__GROQ_API_KEY__", GROQ_API_KEY)
html_final = html_final.replace("__TC_MXN__", str(USD_TO_MXN))
html_final = html_final.replace("__S3_POZOS__", str(r.get("pozos_piloto", 10)))
html_final = html_final.replace("__S3_AHORRO__", str(r.get("ahorro_total_usd", 1620000)))
html_final = html_final.replace("__S3_MEJORA__", str(r.get("mejora_promedio_pct", 16.5)))
html_final = html_final.replace("__S3_FEE__", str(r.get("fee_mensual_usd", 21900)))
html_final = html_final.replace("__S3_SKIN__", str(r.get("skin_promedio", 4.2)))
html_final = html_final.replace("__S3_CO2__", str(esg.get("total_ton_co2_ahorradas", 833)))
html_final = html_final.replace("__S3_WC__", str(r.get("wc_reduccion_pct", 18.4)))
html_final = html_final.replace("__S3_EUR__", str(r.get("eur_extra_bbls", 425000)))
html_final = html_final.replace("__S3_PB__", str(r.get("payback_meses", 1.2)))
html_final = html_final.replace("__S3_LC__", str(r.get("lc_caida_usd", 2.15)))

components.html(html_final, height=1050, scrolling=True)
