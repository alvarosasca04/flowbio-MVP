import streamlit as st
import streamlit.components.v1 as components

# 1. ELIMINAR CUALQUER CONFIGURACIÓN PREVIA Y FORZAR MODO ANCHO
st.set_page_config(
    page_title="FlowBio | Command Center",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. ELIMINAR EL "ESQUELETO" DE STREAMLIT (ESTO ES LO MÁS IMPORTANTE)
st.markdown("""
    <style>
        /* Ocultar todos los elementos de Streamlit */
        header, footer, #MainMenu, [data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
        
        /* Reset de márgenes para que el contenido sea 100% real */
        .stApp { margin: 0; padding: 0; background-color: #0b0f13; }
        .block-container { padding: 0 !important; max-width: 100vw !important; margin: 0 !important; }
        
        /* Forzar al iframe a ser el dueño del navegador */
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            z-index: 9999;
        }
    </style>
""", unsafe_allow_html=True)

# 3. TU INTERFAZ DE ALTA DEFINICIÓN (INSPIRADA EN MINERS IA)
html_ui = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; height: 100vh; width: 100vw; overflow: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; font-size: 10px; letter-spacing: 1px; }
        .terminal { background: #080a0d; border: 1px solid var(--border); color: var(--primary); font-family: 'JetBrains Mono'; font-size: 11px; }
        .hidden { display: none !important; }
    </style>
</head>
<body class="flex flex-col">

    <div id="dashboard" class="h-screen w-full flex flex-col p-4 gap-4">
        
        <header class="flex justify-between items-center glass px-6 py-4">
            <div class="flex items-center gap-6">
                <span class="text-xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-4 w-[1px] bg-slate-800"></div>
                <div class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="mono text-[10px] text-emerald-500 font-bold uppercase">S3_DATA_LINK: ACTIVE</span>
                </div>
            </div>
            <div class="flex gap-3">
                <button onclick="deployAgents()" class="btn-deploy px-5 py-2 rounded uppercase">⚡ Desplegar Agentes</button>
                <button class="px-4 py-2 glass text-[10px] text-slate-500 mono uppercase hover:text-white">Export PDF</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="glass p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Producción Incremental</p>
                <h2 class="mono text-3xl font-bold text-emerald-500">+22,500 <span class="text-xs font-normal text-slate-700">bbl</span></h2>
            </div>
            <div class="glass p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Ebitda Proyectado (36m)</p>
                <h2 class="mono text-3xl font-bold text-white">$1.46M <span class="text-xs font-normal text-slate-700">USD</span></h2>
            </div>
            <div class="glass p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Factor de Daño (PIML)</p>
                <h2 class="mono text-3xl font-bold text-white">0.92 <span class="text-xs font-normal text-slate-700">idx</span></h2>
            </div>
            <div class="glass p-5 border-emerald-500/30">
                <p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee Estimado</p>
                <h2 class="mono text-3xl font-bold text-white">$73,125 <span class="text-xs font-normal text-emerald-900">USD</span></h2>
            </div>
        </div>

        <div class="flex-1 grid grid-cols-12 gap-4 min-h-0">
            <div class="col-span-12 lg:col-span-9 glass p-6 flex flex-col">
                <div class="flex justify-between items-center mb-4">
                    <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">PIML Recovery Forecast</span>
                    <div class="flex gap-4 text-[9px] mono text-slate-500 uppercase">
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span> Baseline</span>
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> FlowBio</span>
                    </div>
                </div>
                <div id="chart" class="flex-1 w-full"></div>
            </div>

            <div class="col-span-12 lg:col-span-3 terminal flex flex-col">
                <div class="px-4 py-2 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                    <span class="mono text-[9px] text-slate-500">AGENT_LOGS</span>
                    <i data-lucide="terminal" class="w-3 h-3 text-slate-700"></i>
                </div>
                <div id="logs" class="p-4 flex-1 overflow-y-auto space-y-2">
                    <div class="text-slate-700 italic">Esperando inicialización...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function deployAgents() {
            const l = document.getElementById('logs');
            const msgs = [
                "> Handshake S3: OK",
                "> Fetching Production Logs...",
                "> Agente Física: Procesando Darcy...",
                "> PIML Simulation: M=1.0",
                "> ROI Calculated.",
                "> Dashboard Updated."
            ];
            l.innerHTML = "";
            for (const m of msgs) {
                const d = document.createElement('div');
                d.textContent = m;
                if(m.includes('OK') || m.includes('Updated')) d.className = "text-white font-bold";
                l.appendChild(d);
                await new Promise(r => setTimeout(r, 600));
            }
        }

        function initChart() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3000 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));

            const data = [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 1, dash: 'dot'}, name: 'Base' },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 3}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)', name: 'Opt' }
            ];

            const lay = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('chart', data, lay, {responsive: true, displayModeBar: false});
        }

        window.onload = () => { lucide.createIcons(); initChart(); };
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_ui, height=2000)
