import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. BYPASS UI (PANTALLA COMPLETA)
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (RESULTADOS REDISEÑADOS)
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background-color: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; height: 100vh; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 16px; }
        .btn-main { background: var(--primary); color: #000; font-weight: 900; text-transform: uppercase; border-radius: 12px; cursor: pointer; border: none; transition: 0.2s; }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
        .hidden { display: none !important; }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; color: #10b981; }
        
        /* Efecto Glow para KPIs */
        .kpi-card { border-top: 4px solid var(--primary); background: linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, rgba(20, 26, 33, 1) 100%); }
        .kpi-value { letter-spacing: -2px; }
        
        input[type=range] { width: 100%; accent-color: #10b981; }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 bg-[#080a0d]">
        <h1 class="text-7xl md:text-9xl font-black text-white italic mb-12 tracking-tighter uppercase">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
        <button id="btn-start" class="btn-main px-20 py-6 text-sm tracking-widest shadow-2xl">INICIALIZAR INSTANCIA CLOUD</button>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-6xl mx-auto space-y-8 h-screen justify-center">
        <h2 class="text-4xl font-black text-white uppercase italic tracking-tighter">Digital Twin Configuration</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="glass p-8 space-y-6">
                <div><label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2 tracking-widest">EOR Solution</label><select id="chem-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none"><option value="HPAM Tradicional">HPAM Polymer</option><option value="FlowBio S3">FlowBio S3 Bio-System</option></select></div>
                <div><label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2 tracking-widest">Pump Infrastructure</label><select id="infra-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none"><option value="Vertical ESP">Vertical ESP</option><option value="Horizontal Pad">Horizontal Multi-Pad</option></select></div>
            </div>
            <div class="glass p-8 space-y-8">
                <div><div class="flex justify-between text-[10px] mb-2 font-bold"><span>Reservoir Permeability (mD)</span><span id="k-label" class="text-emerald-500">450</span></div><input type="range" id="k-input" min="50" max="1500" value="450"></div>
                <div><div class="flex justify-between text-[10px] mb-2 font-bold"><span>Fluid Viscosity (cP)</span><span id="v-label" class="text-emerald-500">120</span></div><input type="range" id="v-input" min="10" max="500" value="120"></div>
            </div>
        </div>
        <div class="flex justify-center"><button id="btn-run" class="btn-main px-16 py-5 text-xs tracking-widest">⚡ Run Cloud Simulation</button></div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen max-w-4xl mx-auto p-10">
        <div class="terminal flex-1 p-10 text-sm leading-relaxed overflow-y-auto" id="log-box"></div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6 h-screen overflow-y-auto pb-20">
        <header class="flex justify-between items-end border-b border-white/5 pb-4">
            <div>
                <h1 class="text-3xl font-black italic tracking-tighter">FLOW<span class="text-emerald-500">BIO</span> DASHBOARD</h1>
                <p class="text-[10px] mono text-slate-500 uppercase tracking-[0.3em]">Advanced Recovery & NPV Analytics</p>
            </div>
            <div class="flex gap-4">
                <button id="btn-back" class="px-4 py-2 border border-white/10 rounded text-[9px] font-bold text-slate-400 hover:text-white transition-all uppercase">← Adjust Parameters</button>
                <button class="bg-emerald-500 text-black px-6 py-2 rounded font-black text-[9px] uppercase">Export Report</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass kpi-card p-8">
                <div class="flex justify-between items-start mb-4">
                    <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Incremental Recovery</p>
                    <span class="text-[8px] bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded">ESTIMATED P50</span>
                </div>
                <h3 id="res-extra" class="kpi-value text-6xl font-black text-emerald-500 tracking-tighter">--</h3>
                <p class="text-[10px] text-slate-600 mt-2 mono">Total barrels above baseline</p>
            </div>

            <div class="glass kpi-card p-8" style="border-top-color: white;">
                <div class="flex justify-between items-start mb-4">
                    <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Asset NPV Impact</p>
                    <span class="text-[8px] bg-white/10 text-white px-2 py-1 rounded">USD 2026</span>
                </div>
                <h3 id="res-npv" class="kpi-value text-6xl font-black text-white tracking-tighter">--</h3>
                <p class="text-[10px] text-slate-600 mt-2 mono">Net Present Value Generation</p>
            </div>

            <div class="glass kpi-card p-8" style="border-top-color: #3b82f6;">
                <div class="flex justify-between items-start mb-4">
                    <p class="text-[10px] text-blue-400 font-bold uppercase tracking-widest">Performance Fee</p>
                    <span class="text-[8px] bg-blue-500/10 text-blue-400 px-2 py-1 rounded">SUCCESS BASED</span>
                </div>
                <h3 id="res-fee" class="kpi-value text-6xl font-black text-white tracking-tighter">--</h3>
                <p class="text-[10px] text-slate-600 mt-2 mono">Payable upon extraction</p>
            </div>
        </div>

        <div class="glass p-8">
            <div class="flex justify-between items-center mb-8">
                <div>
                    <h4 class="text-xs font-bold uppercase text-white">Production Forecasting</h4>
                    <p class="text-[10px] text-slate-500 mono">PIML Simulation vs Status Quo Declinación</p>
                </div>
                <div class="flex gap-8 text-[9px] font-black mono">
                    <div class="flex items-center gap-2"><div class="w-3 h-0.5 bg-rose-500"></div><span class="text-rose-500">STATUS QUO</span></div>
                    <div class="flex items-center gap-2"><div class="w-3 h-0.5 bg-emerald-500"></div>
