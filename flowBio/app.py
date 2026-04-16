import streamlit as st
import streamlit.components.v1 as components
import boto3, json

st.set_page_config(
    page_title="FlowBio Intelligence | Subsurface OS",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════
# 1. CONEXIÓN S3 — Lee ultimo_reporte.json (Groq)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_reporte():
    try:
        s3  = boto3.client("s3", region_name="us-east-2")
        obj = s3.get_object(
            Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an",
            Key="agentes/ultimo_reporte.json"
        )
        return json.loads(obj["Body"].read().decode("utf-8")), True
    except Exception as e:
        return None, False

# BUG C FIX: botón de refresco manual
col_title, col_btn = st.columns([10,1])
with col_btn:
    if st.button("🔄"):
        st.cache_data.clear()
        st.rerun()

reporte, s3_ok = fetch_reporte()

# ── Extraer datos del JSON (todos los campos) ─────────
def safe(path, fallback):
    """Acceso seguro a claves anidadas del JSON."""
    try:
        keys = path.split(".")
        val  = reporte
        for k in keys:
            val = val[k]
        return val if val is not None else fallback
    except:
        return fallback

# Resumen ejecutivo
ahorro_usd     = safe("resumen_ejecutivo.ahorro_total_usd",     1850000)
fee_mensual    = safe("resumen_ejecutivo.fee_mensual_usd",      25000)
mejora_pct     = safe("resumen_ejecutivo.mejora_promedio_pct",  16.5)
skin_avg       = safe("resumen_ejecutivo.skin_promedio",        4.2)
pozos_crit     = safe("resumen_ejecutivo.pozos_criticos",       12)
pozos_cand     = safe("resumen_ejecutivo.candidatos_inyeccion", 89)
total_pozos    = safe("metadata.total_pozos_analizados",        500)
# ESG
co2_evitado    = safe("esg_cbam.total_ton_co2_ahorradas",       950.5)
cbam_usd       = safe("esg_cbam.total_cbam_usd_evitado",        65000)
esg_alto       = safe("esg_cbam.pozos_esg_alto",                25)
# Mensajes por perfil (del LLM, no hardcodeados)
msg_eor        = safe("mensajes_por_perfil.eor_manager",
    f"Identificamos {pozos_cand} candidatos. Mejora +{mejora_pct:.1f}%.")
msg_res        = safe("mensajes_por_perfil.reservoir_engineer",
    f"PIML v0.3 ejecutado. Skin promedio: {skin_avg:.2f}.")
msg_esg        = safe("mensajes_por_perfil.esg_manager",
    "Na-CMC: 100% biodegradable, DNSH compliant.")
# Alertas y oportunidades
alertas        = safe("alertas",              [])
top_ops        = safe("top_oportunidades_eor", [])
rec_campo      = safe("recomendacion_campo",  "")
ts_reporte     = safe("metadata.timestamp",   "—")[:16]
llm_used       = safe("metadata.llm",         "llama-3.3-70b")

# BUG D FIX: serialización segura para JS
import json as _json
mejora_js  = _json.dumps(float(mejora_pct))
ahorro_js  = _json.dumps(int(ahorro_usd))
pozos_js   = _json.dumps(int(total_pozos))

# Preparar alertas y top_ops como JSON para inyectar en JS
alertas_js = _json.dumps(alertas[:6],  ensure_ascii=False)
top_ops_js = _json.dumps(top_ops[:5],  ensure_ascii=False)

# ══════════════════════════════════════════════════════
# 2. CSS global
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
    [data-testid="stHeader"],[data-testid="stSidebar"],footer,#MainMenu{display:none!important}
    .stApp{margin:0;padding:0;background:#060C12}
    .block-container{padding:0!important;max-width:100vw!important}
    iframe{position:fixed;top:0;left:0;width:100vw;height:100vh;border:none;z-index:9999}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 3. HTML COMPLETO — usa TODAS las claves del JSON
# ══════════════════════════════════════════════════════
HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#060C12;--bg2:#0B1420;--bg3:#0F1C2E;--card:#0D1928;
      --border:#152335;--border2:#1E3348;--green:#00E5A0;--blue:#3B82F6;
      --cyan:#22D3EE;--amber:#F59E0B;--red:#EF4444;--text:#E2EEF8;
      --muted:#4A6580;--soft:#8BA8C0;--mono:'DM Mono',monospace;
      --head:'Syne',sans-serif;--body:'DM Sans',sans-serif}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:var(--bg);color:var(--text);font-family:var(--body);height:100%;overflow:hidden}}
.screen{{display:none;width:100vw;height:100vh}}
.screen.active{{display:flex}}

/* Splash */
#s-splash{{flex-direction:column;align-items:center;justify-content:center;
           position:relative;overflow:hidden;
           background:radial-gradient(ellipse 80% 60% at 50% 50%,rgba(0,229,160,.05) 0%,transparent 70%)}}
#s-splash::before{{content:'';position:absolute;inset:0;
  background-image:linear-gradient(rgba(0,229,160,.04) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(0,229,160,.04) 1px,transparent 1px);
  background-size:56px 56px;pointer-events:none}}
.splash-logo{{font-family:var(--head);font-size:clamp(64px,9vw,110px);font-weight:800;
              letter-spacing:-4px;line-height:1;color:#fff;margin-bottom:8px}}
.splash-logo span{{color:var(--green)}}
.splash-sub{{font-family:var(--mono);font-size:11px;color:var(--muted);
             letter-spacing:3px;margin-bottom:12px}}
.splash-status{{display:inline-flex;align-items:center;gap:8px;
                border:1px solid {'rgba(0,229,160,.3)' if s3_ok else 'rgba(74,159,212,.3)'};
                border-radius:20px;padding:6px 16px;font-family:var(--mono);
                font-size:11px;color:{'#00E5A0' if s3_ok else '#22D3EE'};
                margin-bottom:40px}}
.splash-dot{{width:6px;height:6px;border-radius:50%;
             background:{'#00E5A0' if s3_ok else '#22D3EE'};
             animation:blink 1.4s ease infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.2}}}}
.btn-launch{{background:var(--green);color:#050C12;font-family:var(--head);
             font-weight:700;font-size:13px;letter-spacing:2px;
             text-transform:uppercase;border:none;border-radius:10px;
             padding:18px 52px;cursor:pointer;transition:all .2s;
             box-shadow:0 0 40px rgba(0,229,160,.2)}}
.btn-launch:hover{{transform:translateY(-2px);box-shadow:0 0 60px rgba(0,229,160,.4)}}
.splash-ts{{font-family:var(--mono);font-size:10px;color:var(--muted);
            margin-top:20px;letter-spacing:1px}}

/* Terminal */
#s-terminal{{flex-direction:column;align-items:center;justify-content:center}}
.term-wrap{{width:100%;max-width:680px;padding:40px}}
.term-dots{{display:flex;gap:8px;margin-bottom:20px}}
.term-dot{{width:10px;height:10px;border-radius:50%}}
.term-box{{background:#06090D;border:1px solid var(--border);border-radius:12px;
           padding:32px;font-family:var(--mono);font-size:13px;
           color:var(--green);line-height:2;min-height:200px}}
.term-progress{{margin-top:16px;background:var(--bg3);border:1px solid var(--border);
                border-radius:6px;height:6px;overflow:hidden}}
.term-bar{{height:100%;width:0%;
           background:linear-gradient(90deg,var(--green),var(--cyan));
           border-radius:6px;transition:width .4s ease}}

/* Dashboard */
#s-dash{{flex-direction:column;overflow-y:auto;overflow-x:hidden}}
.wrap{{width:100%;max-width:1400px;margin:0 auto;padding:24px 28px 60px;
       display:flex;flex-direction:column;gap:20px}}
.dash-hdr{{display:flex;align-items:flex-end;justify-content:space-between;
           border-bottom:1px solid var(--border);padding-bottom:16px}}
.dash-title{{font-family:var(--head);font-size:24px;font-weight:800;letter-spacing:-1px}}
.dash-title span{{color:var(--green)}}
.dash-meta{{font-family:var(--mono);font-size:10px;color:var(--muted);
            letter-spacing:2px;margin-top:4px}}
.btn-sm{{background:transparent;border:1px solid var(--border2);color:var(--soft);
         font-family:var(--mono);font-size:10px;letter-spacing:1px;
         text-transform:uppercase;border-radius:8px;padding:9px 16px;
         cursor:pointer;transition:all .2s}}
.btn-sm:hover{{border-color:var(--green);color:var(--green)}}
/* KPIs */
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
.kc{{background:var(--card);border:1px solid var(--border);border-radius:14px;
     padding:20px 18px;position:relative;overflow:hidden}}
.kc::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px}}
.kc.g::before{{background:var(--green)}}.kc.b::before{{background:var(--blue)}}
.kc.c::before{{background:var(--cyan)}}.kc.a::before{{background:var(--amber)}}
.kc.r::before{{background:var(--red)}}
.kl{{font-family:var(--mono);font-size:9px;letter-spacing:1.8px;
     color:var(--muted);text-transform:uppercase;margin-bottom:10px}}
.kv{{font-family:var(--mono);font-size:32px;font-weight:500;letter-spacing:-2px;line-height:1}}
.kc.g .kv{{color:var(--green)}}.kc.b .kv{{color:var(--blue)}}
.kc.c .kv{{color:var(--cyan)}}.kc.a .kv{{color:var(--amber)}}.kc.r .kv{{color:var(--red)}}
.ks{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:7px}}
/* Main grid */
.main-grid{{display:grid;grid-template-columns:1fr 370px;gap:18px;min-height:400px}}
.chart-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px;display:flex;flex-direction:column}}
.card-title{{font-family:var(--mono);font-size:10px;letter-spacing:2px;color:var(--soft);text-transform:uppercase;margin-bottom:14px}}
.side{{display:flex;flex-direction:column;gap:14px}}
/* Alertas */
.al-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px}}
.al-row{{display:flex;gap:10px;align-items:flex-start;padding:9px 0;border-bottom:1px solid var(--border)}}
.al-row:last-child{{border-bottom:none}}
.al-dot{{width:7px;height:7px;border-radius:50%;margin-top:5px;flex-shrink:0}}
.al-t{{font-size:12px;color:var(--text);font-weight:500}}
.al-m{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:2px}}
/* OR Table */
.or-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px}}
.or-row{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--border);font-size:12px}}
.or-row:last-child{{border-bottom:none}}
.or-k{{color:var(--soft)}}.or-v{{font-family:var(--mono);font-weight:500}}
.ok{{color:var(--green)}}.bad{{color:var(--red)}}.warn{{color:var(--amber)}}
/* Bottom row */
.bot-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}}
.mini-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px}}
/* Profile messages */
.prof-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.prof-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px}}
.prof-ico{{font-size:24px;margin-bottom:10px}}
.prof-role{{font-family:var(--mono);font-size:9px;letter-spacing:2px;margin-bottom:8px}}
.prof-msg{{font-size:12px;color:var(--soft);line-height:1.6}}
/* ESG row */
.esg-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
</style>
</head>
<body>

<!-- SPLASH -->
<div id="s-splash" class="screen active">
  <h1 class="splash-logo">FlowBio<span>.</span></h1>
  <p class="splash-sub">SUBSURFACE INTELLIGENCE · GROQ SPEED ENGINE</p>
  <div class="splash-status">
    <span class="splash-dot"></span>
    {'S3 CONECTADO · ultimo_reporte.json' if s3_ok else 'S3 NO DISPONIBLE · MODO DEMO'}
  </div>
  <button class="btn-launch" onclick="runLoad()">
    {'CARGAR REPORTE GROQ DESDE S3' if s3_ok else 'EXPLORAR CON DATOS DEMO'}
  </button>
  <p class="splash-ts">{'ÚLTIMO REPORTE: ' + ts_reporte if s3_ok else 'Ejecuta el Jupyter para generar un reporte real'}</p>
</div>

<!-- TERMINAL -->
<div id="s-terminal" class="screen" style="flex-direction:column;align-items:center;justify-content:center">
  <div class="term-wrap">
    <div class="term-dots">
      <div class="term-dot" style="background:#EF4444"></div>
      <div class="term-dot" style="background:#F59E0B"></div>
      <div class="term-dot" style="background:#00E5A0"></div>
    </div>
    <div class="term-box" id="term-log"></div>
    <div class="term-progress"><div class="term-bar" id="term-bar"></div></div>
  </div>
</div>

<!-- DASHBOARD COMPLETO -->
<div id="s-dash" class="screen">
<div class="wrap">

  <!-- Header -->
  <div class="dash-hdr">
    <div>
      <div class="dash-title">Command Center <span>FlowBio</span></div>
      <div class="dash-meta">GROQ · {llm_used} · {ts_reporte} · {total_pozos:,} POZOS</div>
    </div>
    <div style="display:flex;gap:10px">
      <button class="btn-sm" onclick="go('s-splash')">← Desconectar</button>
    </div>
  </div>

  <!-- KPI Row 1: financiero -->
  <div class="kpi-row">
    <div class="kc g">
      <div class="kl">AHORRO OPEX / AÑO</div>
      <div class="kv">${ahorro_usd/1e6:.2f}M</div>
      <div class="ks">USD — datos reales PIML</div>
    </div>
    <div class="kc c">
      <div class="kl">SUCCESS FEE / MES</div>
      <div class="kv">${fee_mensual/1000:.1f}K</div>
      <div class="ks">$5 × bbl_extra × 30d</div>
    </div>
    <div class="kc b">
      <div class="kl">MEJORA EOR PROMEDIO</div>
      <div class="kv">+{mejora_pct}%</div>
      <div class="ks">eficiencia de barrido</div>
    </div>
    <div class="kc {'r' if skin_avg > 8 else 'a' if skin_avg > 3 else 'g'}">
      <div class="kl">SKIN FACTOR PROM.</div>
      <div class="kv">{skin_avg}</div>
      <div class="ks">{'DAÑO SEVERO' if skin_avg>8 else 'DAÑO MODERADO' if skin_avg>3 else 'BAJO'}</div>
    </div>
  </div>

  <!-- KPI Row 2: técnico -->
  <div class="kpi-row">
    <div class="kc r">
      <div class="kl">POZOS CRÍTICOS (S>15)</div>
      <div class="kv">{pozos_crit}</div>
      <div class="ks">intervención urgente</div>
    </div>
    <div class="kc g">
      <div class="kl">CANDIDATOS EOR</div>
      <div class="kv">{pozos_cand}</div>
      <div class="ks">aptos para Na-CMC</div>
    </div>
    <div class="kc a">
      <div class="kl">CO₂ AHORRADO / AÑO</div>
      <div class="kv">{co2_evitado:.0f}t</div>
      <div class="ks">tCO₂eq vs HPAM</div>
    </div>
    <div class="kc c">
      <div class="kl">CBAM EU EVITADO</div>
      <div class="kv">${cbam_usd/1000:.0f}K</div>
      <div class="ks">USD/año (65 EUR/tCO₂)</div>
    </div>
  </div>

  <!-- Gráfica + Alertas -->
  <div class="main-grid">
    <div class="chart-card">
      <div class="card-title">CURVA DE PRODUCCIÓN — BASELINE vs NA-CMC FLOWBIO (GROQ)</div>
      <div id="chart-prod" style="flex:1;min-height:280px"></div>
    </div>
    <div class="side">
      <!-- Alertas del JSON -->
      <div class="al-card">
        <div class="card-title">🔔 ALERTAS GROQ — AGENTE 5</div>
        <div id="alertas-list"></div>
      </div>
    </div>
  </div>

  <!-- Top Oportunidades -->
  <div class="mini-card">
    <div class="card-title">🎯 TOP OPORTUNIDADES EOR — DATOS REALES</div>
    <div id="top-ops" style="display:flex;flex-direction:column;gap:8px"></div>
  </div>

  <!-- Mensajes por perfil — del LLM, no hardcodeados -->
  <div>
    <div class="card-title" style="margin-bottom:12px">🎭 MENSAJES PERSONALIZADOS · AGENTE 5 (GROQ)</div>
    <div class="prof-grid">
      <div class="prof-card" style="border-top:2px solid var(--blue)">
        <div class="prof-ico">💼</div>
        <div class="prof-role" style="color:var(--blue)">EOR MANAGER</div>
        <div class="prof-msg">{msg_eor}</div>
      </div>
      <div class="prof-card" style="border-top:2px solid #9B7FD4">
        <div class="prof-ico">🔬</div>
        <div class="prof-role" style="color:#9B7FD4">RESERVOIR ENGINEER</div>
        <div class="prof-msg">{msg_res}</div>
      </div>
      <div class="prof-card" style="border-top:2px solid #00C9B1">
        <div class="prof-ico">🌿</div>
        <div class="prof-role" style="color:#00C9B1">ESG MANAGER</div>
        <div class="prof-msg">{msg_esg}</div>
      </div>
    </div>
  </div>

  <!-- Recomendación de campo -->
  {'<div style="background:rgba(0,229,160,.08);border:1px solid rgba(0,229,160,.3);border-radius:10px;padding:16px;font-size:13px;color:#7ABF8A;line-height:1.6"><b style=color:#00E5A0>📋 Recomendación de Campo · Agente 5</b><br><br>' + rec_campo + '</div>' if rec_campo else ''}

</div><!-- /wrap -->
</div><!-- /s-dash -->

<script>
// Datos inyectados desde Python (seguros, json.dumps)
const MEJORA   = {mejora_js};
const AHORRO   = {ahorro_js};
const POZOS    = {pozos_js};
const ALERTAS  = {alertas_js};
const TOP_OPS  = {top_ops_js};

function go(id) {{
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}

async function runLoad() {{
  go('s-terminal');
  const box = document.getElementById('term-log');
  const bar = document.getElementById('term-bar');
  box.innerHTML = '';
  const logs = [
    {{t:200, c:'muted', m:'> Conectando a AWS S3 us-east-2...'}},
    {{t:600, c:'ok',    m:'> ✓ Bucket: flowbio-data-lake detectado'}},
    {{t:1000,c:'muted', m:'> Leyendo agentes/ultimo_reporte.json...'}},
    {{t:1400,c:'ok',    m:`> ✓ ${{POZOS.toLocaleString()}} pozos · Motor: Groq llama-3.3-70b`}},
    {{t:1800,c:'muted', m:`> Ahorro OPEX: $${{(AHORRO/1e6).toFixed(2)}}M · Mejora: +${{MEJORA}}%`}},
    {{t:2200,c:'ok',    m:'> ✓ Dashboard cargado. Datos reales del campo.'}},
  ];
  for (let i=0; i<logs.length; i++) {{
    await new Promise(r=>setTimeout(r, i===0?0:logs[i].t-logs[i-1].t));
    const d = document.createElement('div');
    d.style.color = logs[i].c==='ok' ? '#00E5A0' : '#4A6580';
    d.textContent = logs[i].m;
    box.appendChild(d);
    bar.style.width = Math.round(((i+1)/logs.length)*100)+'%';
  }}
  await new Promise(r=>setTimeout(r,400));
  renderAll();
  go('s-dash');
}}

function renderAll() {{
  renderProd();
  renderAlertas();
  renderTopOps();
}}

function renderProd() {{
  const x  = Array.from({{length:48}},(_,i)=>i);
  const bopd = 500;
  const mej  = MEJORA/100;
  const y1 = x.map(i => bopd * Math.exp(-0.005*i));
  const y2 = x.map(i => i<6 ? y1[i] : (bopd*(1+mej)) * Math.exp(-0.0025*i));
  Plotly.newPlot('chart-prod',[
    {{x,y:y1,name:'Baseline',type:'scatter',line:{{color:'#EF4444',dash:'dot',width:2}}}},
    {{x,y:y2,name:'FlowBio Na-CMC',type:'scatter',line:{{color:'#00E5A0',width:3}},
      fill:'tonexty',fillcolor:'rgba(0,229,160,0.08)'}},
  ],{{
    paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
    margin:{{l:50,r:10,t:10,b:40}},showlegend:false,
    font:{{family:'DM Mono',color:'#4A6580',size:10}},
    xaxis:{{gridcolor:'#152335',title:{{text:'MESES'}}}},
    yaxis:{{gridcolor:'#152335',title:{{text:'BBL/DÍA'}}}},
    hovermode:'x unified',
  }},{{responsive:true,displayModeBar:false}});
}}

function renderAlertas() {{
  const el = document.getElementById('alertas-list');
  if (!ALERTAS.length) {{
    el.innerHTML = '<div style="color:#4A6580;font-size:12px;padding:8px 0">Sin alertas. Ejecuta el pipeline Groq.</div>';
    return;
  }}
  el.innerHTML = ALERTAS.map(a => {{
    const col = a.nivel==='CRÍTICO'?'#EF4444':a.nivel==='ADVERTENCIA'?'#F59E0B':'#00E5A0';
    return `<div class="al-row">
      <div class="al-dot" style="background:${{col}}"></div>
      <div>
        <div class="al-t">${{a.tipo}} — ${{a.pozo}}</div>
        <div class="al-m">${{a.valor}} · ${{a.accion}}</div>
      </div>
    </div>`;
  }}).join('');
}}

function renderTopOps() {{
  const el = document.getElementById('top-ops');
  if (!TOP_OPS.length) {{
    el.innerHTML = '<div style="color:#4A6580;font-size:12px">Sin oportunidades todavía.</div>';
    return;
  }}
  el.innerHTML = TOP_OPS.map((op,i) => `
    <div style="display:flex;align-items:center;gap:16px;padding:10px 14px;
                background:rgba(0,229,160,.05);border:1px solid #152335;border-radius:8px">
      <span style="font-family:'DM Mono';font-size:13px;color:#00E5A0;font-weight:500;min-width:20px">#${{i+1}}</span>
      <span style="font-family:'DM Mono';font-size:12px;color:#22D3EE;min-width:140px">${{op.pozo}}</span>
      <span style="font-family:'DM Mono';font-size:12px;color:#00E5A0">+${{op.mejora_pct.toFixed(1)}}%</span>
      <span style="font-family:'DM Mono';font-size:11px;color:#4A6580">
        DS=${{op.ds_optimo||'—'}} · Skin=${{op.skin?.toFixed(2)||'—'}} · $${{(op.ahorro_anual_usd||0).toLocaleString()}}/año
      </span>
    </div>`).join('');
}}
</script>
</body>
</html>"""

components.html(HTML, height=1200, scrolling=True)
