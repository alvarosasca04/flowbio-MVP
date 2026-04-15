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

# 3. INTERFAZ INTEGRAL CON CATÁLOGO DINÁMICO
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
        
        /* Buscador Mejorado */
        .search-box { background: #080a0d; border: 1px solid var(--border); transition: 0.3s; }
        .search-box:focus-within { border-color: var(--primary); background: #0c1218; box-shadow: 0 0 20px rgba(16, 185, 129, 0.1); }
        
        /* Dropdown de Sugerencias */
        .suggestion-card { cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: 0.2s; }
        .suggestion-card:hover { background: rgba(16, 185, 129, 0.15); transform: translateX(5px); }
        .tag { font-size: 8px; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-weight: bold; }
        .tag-active { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        
        .btn-action { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-action:hover { filter: brightness(1.2); transform: translateY(-1px); }
        
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
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
        <div class="relative z-10 max-w-4xl space-y-8">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-400 font-light max-w-2xl mx-auto">Soberanía de Datos y Optimización Agéntica de Hidrocarburos.</p>
            <div class="pt-8 flex gap-4 justify-center items-center">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                    <div class="glass p-4"><p class="text-white font-bold text-[10px] uppercase">Optimización</p><p class="text-slate-500 text-[9px]">Ahorro de OPEX + Success Fee</p></div>
                    <div class="glass p-4"><p class="text-white font-bold text-[10px] uppercase">Infraestructura</p><p class="text-slate-500 text-[9px]">Reología PAM/HPAM Avanzada</p></div>
                    <div class="glass p-4"><p class="text-white font-bold text-[10px] uppercase">Metrología</p><p class="text-slate-500 text-[9px]">Incertidumbre Validada ISO-17025</p></div>
                </div>
            </div>
            <button onclick="nav('dashboard')" class="btn-action mt-8 px-12 py-4 rounded-md tracking-widest text-xs"> Inicializar Centro de Comando </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-4 gap-4">
        
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-8">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                
                <div class="relative w-96">
                    <div class="flex items-center gap-3 search-box px-4 py-2 rounded-lg">
                        <i data-lucide="search" class="w-4 h-4 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscar pozo o explorar catálogo..." 
                               class="bg-transparent text-xs w-full outline-none text-white mono" 
                               onfocus="showAllSuggestions()" oninput="filterWells()">
                    </div>
                    
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-2 glass max-h-64 overflow-y-auto z-50 hidden shadow-2xl">
                        <div class="p-2 text-[9px] uppercase tracking-widest text-slate-500 border-b border-white/5 bg-white/5">Explorar Pozos Disponibles</div>
                        <div id="results-list"></div>
                    </div>
                </div>
            </div>
            
            <div class="flex gap-4">
                <button onclick="nav('home')" class="text-[10px] mono text-slate-500 hover:text-white transition-all uppercase">Menu</button>
                <button onclick="startAgents()" id="run-btn" class="hidden btn-action px-8 py-2 rounded text-[10px] tracking-tighter"> ⚡ Desplegar Agentes </button>
            </div>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-4 min-h-0">
            
            <div id="meta-panel" class="hidden grid grid-cols-5 gap-4 reveal">
                <div class="glass p-4 border-l-2 border-emerald-500"><p class="text-[8px] text-slate-500 uppercase mono">Infraestructura</p><p id="v-infra" class="mono text-white text-[11px] mt-1">--</p></div>
                <div class="glass p-4 border-l-2 border-emerald-500"><p class="text-[8px] text-slate-500 uppercase mono">Químico Sugerido</p><p id="v-chem" class="mono text-white text-[11px] mt-1">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Well_ID</p><p id="v-id" class="mono text-emerald-500 text-[11px] mt-1">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Temp. Reservoir</p><p id="v-temp" class="mono text-white text-[11px] mt-1">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Presión Estática</p><p id="v-pres" class="mono text-white text-[11px] mt-1">--</p></div>
            </div>

            <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-4 py-2 border-b border-slate-900 bg-black/40 flex justify-between">
                    <span class="mono text-[9px] text-slate-500 uppercase tracking-widest">Agent_Core_Stream_v4.0.1</span>
                    <span id="proc-text" class="hidden text-[9px] text-emerald-500 animate-pulse font-bold uppercase">Procesando PIML...</span>
                </div>
                <div id="term-content" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-1.5 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600 italic">> Seleccione un activo del buscador para visualizar la infraestructura técnica...</div>
                </div>
            </div>

            <div id="results-view" class="hidden flex flex-col gap-4 h-full overflow-y-auto pb-4">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental BBL</p><h2 class="mono text-3xl font-bold text-emerald-500">+22,500</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Proyectado</p><h2 class="mono text-4xl font-bold text-white">$1.46M</h2></div>
                    <div class="glass p-5 border-emerald-500/30"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-4xl font-bold text-white">$73,125</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incertidumbre</p><h2 class="mono text-3xl font-bold text-slate-600">±2.1%</h2></div>
                </div>
                <div class="glass p-6 h-80">
                    <div id="main-plot" class="w-full h-full"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const DATABASE = [
            { id: "FB-PRD-101", infra: "Inyector Vertical (ESP)", chem: "HPAM-1500", temp: "84°C", pres: "3240 psi", status: "Produciendo" },
            { id: "FB-PRD-102", infra: "Dual-Zone Horizontal", chem: "Bio-Polímero", temp: "89°C", pres: "3100 psi", status: "Produciendo" },
            { id: "FB-INJ-205", infra: "Smart Completion", chem: "Xanthan High", temp: "77°C", pres: "2950 psi", status: "Activo" },
            { id: "FB-EXP-308", infra: "Offshore Platform", chem: "Surfactante-P", temp: "112°C", pres: "4500 psi", status: "Exploración" }
        ];

        function nav(p) {
            document.getElementById('page-home').classList.toggle('hidden', p !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', p !== 'dashboard');
            if(p === 'home') location.reload();
            lucide.createIcons();
        }

        function showAllSuggestions() {
            const res = document.getElementById('search-results');
            const list = document.getElementById('results-list');
            res.classList.remove('hidden');
            renderList(DATABASE);
        }

        function filterWells() {
            const q = document.getElementById('well-search').value.toUpperCase();
            const filtered = DATABASE.filter(w => w.id.includes(q));
            renderList(filtered);
        }

        function renderList(items) {
            const list = document.getElementById('results-list');
            if(items.length === 0) {
                list.innerHTML = '<div class="p-4 text-xs text-slate-600 italic">No se encontraron resultados</div>';
                return;
            }
            list.innerHTML = items.map(w => `
                <div class="suggestion-card p-4 flex justify-between items-center" onclick="selectWell('${w.id}')">
                    <div>
                        <div class="text-xs font-bold text-white mono">${w.id}</div>
                        <div class="text-[9px] text-slate-500 mono">${w.infra}</div>
                    </div>
                    <span class="tag tag-active">${w.status}</span>
                </div>
            `).join('');
        }

        function selectWell(id) {
            const w = DATABASE.find(x => x.id === id);
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('run-btn').classList.remove('hidden');
            
            document.getElementById('v-id').textContent = id;
            document.getElementById('v-infra').textContent = w.infra;
            document.getElementById('v-chem').textContent = w.chem;
            document.getElementById('v-temp').textContent = w.temp;
            document.getElementById('v-pres').textContent = w.pres;
            document.getElementById('meta-panel').classList.remove('hidden');
            
            document.getElementById('term-content').innerHTML = `<div class="text-white font-bold">> Pozo ${id} seleccionado. Infraestructura y reología listas. Esperando ejecución de agentes...</div>`;
        }

        async function startAgents() {
            const t = document.getElementById('term-content');
            const p = document.getElementById('proc-text');
            document.getElementById('run-btn').classList.add('hidden');
            p.classList.remove('hidden');
            t.innerHTML = "";

            const msgs = [
                "> Handshake AWS S3 Data Lake... OK",
                "> Agente Metrología: Evaluando incertidumbre ±2.1%...",
                "> Agente Reología: Optimizando concentración de polímero...",
                "> Physics-Informed ML: Resolviendo Navier-Stokes...",
                "> Agente Financiero: ROI Success Fee Proyectado...",
                "> SISTEMA ACTUALIZADO."
            ];

            for (const m of msgs) {
                const d = document.createElement('div');
                d.textContent = m;
                if(m.includes('OK') || m.includes('ACTUALIZADO')) d.className = "text-white font-bold";
                t.appendChild(d);
                t.scrollTop = t.scrollHeight;
                await new Promise(r => setTimeout(r, 700));
            }

            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('meta-panel').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            renderPlot();
        }

        function renderPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3500 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
            Plotly.newPlot('main-plot', [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'}, name: 'Base' },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)', name: 'FlowBio' }
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} }
            }, {responsive: true, displayModeBar: false});
        }
        
        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=False)
