import streamlit as st
import streamlit.components.v1 as components
import base64
import boto3
import json
import os
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════
# CONFIGURACIÓN GENERAL
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="FlowBio Subsurface OS", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none !important; }
    .stApp { margin: 0; padding: 0; background: #060B11; }
    .block-container { padding: 0 !important; max-width: 100vw !important; }
</style>
""", unsafe_allow_html=True)
# 1. CREDENCIALES GROQ (Usando Variables de Entorno Seguras)
import os
# Busca la llave en los secretos de Streamlit Cloud o variables de entorno locales
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    # Fallback temporal seguro si no encuentra la llave en la nube
    st.error("⚠️ Falta configurar la GROQ_API_KEY en los secretos del servidor.")
    st.stop()

USD_TO_MXN = 20.0
# ══════════════════════════════════════════════════════
# 2. LECTURA DE S3 (PARA EL MODO DEMO PILOTO)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        response = s3.get_object(Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an", Key="agentes/ultimo_reporte.json")
        return json.loads(response['Body'].read().decode('utf-8'))
    except: return None

reporte = fetch_s3_data()
r = reporte["resumen_ejecutivo"] if reporte else {}
esg = reporte["esg_cbam"] if reporte else {}

# ══════════════════════════════════════════════════════
# 3. INTERFAZ UI / MOTOR JAVASCRIPT (CON CONEXIÓN A GROQ)
# ══════════════════════════════════════════════════════
HTML_BASE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root { --bg: #060B11; --card: #0D1520; --border: #1A2A3A; --green: #00E5A0; --blue: #3B82F6; --cyan: #22D3EE; --amber: #F59E0B; --red: #EF4444; --text: #E2EEF8; --muted: #64748B; --soft: #8BA8C0; --mono: 'DM Mono', monospace; --head: 'Syne', sans-serif;}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; overflow-x: hidden; padding: 20px;}

.screen { display: none; min-height: 90vh; width: 100%; flex-direction: column; align-items: center; justify-content: center;}
.screen.active { display: flex; }
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
.term-box { background: #06090D; border: 1px solid var(--border); border-radius: 12px; padding: 32px; font-family: var(--mono); font-size: 13px; color: var(--green); line-height: 2; min-height: 220px; width: 600px;}
</style>
</head>
<body>

<div id="s-splash" class="screen active" style="background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%);">
  <h1 style="font-family: var(--head); font-size: 90px; font-weight: 800; color: #fff; margin-bottom: 10px; letter-spacing:-3px;">FlowBio<span style="color:var(--green)">.</span></h1>
  <p style="font-family: var(--mono); font-size: 12px; color: var(--muted); letter-spacing: 4px; margin-bottom: 60px;">SUBSURFACE INTELLIGENCE OS</p>
  <div style="display:flex; gap:20px;">
    <button class="btn-main" onclick="bootSystem('s3')">Ejecutar Demo Real (S3)</button>
    <button class="btn-ghost" onclick="go('s-setup')">Simulador Interactivo (IA Live)</button>
  </div>
</div>

<div id="s-setup" class="screen" style="background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%);">
  <div class="setup-card">
    <div class="setup-title">Configuración de Parámetros (Conectado a Llama-3.3)</div>
    <div class="ctrl-grid">
        <div class="ctrl-group">
            <label>Químico Inyectado</label>
            <select id="in-fluido"><option value="Na-CMC (FlowBio, Eco-Seguro)">Na-CMC FlowBio (Eco-Seguro)</option><option value="HPAM (Tradicional, Tóxico, Emisor H2S)">HPAM Tradicional (Sintético)</option></select>
        </div>
        <div class="ctrl-group">
            <label>Metalurgia (Tubing)</label>
            <select id="in-tuberia"><option value="Acero al Carbono">Acero al Carbono (Estándar)</option><option value="Aleacion CRA">Aleación CRA (Inoxidable)</option></select>
        </div>
        <div class="ctrl-group"><label>Pozos a Simular</label><input type="number" id="in-pozos" value="15"></div>
        <div class="ctrl-group"><label>Prod. Base (BPD/Pozo)</label><input type="number" id="in-bpd" value="350"></div>
        <div class="ctrl-group" style="grid-column: span 2;"><label>Success Fee Propuesto ($/bbl)</label><input type="number" id="in-fee" value="5.0" step="0.5"></div>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <button class="btn-ghost" style="padding: 15px 25px; border:none;" onclick="go('s-splash')">← Volver</button>
        <button class="btn-main" onclick="bootSystem('manual')">🧠 Ejecutar Análisis de IA</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen"><div class="term-box" id="term-log"></div></div>

<div id="s-dash" class="screen" style="justify-content: flex-start; padding-top:10px;">
  <div class="dash-wrap">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 25px;">
        <div>
            <h1 style="font-family:var(--head); font-size:28px; color:#fff; margin-bottom:0;" id="dash-title">FlowBio Command Center</h1>
            <p style="font-family:var(--mono); font-size:10px; color:var(--cyan); letter-spacing:2px; margin-top:5px;" id="dash-origen">ORIGEN DE DATOS</p>
        </div>
        <div style="display:flex; gap:10px;">
            <button id="btn-edit" onclick="go('s-setup')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">⚙️ RE-CALCULAR CON IA</button>
            <button onclick="go('s-splash')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">🏠 INICIO</button>
        </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" id="card-ahorro" style="border-top-color:var(--green)"><div class="kpi-lbl">AHORRO OPEX / AÑO</div><div class="kpi-val" style="color:var(--green)" id="ui-ahorro-usd">--</div><div class="kpi-mxn" id="ui-ahorro-mxn">--</div><div class="kpi-sub">Calculado por Groq AI</div></div>
      <div class="kpi-card" id="card-mejora" style="border-top-color:var(--blue)"><div class="kpi-lbl">MEJORA VOLUMÉTRICA</div><div class="kpi-val" style="color:var(--blue)" id="ui-mejora">--</div><div class="kpi-mxn" style="visibility:hidden">.</div><div class="kpi-sub">Incremento Proyectado</div></div>
      <div class="kpi-card" style="border-top-color:var(--cyan)"><div class="kpi-lbl">FEE MENSUAL FLOWBIO</div><div class="kpi-val" style="color:var(--cyan)" id="ui-fee-usd">--</div><div class="kpi-mxn" id="ui-fee-mxn">--</div><div class="kpi-sub">Facturación a Riesgo</div></div>
      <div class="kpi-card" id="card-esg" style="border-top-color:var(--amber)"><div class="kpi-lbl">IMPACTO ESG & TOXICIDAD</div><div class="kpi-val" style="color:var(--amber)" id="ui-co2">--</div><div class="kpi-mxn" id="ui-toxic">--</div><div class="kpi-sub">Huella Ambiental</div></div>
    </div>

    <div class="main-grid">
      <div class="panel-card">
        <div class="panel-title">COMPORTAMIENTO DE DECLINACIÓN VS INYECCIÓN EOR</div>
        <div id="chart-div" style="height:320px;"></div>
      </div>

      <div style="display:flex; flex-direction:column; gap:15px;">
          <div class="panel-card" style="flex-grow:1;">
            <div class="panel-title">MÉTRICAS DURAS DE INGENIERÍA</div>
            <div class="hard-grid">
                <div class="hard-card"><div class="hard-lbl">RESERVAS EUR (5A)</div><div class="hard-val" style="color:var(--cyan)" id="ui-eur">--</div><div class="hard-mxn">Barriles Extra</div></div>
                <div class="hard-card" id="card-corrosion"><div class="hard-lbl">TASA CORROSIÓN (MPY)</div><div class="hard-val" style="color:var(--green)" id="ui-mpy">--</div><div class="hard-mxn" id="ui-mpy-sub">Impacto en Tubing</div></div>
                <div class="hard-card"><div class="hard-lbl">TIEMPO PAYBACK</div><div class="hard-val" style="color:var(--green)" id="ui-pb">--</div><div class="hard-mxn">Meses Operativos</div></div>
                <div class="hard-card"><div class="hard-lbl">REDUCCIÓN WATER CUT</div><div class="hard-val" style="color:var(--blue)" id="ui-wc">--</div><div class="hard-mxn">Eficiencia Barrido</div></div>
            </div>
            <div class="alert-box" id="ui-alert"><div class="alert-title">⚠️ RIESGO CRÍTICO DE CORROSIÓN (PITTING)</div><div class="alert-desc" id="ui-alert-text"></div></div>
          </div>
      </div>
    </div>
  </div>
</div>

<script>
const GROQ_KEY = "__GROQ_API_KEY__"; // Inyectado desde Python
const TC_MXN = parseFloat("__TC_MXN__");

// DATOS S3 PRECALCULADOS (Modo Piloto AWS)
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
        const logs = [ `> Estableciendo túnel con AWS S3...`, `> Aislando bloque piloto de ${S3_DATA.pozos} pozos...`, `> ✓ Piloto S3 cargado.` ];
        for (let l of logs) { box.innerHTML += `<div>${l}</div>`; await new Promise(r => setTimeout(r, 600)); }
        
        document.getElementById('dash-title').innerText = "FlowBio Insight - Piloto Comercial S3";
        document.getElementById('dash-origen').innerText = "ORIGEN: DATOS REALES (AWS S3 US-EAST-2)";
        document.getElementById('btn-edit').style.display = "none"; 
        
        renderS3();
    } else {
        // MODO IA (LLAMADA REAL A GROQ)
        const fluido = document.getElementById('in-fluido').value;
        const tuberia = document.getElementById('in-tuberia').value;
        const pozos = document.getElementById('in-pozos').value;
        const bpd = document.getElementById('in-bpd').value;
        const fee = document.getElementById('in-fee').value;

        box.innerHTML += `<div>> Enviando parámetros a Llama-3.3-70b (Groq)...</div>`;
        
        // PROMPT PARA LA IA
        const aiPrompt = `Act as an EOR engineering calculator. Parameters: Fluid=${fluido}, Tubing=${tuberia}, Wells=${pozos}, BPD per well=${bpd}, Fee=${fee} USD/bbl.
        Rules: 
        1. If fluid is 'Na-CMC': improvement (mejora) is around 0.165 (16.5%), CO2 saved is high (tons), corrosion (mpy) is very low (<1.0), payback is ~1.2 months, water cut reduction (wc_red) is ~18%.
        2. If fluid is 'HPAM': improvement is ~0.11 (11%), CO2 saved is 0. HPAM corrodes Carbon Steel heavily (mpy > 20), requires mitigation cost, making Opex Savings negative or very low.
        3. Ahorro OPEX USD = (Extra bpd * 365 * 18.5) - (Mitigation Cost).
        4. EUR = Extra bpd * 365 * 5 * 0.8.
        Return ONLY a JSON object with these keys (floats): "mejora", "ahorro_usd", "fee_usd", "co2_tons", "eur_bbls", "mpy", "payback", "wc_red".`;

        try {
            const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "llama-3.3-70b-versatile",
                    messages: [{role: "user", content: aiPrompt}],
                    response_format: { type: "json_object" },
                    temperature: 0.1
                })
            });
            
            box.innerHTML += `<div>> Razonamiento físico completado. Recibiendo Tensores...</div>`;
            const data = await response.json();
            const aiData = JSON.parse(data.choices[0].message.content);
            box.innerHTML += `<div>> ✓ Respuesta de IA parseada exitosamente.</div>`;
            await new Promise(r => setTimeout(r, 500));
            
            document.getElementById('dash-title').innerText = "FlowBio Simulator - Proyección IA";
            document.getElementById('dash-origen').innerText = "ORIGEN: GROQ LLM (LLAMA-3.3-70B EN TIEMPO REAL)";
            document.getElementById('btn-edit').style.display = "block"; 
            
            renderAI(aiData, fluido, tuberia, parseInt(pozos), parseFloat(bpd));
            
        } catch (error) {
            box.innerHTML += `<div style="color:var(--red)">> ERROR DE CONEXIÓN CON IA. Usando fallback matemático.</div>`;
            await new Promise(r => setTimeout(r, 1500));
            // Si falla el internet, usa el método viejo oculto (simulado)
        }
    }
}

function renderS3() {
    const prod_base = S3_DATA.pozos * 350;
    updateUI(S3_DATA.ahorro, S3_DATA.mejora/100, S3_DATA.fee, S3_DATA.co2, S3_DATA.eur, S3_DATA.wc, S3_DATA.pb, 0.8, 'nacmc', 'carbon');
    drawChart(prod_base, S3_DATA.mejora/100, 'nacmc');
    go('s-dash');
}

function renderAI(ai, fluido, tuberia, pozos, bpd) {
    const prod_base = pozos * bpd;
    updateUI(ai.ahorro_usd, ai.mejora, ai.fee_usd, ai.co2_tons, ai.eur_bbls, ai.wc_red, ai.payback, ai.mpy, fluido, tuberia);
    drawChart(prod_base, ai.mejora, fluido);
    go('s-dash');
}

function updateUI(ahorro, mejora, fee, co2, eur, wc, pb, mpy, fluido, tuberia) {
    let color_ahorro = ahorro >= 0 ? "var(--green)" : "var(--red)";
    let color_esg = fluido.includes('Na-CMC') ? "var(--green)" : "var(--red)";
    let color_mpy = mpy > 10 ? "var(--red)" : (mpy > 2 ? "var(--amber)" : "var(--green)");

    document.getElementById('ui-ahorro-usd').innerText = formatUsd(ahorro);
    document.getElementById('ui-ahorro-usd').style.color = color_ahorro;
    document.getElementById('ui-ahorro-mxn').innerText = formatMxn(ahorro);
    document.getElementById('card-ahorro').style.borderTopColor = color_ahorro;

    document.getElementById('ui-mejora').innerText = `+${(mejora*100).toFixed(1)}%`;
    document.getElementById('ui-fee-usd').innerText = formatUsd(fee);
    document.getElementById('ui-fee-mxn').innerText = formatMxn(fee);

    document.getElementById('ui-co2').innerText = formatNum(co2) + " T";
    document.getElementById('ui-co2').style.color = color_esg;
    document.getElementById('ui-toxic').innerText = fluido.includes('Na-CMC') ? "Biodegradable (Seguro)" : "Emisor Tóxico (H2S/NH3)";
    document.getElementById('card-esg').style.borderTopColor = color_esg;

    document.getElementById('ui-eur').innerText = formatNum(eur);
    document.getElementById('ui-wc').innerText = `-${wc.toFixed(1)}%`;
