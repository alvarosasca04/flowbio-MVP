import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP PROFESIONAL
st.set_page_config(
    page_title="FlowBio | Intelligent Asset Manager",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. CLEAN UI BYPASS
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL CON SELECTORES DE QUÍMICO E INFRAESTRUCTURA
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        
        /* Selectores Estilo Imagen */
        .custom-select { 
            background: #080a0d; 
            border: 1px solid var(--border); 
            color: #f3f4f6; 
            padding: 10px 15px; 
            border-radius: 8px; 
            width: 100%;
            outline: none;
            appearance: none;
            cursor: pointer;
        }
        .input-label { font-size: 10px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; display: block; }
        
        .search-box { background: #080a0d; border: 1px solid var(--border); transition: 0.3s; }
        .suggestion-card { cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: 0.2s; }
        .suggestion-card:hover { background: rgba(16, 185, 129, 0.15); transform: translateX(5px); }
        .btn-action { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        .reveal { animation: revealEffect 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(15px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
    </style>
</head>
<body class="flex flex-col h-full overflow-hidden">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-10 text-center relative bg-[#080a0d]">
        <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
        <button onclick="nav('dashboard')" class="btn-action mt-8 px-12 py-4 rounded-md tracking-widest text-xs"> Inicializar Centro de Comando </button>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-4 gap-4">
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-8">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="relative w-96">
                    <div class="flex items-center gap-3 search-box px-4 py-2 rounded-lg">
                        <i data-lucide="search" class="w-4 h-4 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscar pozo..." class="bg-transparent text-xs w-full outline-none text-white mono" onfocus="showAllSuggestions()" oninput="filterWells()">
                    </div>
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-2 glass max-h-64 overflow-y-auto z-50 hidden shadow-2xl">
                        <div id="results-list"></div>
                    </div>
                </div>
            </div>
            <button onclick="nav('home')" class="text-[10px] mono text-slate-500 hover:text-white uppercase">Menu</button>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-4 min-h-0">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 glass p-6">
                <div>
                    <label class="input-label">Químico EOR Actual (Baseline)</label>
                    <div class="relative flex items-center">
                        <i data-lucide="beaker" class="absolute left-3 w-4 h-4 text-slate-500"></i>
                        <select id="chem-select" class="custom-select pl-10">
                            <option value="">Selecciona el químico actual...</option>
                            <option value="HPAM">HPAM (Poliacrilamida Parcialmente Hidrolizada)</option>
                            <option value="Xanthan">Goma Xantana</option>
                            <option value="ASP">ASP (Alcali-Surfactante-Polímero)</option>
                            <option value="Water">Solo Agua (Waterflooding)</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="input-label">Infraestructura en Superficie</label>
                    <div class="relative flex items-center">
                        <i data-lucide="settings" class="absolute left-3 w-4 h-4 text-slate-500"></i>
                        <select id="infra-select" class="custom-select pl-10">
                            <option value="">Selecciona la infraestructura...</option>
                            <option value="Skid">Skid de Inyección Modular</option>
                            <option value="Central">Planta de Preparación Centralizada</option>
                            <option value="Automatic">Dosificación Automática en Boca de Pozo</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-4 py-2 border-b border-slate-900 bg-black/40 flex justify-between">
                    <span class="mono text-[9px] text-slate-500 uppercase">Agent_Core_Stream</span>
                    <button onclick="startAgents()" id="run-btn" class="hidden text-emerald-500 font-bold text-[9px] uppercase">▶ Ejecutar Agentes</button>
                </div>
                <div id="term-content" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-1.5 overflow-y-auto">
                    > Configure el químico e infraestructura para habilitar la simulación...
                </div>
            </div>

            <div id="results-view" class="hidden flex flex-col gap-4 h-full overflow-y-auto pb-4">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">Incremental</p><h2 class="mono text-3xl font-bold text-emerald-500">+22,500</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">NPV</p><h2 class="mono text-3xl font-bold text-white">$1.46M</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">Success Fee</p><h2 class="mono text-3xl font-bold text-white">$73,125</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">Incertidumbre</p><h2 class="mono text-3xl font-bold text-slate-600">±2.1%</h2></div>
                </div>
                <div class="glass p-6 h-80">
                    <div id="main-plot" class="w-full h-full"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const DATABASE = [
            { id: "FB-PRD-101", temp: "84°C", pres: "3240 psi" },
            { id: "FB-PRD-102", temp: "89°C", pres: "3100 psi" }
        ];

        function nav(p) {
            document.getElementById('page-home').classList.toggle('hidden', p !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', p !== 'dashboard');
            lucide.createIcons();
        }

        function showAllSuggestions() {
            const res = document.getElementById('search-results');
            res.classList.remove('hidden');
            renderList(DATABASE);
        }

        function renderList(items) {
            const list = document.getElementById('results-list');
            list.innerHTML = items.map(w => `
                <div class="suggestion-card p-4" onclick="selectWell('${w.id}')">
                    <div class="text-xs font-bold text-white mono">${w.id}</div>
                </div>
            `).join('');
        }

        function selectWell(id) {
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('run-btn').classList.remove('hidden');
            document.getElementById('term-content').innerHTML = "> Pozo " + id + " seleccionado. Ajuste la configuración y ejecute agentes.";
        }

        async function startAgents() {
            const chem = document.getElementById('chem-select').value;
            const infra = document.getElementById('infra-select').value;
            if(!chem || !infra) { alert("Por favor seleccione químico e infraestructura"); return; }

            const t = document.getElementById('term-content');
            t.innerHTML = "";
            const msgs = [
                "> Conectando a Data Lake...",
                "> Agente Reología: Analizando viscosidad de " + chem,
                "> Agente Operaciones: Validando compatibilidad con " + infra,
                "> Physics-Informed ML: Ejecutando simulación...",
                "> SISTEMA ACTUALIZADO."
            ];

            for (const m of msgs) {
                const d = document.createElement('div');
                d.textContent = m;
                t.appendChild(d);
                await new Promise(r => setTimeout(r, 600));
            }

            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            renderPlot();
        }

        function renderPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            Plotly.newPlot('main-plot', [
                { x: x, y: x.map(m => 3500 * Math.exp(-0.06 * m)), type: 'scatter', line: {color: '#f43f5e'}, name: 'Base' },
                { x: x, y: x.map((m, i) => m < 12 ? 3500 * Math.exp(-0.06 * m) : 3000 * Math.exp(-0.03 * m)), type: 'scatter', line: {color: '#10b981'}, name: 'FlowBio' }
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f' }, yaxis: { gridcolor: '#1e262f' }
            });
        }
        
        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""
components.html(html_code, height=1200, scrolling=False)
