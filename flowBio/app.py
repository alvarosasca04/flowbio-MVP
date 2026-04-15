import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Cloud Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. BYPASS UI STREAMLIT
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. CORE UI (FLUJO SIN RECUADRO DE CARGA + SELECTORES)
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(16, 185, 129, 0.4); transform: translateY(-2px); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        
        /* Selectores Estilo Elite */
        select { 
            background: #080a0d; border: 1px solid var(--border); color: #f3f4f6; 
            padding: 12px; border-radius: 8px; width: 100%; font-size: 11px; outline: none;
            cursor: pointer; transition: 0.3s;
        }
        select:focus { border-color: var(--primary); }
        .label-tech { font-size: 10px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block; }
        
        .hidden { display: none !important; }
        .reveal { animation: revealEffect 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; width: 100%; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; cursor: pointer; }
    </style>
</head>
<body class="min-h-screen">

    <div id="page-landing" class="h-screen w-full flex flex-col justify-center items-center p-10 text-center relative overflow-hidden bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <div class="relative z-10 max-w-5xl space-y-10">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-slate-500 mono text-sm uppercase tracking-[0.5em]">Agentic PIML Reservoir Optimization</p>
            <button onclick="goToStep1()" class="btn-deploy px-14 py-5 rounded-xl tracking-widest text-xs"> 
                INICIALIZAR INSTANCIA CLOUD 
            </button>
        </div>
    </div>

    <div id="step-1" class="hidden max-w-5xl mx-auto space-y-8 py-10 reveal">
        <header class="flex justify-between items-center mb-6">
            <span class="text-xl font-black text-white italic">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div><span class="text-[9px] mono text-blue-400">AWS_READY</span></div>
        </header>

        <div class="text-center space-y-2 mb-8">
            <h2 class="text-3xl font-bold text-white uppercase tracking-tight">Configuración del Activo</h2>
            <p class="text-slate-500 mono text-[10px] uppercase tracking-widest italic">Phase: Digital Twin Synchronization</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass p-8">
                <label class="label-tech"><i data-lucide="beaker" class="inline w-3 h-3 mr-1"></i> Químico EOR Actual</label>
                <select id="chem-select">
                    <option value="">Selecciona el fluido...</option>
                    <option value="HPAM">HPAM (Polímero Tradicional)</option>
                    <option value="Bio">FlowBio S3 (Bio-Polímero)</option>
                    <option value="ASP">ASP (Álcali-Surfactante)</option>
                </select>
            </div>
            <div class="glass p-8">
                <label class="label-tech"><i data-lucide="settings" class="inline w-3 h-3 mr-1"></i> Infraestructura de Bombeo</label>
                <select id="infra-select">
                    <option value="">Selecciona la infraestructura...</option>
                    <option value="ESP">Vertical ESP (Bomba Electrosumergible)</option>
                    <option value="Horizontal">Horizontal Multi-Pad</option>
                    <option value="Smart">Smart Completion (Inyección Selectiva)</option>
                </select>
            </div>
        </div>

        <div class="glass p-8 space-y-6">
            <p class="text-[10px] font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Variables del Yacimiento</p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                    <div class="flex justify-between text-[10px] mono mb-3 text-slate-400"><span>Permeabilidad ($K$)</span><span class="text-emerald-500">450 mD</span></div>
                    <input type="range" min="10" max="2000" value="450">
                </div>
                <div>
                    <div class="flex justify-between text-[10px] mono mb-3 text-slate-400"><span>Viscosidad Crudo</span><span class="text-emerald-500">120 cP</span></div>
                    <input type="range" min="1" max="500" value="120">
                </div>
                <div>
                    <div class="flex justify-between text-[10px] mono mb-3 text-slate-400"><span>Saturación Agua ($S_w$)</span><span class="text-emerald-500">0.35</span></div>
                    <input type="range" min="0" max="1" step="0.01" value="0.35">
                </div>
            </div>
        </div>

        <div class="flex justify-center pt-6">
            <button onclick="runSimulation()" class="btn-deploy px-16 py-5 rounded-xl text-xs tracking-widest"> ⚡ Desplegar Agentes en AWS </button>
        </div>
    </div>

    <div id="step-2" class="hidden max-w-3xl mx-auto py-20">
        <div class="terminal flex flex-col h-[420px] shadow-2xl overflow-hidden">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <div class="flex gap-2 items-center"><i data-lucide="cloud" class="w-3 h-3 text-slate-500"></i><span class="mono text-[10px] text-slate-500 uppercase tracking-widest italic">AWS_COMPUTE_NODE_01</span></div>
                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            </div>
            <div id="terminal-content" class="p-8 flex-1 mono text-[13px] text-emerald-500/80 space-y-4 overflow-y-auto leading-relaxed">
                </div>
        </div>
    </div>

    <div id="step-3" class="hidden space-y-6 reveal p-4">
        <header class="flex justify-between items-center glass px-8 py-4">
            <span class="text-2xl font-black text-white tracking-tighter italic">Flow<span class="text-emerald-500">Bio</span></span>
            <button onclick="location.reload()" class="text-[10px] mono text-slate-600 uppercase">Reiniciar</button>
        </header>

        <div class="glass p-8">
            <h2 class="text-xl font-bold text-white uppercase mb-6 italic tracking-tight">Curva de Declinación vs Optimización (AWS Cloud)</h2>
            <div id="main-plot" class="w-full h-96"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-8 border-l-4 border-emerald-
