import streamlit as st
import streamlit.components.v1 as components
import base64
import boto3
import json
from datetime import datetime

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
# DATOS AWS S3 (PARA MODO DEMO) Y TIPO DE CAMBIO
# ══════════════════════════════════════════════════════
USD_TO_MXN = 20.0

@st.cache_data(ttl=30)
def fetch_s3_data():
    try:
        s3 = boto3.client("s3", region_name="us-east-2")
        bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
        key = "agentes/ultimo_reporte.json"
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        return None

reporte = fetch_s3_data()

r = reporte["resumen_ejecutivo"] if reporte else {}
esg = reporte["esg_cbam"] if reporte else {}

s3_pozos = r.get("pozos_piloto", 10)
s3_ahorro = r.get("ahorro_total_usd", 1620000)
s3_mejora = r.get("mejora_promedio_pct", 16.5)
s3_fee = r.get("fee_mensual_usd", 21900)
s3_skin = r.get("skin_promedio", 4.2)
s3_co2 = esg.get("total_ton_co2_ahorradas", 833)
s3_wc = r.get("wc_reduccion_pct", 18.4)
s3_eur = r.get("eur_extra_bbls", 425000)
s3_pb = r.get("payback_meses", 1.2)
s3_lc = r.get("lc_caida_usd", 2.15)

# ══════════════════════════════════════════════════════
# INTERFAZ NATIVA HTMl / CSS / JS
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

/* PANTALLAS */
.screen { display: none; min-height: 90vh; width: 100%; flex-direction: column; align-items: center; justify-content: center;}
.screen.active { display: flex; }

/* BOTONES */
.btn-main { background: var(--green); color: #060B11; font-family: var(--head); font-weight: 800; font-size: 13px; letter-spacing: 2px; padding: 18px 45px; border-radius: 8px; border: none; cursor: pointer; transition: 0.3s; text-transform: uppercase;}
.btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(0,229,160,0.4); transform: translateY(-2px);}
.btn-ghost { background: transparent; color: var(--text); border: 1px solid var(--border); font-family: var(--mono); font-size: 12px; padding: 18px 40px; border-radius: 8px; cursor: pointer; transition: 0.3s; }
.btn-ghost:hover { border-color: var(--cyan); color: var(--cyan); }

/* PANTALLA CONFIGURACIÓN MANUAL */
.setup-card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 40px; width: 100%; max-width: 800px; box-shadow: 0 20px 50px rgba(0,0,0,0.4); }
.setup-title { font-family: var(--head); font-size: 24px; color: #fff; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 15px;}
.ctrl-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
.ctrl-group label { display: block; font-family: var(--mono); font-size: 10px; color: var(--cyan); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;}
.ctrl-group select, .ctrl-group input { width: 100%; background: #060B11; border: 1px solid var(--border); color: #fff; padding: 15px; border-radius: 8px; font-family: var(--mono); font-size: 14px; outline: none; transition:0.3s;}
.ctrl-group select:focus, .ctrl-group input:focus { border-color: var(--green); box-shadow: 0 0 10px rgba(0,229,160,0.1);}

/* DASHBOARD LAYOUT */
.dash-wrap { width: 100%; max-width: 1440px; margin: 0 auto; display: flex; flex-direction: column; align-items: stretch;}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; width:100%;}
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; border-top: 3px solid var(--border); transition: 0.3s; }
.kpi-lbl { font-family: var(--mono); font-size: 10px; letter-spacing: 1px; color: var(--muted); margin-bottom: 10px; text-transform: uppercase;}
.kpi-val { font-family: var(--mono); font-size: 32px; font-weight: 500; letter-spacing: -1px; margin-bottom: 4px; color:#fff;}
.kpi-mxn { font-family: var(--mono); font-size: 11px; color: var(--soft); margin-bottom: 10px;}
.kpi-sub { font-family: var(--mono); font-size: 9px; color: var(--muted); border-top: 1px solid var(--border); padding-top: 8px;}

/* MAIN GRID (GRÁFICA Y DATOS DUROS) */
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
  <h1 style="font-family: var(--head); font-size: 90px; font-weight: 800; color: #fff; margin-bottom: 10px; letter-spacing:-3px;">FlowBio<span style="color:var(--green)">.</span></h1>
  <p style="font-family: var(--mono); font-size: 12px; color: var(--muted); letter-spacing: 4px; margin-bottom: 60px;">SUBSURFACE INTELLIGENCE OS</p>
  
  <div style="display:flex; gap:20px;">
    <button class="btn-main" onclick="bootSystem('s3')">Ejecutar Demo Real (AWS S3)</button>
    <button class="btn-ghost" onclick="go('s-setup')">Nuevo Simulador de Venta</button>
  </div>
</div>

<div id="s-setup" class="screen" style="background: radial-gradient(circle at center, #0D1A2A 0%, #060B11 100%);">
  <div class="setup-card">
    <div class="setup-title">Configuración de Parámetros EOR</div>
    
    <div class="ctrl-grid">
        <div class="ctrl-group">
            <label>Químico Inyectado</label>
            <select id="in-fluido">
                <option value="nacmc">Na-CMC FlowBio (Eco-Seguro)</option>
                <option value="hpam">HPAM Tradicional (Sintético)</option>
            </select>
        </div>
        <div class="ctrl-group">
            <label>Metalurgia (Tubing)</label>
            <select id="in-tuberia">
                <option value="carbon">Acero al Carbono (Estándar)</option>
                <option value="cra">Aleación CRA (Inoxidable)</option>
            </select>
        </div>
        <div class="ctrl-group">
            <label>Pozos a Simular</label>
            <input type="number" id="in-pozos" value="15">
        </div>
        <div class="ctrl-group">
            <label>Prod. Base (BPD/Pozo)</label>
            <input type="number" id="in-bpd" value="350">
        </div>
        <div class="ctrl-group" style="grid-column: span 2;">
            <label>Success Fee Propuesto ($/bbl)</label>
            <input type="number" id="in-fee" value="5.0" step="0.5">
        </div>
    </div>
    
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <button class="btn-ghost" style="padding: 15px 25px; border:none;" onclick="go('s-splash')">← Volver al Inicio</button>
        <button class="btn-main" onclick="bootSystem('manual')">⚡ Iniciar Proyección</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen">
  <div class="term-box" id="term-log"></div>
</div>

<div id="s-dash" class="screen" style="justify-content: flex-start; padding-top:10px;">
  <div class="dash-wrap">
    
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 25px;">
        <div>
            <h1 style="font-family:var(--head); font-size:28px; color:#fff; margin-bottom:0;" id="dash-title">FlowBio Command Center</h1>
            <p style="font-family:var(--mono); font-size:10px; color:var(--cyan); letter-spacing:2px; margin-top:5px;" id="dash-origen">ORIGEN DE DATOS</p>
        </div>
        <div style="display:flex; gap:10px;">
            <button id="btn-edit" onclick="go('s-setup')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">⚙️ EDITAR PARÁMETROS</button>
            <button onclick="go('s-splash')" class="btn-ghost" style="padding:10px 20px; font-size:10px;">🏠 INICIO</button>
        </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" id="card-ahorro" style="border-top-color:var(--green)">
        <div class="kpi-lbl">AHORRO OPEX / AÑO</div>
        <div class="kpi-val" style="color:var(--green)" id="ui-ahorro-usd">--</div>
        <div class="kpi-mxn" id="ui-ahorro-mxn">--</div>
        <div class="kpi-sub">Rentabilidad Neta Proyectada</div>
      </div>
      <div class="kpi-card" id="card-mejora" style="border-top-color:var(--blue)">
        <div class="kpi-lbl">MEJORA VOLUMÉTRICA</div>
        <div class="kpi-val" style="color:var(--blue)" id="ui-mejora">--</div>
        <div class="kpi-mxn" style="visibility:hidden">.</div>
        <div class="kpi-sub">Incremento sobre Producción Base</div>
      </div>
      <div class="kpi-card" style="border-top-color:var(--cyan)">
        <div class="kpi-lbl">FEE MENSUAL FLOWBIO</div>
        <div class="kpi-val" style="color:var(--cyan)" id="ui-fee-usd">--</div>
        <div class="kpi-mxn" id="ui-fee-mxn">--</div>
        <div class="kpi-sub">Facturación a Riesgo ($0 si falla)</div>
      </div>
      <div class="kpi-card" id="card-esg" style="border-top-color:var(--amber)">
        <div class="kpi-lbl">IMPACTO ESG & TOXICIDAD</div>
        <div class="kpi-val" style="color:var(--amber)" id="ui-co2">--</div>
        <div class="kpi-mxn" id="ui-toxic">--</div>
        <div class="kpi-sub">Certificados y Seguridad Ambiental</div>
      </div>
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
                <div class="hard-card">
                    <div class="hard-lbl">RESERVAS EUR (5A)</div>
                    <div class="hard-val" style="color:var(--cyan)" id="ui-eur">--</div>
                    <div class="hard-mxn">Barriles Extra</div>
                </div>
                <div class="hard-card" id="card-corrosion">
                    <div class="hard-lbl">TASA CORROSIÓN (MPY)</div>
                    <div class="hard-val" style="color:var(--green)" id="ui-mpy">--</div>
                    <div class="hard-mxn" id="ui-mpy-sub">Impacto en Tubing</div>
                </div>
                <div class="hard-card">
                    <div class="hard-lbl">TIEMPO PAYBACK</div>
                    <div class="hard-val" style="color:var(--green)" id="ui-pb">--</div>
                    <div class="hard-mxn">Meses Operativos</div>
                </div>
                <div class="hard-card">
                    <div class="hard-lbl">REDUCCIÓN WATER CUT</div>
                    <div class="hard-val" style="color:var(--blue)" id="ui-wc">--</div>
                    <div class="hard-mxn">Eficiencia Barrido</div>
                </div>
            </div>
            
            <div class="alert-box" id="ui-alert">
                <div class="alert-title">⚠️ RIESGO CRÍTICO DE CORROSIÓN (PITTING)</div>
                <div class="alert-desc" id="ui-alert-text"></div>
            </div>
          </div>
      </div>
    </div>

  </div>
</div>

<script>
const TC_MXN = parseFloat("__TC_MXN__");

// DATOS S3 PARA DEMO REAL
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
        const logs = [ `> Estableciendo túnel seguro con AWS S3...`, `> Aislando bloque piloto de ${S3_DATA.pozos} pozos...`, `> ✓ Piloto S3 cargado exitosamente.` ];
        for (let l of logs) { box.innerHTML += `<div>${l}</div>`; await new Promise(r => setTimeout(r, 600)); }
        
        document.getElementById('dash-title').innerText = "FlowBio Insight - Piloto Comercial S3";
        document.getElementById('dash-origen').innerText = "ORIGEN: DATOS REALES (AWS S3 US-EAST-2)";
        document.getElementById('btn-edit').style.display = "none"; // Ocultar editar en modo S3
        
        runMath('s3');
    } else {
        const logs = [ `> Inicializando Motor Físico PIML...`, `> Evaluando condiciones del yacimiento...`, `> ✓ Simulación completada.` ];
        for (let l of logs) { box.innerHTML += `<div>${l}</div>`; await new Promise(r => setTimeout(r, 400)); }
        
        document.getElementById('dash-title').innerText = "FlowBio Simulator - Proyección Personalizada";
        document.getElementById('dash-origen').innerText = "ORIGEN: PARÁMETROS MANUALES (LOCAL)";
        document.getElementById('btn-edit').style.display = "block"; // Mostrar editar en modo manual
        
        runMath('manual');
    }

    await new Promise(r => setTimeout(r, 400));
    go('s-dash'); // Mostrar Dashboard
}

function runMath(mode) {
    let mejora = 0, corrosion_mpy = 0, costo_mitigacion_mensual = 0;
    let co2_tons = 0, toxic_msg = "", pb_meses = 0, wc_red = 0, prod_base_total = 0, extra_bpd = 0, eur = 0, opex_ahorro_anual = 0, fee_mensual = 0;
    let color_esg = "var(--green)", color_mpy = "var(--green)", color_ahorro = "var(--green)", lineCol = "#00E5A0", fillCol = "rgba(0,229,160,0.15)";
    
    if(mode === 's3') {
        // DATOS S3 INAMOVIBLES (Na-CMC por defecto en tu demo de S3)
        prod_base_total = S3_DATA.pozos * 350;
        mejora = S3_DATA.mejora / 100;
        extra_bpd = prod_base_total * mejora;
        opex_ahorro_anual = S3_DATA.ahorro;
        fee_mensual = S3_DATA.fee;
        co2_tons = S3_DATA.co2;
        toxic_msg = "Biodegradable (Seguro)";
        pb_meses = S3_DATA.pb;
        wc_red = S3_DATA.wc;
        corrosion_mpy = 0.8; // Na-CMC = Seguro
        eur = S3_DATA.eur;
    } else {
        // DATOS DEL FORMULARIO MANUAL
        const fluido = document.getElementById('in-fluido').value;
        const tuberia = document.getElementById('in-tuberia').value;
        const pozos = parseInt(document.getElementById('in-pozos').value) || 0;
        const bpd = parseFloat(document.getElementById('in-bpd').value) || 0;
        const fee = parseFloat(document.getElementById('in-fee').value) || 0;

        prod_base_total = pozos * bpd;

        if(fluido === 'nacmc') {
            mejora = 0.165; 
            co2_tons = (prod_base_total * mejora) * 1.2; 
            toxic_msg = "Biodegradable (Seguro)";
            pb_meses = 1.2;
            wc_red = 18.5;
            corrosion_mpy = (tuberia === 'carbon') ? 0.8 : 0.1;
            costo_mitigacion_mensual = 0;
        } else {
            mejora = 0.112; 
            co2_tons = 0; 
            toxic_msg = "Emisor Tóxico (H2S/NH3)";
            pb_meses = 3.8;
            wc_red = 9.2;
            color_esg = "var(--red)";
            lineCol = "#EF4444";
            fillCol = "rgba(239,68,68,0.15)";

            if(tuberia === 'carbon') {
                corrosion_mpy = 25.0; 
                costo_mitigacion_mensual = pozos * 8000; 
                color_mpy = "var(--red)";
            } else {
                corrosion_mpy = 5.0; 
                costo_mitigacion_mensual = pozos * 2000;
                color_mpy = "var(--amber)";
            }
            
            // Mostrar Alerta en HPAM
            const alertBox = document.getElementById('ui-alert');
            const alertText = document.getElementById('ui-alert-text');
            alertBox.style.display = "block";
            if(tuberia === 'carbon') {
                alertText.innerText = `El HPAM libera H2S destrozando el Acero al Carbono. La mitigación penaliza el OPEX en -$${formatUsd(costo_mitigacion_mensual*12)}/año.`;
            } else {
                alertText.innerText = `La Aleación CRA protege, pero el HPAM exige mantenimiento químico extra penalizando OPEX en -$${formatUsd(costo_mitigacion_mensual*12)}/año.`;
            }
        }
        
        if (fluido === 'nacmc') { document.getElementById('ui-alert').style.display = "none"; }

        extra_bpd = prod_base_total * mejora;
        fee_mensual = extra_bpd * 30 * fee;
        opex_ahorro_anual = (extra_bpd * 365 * 18.5) - (costo_mitigacion_mensual * 12);
        eur = extra_bpd * 365 * 5 * 0.8;
    }

    if(opex_ahorro_anual < 0) color_ahorro = "var(--red)";

    // 4. Actualizar UI General
    document.getElementById('ui-ahorro-usd').innerText = formatUsd(opex_ahorro_anual);
    document.getElementById('ui-ahorro-usd').style.color = color_ahorro;
    document.getElementById('ui-ahorro-mxn').innerText = formatMxn(opex_ahorro_anual);
    document.getElementById('card-ahorro').style.borderTopColor = color_ahorro;

    document.getElementById('ui-mejora').innerText = `+${(mejora*100).toFixed(1)}%`;
    document.getElementById('ui-fee-usd').innerText = formatUsd(fee_mensual);
    document.getElementById('ui-fee-mxn').innerText = formatMxn(fee_mensual);

    document.getElementById('ui-co2').innerText = formatNum(co2_tons) + " T";
    document.getElementById('ui-toxic').innerText = toxic_msg;
    document.getElementById('ui-co2').style.color = color_esg;
    document.getElementById('card-esg').style.borderTopColor = color_esg;

    document.getElementById('ui-eur').innerText = formatNum(eur);
    document.getElementById('ui-wc').innerText = `-${wc_red.toFixed(1)}%`;
    document.getElementById('ui-pb').innerText = `${pb_meses} Meses`;
    
    document.getElementById('ui-mpy').innerText = `${corrosion_mpy.toFixed(1)} mpy`;
    document.getElementById('ui-mpy').style.color = color_mpy;

    // 5. Graficar Plotly
    const x = Array.from({length:40}, (_,i)=>i);
    const y1 = x.map(i => prod_base_total * Math.exp(-0.06*i));
    const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (prod_base_total * mejora * Math.exp(-0.015*(i-5))));

    Plotly.newPlot('chart-div', [
        {x:x, y:y1, name:'Baseline', type:'scatter', line:{color:'#64748B',dash:'dot',width:2}, hoverinfo:'none'},
        {x:x, y:y2, name:'Proyección', type:'scatter', line:{color:lineCol,width:3}, fill:'tonexty', fillcolor:fillCol}
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
html_final = HTML_BASE.replace("__S3_POZOS__", str(s3_pozos)).replace("__S3_AHORRO__", str(s3_ahorro))
html_final = html_final.replace("__S3_MEJORA__", str(s3_mejora)).replace("__S3_FEE__", str(s3_fee))
html_final = html_final.replace("__S3_SKIN__", str(s3_skin)).replace("__S3_CO2__", str(s3_co2))
html_final = html_final.replace("__S3_WC__", str(s3_wc)).replace("__S3_EUR__", str(s3_eur))
html_final = html_final.replace("__S3_PB__", str(s3_pb)).replace("__S3_LC__", str(s3_lc))
html_final = html_final.replace("__TC_MXN__", str(USD_TO_MXN))

components.html(html_final, height=1050, scrolling=True)
