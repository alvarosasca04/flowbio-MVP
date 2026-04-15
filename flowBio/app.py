import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE ALTA PRIORIDAD
st.set_page_config(
    page_title="FlowBio | Agentic EOR Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE UI PARA PANTALLA COMPLETA "PIXEL PERFECT"
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (BASE DE DATOS TÉCNICA + BUSCADOR)
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
        .search-container { background: #080a0d; border: 1px solid var(--border); transition: 0.2s; }
        .search-container:focus-within { border-color: var(--primary); }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); }
        .well-item { cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 11px; }
        .well-item:hover { background: rgba(16, 185, 129, 0.1); color: var(--primary); }
        .reveal { animation: revealEffect 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(15px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col h-full overflow-hidden">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-10 text-center relative bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 40px 40px;"></div>
        <div class="relative z-10 space-y-8">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-500 font-light max-w-2xl mx-auto">Infraestructura Agéntica para Optimización de Recobro Incremental</p>
            <div class="pt-8 flex gap-4 justify-center">
                <button onclick="nav('dashboard')" class="btn-deploy px-12 py-4 rounded-md tracking-widest text-xs"> Inicializar Consola </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-4 gap-4">
        
        <header class="flex justify-between items-center glass px-6 py-4">
            <div class="flex items-center gap-6">
                <span class="text-xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-4 w-[1px] bg-slate-800"></div>
                <div class="relative w-72">
                    <div class="flex items-center gap-3 search-container px-3 py-1.5 rounded">
                        <i data-lucide="search" class="w-3.5 h-3.5 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscar ID de Pozo..." class="bg-transparent text-[11px] w-full outline-none text-white mono" oninput="filterWells()">
                    </div>
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-1 glass max-h-48 overflow-y-auto z-50 hidden"></div>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="nav('home')" class="text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">← Menú</button>
                <button onclick="startAgents()" id="run-btn" class="hidden btn-deploy px-6 py-2 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Simulación </button>
            </div>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-4 min-h-0">
            
            <div id="meta-panel" class="hidden grid grid-cols-4 gap-4 reveal">
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase mono">Well_ID</p><p id="v-id" class="mono text-emerald-500 text-sm font-bold">--</p></div>
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase mono">Pressure (psi)</p><p id="v-pres" class="mono text-white text-sm">--</p></div>
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase mono">Temperature (°C)</p><p id="v-temp" class="mono text-white text-sm">--</p></div>
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase mono">Permeability (mD)</p><p id="v-perm" class="mono text-white text-sm">--</p></div>
            </div>

            <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-4 py-2 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                    <span class="mono text-[9px] text-slate-500 uppercase tracking-widest">Agent_Workflow_Terminal</span>
                </div>
                <div id="term-content" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-1.5 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600 italic">> Ingrese ID de pozo para iniciar validación metrológica...</div>
                </div>
            </div>

            <div id="results-view" class="hidden flex flex-col gap-4 h-full overflow-y-auto pb-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental (P50)</p><h2 class="mono text-3xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-700">bbl</span></h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Estimado</p><h2 class="mono text-3xl font-bold text-white">$1.46M <span class="text-xs text-slate-700">USD</span></h2></div>
                    <div class="glass p-5 border-emerald-500/20"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-3xl font-bold text-white">$73,125 <span class="text-xs text-slate-700">USD</span></h2></div>
                </div>
                <div class="glass p-6 h-80">
                    <div id="main-plot" class="w-full h-full"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // BASE DE DATOS REALISTA (Claves de Pozos)
        const DATABASE = [
            { id: "FB-PRD-001", pres: "3240", temp: "84.2", perm: "450" },
            { id: "FB-PRD-002", pres: "3100", temp: "82.5", perm: "410" },
            { id: "FB-INJ-004", pres: "2950", temp: "79.1", perm: "380" },
            { id: "FB-EXP-008", pres: "4500", temp: "112.4", perm: "125" },
            { id: "FB-EXP-012", pres: "3850", temp: "95.0", perm: "290" }
        ];

        function nav(page) {
            document.getElementById('page-home').classList.toggle('hidden', page !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', page !== 'dashboard');
            if(page === 'home') location.reload();
            lucide.createIcons();
        }

        function filterWells() {
            const query = document.getElementById('well-search').value.toUpperCase();
            const res = document.getElementById('search-results');
            if (query.length < 1) { res.classList.add('hidden'); return; }
            const filtered = DATABASE.filter(w => w.id.includes(query));
            res.classList.remove('hidden');
            res.innerHTML = filtered.map(w => `<div class="well-item p-2.5 mono" onclick="selectWell('${w.id}')">${w.id}</div>`).join('');
        }

        function selectWell(id) {
            const well = DATABASE.find(w => w.id === id);
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('run-btn').classList.remove('hidden');
            
            // Cargar datos
            document.getElementById('v-id').textContent = id;
            document.getElementById('v-pres').textContent = well.pres;
            document.getElementById('v-temp').textContent = well.temp;
            document.getElementById('v-perm').textContent = well.perm;
            document.getElementById('meta-panel').classList.remove('hidden');
            
            document.getElementById('term-content').innerHTML = `<div class="text-white font-bold">> Pozo ${id} identificado. Parámetros de yacimiento cargados. Esperando ejecución de agentes...</div>`;
        }

        async function startAgents() {
            const term = document.getElementById('term-content');
            const btn = document.getElementById('run-btn');
            btn.disabled = true; btn.style.opacity = "0.3";
            term.innerHTML = "";

            const logs = [
                "> Estableciendo conexión segura con AWS Data Sync...",
                "> Agente Metrología: Validando incertidumbre de sensores S3...",
                "> Agente Física: Procesando leyes de Darcy para fluidos no-Newtonianos...",
                "> PIML Engine: Ejecutando simulación de recobro incremental...",
                "> Validando QA/QC sobre proyecciones financieras...",
                "> SISTEMA ACTUALIZADO: Resultados disponibles."
            ];

            for (const line of logs) {
                const div = document.createElement('div');
                div.textContent = line;
                if(line.includes('Resultados')) div.className = "text-white font-bold";
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                await new Promise(r => setTimeout(r, 700));
            }

            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('meta-panel').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            setTimeout(drawPlot, 100);
        }

        function drawPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3500 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
            const data = [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'} },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)' }
            ];
            const lay = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('main-plot', data, lay, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=False)
