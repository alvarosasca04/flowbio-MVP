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
