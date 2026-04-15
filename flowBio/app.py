import streamlit as st
import streamlit.components.v1 as components

# 1. BOOTSTRAP DE PLATAFORMA
st.set_page_config(
    page_title="FlowBio | Agentic EOR Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. INYECCIÓN DE ESTÉTICA "MINERS-STEALTH"
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        .block-container {padding: 0px; max-width: 100%; height: 100vh;}
        iframe {border: none; width: 100%; height: 100vh;}
    </style>
""", unsafe_allow_html=True)

# 3. CÓDIGO CORE (HTML5 / TAILWIND / PLOTLY / JETBRAINS MONO)
html_content = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .stat-value { font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; }
        .btn-action { background: var(--primary); color: #000; font-weight: 700; transition: all 0.2s; }
        .btn-action:hover { filter: brightness(1.2); transform: translateY(-1px); box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-size: 11px; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
        .hidden { display: none !important; }
    </style>
</head>
<body class="min-h-screen">

    <div id="page-home" class="h-screen w-full flex flex-col justify-center items-center p-8 bg-[#080a0d]">
        <div class="max-w-4xl text-center space-y-8">
            <div class="flex justify-center mb-4">
                <div class="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
                    <i data-lucide="microscope" class="w-12 h-12 text-emerald-500"></i>
                </div>
            </div>
            <h1 class="text-6xl md:text-8xl font-black tracking-tight text-white uppercase">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-400 font-light tracking-wide">Infrastructure for Intelligent Enhanced Oil Recovery</p>
            <div class="pt-8">
                <button onclick="nav('dashboard')" class="btn-action px-10 py-4 rounded-lg tracking-widest text-xs uppercase"> Initialize Command Console </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-screen w-full flex flex-col p-4 space-y-4">
        
        <header class="flex justify-between items-center glass px-6 py-4">
            <div class="flex items-center gap-6">
                <span class="text-xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-4 w-[1px] bg-slate-700"></div>
                <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    <span class="mono text-[10px] text-emerald-500 uppercase font-bold">Agents-Cluster: Online</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button class="px-3 py-1.5 glass text-[10px] mono hover:bg-slate-800 transition-all">SYSTEM_LOGS</button>
                <button onclick="nav('home')" class="px-3 py-1.5 text-[10px] mono text-slate-500 hover:text-white transition-all">TERMINATE</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="glass p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental Production</p>
                <h2 class="stat-value text-3xl font-bold text-emerald-500">+22.5k <span class="text-xs font-normal">bbl</span></h2>
            </div>
            <div class="glass p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Additional NPV</p>
                <h2 class="stat-value text-3xl font-bold text-white">$1.46M <span class="text-xs font-normal">usd</span></h2>
            </div>
            <div class="glass p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Performance Index</p>
                <h2 class="stat-value text-3xl font-bold text-emerald-500">0.94 <span class="text-xs font-normal">PIML</span></h2>
            </div>
            <div class="glass p-5 border-emerald-500/30">
                <p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee (5%)</p>
                <h2 class="stat-value text-3xl font-bold text-white">$73.1k <span class="text-xs font-normal">usd</span></h2>
            </div>
        </div>

        <div class="flex-1 grid grid-cols-12 gap-4 min-h-0">
            <div class="col-span-12 lg:col-span-9 glass p-6 flex flex-col">
                <div class="flex justify-between items-center mb-6">
                    <div class="flex flex-col">
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-300">PIML Recovery Forecast</h3>
                        <span class="text-[10px] text-slate-500 mono">Asset_ID: S3_FIELD_NORTH_SEA_01</span>
                    </div>
                    <div class="flex gap-6 text-[9px] mono text-slate-500">
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span> Status Quo</span>
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> FlowBio EOR</span>
                    </div>
                </div>
                <div id="viz-chart" class="flex-1 w-full"></div>
            </div>

            <div class="col-span-12 lg:col-span-3 terminal flex flex-col">
                <div class="px-4 py-3 border-b border-slate-800 flex justify-between items-center">
                    <span class="mono text-[10px] text-slate-500 uppercase">Agent_Workstream</span>
                </div>
                <div id="term-stream" class="p-4 flex-1 mono text-[10px] text-emerald-500 space-y-1.5 overflow-y-auto">
                    <div class="text-slate-500">[SYSTEM] Initialization authorized.</div>
                    <div>> FETCHING_FROM_LAKE... OK</div>
                    <div>> VALIDATING_DARCY_TENSOR... OK</div>
                    <div class="text-white">> CALCULATING_POLYMERIC_SWEEP_EFFICIENCY...</div>
                    <div class="text-emerald-400">> ROI_PROJECTION_COMPLETE (36m Horizon)</div>
                    <div class="animate-pulse">_</div>
                </div>
                <div class="p-4 bg-emerald-500/5">
                    <button class="w-full py-2.5 btn-action rounded text-[10px] uppercase tracking-tighter">Generate Technical PDF</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function nav(page) {
            document.getElementById('page-home').classList.toggle('hidden', page !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', page !== 'dashboard');
            if(page === 'dashboard') { setTimeout(init, 50); }
        }

        function init() {
            lucide.createIcons();
            const months = Array.from({length: 36}, (_, i) => i + 1);
            const base = months.map(m => 3000 * Math.exp(-0.06 * m));
            const flow = months.map((m, i) => m < 12 ? base[i] : base[i] + 1300 * Math.exp(-0.028 * (m - 12)));

            const data = [
                { x: months, y: base, name: 'Base', type: 'scatter', line: {color: '#f43f5e', width: 1, dash: 'dot'} },
                { x: months, y: flow, name: 'Flow', type: 'scatter', line: {color: '#10b981', width: 3}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)' }
            ];

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };

            Plotly.newPlot('viz-chart', data, layout, {responsive: true, displayModeBar: false});
        }
        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDERIZADO FINAL
components.html(html_content, height=1200, scrolling=False)
