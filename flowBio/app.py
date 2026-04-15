import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PODER (BYPASS TOTAL)
st.set_page_config(
    page_title="FlowBio Intelligence | Enterprise EOR OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. LIMPIEZA DE INTERFAZ (ESTILO MINERSIA / HIGH-TECH)
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL CON LOS 3 ÁMBITOS
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
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; --accent: #38bdf8; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
        .search-container { background: #080a0d; border: 1px solid var(--border); transition: 0.2s; }
        .search-container:focus-within { border-color: var(--primary); }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-deploy:hover { filter: brightness(1.2); transform: translateY(-1px); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        .well-item { cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 11px; padding: 10px; }
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
        
        <div class="relative z-10 max-w-5xl space-y-8">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mt-12">
                <div class="glass p-6">
                    <i data-lucide="trending-down" class="text-emerald-500 mb-4"></i>
                    <h3 class="text-white font-bold text-sm uppercase">01. Optimización Coste</h3>
                    <p class="text-slate-500 text-xs mt-2 leading-relaxed">Modelo Success Fee: Solo paga por el incremental real. Reducción de OPEX mediante dosificación autónoma.</p>
                </div>
                <div class="glass p-6">
                    <i data-lucide="settings-2" class="text-emerald-500 mb-4"></i>
                    <h3 class="text-white font-bold text-sm uppercase">02. Infraestructura</h3>
                    <p class="text-slate-500 text-xs mt-2 leading-relaxed">Configuración de inyección y selección de químicos (PAM/HPAM) optimizada por reología PIML.</p>
                </div>
                <div class="glass p-6">
                    <i data-lucide="shield-check" class="text-emerald-500 mb-4"></i>
                    <h3 class="text-white font-bold text-sm uppercase">03. Metrología</h3>
                    <p class="text-slate-500 text-xs mt-2 leading-relaxed">Validación de incertidumbre de medición ±2% bajo normas ISO 17025 para toma de decisiones segura.</p>
                </div>
            </div>

            <div class="pt-8">
                <button onclick="nav('dashboard')" class="btn-deploy px-12 py-4 rounded-md tracking-widest text-xs"> Inicializar Consola de Comando </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-4 gap-4">
        
        <header class="flex justify-between items-center glass px-6 py-4">
            <div class="flex items-center gap-8">
                <span class="text-xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="relative w-64">
                    <div class="flex items-center gap-3 search-container px-3 py-1.5 rounded">
                        <i data-lucide="search" class="w-3.5 h-3.5 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscar Well ID..." class="bg-transparent text-[11px] w-full outline-none text-white mono" oninput="filterWells()">
                    </div>
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-1 glass max-h-48 overflow-y-auto z-50 hidden"></div>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="nav('home')" class="text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">Menu</button>
                <button onclick="startSimulation()" id="run-btn" class="hidden btn-deploy px-6 py-2 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Agentes </button>
            </div>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-4 min-h-0">
            
            <div id="meta-panel" class="hidden grid grid-cols-4 gap-4 reveal">
                <div class="glass p-4 border-l-2 border-emerald-500">
                    <p class="text-[9px] text-slate-500 uppercase mono">Well_Infrastructure</p>
                    <p id="v-infra" class="mono text-white text-xs mt-1">--</p>
                </div>
                <div class="glass p-4 border-l-2 border-emerald-500">
                    <p class="text-[9px] text-slate-500 uppercase mono">Químico EOR Sugerido</p>
                    <p id="v-chem" class="mono text-white text-xs mt-1">--</p>
                </div>
                <div class="glass p-4">
                    <p class="text-[9px] text-slate-500 uppercase mono">Temp. Reservoir</p>
                    <p id="v-temp" class="mono text-white text-xs mt-1">--</p>
                </div>
                <div class="glass p-4">
                    <p class="text-[9px] text-slate-500 uppercase mono">Presión Estática</p>
                    <p id="v-pres" class="mono text-white text-xs mt-1">--</p>
                </div>
            </div>

            <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-4 py-2 border-b border-slate-900 bg-black/40 flex justify-between">
                    <span class="mono text-[9px] text-slate-500 uppercase">Agent_Stream_v4.0.1</span>
                    <span id="proc-text" class="hidden text-[9px] text-emerald-500 animate-pulse">PROCESANDO PIML...</span>
                </div>
                <div id="term-content" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-1.5 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600 italic">> Seleccione un activo del repositorio para visualizar configuración de infraestructura...</div>
                </div>
            </div>

            <div id="results-view" class="hidden flex flex-col gap-4 h-full overflow-y-auto pb-4">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental BBL</p><h2 class="mono text-3xl font-bold text-emerald-500">+22.5k</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Proyectado</p><h2 class="mono text-3xl font-bold text-white">$1.46M</h2></div>
                    <div class="glass p-5 border-emerald-500/30"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-3xl font-bold text-white">$73.1k</h2></div>
                    <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incertidumbre</p><h2 class="mono text-3xl font-bold text-slate-500">±2.1%</h2></div>
                </div>
                <div class="glass p-6 h-80">
                    <div id="main-plot" class="w-full h-full"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const DATABASE = [
            { id: "FB-PRD-001", infra: "Inyector Vertical (ESP)", chem: "HPAM - 1500ppm", temp: "84.2 °C", pres: "3240 psi" },
            { id: "FB-PRD-002", infra: "Horizontal Dual-Zone", chem: "Bio-Polímero S3", temp: "89.5 °C", pres: "3100 psi" },
            { id: "FB-INJ-008", infra: "Smart Well Completion", chem: "Xanthan High Visc", temp: "77.1 °C", pres: "2950 psi" }
        ];

        function nav(p) {
            document.getElementById('page-home').classList.toggle('hidden', p !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', p !== 'dashboard');
            if(p === 'home') location.reload();
            lucide.createIcons();
        }

        function filterWells() {
            const q = document.getElementById('well-search').value.toUpperCase();
            const r = document.getElementById('search-results');
            if (q.length < 1) { r.classList.add('hidden'); return; }
            const fil = DATABASE.filter(w => w.id.includes(q));
            r.classList.remove('hidden');
            r.innerHTML = fil.map(w => `<div class="well-item mono" onclick="selectWell('${w.id}')">${w.id}</div>`).join('');
        }

        function selectWell(id) {
            const w = DATABASE.find(x => x.id === id);
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('run-btn').classList.remove('hidden');
            
            document.getElementById('v-id')?.classList.add('hidden');
            document.getElementById('v-infra').textContent = w.infra;
            document.getElementById('v-chem').textContent = w.chem;
            document.getElementById('v-temp').textContent = w.temp;
            document.getElementById('v-pres').textContent = w.pres;
            document.getElementById('meta-panel').classList.remove('hidden');
            
            document.getElementById('term-content').innerHTML = `<div class="text-white font-bold">> Pozo ${id} cargado. Infraestructura verificada. Agentes de IA listos para simulación PIML.</div>`;
        }

        async function startSimulation() {
            const t = document.getElementById('term-content');
            const l = document.getElementById('proc-text');
            document.getElementById('run-btn').classList.add('hidden');
            l.classList.remove('hidden');
            t.innerHTML = "";

            const msgs = [
                "> Handshake con AWS S3 Data Sync... OK",
                "> Agente Metrología: Validando sensores de presión ISO-17025...",
                "> Agente Reología: Optimizando concentración de " + document.getElementById('v-chem').textContent + "...",
                "> Physics-Informed Engine: Aplicando Navier-Stokes para fluidos no-Newtonianos...",
                "> Agente Financiero: Calculando ROI Success Fee (Ahorro OPEX proyectado)...",
                "> SISTEMA ACTUALIZADO: Dashboard en linea."
            ];

            for (const m of msgs) {
                const d = document.createElement('div');
                d.textContent = m;
                if(m.includes('OK') || m.includes('linea')) d.className = "text-white font-bold";
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

# 4. LANZAMIENTO SIN ESCALAS
components.html(html_code, height=1200, scrolling=False)
