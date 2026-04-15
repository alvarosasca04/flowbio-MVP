import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="FlowBio Intelligence | Subsurface OS",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FlowBio Intelligence</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════
   TOKENS
═══════════════════════════════════════════════════ */
:root {
  --bg:      #060C12;
  --bg2:     #0B1420;
  --bg3:     #0F1C2E;
  --card:    #0D1928;
  --border:  #152335;
  --border2: #1E3348;
  --green:   #00E5A0;
  --blue:    #3B82F6;
  --cyan:    #22D3EE;
  --amber:   #F59E0B;
  --red:     #EF4444;
  --text:    #E2EEF8;
  --muted:   #4A6580;
  --soft:    #8BA8C0;
  --mono:    'DM Mono', monospace;
  --head:    'Syne', sans-serif;
  --body:    'DM Sans', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--body);
  height: 100%;
  overflow: hidden;
}

/* ═══════════════════════════════════════════════════
   LAYOUT
═══════════════════════════════════════════════════ */
.screen { display: none; width: 100vw; height: 100vh; }
.screen.active { display: flex; }

/* ═══════════════════════════════════════════════════
   SPLASH
═══════════════════════════════════════════════════ */
#s-splash {
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: radial-gradient(ellipse 80% 60% at 50% 50%,
    rgba(0,229,160,.05) 0%, transparent 70%);
}

#s-splash::before {
  content: '';
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0,229,160,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,229,160,.04) 1px, transparent 1px);
  background-size: 56px 56px;
  pointer-events: none;
}

.splash-badge {
  display: inline-flex; align-items: center; gap: 8px;
  border: 1px solid rgba(0,229,160,.3);
  border-radius: 20px; padding: 5px 16px;
  font-family: var(--mono); font-size: 11px; color: var(--green);
  letter-spacing: 1.5px; margin-bottom: 32px;
  animation: fadeUp .8s ease both;
}
.splash-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green);
  animation: blink 1.4s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

.splash-logo {
  font-family: var(--head);
  font-size: clamp(64px, 9vw, 120px);
  font-weight: 800;
  letter-spacing: -4px;
  line-height: 1;
  color: #fff;
  margin-bottom: 8px;
  animation: fadeUp .8s .1s ease both;
}
.splash-logo span { color: var(--green); }

.splash-sub {
  font-family: var(--mono); font-size: 12px;
  color: var(--muted); letter-spacing: 3px;
  margin-bottom: 56px;
  animation: fadeUp .8s .2s ease both;
}

.btn-launch {
  background: var(--green);
  color: #050C12;
  font-family: var(--head); font-weight: 700;
  font-size: 13px; letter-spacing: 2px;
  text-transform: uppercase;
  border: none; border-radius: 10px;
  padding: 18px 52px; cursor: pointer;
  transition: all .2s;
  box-shadow: 0 0 40px rgba(0,229,160,.2);
  animation: fadeUp .8s .35s ease both;
}
.btn-launch:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 60px rgba(0,229,160,.4);
}

.splash-stats {
  display: flex; gap: 48px; margin-top: 64px;
  animation: fadeUp .8s .45s ease both;
}
.splash-stat { text-align: center; }
.splash-stat-val {
  font-family: var(--mono); font-size: 28px; font-weight: 500;
  color: var(--text);
}
.splash-stat-lbl {
  font-family: var(--mono); font-size: 10px;
  color: var(--muted); letter-spacing: 1.5px; margin-top: 4px;
}
.splash-stat-val.g { color: var(--green); }

@keyframes fadeUp {
  from { opacity:0; transform:translateY(24px); }
  to   { opacity:1; transform:translateY(0); }
}

/* ═══════════════════════════════════════════════════
   CONFIG
═══════════════════════════════════════════════════ */
#s-config {
  flex-direction: column;
  overflow-y: auto;
}

.config-wrap {
  width: 100%; max-width: 1200px; margin: 0 auto;
  padding: 48px 40px; display: flex; flex-direction: column;
  gap: 32px;
}

.config-header {
  display: flex; align-items: flex-end;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  padding-bottom: 20px;
}
.config-title {
  font-family: var(--head); font-size: 32px;
  font-weight: 800; letter-spacing: -1px;
}
.config-title span { color: var(--green); }
.config-step {
  font-family: var(--mono); font-size: 11px;
  color: var(--muted); letter-spacing: 2px;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 20px;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px;
}
.card-title {
  font-family: var(--mono); font-size: 10px;
  letter-spacing: 2px; color: var(--green);
  margin-bottom: 20px; font-weight: 500;
}

.field { margin-bottom: 20px; }
.field:last-child { margin-bottom: 0; }
.field label {
  display: block;
  font-family: var(--mono); font-size: 10px;
  letter-spacing: 1.5px; color: var(--soft);
  margin-bottom: 8px;
}
.field select, .field input[type=number] {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  font-family: var(--body); font-size: 13px;
  padding: 11px 14px;
  outline: none;
  transition: border .2s;
  appearance: none;
}
.field select:focus, .field input[type=number]:focus {
  border-color: var(--green);
}

.slider-row {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 8px;
}
.slider-lbl { font-family: var(--mono); font-size: 10px; color: var(--soft); letter-spacing:1px; }
.slider-val { font-family: var(--mono); font-size: 13px; color: var(--green); font-weight:500; }
.slider-lbl.fin { color: var(--cyan); }
.slider-val.fin { color: var(--cyan); }
input[type=range] {
  width: 100%; accent-color: var(--green);
  height: 4px; cursor: pointer; margin-bottom: 18px;
}
input[type=range].fin-slider { accent-color: var(--cyan); }

.piml-box {
  background: var(--bg3); border: 1px solid var(--border); border-radius: 8px;
  padding: 16px 18px; display: flex; gap: 16px; flex-wrap: wrap; margin-top: 4px;
}
.piml-eq { font-family: var(--mono); font-size: 13px; color: var(--cyan); }
.piml-eq span { color: var(--muted); font-size:11px; }

.btn-sim {
  width: 100%; background: var(--green); color: #050C12;
  font-family: var(--head); font-weight: 700; font-size: 13px; letter-spacing: 2px;
  text-transform: uppercase; border: none; border-radius: 10px;
  padding: 17px; cursor: pointer; transition: all .2s;
}
.btn-sim:hover { filter: brightness(1.1); box-shadow: 0 0 30px rgba(0,229,160,.3); }
.btn-back-sm {
  background: transparent; border: 1px solid var(--border2); color: var(--muted);
  font-family: var(--mono); font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
  border-radius: 8px; padding: 10px 22px; cursor: pointer; transition: all .2s;
}
.btn-back-sm:hover { border-color: var(--soft); color: var(--text); }

/* ═══════════════════════════════════════════════════
   TERMINAL
═══════════════════════════════════════════════════ */
#s-terminal {
  flex-direction: column; align-items: center; justify-content: center; background: var(--bg);
}
.term-wrap { width: 100%; max-width: 720px; padding: 40px; }
.term-header { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.term-dot { width: 10px; height: 10px; border-radius: 50%; }
.term-box {
  background: #06090D; border: 1px solid var(--border); border-radius: 12px;
  padding: 32px; font-family: var(--mono); font-size: 13px; color: var(--green);
  line-height: 2; min-height: 220px;
}
.term-line { opacity: 0; animation: termShow .3s forwards; }
@keyframes termShow { to { opacity:1; } }
.term-line.dim { color: var(--muted); }
.term-line.ok  { color: var(--green); }
.term-line.warn { color: var(--amber); }
.term-progress {
  margin-top: 20px; background: var(--bg3); border: 1px solid var(--border);
  border-radius: 6px; height: 6px; overflow: hidden;
}
.term-bar {
  height: 100%; width: 0%; background: linear-gradient(90deg, var(--green), var(--cyan));
  border-radius: 6px; transition: width .4s ease;
}

/* ═══════════════════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════════════════ */
#s-dash { flex-direction: column; overflow-y: auto; overflow-x: hidden; }

.dash-wrap {
  width: 100%; max-width: 1400px; margin: 0 auto;
  padding: 28px 32px 60px; display: flex; flex-direction: column; gap: 24px;
}

.dash-header { display: flex; align-items: flex-end; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 18px; }
.dash-title { font-family: var(--head); font-size: 26px; font-weight: 800; letter-spacing:-1px; }
.dash-title span { color: var(--green); }
.dash-meta { font-family: var(--mono); font-size: 10px; color: var(--muted); letter-spacing:2px; margin-top:4px; }
.dash-actions { display: flex; gap: 10px; }

.btn-action {
  background: transparent; border: 1px solid var(--border2); color: var(--soft);
  font-family: var(--mono); font-size: 10px; letter-spacing: 1px; text-transform: uppercase;
  border-radius: 8px; padding: 9px 18px; cursor: pointer; transition: all .2s; display: flex; align-items: center; gap: 6px;
}
.btn-action:hover { border-color: var(--green); color: var(--green); }
.btn-action.primary { background: var(--green); color: #050C12; border-color: var(--green); font-weight:700; }
.btn-action.primary:hover { filter: brightness(1.1); }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  padding: 22px 20px; position: relative; overflow: hidden; transition: border-color .2s;
}
.kpi-card:hover { border-color: var(--border2); }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-card.g::before { background: var(--green); }
.kpi-card.b::before { background: var(--blue); }
.kpi-card.c::before { background: var(--cyan); }
.kpi-card.a::before { background: var(--amber); }

.kpi-lbl { font-family: var(--mono); font-size: 9px; letter-spacing: 1.8px; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; }
.kpi-val { font-family: var(--mono); font-size: 36px; font-weight: 500; letter-spacing: -2px; line-height: 1; }
.kpi-card.g .kpi-val { color: var(--green); }
.kpi-card.b .kpi-val { color: var(--blue); }
.kpi-card.c .kpi-val { color: var(--cyan); }
.kpi-card.a .kpi-val { color: var(--amber); }
.kpi-sub { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 8px; }
.kpi-delta { position: absolute; top: 18px; right: 18px; font-family: var(--mono); font-size: 10px; color: var(--green); background: rgba(0,229,160,.1); border: 1px solid rgba(0,229,160,.2); border-radius: 4px; padding: 3px 8px; }

.content-grid { display: grid; grid-template-columns: 1fr 380px; gap: 20px; min-height: 420px; }

.chart-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 24px; display: flex; flex-direction: column; }
.chart-card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.chart-card-title { font-family: var(--mono); font-size: 11px; letter-spacing: 1.8px; color: var(--soft); text-transform: uppercase; }
.chart-legend { display: flex; gap: 16px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-family: var(--mono); font-size: 10px; color: var(--muted); }
.legend-dot { width: 8px; height: 3px; border-radius: 2px; }

.side-panel { display: flex; flex-direction: column; gap: 16px; }

.or-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 22px; flex: 1; }
.or-title { font-family: var(--mono); font-size: 10px; letter-spacing: 1.8px; color: var(--muted); margin-bottom: 16px; }
.or-row { display: flex; justify-content: space-between; align-items: center; padding: 9px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.or-row:last-child { border-bottom: none; }
.or-key { color: var(--soft); }
.or-val { font-family: var(--mono); font-weight: 500; }
.or-val.ok   { color: var(--green); }
.or-val.warn { color: var(--amber); }
.or-val.bad  { color: var(--red); }

.alert-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; }
.alert-row { display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid var(--border); }
.alert-row:last-child { border-bottom: none; }
.alert-dot { width: 7px; height: 7px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
.alert-dot.ok   { background: var(--green); }
.alert-dot.warn { background: var(--amber); }
.alert-dot.bad  { background: var(--red); }
.alert-text { font-size: 12px; color: var(--soft); line-height: 1.5; }
.alert-meta { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 3px; }

.bottom-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

.mini-chart-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; }
.mini-title { font-family: var(--mono); font-size: 10px; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 14px; text-transform: uppercase;}

.rheo-bar-wrap { display:flex; flex-direction:column; gap:8px; }
.rheo-bar-row { display:flex; align-items:center; gap:10px; }
.rheo-lbl { font-family:var(--mono); font-size:10px; color:var(--muted); width:60px; flex-shrink:0; }
.rheo-track { flex:1; background:var(--bg3); border-radius:3px; height:6px; overflow:hidden; }
.rheo-fill  { height:100%; border-radius:3px; }
.rheo-val   { font-family:var(--mono); font-size:10px; color:var(--text); width:48px; text-align:right; }

.roi-center { text-align:center; padding: 12px 0; }
.roi-big { font-family:var(--mono); font-size:40px; color:var(--green); letter-spacing:-2px; }
.roi-sub { font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:1px; margin-top:4px; }
.roi-rows { display:flex; flex-direction:column; gap:8px; margin-top:14px; }
.roi-row  { display:flex; justify-content:space-between; font-size:12px; }
.roi-row-k { color:var(--muted); }
.roi-row-v { font-family:var(--mono); }

/* Tooltip badge */
.tooltip-wrap { position: relative; display: inline-flex; align-items: center; gap: 6px; }
.tooltip-icon { width: 14px; height: 14px; border-radius: 50%; background: var(--bg3); border: 1px solid var(--border2); display: flex; align-items: center; justify-content: center; font-size: 9px; color: var(--muted); cursor: default; }
.tooltip-box { position: absolute; top: calc(100% + 8px); left: 50%; transform: translateX(-50%); background: var(--bg2); border: 1px solid var(--border2); border-radius: 8px; padding: 8px 12px; font-family: var(--mono); font-size: 10px; color: var(--soft); white-space: nowrap; pointer-events: none; opacity: 0; transition: opacity .15s; z-index: 50; }
.tooltip-wrap:hover .tooltip-box { opacity: 1; }
</style>
</head>
<body>

<div id="s-splash" class="screen active">
  <div class="splash-badge">
    <span class="splash-dot"></span>
    PIML ENGINE v0.3 · TRL 4 · AWS ACTIVE
  </div>
  <h1 class="splash-logo">FlowBio<span>.</span></h1>
  <p class="splash-sub">SUBSURFACE INTELLIGENCE PLATFORM</p>
  <button class="btn-launch" onclick="go('s-config')">
    INICIALIZAR INSTANCIA CLOUD
  </button>
</div>

<div id="s-config" class="screen">
  <div class="config-wrap">
    <div class="config-header">
      <div>
        <h2 class="config-title">Asset <span>Configuration</span></h2>
        <p class="config-step">PARÁMETROS DEL YACIMIENTO & FINANCIEROS</p>
      </div>
      <button class="btn-back-sm" onclick="go('s-splash')">← Volver</button>
    </div>

    <div class="config-grid">
      <div class="card">
        <div class="card-title">INFRAESTRUCTURA Y ECONOMÍA</div>

        <div class="field">
          <label>FLUIDO EOR</label>
          <select id="chem-input">
            <option value="nacmc">Na-CMC FlowBio (Biodegradable)</option>
            <option value="hpam">HPAM (Poliacrilamida)</option>
          </select>
        </div>

        <div class="field">
          <label>CUENCA / REGIÓN</label>
          <select id="basin-input">
            <option value="mexico">México · Cuenca de Burgos</option>
            <option value="colombia">Colombia · Llanos Orientales</option>
          </select>
        </div>

        <div style="margin-top: 30px; border-top: 1px solid var(--border2); padding-top: 20px;">
          <div class="card-title" style="color:var(--cyan)">SENSIBILIDAD FINANCIERA</div>
          
          <div class="slider-row">
            <span class="slider-lbl fin">PRECIO DEL BARRIL (USD)</span>
            <span class="slider-val fin" id="price-disp">$75</span>
          </div>
          <input type="range" class="fin-slider" id="price-in" min="40" max="120" value="75" oninput="upd()">

          <div class="slider-row">
            <span class="slider-lbl fin">SUCCESS FEE (%)</span>
            <span class="slider-val fin" id="fee-disp">5%</span>
          </div>
          <input type="range" class="fin-slider" id="fee-in" min="1" max="15" value="5" oninput="upd()">

          <div class="slider-row">
            <span class="slider-lbl fin">CAPEX / COSTO FIJO (USD/mes)</span>
            <span class="slider-val fin" id="capex-disp">$25,000</span>
          </div>
          <input type="range" class="fin-slider" id="capex-in" min="5000" max="150000" step="5000" value="25000" oninput="upd()">
        </div>
      </div>

      <div class="card">
        <div class="card-title">PARÁMETROS DEL YACIMIENTO</div>

        <div class="slider-row"><span class="slider-lbl">PERMEABILIDAD (mD)</span><span class="slider-val" id="k-disp">850</span></div>
        <input type="range" id="k-in" min="50" max="3000" value="850" oninput="upd()">

        <div class="slider-row"><span class="slider-lbl">VISCOSIDAD CRUDO (cP)</span><span class="slider-val" id="v-disp">120</span></div>
        <input type="range" id="v-in" min="5" max="800" value="120" oninput="upd()">

        <div class="slider-row"><span class="slider-lbl">TEMPERATURA (°C)</span><span class="slider-val" id="t-disp">82</span></div>
        <input type="range" id="t-in" min="40" max="130" value="82" oninput="upd()">

        <div class="slider-row"><span class="slider-lbl">SALINIDAD (ppm)</span><span class="slider-val" id="s-disp">38,000</span></div>
        <input type="range" id="s-in" min="5000" max="100000" value="38000" oninput="upd()">

        <div class="slider-row"><span class="slider-lbl">PRODUCCIÓN BASE (bbl/día)</span><span class="slider-val" id="bopd-disp">500</span></div>
        <input type="range" id="bopd-in" min="50" max="3000" value="500" oninput="upd()">
      </div>
    </div>

    <div style="display:flex; gap:12px;">
      <button class="btn-back-sm" onclick="go('s-splash')" style="padding:14px 28px">← Atrás</button>
      <button class="btn-sim" onclick="runSim()">⚡ EJECUTAR SIMULACIÓN PIML Y ROI</button>
    </div>
  </div>
</div>

<div id="s-terminal" class="screen" style="flex-direction:column;align-items:center;justify-content:center;">
  <div class="term-wrap">
    <div class="term-header">
      <div class="term-dot" style="background:#EF4444"></div>
      <div class="term-dot" style="background:#F59E0B"></div>
      <div class="term-dot" style="background:#00E5A0"></div>
    </div>
    <div class="term-box" id="term-log"></div>
    <div class="term-progress" style="margin-top:16px;">
      <div class="term-bar" id="term-bar"></div>
    </div>
  </div>
</div>

<div id="s-dash" class="screen">
  <div class="dash-wrap">
    <div class="dash-header">
      <div>
        <h1 class="dash-title">Command Center <span>FlowBio</span></h1>
        <p class="dash-meta" id="dash-meta">ASSET · SIMULACIÓN PIML v0.3</p>
      </div>
      <div class="dash-actions">
        <button class="btn-action" onclick="go('s-config')">← Ajustar Sensibilidad</button>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card g">
        <div class="kpi-lbl">BARRILES EXTRA/MES</div>
        <div class="kpi-val" id="kpi-extra">--</div>
        <div class="kpi-sub">Incremento estimado</div>
      </div>
      <div class="kpi-card c">
        <div class="kpi-lbl">SUCCESS FEE / MES</div>
        <div class="kpi-val" id="kpi-fee">--</div>
        <div class="kpi-sub">Modelo Sin Riesgo OPEX</div>
      </div>
      <div class="kpi-card a">
        <div class="kpi-lbl">COSTO FIJO (CAPEX/OPEX)</div>
        <div class="kpi-val" id="kpi-capex">--</div>
        <div class="kpi-sub">Logística y operación/mes</div>
      </div>
      <div class="kpi-card b">
        <div class="kpi-lbl">FACTOR SKIN (S)</div>
        <div class="kpi-val" id="kpi-skin">--</div>
        <div class="kpi-sub" id="kpi-skin-sub">diagnóstico</div>
      </div>
    </div>

    <div class="content-grid">
      <div class="chart-card">
        <div class="chart-card-head">
          <span class="chart-card-title">CURVA DE PRODUCCIÓN — BASELINE vs NA-CMC FLOWBIO</span>
        </div>
        <div id="chart-prod" style="flex:1;min-height:300px"></div>
      </div>

      <div class="side-panel">
        <div class="or-card">
          <div class="or-title">OPERATIONAL READINESS</div>
          <div class="or-row"><span class="or-key">Estabilidad térmica</span><span class="or-val" id="or-temp">—</span></div>
          <div class="or-row"><span class="or-key">Skin Damage</span><span class="or-val" id="or-skin">—</span></div>
          <div class="or-row"><span class="or-key">Biodegradabilidad</span><span class="or-val" id="or-bio">—</span></div>
        </div>
      </div>
    </div>

    <div class="bottom-grid">
      <div class="mini-chart-card">
        <div class="mini-title">REOLOGÍA POWER LAW — η vs γ</div>
        <div id="chart-rheo" style="height:200px"></div>
      </div>

      <div class="mini-chart-card" style="border-color: var(--cyan);">
        <div class="mini-title" style="color: var(--cyan);">ANÁLISIS ECONÓMICO REALISTA</div>
        <div class="roi-center">
          <div class="roi-big" id="roi-pct" style="color: var(--cyan);">—</div>
          <div class="roi-sub">NET ROI MENSUAL</div>
        </div>
        <div class="roi-rows">
          <div class="roi-row">
            <span class="roi-row-k">Gross Fee Mensual</span>
            <span class="roi-row-v" id="roi-fee-gross" style="color:var(--green)">—</span>
          </div>
          <div class="roi-row">
            <span class="roi-row-k">Costo Polímero</span>
            <span class="roi-row-v" id="roi-poly" style="color:var(--amber)">—</span>
          </div>
          <div class="roi-row">
            <span class="roi-row-k">CAPEX/Costo Fijo</span>
            <span class="roi-row-v" id="roi-cost-fijo" style="color:var(--red)">—</span>
          </div>
          <div class="roi-row" style="border-top: 1px solid var(--border); padding-top: 8px; margin-top: 4px;">
            <span class="roi-row-k" style="color:var(--text); font-weight:bold;">Neto Mensual</span>
            <span class="roi-row-v" id="roi-net" style="color:var(--cyan); font-weight:bold;">—</span>
          </div>
        </div>
      </div>

      <div class="mini-chart-card">
        <div class="mini-title">VISCOSIDAD A 10 s⁻¹ — COMPARATIVO</div>
        <div class="rheo-bar-wrap" id="rheo-bars"></div>
      </div>
    </div>
  </div>
</div>

<script>
let SIM = {};

function go(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function piml(T, S, C, perm, visc, bopd, fluid, price, fee_pct, capex) {
  let n, K;
  if (fluid === 'nacmc') {
    n = Math.min(0.90, Math.max(0.25, 0.65 - T/1200 - S/600000 - C*0.08));
    K = Math.max(30, 160 - T*0.75 + S*0.001 + C*12);
  } else {
    n = Math.min(0.90, Math.max(0.30, 0.78 - T/900 - S/500000 - C*0.05));
    K = Math.max(30, 200 - T*0.90 + S*0.0008 + C*10);
  }

  const eta = K * Math.pow(10, n - 1);
  const Kd  = perm * 0.25;
  const skin = (Kd > 0) ? (perm/Kd - 1) * Math.log(8.0/0.35) : 0;
  const M = Math.min(8, Math.max(0.05, (0.4/eta) / (0.8/visc)));

  function sweep(m) {
    if (m <= 0.5) return 90;
    if (m <= 1.0) return 90 - (m-0.5)*20;
    if (m <= 2.0) return 80 - (m-1.0)*25;
    return Math.max(30, 55 - (m-2)*10);
  }
  
  const eff_base  = sweep(2.5);
  const eff_nacmc = sweep(M);
  const mej = Math.max(0, (eff_nacmc - eff_base) / Math.max(1, eff_base) * 100);

  const extra_bbl_day = bopd * mej / 100;
  const extra_bbl_month = extra_bbl_day * 30;
  
  // FINANZAS REALISTAS
  const gross_revenue_month = extra_bbl_month * price;
  const fee_month = gross_revenue_month * (fee_pct / 100);
  
  // Costos
  const poly_cost_month = 150 * 0.159 * (C/100) * 1000 * 2.8; 
  const total_cost_month = capex + poly_cost_month;
  
  // Netos
  const net_month = fee_month - total_cost_month;
  const roi_pct = Math.round((net_month / total_cost_month) * 100);

  return {n, K, eta, skin, M, eff_base, eff_nacmc, mej, extra: extra_bbl_day, extra_bbl_month,
          fee_month, poly_cost_month, total_cost_month, net_month, roi_pct,
          T, S, perm, visc, bopd, fluid, price, fee_pct, capex};
}

function upd() {
  document.getElementById('k-disp').textContent    = document.getElementById('k-in').value;
  document.getElementById('v-disp').textContent    = document.getElementById('v-in').value;
  document.getElementById('t-disp').textContent    = document.getElementById('t-in').value;
  document.getElementById('s-disp').textContent    = (+document.getElementById('s-in').value).toLocaleString();
  document.getElementById('bopd-disp').textContent = document.getElementById('bopd-in').value;
  
  document.getElementById('price-disp').textContent = "$" + document.getElementById('price-in').value;
  document.getElementById('fee-disp').textContent   = document.getElementById('fee-in').value + "%";
  document.getElementById('capex-disp').textContent = "$" + (+document.getElementById('capex-in').value).toLocaleString();
}

async function runSim() {
  const fluid = document.getElementById('chem-input').value;
  const basin = document.getElementById('basin-input').value;
  const T     = +document.getElementById('t-in').value;
  const S     = +document.getElementById('s-in').value;
  const perm  = +document.getElementById('k-in').value;
  const visc  = +document.getElementById('v-in').value;
  const bopd  = +document.getElementById('bopd-in').value;
  
  const price = +document.getElementById('price-in').value;
  const fee_pct = +document.getElementById('fee-in').value;
  const capex = +document.getElementById('capex-in').value;

  go('s-terminal');
  const box = document.getElementById('term-log');
  const bar = document.getElementById('term-bar');
  box.innerHTML = '';

  const logs = [
    {t:300, c:'dim', m:`> Calculando sensibilidad financiera con CAPEX...`},
    {t:800, c:'ok',  m:`> ✓ Modelo Power Law y factor Skin calculados`},
    {t:1400,c:'ok',  m:`> ✓ Simulación PIML y ROI Financiero completado`},
  ];

  for (let i = 0; i < logs.length; i++) {
    await sleep(i === 0 ? 0 : logs[i].t - logs[i-1].t);
    const d = document.createElement('div');
    d.className = `term-line ${logs[i].c}`;
    d.textContent = logs[i].m;
    box.appendChild(d);
    bar.style.width = Math.round(((i+1)/logs.length)*100) + '%';
  }

  await sleep(400);

  SIM = piml(T, S, 0.8, perm, visc, bopd, fluid, price, fee_pct, capex);
  SIM.basin = basin;
  renderDash();
  go('s-dash');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function renderDash() {
  const r = SIM;

  document.getElementById('dash-meta').textContent = `ACTIVO · SIMULACIÓN PIML v0.3`;

  document.getElementById('kpi-extra').textContent = '+' + fmt(r.extra_bbl_month);
  document.getElementById('kpi-skin').textContent = r.skin.toFixed(2);
  document.getElementById('kpi-skin-sub').textContent = r.skin>8?'DAÑO SEVERO':'DAÑO MODERADO/BAJO';
  document.getElementById('kpi-fee').textContent = '$' + fmt(r.fee_month);
  document.getElementById('kpi-capex').textContent = '$' + fmt(r.capex);

  const setOR = (id, val, ok, warn) => {
    const el = document.getElementById(id);
    el.textContent = val;
    el.className = 'or-val ' + ok;
  };
  setOR('or-temp', r.T < 90 ? '✓ OK ('+r.T+'°C)' : '⚠ '+r.T+'°C', r.T<90?'ok':'warn');
  setOR('or-skin', r.skin>8?'✗ Alto S='+r.skin.toFixed(1):'✓ OK', r.skin>8?'bad':'ok');
  setOR('or-bio',  r.fluid==='nacmc'?'✓ 100%':'✗ No', r.fluid==='nacmc'?'ok':'bad');

  // ROI Financiero Realista
  document.getElementById('roi-pct').textContent       = r.roi_pct + '%';
  document.getElementById('roi-fee-gross').textContent = '$' + fmt(r.fee_month);
  document.getElementById('roi-poly').textContent      = '$' + fmt(r.poly_cost_month);
  document.getElementById('roi-cost-fijo').textContent = '$' + fmt(r.capex);
  document.getElementById('roi-net').textContent       = '$' + fmt(r.net_month);

  const fluids = [
    {lbl:'Na-CMC', eta: piml(r.T,r.S,0.8,r.perm,r.visc,r.bopd,r.fluid,r.price,r.fee_pct,r.capex).eta, col:'#00E5A0'},
    {lbl:'HPAM',   eta: piml(r.T,r.S,0.8,r.perm,r.visc,r.bopd,'hpam',r.price,r.fee_pct,r.capex).eta,  col:'#EF4444'},
  ];
  const maxEta = Math.max(...fluids.map(f=>f.eta));
  document.getElementById('rheo-bars').innerHTML = fluids.map(f => `
    <div class="rheo-bar-row"><span class="rheo-lbl">${f.lbl}</span>
    <div class="rheo-track"><div class="rheo-fill" style="width:${(f.eta/maxEta*100).toFixed(1)}%;background:${f.col}"></div></div>
    <span class="rheo-val">${Math.round(f.eta)} mPa·s</span></div>`).join('');

  renderProdChart();
  renderRheoChart();
}

function renderProdChart() {
  const r = SIM;
  const x = Array.from({length:48},(_,i)=>i);
  const y1 = x.map(i => r.bopd * Math.exp(-0.0055*i));
  const y2 = x.map(i => i<6 ? y1[i] : (r.bopd + r.extra) * Math.exp(-0.0025*i));

  Plotly.newPlot('chart-prod',[
    {x,y:y1, name:'Baseline', type:'scatter', line:{color:'#EF4444',dash:'dot',width:2}},
    {x,y:y2, name:'FlowBio', type:'scatter', line:{color:'#00E5A0',width:3}, fill:'tonexty', fillcolor:'rgba(0,229,160,0.08)'},
  ],{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,
