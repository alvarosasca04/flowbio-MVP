import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE ALTA PRIORIDAD (STREAMLIT BYPASS)
st.set_page_config(
    page_title="FlowBio | Agentic EOR Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE UI PARA PANTALLA COMPLETA "ZERO-MARGIN"
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (LANDING + BUSCADOR + AGENTES + VALIDACIÓN)
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
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .search-input { background: #080a0d; border: 1px solid var(--border); transition: 0.3s; }
        .search-input:focus-within { border-color: var(--primary); box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); transform: translateY(-1px); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        .well-item { cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: 0.2s; }
        .well-item:hover { background: rgba(16, 185, 129, 0.1); color: var(--primary); }
        .reveal { animation: revealEffect 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(20px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col h-full overflow-hidden">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-10 text-center relative overflow-hidden bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <div class="relative z-10 max-w-4xl space-y-8 fade-up">
            <div class="flex justify-center mb-4">
                <div class="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
                    <i data-lucide="microscope" class="w-12 h-12 text-emerald-500"></i>
                </div>
            </div>
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-400 font-light leading-relaxed max-w-2xl mx-auto">
                Infraestructura agéntica basada en <b class="text-white">Metrología y PIML</b> para la optimización autónoma de campos maduros.
            </p>
            <div class="pt-8">
                <button onclick="nav('dashboard')" class="btn-deploy px-12 py-4 rounded-lg tracking-widest text-xs"> Inicializar Consola de Comando </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-6 gap-6">
        
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-8">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-6 w-[1px] bg-slate-800"></div>
                <div class="relative w-80">
                    <div class="flex items-center gap-3 search-input px-4 py-2 rounded-lg">
                        <i data-lucide="search" class="w-4 h-4 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscar pozo en base de datos..." class="bg-transparent text-xs w-full outline-none text-white" oninput="filterWells()">
                    </div>
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-2 glass max-h-48 overflow-y-auto z-50 hidden"></div>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="nav('home')" class="px-4 py-2 text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">← Inicio</button>
                <button onclick="startAgentSimulation()" id="run-btn" class="hidden btn-deploy px-8 py-2.5 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Agentes </button>
            </div>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-6 min-h-0">
            
            <div id="well-metadata" class="hidden grid grid-cols-4 gap-4 reveal">
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Temperatura</p><p id="v-temp" class="mono text-white text-sm">--</p></div>
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Presión (psi)</p><p id="v-pres" class="mono text-white text-sm">--</p></div>
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Permeabilidad</p><p id="v-perm" class="mono text-white text-sm">--</p></div>
                <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Viscosidad</p><p id="v-visc" class="mono text-white text-sm">--</p></div>
            </div>

            <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                    <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Agent_Core_Process</span>
                    <span id="loader-text" class="hidden text-[9px] text-emerald-500 mono animate-pulse">VALIDANDO INCERTIDUMBRE...</span>
                </div>
                <div id="terminal-content" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-2 overflow-y-auto">
                    <div class="text-slate-600 italic">> Use el buscador superior para seleccionar un activo y cargar sus metadatos.</div>
                </div>
            </div>

            <div id="results-view" class="hidden flex flex-col gap-6 h-full overflow-y-auto pb-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental (P50)</p><h2 class="mono text-4xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-700">bbl</span></h2></div>
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Ajustado</p><h2 class="mono text-4xl font-bold text-white">$1.46M <span class="text-xs text-slate-700">USD</span></h2></div>
                    <div class="glass p-6 border-emerald-500/20"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-4xl font-bold text-white">$73,125 <span class="text-xs text-slate-700">USD</span></h2></div>
                </div>
                <div class="glass p-8">
                    <div id="main-plot" class="w-full h-80"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // BASE DE DATOS CSV SIMULADA
        const DATABASE = [
            { id: "VER-ORIZABA-01", temp: "85°C", pres: "3200", perm: "450 mD", visc: "120 cP" },
            { id: "VER-ORIZABA-05", temp: "88°C", pres: "3100", perm: "420 mD", visc: "115 cP" },
            { id: "UKCS-NORTH-SEA-04", temp: "115°C", pres: "4500", perm: "120 mD", visc: "45 cP" },
            { id: "TEXAS-EAGLE-88", temp: "95°C", pres: "2850", perm: "800 mD", visc: "210 cP" },
            { id: "MEX-SURESTE-A2", temp: "102°C", pres: "3900", perm: "310 mD", visc: "80 cP" }
        ];

        let selectedWell = null;

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
            res.innerHTML = filtered.map(w => `<div class="well-item p-3 text-xs mono" onclick="selectWell('${w.id}')">${w.id}</div>`).join('');
        }

        function selectWell(id) {
            selectedWell = DATABASE.find(w => w.id === id);
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('run-btn').classList.remove('hidden');
            
            // Cargar Metadatos
            document.getElementById('v-temp').textContent = selectedWell.temp;
            document.getElementById('v-pres').textContent = selectedWell.pres;
            document.getElementById('v-perm').textContent = selectedWell.perm;
            document.getElementById('v-visc').textContent = selectedWell.visc;
            document.getElementById('well-metadata').classList.remove('hidden');
            
            document.getElementById('terminal-content').innerHTML = `<div class="text-white font-bold">> Activo ${id} cargado exitosamente. Listo para simulación agéntica.</div>`;
        }

        async function startAgentSimulation() {
            const term = document.getElementById('terminal-content');
            const loader = document.getElementById('loader-text');
            const btn = document.getElementById('run-btn');
            
            btn.disabled = true; btn.style.opacity = "0.3";
            loader.classList.remove('hidden');
            term.innerHTML = "";

            const logs = [
                "> Conectando a Data Lake S3 (Metadatos Trazables)...",
                "> Agente Metrología: Evaluando incertidumbre de medición ±2.4%...",
                "> Agente Física: Resolviendo tensores de Darcy y movilidad...",
                "> Ejecutando 10,000 iteraciones Monte Carlo...",
                "> Validando QA/QC de datos históricos...",
                "> SIMULACIÓN COMPLETADA CON ÉXITO."
            ];

            for (const line of logs) {
                const div = document.createElement('div');
                div.textContent = line;
                if(line.includes('ÉXITO')) div.className = "text-white font-bold";
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                await new Promise(r => setTimeout(r, 700));
            }

            // Ocultar terminal y mostrar resultados
            loader.classList.add('hidden');
            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('well-metadata').classList.add('hidden');
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
                margin: {l: 50, r: 20, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('main-plot', data, lay, {responsive: true, displayModeBar: false});
        }

        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=False)
