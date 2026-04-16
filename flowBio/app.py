import streamlit as st
import streamlit.components.v1 as components
import base64

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
# EL MOTOR DEL DASHBOARD INTERACTIVO (HTML + JS)
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

/* CONTROLES SUPERIORES */
.control-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);}
.ctrl-group label { display: block; font-family: var(--mono); font-size: 9px; color: var(--cyan); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;}
.ctrl-group select, .ctrl-group input { width: 100%; background: #060B11; border: 1px solid var(--border); color: #fff; padding: 10px; border-radius: 6px; font-family: var(--mono); font-size: 12px; outline: none;}
.ctrl-group select:focus, .ctrl-group input:focus { border-color: var(--green); }

/* DASHBOARD LAYOUT */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px;}
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; border-top: 3px solid var(--border); transition: 0.3s; }
.kpi-lbl { font-family: var(--mono); font-size: 10px; letter-spacing: 1px; color: var(--muted); margin-bottom: 10px; text-transform: uppercase;}
.kpi-val { font-family: var(--mono); font-size: 32px; font-weight: 500; letter-spacing: -1px; margin-bottom: 4px; color:#fff;}
.kpi-mxn { font-family: var(--mono); font-size: 11px; color: var(--soft); margin-bottom: 10px;}
.kpi-sub { font-family: var(--mono); font-size: 9px; color: var(--muted); border-top: 1px solid var(--border); padding-top: 8px;}

/* MAIN GRID (GRÁFICA Y DATOS DUROS) */
.main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
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
</style>
</head>
<body>

<div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 15px;">
    <div>
        <h1 style="font-family:var(--head); font-size:28px; color:#fff; margin-bottom:0;">FlowBio Command Center</h1>
        <p style="font-family:var(--mono); font-size:10px; color:var(--cyan); letter-spacing:2px; margin-top:5px;">SIMULADOR INTERACTIVO · MODO VENTAS</p>
    </div>
</div>

<div class="control-panel">
    <div class="ctrl-group">
        <label>Químico Inyectado</label>
        <select id="in-fluido" onchange="runSim()">
            <option value="nacmc">Na-CMC FlowBio (Eco-Seguro)</option>
            <option value="hpam">HPAM Tradicional (Sintético)</option>
        </select>
    </div>
    <div class="ctrl-group">
        <label>Metalurgia (Tubing)</label>
        <select id="in-tuberia" onchange="runSim()">
            <option value="carbon">Acero al Carbono (Estándar)</option>
            <option value="cra">Aleación CRA (Inoxidable)</option>
        </select>
    </div>
    <div class="ctrl-group">
        <label>Pozos en Piloto</label>
        <input type="number" id="in-pozos" value="15" oninput="runSim()">
    </div>
    <div class="ctrl-group">
        <label>Prod. Base (BPD/Pozo)</label>
        <input type="number" id="in-bpd" value="350" oninput="runSim()">
    </div>
    <div class="ctrl-group">
        <label>Success Fee ($/bbl)</label>
        <input type="number" id="in-fee" value="5.0" step="0.5" oninput="runSim()">
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
    <div class="panel-title">COMPORTAMIENTO DE DECLINACIÓN VS INYECCIÓN</div>
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
            <div class="alert-desc" id="ui-alert-text">La degradación del HPAM libera H2S, atacando el Acero al Carbono. Costo de mitigación penaliza el OPEX.</div>
        </div>
      </div>
  </div>
</div>

<script>
const TC_MXN = 20.0;

function formatUsd(n) { return n >= 1e6 ? '$'+(n/1e6).toFixed(2)+'M' : (n >= 1e3 ? '$'+(n/1e3).toFixed(1)+'K' : '$'+Math.round(n).toLocaleString()); }
function formatMxn(n) { let mxn = n * TC_MXN; return mxn >= 1e6 ? '≈ $'+(mxn/1e6).toFixed(2)+'M MXN' : '≈ $'+Math.round(mxn).toLocaleString()+' MXN'; }
function formatNum(n) { return n >= 1e6 ? (n/1e6).toFixed(2)+'M' : (n >= 1e3 ? (n/1e3).toFixed(1)+'K' : Math.round(n).toLocaleString()); }

function runSim() {
    // 1. Leer Controles
    const fluido = document.getElementById('in-fluido').value;
    const tuberia = document.getElementById('in-tuberia').value;
    const pozos = parseInt(document.getElementById('in-pozos').value) || 0;
    const bpd = parseFloat(document.getElementById('in-bpd').value) || 0;
    const fee = parseFloat(document.getElementById('in-fee').value) || 0;

    // 2. Motor Físico B2B (Las Reglas de Negocio)
    let mejora = 0, corrosion_mpy = 0, costo_mitigacion_mensual = 0;
    let co2_tons = 0, toxic_msg = "", pb_meses = 0, wc_red = 0;
    let color_esg = "var(--green)", color_mpy = "var(--green)", color_ahorro = "var(--green)";

    const prod_base_total = pozos * bpd;

    if(fluido === 'nacmc') {
        mejora = 0.165; // 16.5%
        co2_tons = (prod_base_total * mejora) * 1.2; // Ahorro masivo CO2
        toxic_msg = "Biodegradable (Cero Toxicidad)";
        pb_meses = 1.2;
        wc_red = 18.5;
        
        // Na-CMC no corroe, no importa la tubería
        if(tuberia === 'carbon') { corrosion_mpy = 0.8; } else { corrosion_mpy = 0.1; }
        costo_mitigacion_mensual = 0;
        
    } else {
        // HPAM Tradicional
        mejora = 0.112; // 11.2% (Menos eficiente)
        co2_tons = 0; // Contaminante
        toxic_msg = "Emisor Tóxico (H2S / NH3)";
        pb_meses = 3.8;
        wc_red = 9.2;
        color_esg = "var(--red)";

        // Impacto severo en tubería
        if(tuberia === 'carbon') {
            corrosion_mpy = 25.0; // Pitting destructivo
            costo_mitigacion_mensual = pozos * 8000; // $8k USD al mes por pozo en inhibidores
            color_mpy = "var(--red)";
        } else {
            corrosion_mpy = 5.0; // CRA resiste mejor, pero hay costo
            costo_mitigacion_mensual = pozos * 2000;
            color_mpy = "var(--amber)";
        }
    }

    // 3. Matemáticas Financieras
    const extra_bpd = prod_base_total * mejora;
    const revenue_anual = extra_bpd * 365 * 75.0; // $75 usd/bbl
    const fee_mensual = extra_bpd * 30 * fee;
    
    // Ahorro OPEX = (Ganancia del crudo extra) - (Lo que pagas de Fee + Mitigación de Corrosión)
    const opex_ahorro_anual = (extra_bpd * 365 * 18.5) - (costo_mitigacion_mensual * 12);
    const eur = extra_bpd * 365 * 5 * 0.8;

    if(opex_ahorro_anual < 0) color_ahorro = "var(--red)";

    // 4. Actualizar DOM (UI)
    document.getElementById('ui-ahorro-usd').innerText = formatUsd(opex_ahorro_anual);
    document.getElementById('ui-ahorro-usd').style.color = color_ahorro;
    document.getElementById('ui-ahorro-mxn').innerText = formatMxn(opex_ahorro_anual);
    document.getElementById('card-ahorro').style.borderTopColor = color_ahorro;

    document.getElementById('ui-mejora').innerText = `+${(mejora*100).toFixed(1)}%`;
    
    document.getElementById('ui-fee-usd').innerText = formatUsd(fee_mensual);
    document.getElementById('ui-fee-mxn').innerText = formatMxn(fee_mensual);

    document.getElementById('ui-co2').innerText = formatNum(co2_tons);
    document.getElementById('ui-toxic').innerText = toxic_msg;
    document.getElementById('ui-co2').style.color = color_esg;
    document.getElementById('card-esg').style.borderTopColor = color_esg;

    document.getElementById('ui-eur').innerText = formatNum(eur);
    document.getElementById('ui-wc').innerText = `-${wc_red.toFixed(1)}%`;
    document.getElementById('ui-pb').innerText = `${pb_meses} Meses`;
    
    document.getElementById('ui-mpy').innerText = `${corrosion_mpy.toFixed(1)} mpy`;
    document.getElementById('ui-mpy').style.color = color_mpy;
    
    // Mostrar/Ocultar Alerta de Corrosión
    const alertBox = document.getElementById('ui-alert');
    const alertText = document.getElementById('ui-alert-text');
    if(fluido === 'hpam' && tuberia === 'carbon') {
        alertBox.style.display = "block";
        alertText.innerText = `La degradación del HPAM libera H2S, atacando el Acero al Carbono. Costo de inhibidores de corrosión penaliza el OPEX en -$${formatUsd(costo_mitigacion_mensual*12)} al año.`;
    } else if (fluido === 'hpam' && tuberia === 'cra') {
        alertBox.style.display = "block";
        alertText.innerText = `Tubería CRA protege contra Pitting Severo, pero el HPAM requiere mantenimiento químico extra penalizando el OPEX en -$${formatUsd(costo_mitigacion_mensual*12)} al año.`;
    } else {
        alertBox.style.display = "none";
    }

    // 5. Graficar Plotly
    const x = Array.from({length:40}, (_,i)=>i);
    const y1 = x.map(i => prod_base_total * Math.exp(-0.06*i));
    const y2 = x.map(i => i<5 ? y1[i] : y1[i] + (prod_base_total * mejora * Math.exp(-0.015*(i-5))));
    const fillCol = fluido === 'nacmc' ? 'rgba(0,229,160,0.15)' : 'rgba(59,130,246,0.15)';
    const lineCol = fluido === 'nacmc' ? '#00E5A0' : '#3B82F6';

    Plotly.newPlot('chart-div', [
        {x:x, y:y1, name:'Baseline', type:'scatter', line:{color:'#EF4444',dash:'dot',width:2}, hoverinfo:'none'},
        {x:x, y:y2, name:'Proyección EOR', type:'scatter', line:{color:lineCol,width:3}, fill:'tonexty', fillcolor:fillCol}
    ], {
        paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', margin:{l:40,r:10,t:10,b:25}, showlegend:false,
        font:{family:'DM Mono',color:'#64748B',size:10}, 
        xaxis:{gridcolor:'#1A2A3A', showline:false, zeroline:false}, 
        yaxis:{gridcolor:'#1A2A3A', showline:false, zeroline:false}
    }, {responsive:true, displayModeBar:false});
}

// Ejecutar al cargar la página
window.onload = runSim;
</script>
</body>
</html>
"""

# Renderizar en Streamlit
b64_html = base64.b64encode(HTML_BASE.encode()).decode()
iframe_html = f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="950px" style="border:none; border-radius:12px;"></iframe>'

st.components.v1.html(HTML_BASE, height=950, scrolling=True)
