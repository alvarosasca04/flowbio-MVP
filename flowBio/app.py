import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PODER
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. BYPASS DE INTERFAZ STREAMLIT
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. CORE UI (LANDING + MAPA CLUSTERS + AGENTES)
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
    
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        
        /* Estilo Mapa */
        #map { height: 350px; width: 100%; border-radius: 12px; border: 1px solid var(--border); }
        
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; }
        .btn-deploy:hover { filter: brightness(1.2); transform: translateY(-2px); box-shadow: 0 0 30px rgba(16, 185, 129, 0.3); }
        
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        
        /* Cluster Customization */
        .marker-cluster-small { background-color: rgba(16, 185, 129, 0.6); }
        .marker-cluster-small div { background-color: rgba(16, 185, 129, 1); color: black; font-weight: bold; }
        
        .reveal { animation: revealEffect 0.6s ease-out forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        
        .hidden { display: none !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col h-full overflow-hidden">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-10 text-center relative bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 40px 40px;"></div>
        
        <div class="relative z-10 max-w-5xl space-y-8">
            <div class="flex justify-center mb-6">
                <div class="p-4 bg-emerald-500/10 rounded-3xl border border-emerald-500/20">
                    <i data-lucide="microscope" class="w-12 h-12 text-emerald-500"></i>
                </div>
            </div>
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mt-12">
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-3">01. Optimización Financiera</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">Modelo <b>Success Fee</b> basado en producción incremental real. Reducción de OPEX mediante dosificación autónoma.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-3">02. Ingeniería de Fondo</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">Simulación de fluidos no-newtonianos y reología avanzada integrada con motores de física <b>PIML</b>.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-3">03. Metrología Certificada</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">Validación de incertidumbre de medición ±2% bajo estándares <b>ISO-17025</b> para reportes auditables.</p>
                </div>
            </div>

            <div class="pt-8">
                <button onclick="nav('dashboard')" class="btn-deploy px-14 py-5 rounded-xl tracking-widest text-xs"> 
                    INICIALIZAR CONSOLA DE COMANDO 
                </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-4 gap-4 overflow-hidden">
        <header class="flex justify-between items-center glass px-8 py-5">
            <span class="text-2xl font-black text-white uppercase tracking-tighter italic">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="flex gap-4">
                <button onclick="nav('home')" class="text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">← Cerrar Sesión</button>
                <button onclick="startAgents()" id="run-btn" class="hidden btn-deploy px-8 py-2.5 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Agentes </button>
            </div>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-4 min-h-0 overflow-y-auto pr-2">
            
            <div class="glass p-2">
                <div class="flex justify-between px-4 py-2 border-b border-white/5 mb-2">
                    <span class="text-[10px] text-slate-500 uppercase mono tracking-widest">Well-Clusters: North Sea UKCS</span>
                    <span class="text-[10px] text-emerald-500 mono animate-pulse">SISTEMA GEOESPACIAL ACTIVO</span>
                </div>
                <div id="map"></div>
            </div>

            <div id="meta-panel" class="hidden grid grid-cols-5 gap-4 reveal">
                <div class="glass p-4 border-l-2 border-emerald-500"><p class="text-[8px] text-slate-500 uppercase mono">Well_ID</p><p id="v-id" class="mono text-emerald-500 text-[11px] font-bold">--</p></div>
                <div class="glass p-4 border-l-2 border-emerald-500"><p class="text-[8px] text-slate-500 uppercase mono">Infraestructura</p><p id="v-infra" class="mono text-white text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Químico Sugerido</p><p id="v-chem" class="mono text-white text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Temp. Reservoir</p><p id="v-temp" class="mono text-white text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Presión Reservoir</p><p id="v-pres" class="mono text-white text-[11px]">--</p></div>
            </div>

            <div id="terminal-view" class="glass terminal p-6 mono text-[12px] text-emerald-500/80 overflow-y-auto leading-relaxed h-32">
                <div id="term-content">> Consola inicializada. Seleccione un cluster o activo en el mapa para cargar parámetros físicos...</div>
            </div>

            <div id="results-view" class="hidden flex flex-col gap-4 pb-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 reveal">
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental Proyectado</p><h2 class="mono text-4
