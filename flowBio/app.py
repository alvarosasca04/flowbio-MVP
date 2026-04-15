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

/* grid de fondo */
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

/* stat row */
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
  width: 100%; max-width: 1100px; margin: 0 auto;
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
  grid-template-columns: 1fr 1fr;
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

/* Campos */
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
.field select option { background: var(--bg2); }

/* Sliders */
.slider-row {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 8px;
}
.slider-lbl { font-family: var(--mono); font-size: 10px; color: var(--soft); letter-spacing:1px; }
.slider-val { font-family: var(--mono); font-size: 13px; color: var(--green); font-weight:500; }
input[type=range] {
  width: 100%;
  accent-color: var(--green);
  height: 4px;
  cursor: pointer;
  margin-bottom: 18px;
}

/* Ecuación PIML */
.piml-box {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 18px;
  display: flex; gap: 16px; flex-wrap: wrap;
  margin-top: 4px;
}
.piml-eq {
  font-family: var(--mono); font-size: 13px;
  color: var(--cyan);
}
.piml-eq span { color: var(--muted); font-size:11px; }

.btn-sim {
  width: 100%;
  background: var(--green); color: #050C12;
  font-family: var(--head); font-weight: 700;
  font-size: 13px; letter-spacing: 2px;
  text-transform: uppercase;
  border: none; border-radius: 10px;
  padding: 17px; cursor: pointer;
  transition: all .2s;
}
.btn-sim:hover {
  filter: brightness(1.1);
  box-shadow: 0 0 30px rgba(0,229,160,.3);
}
.btn-back-sm {
  background: transparent;
  border: 1px solid var(--border2);
  color: var(--muted);
  font-family: var(--mono); font-size: 11px;
  letter-spacing: 1px; text-transform: uppercase;
  border-radius: 8px; padding: 10px 22px;
  cursor: pointer; transition: all .2s;
}
.btn-back-sm:hover { border-color: var(--soft); color: var(--text); }

/* ═══════════════════════════════════════════════════
   TERMINAL
═══════════════════════════════════════════════════ */
#s-terminal {
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}
.term-wrap {
  width: 100%; max-width: 720px;
  padding: 40px;
}
.term-header {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 20px;
}
.term-dot { width: 10px; height: 10px; border-radius: 50%; }
.term-box {
  background: #06090D;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 32px;
  font-family: var(--mono); font-size: 13px;
  color: var(--green); line-height: 2;
  min-height: 220px;
}
.term-line { opacity: 0; animation: termShow .3s forwards; }
@keyframes termShow { to { opacity:1; } }
.term-line.dim { color: var(--muted); }
.term-line.ok  { color: var(--green); }
.term-line.warn { color: var(--amber); }
.term-progress {
  margin-top: 20px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 6px;
  height: 6px; overflow: hidden;
}
.term-bar {
  height: 100%; width: 0%;
  background: linear-gradient(90deg, var(--green), var(--cyan));
  border-radius: 6px;
  transition: width .4s ease;
}

/* ═══════════════════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════════════════ */
#s-dash {
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

.dash-wrap {
  width: 100%; max-width: 1400px; margin: 0 auto;
  padding: 28px 32px 60px;
  display: flex; flex-direction: column; gap: 24px;
}

/* Header */
.dash-header {
  display: flex; align-items: flex-end;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  padding-bottom: 18px;
}
.dash-title { font-family: var(--head); font-size: 26px; font-weight: 800; letter-spacing:-1px; }
.dash-title span { color: var(--green); }
.dash-meta { font-family: var(--mono); font-size: 10px; color: var(--muted); letter-spacing:2px; margin-top:4px; }
.dash-actions { display: flex; gap: 10px; }

.btn-action {
  background: transparent;
  border: 1px solid var(--border2);
  color: var(--soft);
  font-family: var(--mono); font-size: 10px;
  letter-spacing: 1px; text-transform: uppercase;
  border-radius: 8px; padding: 9px 18px;
  cursor: pointer; transition: all .2s;
  display: flex; align-items: center; gap: 6px;
}
.btn-action:hover { border-color: var(--green); color: var(--green); }
.btn-action.primary {
  background: var(--green); color: #050C12;
  border-color: var(--green); font-weight:700;
}
.btn-action.primary:hover { filter: brightness(1.1); }

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.kpi-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 20px;
  position: relative; overflow: hidden;
  transition: border-color .2s;
}
.kpi-card:hover { border-color: var(--border2); }
.kpi-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.kpi-card.g::before { background: var(--green); }
.kpi-card.b::before { background: var(--blue); }
.kpi-card.c::before { background: var(--cyan); }
.kpi-card.a::before { background: var(--amber); }

.kpi-lbl {
  font-family: var(--mono); font-size: 9px;
  letter-spacing: 1.8px; color: var(--muted);
  text-transform: uppercase; margin-bottom: 12px;
}
.kpi-val {
  font-family: var(--mono); font-size: 36px;
  font-weight: 500; letter-spacing: -2px;
  line-height: 1;
}
.kpi-card.g .kpi-val { color: var(--green); }
.kpi-card.b .kpi-val { color: var(--blue); }
.kpi-card.c .kpi-val { color: var(--cyan); }
.kpi-card.a .kpi-val { color: var(--amber); }
.kpi-sub {
  font-family: var(--mono); font-size: 10px;
  color: var(--muted); margin-top: 8px;
}
.kpi-delta {
  position: absolute; top: 18px; right: 18px;
  font-family: var(--mono); font-size: 10px;
  color: var(--green); background: rgba(0,229,160,.1);
  border: 1px solid rgba(0,229,160,.2);
  border-radius: 4px; padding: 3px 8px;
}

/* Main content grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;
  min-height: 420px;
}

.chart-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px;
  display: flex; flex-direction: column;
}
.chart-card-head {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 16px;
}
.chart-card-title {
  font-family: var(--mono); font-size: 11px;
  letter-spacing: 1.8px; color: var(--soft);
  text-transform: uppercase;
}
.chart-legend {
  display: flex; gap: 16px;
}
.legend-item {
  display: flex; align-items: center; gap: 6px;
  font-family: var(--mono); font-size: 10px; color: var(--muted);
}
.legend-dot { width: 8px; height: 3px; border-radius: 2px; }

/* Panel lateral */
.side-panel {
  display: flex; flex-direction: column; gap: 16px;
}

.or-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px;
  flex: 1;
}
.or-title {
  font-family: var(--mono); font-size: 10px;
  letter-spacing: 1.8px; color: var(--muted);
  margin-bottom: 16px;
}
.or-row {
  display: flex; justify-content: space-between;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
}
.or-row:last-child { border-bottom: none; }
.or-key { color: var(--soft); }
.or-val { font-family: var(--mono); font-weight: 500; }
.or-val.ok   { color: var(--green); }
.or-val.warn { color: var(--amber); }
.or-val.bad  { color: var(--red); }

.alert-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
}
.alert-row {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.alert-row:last-child { border-bottom: none; }
.alert-dot {
  width: 7px; height: 7px; border-radius: 50%;
  margin-top: 5px; flex-shrink: 0;
}
.alert-dot.ok   { background: var(--green); }
.alert-dot.warn { background: var(--amber); }
.alert-dot.bad  { background: var(--red); }
.alert-text { font-size: 12px; color: var(--soft); line-height: 1.5; }
.alert-meta {
  font-family: var(--mono); font-size: 10px;
  color: var(--muted); margin-top: 3px;
}

/* Bottom row */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

.mini-chart-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
}
.mini-title {
  font-family: var(--mono); font-size: 10px;
  letter-spacing: 1.5px; color: var(--muted);
  margin-bottom: 14px;
}

/* Rheo bars */
.rheo-bar-wrap { display:flex; flex-direction:column; gap:8px; }
.rheo-bar-row { display:flex; align-items:center; gap:10px; }
.rheo-lbl { font-family:var(--mono); font-size:10px; color:var(--muted); width:60px; flex-shrink:0; }
.rheo-track { flex:1; background:var(--bg3); border-radius:3px; height:6px; overflow:hidden; }
.rheo-fill  { height:100%; border-radius:3px; }
.rheo-val   { font-family:var(--mono); font-size:10px; color:var(--text); width:48px; text-align:right; }

/* ROI donut placeholder */
.roi-center { text-align:center; padding: 12px 0; }
.roi-big { font-family:var(--mono); font-size:40px; color:var(--green); letter-spacing:-2px; }
.roi-sub { font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:1px; margin-top:4px; }
.roi-rows { display:flex; flex-direction:column; gap:8px; margin-top:14px; }
.roi-row  { display:flex; justify-content:space-between; font-size:12px; }
.roi-row-k { color:var(--muted); }
.roi-row-v { font-family:var(--mono); }

/* Tooltip badge */
.tooltip-wrap { position: relative; display: inline-flex; align-items: center; gap: 6px; }
.tooltip-icon {
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--bg3); border: 1px solid var(--border2);
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; color: var(--muted); cursor: default;
}
.tooltip-box {
  position: absolute; top: calc(100% + 8px); left: 50%;
  transform: translateX(-50%);
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: 8px; padding: 8px 12px;
  font-family: var(--mono); font-size: 10px;
  color: var(--soft); white-space: nowrap;
  pointer-events: none; opacity: 0;
  transition: opacity .15s; z-index: 50;
}
.tooltip-wrap:hover .tooltip-box { opacity: 1; }

/* Modal de exportar */
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.6);
  backdrop-filter: blur(4px);
  z-index: 200;
  display: none; align-items: center; justify-content: center;
}
.overlay.active { display: flex; }
.modal {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 16px;
  padding: 36px;
  width: 100%; max-width: 420px;
}
.modal-title {
  font-family: var(--head); font-size: 20px;
  font-weight: 700; margin-bottom: 8px;
}
.modal-sub {
  font-size: 13px; color: var(--muted);
  margin-bottom: 24px; line-height: 1.6;
}
.modal-opts { display: flex; flex-direction: column; gap: 10px; margin-bottom: 24px; }
.modal-opt {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 16px;
  display: flex; align-items: center; gap: 14px;
  cursor: pointer; transition: border-color .2s;
  font-size: 13px; color: var(--text);
}
.modal-opt:hover { border-color: var(--green); }
.modal-opt-icon { font-size: 20px; }
.modal-opt-meta { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 2px; }
.modal-close {
  width: 100%; background: transparent;
  border: 1px solid var(--border2); color: var(--muted);
  font-family: var(--mono); font-size: 11px;
  letter-spacing: 1px; border-radius: 8px; padding: 11px;
  cursor: pointer; transition: all .2s;
}
.modal-close:hover { color: var(--text); border-color: var(--soft); }
</style>
</head>
<body>

<!-- ═══════════════════ SPLASH ═══════════════════ -->
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
  <div class="splash-stats">
    <div class="splash-stat">
      <div class="splash-stat-val g">5,922</div>
      <div class="splash-stat-lbl">POZOS SIMULADOS</div>
    </div>
    <div class="splash-stat">
      <div class="splash-stat-val">+18%</div>
      <div class="splash-stat-lbl">EF. BARRIDO</div>
    </div>
    <div class="splash-stat">
      <div class="splash-stat-val">TRL 4</div>
      <div class="splash-stat-lbl">TECH LEVEL</div>
    </div>
    <div class="splash-stat">
      <div class="splash-stat-val g">$5</div>
      <div class="splash-stat-lbl">USD / BBL EXTRA</div>
    </div>
  </div>
</div>

<!-- ═══════════════════ CONFIG ═══════════════════ -->
<div id="s-config" class="screen">
  <div class="config-wrap">
    <div class="config-header">
      <div>
        <h2 class="config-title">Asset <span>Configuration</span></h2>
        <p class="config-step">PASO 1 DE 2 · PARÁMETROS DEL YACIMIENTO</p>
      </div>
      <button class="btn-back-sm" onclick="go('s-splash')">← Volver</button>
    </div>

    <div class="config-grid">
      <!-- Col 1: Selects -->
      <div class="card">
        <div class="card-title">TIPO DE ACTIVO</div>

        <div class="field">
          <label>FLUIDO EOR</label>
          <select id="chem-input">
            <option value="nacmc">Na-CMC FlowBio (Biodegradable)</option>
            <option value="hpam">HPAM (Poliacrilamida)</option>
            <option value="xanthan">Xanthan Gum</option>
            <option value="scleroglucan">Scleroglucan</option>
          </select>
        </div>

        <div class="field">
          <label>INFRAESTRUCTURA DE INYECCIÓN</label>
          <select id="infra-input">
            <option value="enterprise">Pad Multi-Pozo (Enterprise)</option>
            <option value="single">Pozo Individual (Piloto)</option>
            <option value="offshore">Offshore Platform</option>
          </select>
        </div>

        <div class="field">
          <label>CUENCA / REGIÓN</label>
          <select id="basin-input">
            <option value="ukcs">UKCS · North Sea</option>
            <option value="mexico">México · Cuenca de Burgos</option>
            <option value="colombia">Colombia · Llanos Orientales</option>
            <option value="argentina">Argentina · Vaca Muerta</option>
          </select>
        </div>

        <!-- Ecuación PIML en vivo -->
        <div class="card-title" style="margin-top:20px">PREVIEW PIML</div>
        <div class="piml-box">
          <span class="piml-eq">τ = <span>K·</span>γⁿ</span>
          <span class="piml-eq" id="eq-n">n = <span id="n-val">0.57</span></span>
          <span class="piml-eq" id="eq-k">K = <span id="k-val">142</span> mPa·sⁿ</span>
        </div>
      </div>

      <!-- Col 2: Sliders -->
      <div class="card">
        <div class="card-title">PARÁMETROS DEL YACIMIENTO</div>

        <div class="slider-row">
          <span class="slider-lbl">PERMEABILIDAD (mD)</span>
          <span class="slider-val" id="k-disp">850</span>
        </div>
        <input type="range" id="k-in" min="50" max="3000" value="850"
               oninput="upd()">

        <div class="slider-row">
          <span class="slider-lbl">VISCOSIDAD CRUDO (cP)</span>
          <span class="slider-val" id="v-disp">120</span>
        </div>
        <input type="range" id="v-in" min="5" max="800" value="120"
               oninput="upd()">

        <div class="slider-row">
          <span class="slider-lbl">TEMPERATURA (°C)</span>
          <span class="slider-val" id="t-disp">82</span>
        </div>
        <input type="range" id="t-in" min="40" max="130" value="82"
               oninput="upd()">

        <div class="slider-row">
          <span class="slider-lbl">SALINIDAD (ppm)</span>
          <span class="slider-val" id="s-disp">38,000</span>
        </div>
        <input type="range" id="s-in" min="5000" max="100000" value="38000"
               oninput="upd()">

        <div class="slider-row">
          <span class="slider-lbl">PRODUCCIÓN BASE (bbl/día)</span>
          <span class="slider-val" id="bopd-disp">500</span>
        </div>
        <input type="range" id="bopd-in" min="50" max="3000" value="500"
               oninput="upd()">

        <div class="slider-row">
          <span class="slider-lbl">OPEX ACTUAL (USD/bbl)</span>
          <span class="slider-val" id="opex-disp">18.5</span>
        </div>
        <input type="range" id="opex-in" min="5" max="50" value="18.5" step="0.5"
               oninput="upd()">
      </div>
    </div>

    <div style="display:flex; gap:12px;">
      <button class="btn-back-sm" onclick="go('s-splash')" style="padding:14px 28px">
        ← Atrás
      </button>
      <button class="btn-sim" onclick="runSim()">
        ⚡ EJECUTAR SIMULACIÓN PIML
      </button>
    </div>
  </div>
</div>

<!-- ═══════════════════ TERMINAL ═══════════════════ -->
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
    <div style="margin-top:12px; font-family:var(--mono); font-size:11px;
                color:var(--muted); text-align:right;" id="term-pct">0%</div>
  </div>
</div>

<!-- ═══════════════════ DASHBOARD ═══════════════════ -->
<div id="s-dash" class="screen">
  <div class="dash-wrap">

    <!-- Header -->
    <div class="dash-header">
      <div>
        <h1 class="dash-title">Command Center <span>FlowBio</span></h1>
        <p class="dash-meta" id="dash-meta">ASSET · UKCS NORTH SEA · SIMULACIÓN PIML v0.3</p>
      </div>
      <div class="dash-actions">
        <button class="btn-action" onclick="go('s-config')">← Ajustar</button>
        <button class="btn-action" onclick="openModal()">⬇ Exportar</button>
        <button class="btn-action primary" onclick="runSim()">▶ Re-simular</button>
      </div>
    </div>

    <!-- KPIs -->
    <div class="kpi-grid">
      <div class="kpi-card g">
        <div class="kpi-lbl">
          <span class="tooltip-wrap">
            BARRILES EXTRA/DÍA
            <span class="tooltip-icon">?</span>
            <span class="tooltip-box">Incremento sobre línea base con Na-CMC</span>
          </span>
        </div>
        <div class="kpi-val" id="kpi-extra">--</div>
        <div class="kpi-sub">bbl/día adicionales</div>
        <div class="kpi-delta" id="kpi-extra-pct">+0%</div>
      </div>
      <div class="kpi-card b">
        <div class="kpi-lbl">FACTOR SKIN (S)</div>
        <div class="kpi-val" id="kpi-skin">--</div>
        <div class="kpi-sub" id="kpi-skin-sub">diagnóstico</div>
      </div>
      <div class="kpi-card c">
        <div class="kpi-lbl">SUCCESS FEE / MES</div>
        <div class="kpi-val" id="kpi-fee">--</div>
        <div class="kpi-sub">$5 USD × bbl extra × 30d</div>
      </div>
      <div class="kpi-card a">
        <div class="kpi-lbl">AHORRO OPEX / AÑO</div>
        <div class="kpi-val" id="kpi-opex">--</div>
        <div class="kpi-sub">USD/año proyectado</div>
      </div>
    </div>

    <!-- Chart + Panel -->
    <div class="content-grid">
      <!-- Gráfica principal: Producción -->
      <div class="chart-card">
        <div class="chart-card-head">
          <span class="chart-card-title">CURVA DE PRODUCCIÓN — BASELINE vs NA-CMC FLOWBIO</span>
          <div class="chart-legend">
            <span class="legend-item">
              <span class="legend-dot" style="background:var(--red)"></span> Baseline
            </span>
            <span class="legend-item">
              <span class="legend-dot" style="background:var(--green)"></span> Con Na-CMC
            </span>
          </div>
        </div>
        <div id="chart-prod" style="flex:1;min-height:300px"></div>
      </div>

      <!-- Panel lateral -->
      <div class="side-panel">

        <!-- Operational Readiness -->
        <div class="or-card">
          <div class="or-title">OPERATIONAL READINESS</div>
          <div class="or-row">
            <span class="or-key">Estabilidad térmica</span>
            <span class="or-val" id="or-temp">—</span>
          </div>
          <div class="or-row">
            <span class="or-key">Compat. salina</span>
            <span class="or-val" id="or-sal">—</span>
          </div>
          <div class="or-row">
            <span class="or-key">Skin Damage</span>
            <span class="or-val" id="or-skin">—</span>
          </div>
          <div class="or-row">
            <span class="or-key">FPI taponamiento</span>
            <span class="or-val" id="or-fpi">—</span>
          </div>
          <div class="or-row">
            <span class="or-key">Biodegradabilidad</span>
            <span class="or-val" id="or-bio">—</span>
          </div>
          <div class="or-row">
            <span class="or-key">HSE Factor</span>
            <span class="or-val" id="or-hse">—</span>
          </div>
        </div>

        <!-- Alertas -->
        <div class="alert-card">
          <div class="or-title">ALERTAS DEL SISTEMA</div>
          <div id="alert-list"></div>
        </div>

      </div>
    </div>

    <!-- Bottom: Reología + ROI + Rheo bars -->
    <div class="bottom-grid">

      <!-- Reología -->
      <div class="mini-chart-card">
        <div class="mini-title">REOLOGÍA POWER LAW — η vs γ</div>
        <div id="chart-rheo" style="height:200px"></div>
      </div>

      <!-- ROI -->
      <div class="mini-chart-card">
        <div class="mini-title">ANÁLISIS ECONÓMICO · SUCCESS FEE</div>
        <div class="roi-center">
          <div class="roi-big" id="roi-pct">—</div>
          <div class="roi-sub">ROI MENSUAL</div>
        </div>
        <div class="roi-rows">
          <div class="roi-row">
            <span class="roi-row-k">Fee mensual bruto</span>
            <span class="roi-row-v" id="roi-fee-gross" style="color:var(--green)">—</span>
          </div>
          <div class="roi-row">
            <span class="roi-row-k">Costo polímero/mes</span>
            <span class="roi-row-v" id="roi-cost" style="color:var(--amber)">—</span>
          </div>
          <div class="roi-row">
            <span class="roi-row-k">Neto mensual</span>
            <span class="roi-row-v" id="roi-net" style="color:var(--cyan)">—</span>
          </div>
          <div class="roi-row">
            <span class="roi-row-k">Break-even (días)</span>
            <span class="roi-row-v" id="roi-be">—</span>
          </div>
        </div>
      </div>

      <!-- Viscosidad comparativa -->
      <div class="mini-chart-card">
        <div class="mini-title">VISCOSIDAD A 10 s⁻¹ — COMPARATIVO</div>
        <div class="rheo-bar-wrap" id="rheo-bars"></div>
      </div>

    </div>

  </div><!-- /dash-wrap -->
</div>

<!-- ═══════════════════ MODAL EXPORTAR ═══════════════════ -->
<div class="overlay" id="modal-export">
  <div class="modal">
    <h3 class="modal-title">Exportar Reporte</h3>
    <p class="modal-sub">Descarga los resultados de la simulación PIML en el formato que necesites.</p>
    <div class="modal-opts">
      <div class="modal-opt" onclick="exportData('pdf')">
        <span class="modal-opt-icon">📄</span>
        <div>
          <div>Reporte PDF Ejecutivo</div>
          <div class="modal-opt-meta">FlowBio Executive Insight · Todos los KPIs</div>
        </div>
      </div>
      <div class="modal-opt" onclick="exportData('csv')">
        <span class="modal-opt-icon">📊</span>
        <div>
          <div>Dataset CSV (resultados PIML)</div>
          <div class="modal-opt-meta">Factor Skin · FPI · ROI · Reología</div>
        </div>
      </div>
      <div class="modal-opt" onclick="exportData('json')">
        <span class="modal-opt-icon">⚙️</span>
        <div>
          <div>JSON para S3 / Streamlit</div>
          <div class="modal-opt-meta">Compatible con agentes/ultimo_reporte.json</div>
        </div>
      </div>
    </div>
    <button class="modal-close" onclick="closeModal()">CANCELAR</button>
  </div>
</div>

<script>
/* ═══════════════════════════════════════════════════
   ESTADO GLOBAL
═══════════════════════════════════════════════════ */
let SIM = {};

/* ═══════════════════════════════════════════════════
   NAVEGACIÓN
═══════════════════════════════════════════════════ */
function go(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

/* ═══════════════════════════════════════════════════
   MOTOR PIML (Power Law + Skin + FPI + ROI)
═══════════════════════════════════════════════════ */
function piml(T, S, C, perm, visc, bopd, opex, fluid) {
  // Índice de flujo n (Ostwald-de Waele)
  let n, K;
  if (fluid === 'nacmc') {
    n = Math.min(0.90, Math.max(0.25, 0.65 - T/1200 - S/600000 - C*0.08));
    K = Math.max(30, 160 - T*0.75 + S*0.001 + C*12);
  } else {
    n = Math.min(0.90, Math.max(0.30, 0.78 - T/900 - S/500000 - C*0.05));
    K = Math.max(30, 200 - T*0.90 + S*0.0008 + C*10);
  }

  // Viscosidad aparente a γ = 10 s⁻¹
  const eta = K * Math.pow(10, n - 1);

  // Factor Skin
  const Kd  = perm * 0.25;
  const skin = (Kd > 0) ? (perm/Kd - 1) * Math.log(8.0/0.35) : 0;

  // Ratio de movilidad
  const M = Math.min(8, Math.max(0.05, (0.4/eta) / (0.8/visc)));

  // Eficiencia de barrido
  let eff_base, eff_nacmc;
  function sweep(m) {
    if (m <= 0.5) return 90;
    if (m <= 1.0) return 90 - (m-0.5)*20;
    if (m <= 2.0) return 80 - (m-1.0)*25;
    return Math.max(30, 55 - (m-2)*10);
  }
  eff_base  = sweep(2.5);
  eff_nacmc = sweep(M);
  const mej = Math.max(0, (eff_nacmc - eff_base) / Math.max(1, eff_base) * 100);

  // Barriles extra
  const extra = bopd * mej / 100;

  // FPI
  const pf   = perm<50?2.5 : perm<150?1.5 : perm<400?1.0 : 0.7;
  const sf   = 1 + Math.max(0, (S-60000)/20000);
  const fpi  = Math.min(1, (fluid==='nacmc'?0.12:0.65) * pf * sf);

  // ROI / Success Fee
  const fee_day   = extra * 5.0;
  const poly_day  = 150 * 0.159 * (C/100) * 1000 * 2.8 / 30;
  const net_month = (fee_day - poly_day) * 30;
  const fee_month = fee_day * 30;
  const cost_month= poly_day * 30;
  const be_days   = cost_month / Math.max(1, fee_day);
  const roi_pct   = Math.round(net_month / Math.max(1, cost_month) * 100);
  const ahorro_yr = extra * (74.5 - opex) * 0.19 * 365;

  return {n, K, eta, skin, M, eff_base, eff_nacmc, mej, extra, fpi,
          fee_month, cost_month, net_month, be_days, roi_pct, ahorro_yr,
          T, S, perm, visc, bopd, opex, fluid};
}

/* ═══════════════════════════════════════════════════
   ACTUALIZAR PREVIEW EN CONFIG
═══════════════════════════════════════════════════ */
function upd() {
  const T    = +document.getElementById('t-in').value;
  const S    = +document.getElementById('s-in').value;
  const perm = +document.getElementById('k-in').value;
  const visc = +document.getElementById('v-in').value;
  const bopd = +document.getElementById('bopd-in').value;
  const opex = +document.getElementById('opex-in').value;

  document.getElementById('k-disp').textContent    = perm;
  document.getElementById('v-disp').textContent    = visc;
  document.getElementById('t-disp').textContent    = T;
  document.getElementById('s-disp').textContent    = S.toLocaleString();
  document.getElementById('bopd-disp').textContent = bopd;
  document.getElementById('opex-disp').textContent = opex;

  // Preview PIML
  const r = piml(T, S, 0.8, perm, visc, bopd, opex, 'nacmc');
  document.getElementById('n-val').textContent = r.n.toFixed(3);
  document.getElementById('k-val').textContent = Math.round(r.K);
}

/* ═══════════════════════════════════════════════════
   SIMULACIÓN CON TERMINAL ANIMADO
═══════════════════════════════════════════════════ */
async function runSim() {
  const fluid = document.getElementById('chem-input').value;
  const infra = document.getElementById('infra-input').value;
  const basin = document.getElementById('basin-input').value;
  const T     = +document.getElementById('t-in').value;
  const S     = +document.getElementById('s-in').value;
  const perm  = +document.getElementById('k-in').value;
  const visc  = +document.getElementById('v-in').value;
  const bopd  = +document.getElementById('bopd-in').value;
  const opex  = +document.getElementById('opex-in').value;

  go('s-terminal');
  const box = document.getElementById('term-log');
  const bar = document.getElementById('term-bar');
  const pct = document.getElementById('term-pct');
  box.innerHTML = '';

  const logs = [
    {t:0,   c:'dim', m:`> FlowBio PIML Engine v0.3 — Inicializando...`},
    {t:300, c:'dim', m:`> Conectando a AWS S3 Data Lake...`},
    {t:600, c:'ok',  m:`> ✓ Bucket: flowbio-data-lake · us-east-2`},
    {t:900, c:'dim', m:`> Cargando parámetros del yacimiento...`},
    {t:1100,c:'dim', m:`>   K = ${perm} mD  |  μ = ${visc} cP  |  T = ${T}°C`},
    {t:1300,c:'dim', m:`>   Salinidad = ${S.toLocaleString()} ppm`},
    {t:1600,c:'ok',  m:`> ✓ Modelo Power Law: τ = K·γⁿ (Ostwald-de Waele)`},
    {t:1900,c:'dim', m:`> Calculando Factor Skin — van Everdingen-Hurst...`},
    {t:2300,c:'ok',  m:`> ✓ Simulación PIML completada`},
    {t:2600,c:'dim', m:`> Generando análisis ESG + CBAM...`},
    {t:2900,c:'ok',  m:`> ✓ Reporte listo. Cargando dashboard...`},
  ];

  for (let i = 0; i < logs.length; i++) {
    await sleep(i === 0 ? 0 : logs[i].t - logs[i-1].t);
    const d = document.createElement('div');
    d.className = `term-line ${logs[i].c}`;
    d.textContent = logs[i].m;
    box.appendChild(d);
    box.scrollTop = box.scrollHeight;
    const progress = Math.round(((i+1)/logs.length)*100);
    bar.style.width = progress + '%';
    pct.textContent = progress + '%';
  }

  await sleep(400);

  // Calcular
  SIM = piml(T, S, 0.8, perm, visc, bopd, opex, fluid);
  SIM.infra = infra; SIM.basin = basin;
  renderDash();
  go('s-dash');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/* ═══════════════════════════════════════════════════
   RENDERIZAR DASHBOARD
═══════════════════════════════════════════════════ */
function renderDash() {
  const r = SIM;

  // Meta
  const basinNames = {
    ukcs:'UKCS NORTH SEA', mexico:'CUENCA DE BURGOS',
    colombia:'LLANOS ORIENTALES', argentina:'VACA MUERTA'
  };
  document.getElementById('dash-meta').textContent =
    `ACTIVO · ${basinNames[r.basin]||'CAMPO'} · SIMULACIÓN PIML v0.3`;

  // KPIs
  document.getElementById('kpi-extra').textContent = '+' + r.extra.toFixed(1);
  document.getElementById('kpi-extra-pct').textContent = '+' + r.mej.toFixed(1) + '%';
  document.getElementById('kpi-skin').textContent = r.skin.toFixed(2);
  const skinSub = r.skin>15?'DAÑO CRÍTICO':r.skin>8?'DAÑO SEVERO':r.skin>3?'DAÑO MODERADO':'DAÑO BAJO';
  document.getElementById('kpi-skin-sub').textContent = skinSub;
  document.getElementById('kpi-fee').textContent = '$' + fmt(r.fee_month);
  document.getElementById('kpi-opex').textContent = '$' + fmt(r.ahorro_yr);

  // OR
  const setOR = (id, val, ok, warn) => {
    const el = document.getElementById(id);
    el.textContent = val;
    el.className = 'or-val ' + ok;
  };
  setOR('or-temp', r.T < 90 ? '✓ OK ('+r.T+'°C)' : '⚠ '+r.T+'°C', r.T<90?'ok':'warn');
  setOR('or-sal',  r.S < 70000 ? '✓ OK' : '⚠ Alta', r.S<70000?'ok':'warn');
  setOR('or-skin', r.skin>8?'✗ Alto S='+r.skin.toFixed(1):r.skin>3?'⚠ Mod.':'✓ Bajo', r.skin>8?'bad':r.skin>3?'warn':'ok');
  setOR('or-fpi',  r.fpi<0.25?'✓ Bajo':r.fpi<0.5?'⚠ Medio':'✗ Alto', r.fpi<0.25?'ok':r.fpi<0.5?'warn':'bad');
  setOR('or-bio',  r.fluid==='nacmc'?'✓ 100%':'✗ No', r.fluid==='nacmc'?'ok':'bad');
  setOR('or-hse',  r.fluid==='nacmc'?'✓ Cero':'✗ Tóxico', r.fluid==='nacmc'?'ok':'bad');

  // Alertas
  const alerts = [];
  if (r.skin > 8)  alerts.push({c:'bad', t:'Skin Factor crítico', m:`S = ${r.skin.toFixed(2)} — inyección prioritaria`});
  if (r.fpi > 0.5) alerts.push({c:'warn',t:'FPI elevado', m:`Riesgo taponamiento ${r.fpi.toFixed(3)}`});
  if (r.T >= 90)   alerts.push({c:'warn',t:'Temperatura límite', m:`${r.T}°C — Na-CMC en zona marginal`});
  if (r.fluid==='nacmc' && r.mej > 5)
                   alerts.push({c:'ok',  t:'Candidato EOR confirmado', m:`+${r.mej.toFixed(1)}% mejora · Condiciones óptimas`});
  if (alerts.length === 0)
                   alerts.push({c:'ok',  t:'Sistema nominal', m:'Todos los parámetros dentro de rango'});

  const al = document.getElementById('alert-list');
  al.innerHTML = alerts.map(a => `
    <div class="alert-row">
      <div class="alert-dot ${a.c}"></div>
      <div>
        <div class="alert-text">${a.t}</div>
        <div class="alert-meta">${a.m}</div>
      </div>
    </div>`).join('');

  // ROI
  document.getElementById('roi-pct').textContent       = r.roi_pct + '%';
  document.getElementById('roi-fee-gross').textContent  = '$' + fmt(r.fee_month);
  document.getElementById('roi-cost').textContent       = '$' + fmt(r.cost_month);
  document.getElementById('roi-net').textContent        = '$' + fmt(r.net_month);
  document.getElementById('roi-be').textContent         = Math.round(r.be_days) + 'd';

  // Rheo bars
  const fluids = [
    {lbl:'Na-CMC', eta: piml(r.T,r.S,0.8,r.perm,r.visc,r.bopd,r.opex,'nacmc').eta, col:'#00E5A0'},
    {lbl:'HPAM',   eta: piml(r.T,r.S,0.8,r.perm,r.visc,r.bopd,r.opex,'hpam').eta,  col:'#EF4444'},
    {lbl:'Xanthan',eta: 320, col:'#3B82F6'},
  ];
  const maxEta = Math.max(...fluids.map(f=>f.eta));
  document.getElementById('rheo-bars').innerHTML = fluids.map(f => `
    <div class="rheo-bar-row">
      <span class="rheo-lbl">${f.lbl}</span>
      <div class="rheo-track">
        <div class="rheo-fill" style="width:${(f.eta/maxEta*100).toFixed(1)}%;background:${f.col}"></div>
      </div>
      <span class="rheo-val">${Math.round(f.eta)} mPa·s</span>
    </div>`).join('');

  // Gráficas Plotly
  renderProdChart();
  renderRheoChart();
}

function renderProdChart() {
  const r   = SIM;
  const x   = Array.from({length:48},(_,i)=>i);
  const y1  = x.map(i => r.bopd * Math.exp(-0.0055*i));
  const y2  = x.map(i => i<6 ? y1[i] : (r.bopd + r.extra) * Math.exp(-0.0025*i));

  Plotly.newPlot('chart-prod',[
    {x,y:y1, name:'Baseline', type:'scatter',
     line:{color:'#EF4444',dash:'dot',width:2}},
    {x, y:y2, name:'Con Na-CMC FlowBio', type:'scatter',
     line:{color:'#00E5A0',width:3},
     fill:'tonexty', fillcolor:'rgba(0,229,160,0.08)'},
  ],{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
    margin:{l:50,r:10,t:10,b:40},
    showlegend:false,
    font:{family:'DM Mono',color:'#4A6580',size:10},
    xaxis:{gridcolor:'#152335',title:{text:'MESES',font:{size:10}},tickfont:{size:10}},
    yaxis:{gridcolor:'#152335',title:{text:'BBL/DÍA',font:{size:10}},tickfont:{size:10}},
    hovermode:'x unified',
  },{responsive:true,displayModeBar:false});
}

function renderRheoChart() {
  const r = SIM;
  const gamma = Array.from({length:60},(_,i)=>Math.pow(10,-1+i*4/59));
  function viscArr(fluid) {
    const s = piml(r.T,r.S,0.8,r.perm,r.visc,r.bopd,r.opex,fluid);
    return gamma.map(g => s.K * Math.pow(g, s.n-1));
  }
  const vn = viscArr('nacmc');
  const vh = viscArr('hpam');

  Plotly.newPlot('chart-rheo',[
    {x:gamma,y:vn, name:'Na-CMC', type:'scatter', line:{color:'#00E5A0',width:2.5}},
    {x:gamma,y:vh, name:'HPAM',   type:'scatter', line:{color:'#EF4444',width:1.5,dash:'dot'}},
  ],{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
    margin:{l:45,r:5,t:5,b:35},
    showlegend:false,
    font:{family:'DM Mono',color:'#4A6580',size:9},
    xaxis:{type:'log',gridcolor:'#152335',title:{text:'γ (s⁻¹)',font:{size:9}}},
    yaxis:{type:'log',gridcolor:'#152335',title:{text:'η (mPa·s)',font:{size:9}}},
  },{responsive:true,displayModeBar:false});
}

/* ═══════════════════════════════════════════════════
   EXPORTAR
═══════════════════════════════════════════════════ */
function openModal()  { document.getElementById('modal-export').classList.add('active'); }
function closeModal() { document.getElementById('modal-export').classList.remove('active'); }

function exportData(fmt) {
  const r = SIM;
  if (!r.n) { closeModal(); return; }

  if (fmt === 'csv') {
    const csv = [
      'parametro,valor',
      `n_Power_Law,${r.n.toFixed(4)}`,
      `K_consistencia,${r.K.toFixed(2)}`,
      `Factor_Skin,${r.skin.toFixed(3)}`,
      `FPI,${r.fpi.toFixed(4)}`,
      `Barriles_extra_dia,${r.extra.toFixed(2)}`,
      `Mejora_pct,${r.mej.toFixed(2)}`,
      `Fee_mensual_USD,${r.fee_month.toFixed(2)}`,
      `Ahorro_OPEX_anual_USD,${r.ahorro_yr.toFixed(0)}`,
      `ROI_pct,${r.roi_pct}`,
    ].join('\n');
    download('flowbio_piml_resultado.csv', csv, 'text/csv');
  }

  if (fmt === 'json') {
    const j = {
      metadata:{titulo:'FlowBio PIML Result',timestamp:new Date().toISOString()},
      resumen_ejecutivo:{
        skin:r.skin,fpi:r.fpi,extra_bpd:r.extra,
        mejora_pct:r.mej,fee_mensual:r.fee_month,ahorro_anual:r.ahorro_yr,
      },
    };
    download('ultimo_reporte.json', JSON.stringify(j,null,2), 'application/json');
  }

  if (fmt === 'pdf') {
    // Notificación simple (PDF requiere jsPDF en producción)
    alert('PDF disponible en la versión con jsPDF integrado.\nUsa el CSV o JSON por ahora.');
  }

  closeModal();
}

function download(name, data, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([data],{type}));
  a.download = name;
  a.click();
}

function fmt(n) {
  if (n >= 1e6) return (n/1e6).toFixed(2)+'M';
  if (n >= 1e3) return (n/1e3).toFixed(1)+'K';
  return Math.round(n).toString();
}

// Init preview
upd();
</script>
</body>
</html>
"""

components.html(HTML, height=1080, scrolling=False)
