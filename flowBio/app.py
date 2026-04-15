import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE ALTA PRIORIDAD (ELIMINA MÁRGENES DE STREAMLIT)
st.set_page_config(
    page_title="FlowBio | Asset Command Center",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE UI: PANTALLA COMPLETA Y ESTÉTICA MINERSIA
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (LANDING + BUSCADOR TÉCNICO + AGENTES)
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
        
        /* Buscador Tipo Catálogo */
        .search-box { background: #080a0d; border: 1px solid var(--border); transition: 0.2s; }
        .search-box:focus-within { border-color: var(--primary); box-shadow: 0 0 15px rgba(16, 185, 129, 0.15); }
        .well-card { cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: 0.2s; }
        .well-card:hover { background: rgba(16, 185, 129, 0.1); transform: translateX(4px); }
        
        .btn-run { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-run:hover { filter: brightness(1.2); box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); }
        
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 6px; font-family: 'JetBrains Mono'; }
        .reveal { animation: revealEffect 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(15px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
        .hidden { display: none !important; }
    </style>
</head>
<body class="flex flex-col h-full overflow-hidden">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-10 text-center relative bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <div class="relative z-10 max-w-5xl space-y-10">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">01. Optimización OPEX</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light text-justify">Reducción drástica de costes mediante dosificación inteligente y modelo <b>Success Fee</b> basado en producción real.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">02. Infraestructura EOR</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light text-justify">Análisis de completación y selección de químicos (PAM/HPAM) mediante motores de física informada <b>PIML</b>.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">03. Metrología Avanzada</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light text-justify">Validación de incertidumbre de medición ±2% según normativas <b>ISO-17025</b> para reportes auditables.</p>
                </div>
            </div>

            <button onclick="nav('dashboard')" class="btn-run px-14 py-4 rounded-md tracking-widest text-xs"> Inicializar Consola de Comando </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-4 gap-4">
        
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-8">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                
                <div class="relative w-96">
                    <div class="flex items-center gap-3 search-box px-4 py-2 rounded">
                        <i data-lucide="search" class="w-4 h-4 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscar ID de Pozo en Repositorio..." 
                               class="bg-transparent text-xs w-full outline-none text-white mono uppercase" 
                               onfocus="showCatalogue()" oninput="filterWells()">
                    </div>
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-1 glass max-h-64 overflow-y-auto z-50 hidden shadow-2xl">
                        </div>
                </div>
            </div>
            
            <div class="flex gap-4">
                <button onclick="nav('home')" class="text-[10px] mono text-slate-600 hover:text-white transition-all uppercase">Reiniciar Sesión</button>
                <button onclick="startAgents()" id="run-btn" class="hidden btn-run px-8 py-2 rounded text-[10px] tracking-tighter"> ⚡ Desplegar Agentes </button>
            </div>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-4 min-h-0">
            
            <div id="meta-panel" class="hidden grid grid-cols-4 gap-4 reveal">
                <div class="glass p-4 border-l-2 border-emerald-500">
                    <p class="text-[8px] text-slate-500 uppercase mono mb-1">Tipo de Infraestructura</p>
                    <p id="v-infra" class="mono text-white text-[11px] font-bold italic">--</p>
                </div>
                <div class="glass p-4 border-l-2 border-emerald-500">
                    <p class="text-[8px] text-slate-500 uppercase mono mb-1">Solución Química (IA Sugerida)</p>
                    <p id="v-chem" class="mono text-white text-[11px] font-bold italic">--</p>
                </div>
                <div class="glass p-4">
                    <p class="text-
