import streamlit as st
import streamlit.components.v1 as components

# 1. BOOTSTRAP DE PLATAFORMA (STRICT FIRST)
st.set_page_config(
    page_title="FlowBio | Intelligent EOR",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE LIMPIEZA DE UI
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (LANDING + DEMO LOGIC)
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
        .btn-primary { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-primary:hover { filter: brightness(1.1); transform: translateY(-2px); box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3); }
        .btn-ghost { border: 1px solid var(--border); color: #94a3b8; transition: all 0.2s; }
        .btn-ghost:hover { border-color: #38bdf8; color: #38bdf8; background: rgba(56, 189, 248, 0.05); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        .reveal { animation: revealEffect 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(20px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
    </style>
</head>
<body class="h-full w-full">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-10 text-center relative overflow-hidden">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        
        <div class="relative z-10 max-w-4xl space-y-8">
            <div class="flex justify-center">
                <div class="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
                    <i data-lucide="microscope" class="w-10 h-10 text-emerald-500"></i>
                </div>
            </div>
            <h1 class="text-7xl md:text-8xl font-black text-white tracking-tighter uppercase">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-400 font-light leading-relaxed max-w-2xl mx-auto">
                La plataforma líder en <b class="text-white">IA Agéntica</b> para la optimización de campos maduros. 
                Reducimos la incertidumbre operativa mediante simulación física informada.
            </p>
            
            <div class="flex flex-col md:flex-row gap-4 justify-center pt-6">
                <button onclick="navToDashboard(false)" class="btn-primary px-10 py-4 rounded-lg text-xs tracking-widest"> 
                    Acceso Corporativo 
                </button>
                <button onclick="navToDashboard(true)" class="btn-ghost px-10 py-4 rounded-lg text-xs tracking-widest uppercase font-bold"> 
                    🚀 Iniciar Modo Demo 
                </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-6 gap-6">
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-6">
                <span class="text-2xl font-black text-white tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-6 w-[1px] bg-slate-800"></div>
                <div id="status-tag" class="flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                    <span class="mono text-[9px] text-slate-500 font-bold uppercase tracking-widest">Node_Standby</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="exitDashboard()" class="px-4 py-2 text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">← Menú</button>
                <button onclick="triggerSimulation()" id="run-btn" class="btn-primary px-8 py-2.5 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Agentes </button>
            </div>
        </header>

        <div id="dashboard-content" class="flex-1 flex flex-col gap-6 min-h-0">
            <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                    <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Agent_Pipeline_Monitor</span>
                    <div id="active-loader" class="hidden text-emerald-500 mono text-[9px] animate-pulse italic">SIMULANDO ESCENARIO...</div>
                </div>
                <div id="console-logs" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-2 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600 italic">SISTEMA: En espera de parámetros para inicializar optimización...</div>
                </div>
            </div>

            <div id="results-view" class="hidden space-y-6 h-full overflow-y-auto pb-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 reveal">
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental (Demo)</p><h2 class="mono text-4xl font-bold text-emerald-500">+18,420 <span class="text-xs text-slate-700">bbl</span></h2></div>
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Proyectado</p><h2 class="mono text-4xl font-bold text-white">$1.25M <span class="text-xs text-slate-700">USD</span></h2></div>
                    <div class="glass p-6 border-emerald-500/30"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-4xl font-bold text-white">$62,500 <span class="text-xs text-slate-700">USD</span></h2></div>
                </div>
                <div class="glass p-8 reveal" style="animation-delay: 0.2s;">
                    <div id="main-plot" class="w-full h-80"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isDemoMode = false;

        function navToDashboard(demo) {
            isDemoMode = demo;
            document.getElementById('page-home').classList.add('hidden');
            document.getElementById('page-dashboard').classList.remove('hidden');
            if(demo) {
                const logs = document.getElementById('console-logs');
                logs.innerHTML = '<div class="text-blue-400 mono font-bold">[DEMO_MODE_ACTIVE] Escenario precargado: Campo Veracruz B-01.</div>' + logs.innerHTML;
            }
            lucide.createIcons();
        }

        function exitDashboard() {
            document.getElementById('page-dashboard').classList.add('hidden');
            document.getElementById('page-home').classList.remove('hidden');
            document.getElementById('results-view').classList.add('hidden');
            document.getElementById('terminal-view').classList.remove('hidden');
            document.getElementById('run-btn').disabled = false;
            document.getElementById('run-btn').style.opacity = "1";
        }

        async function triggerSimulation() {
            const btn = document.getElementById('run-btn');
            const logs = document.getElementById('console-logs');
            const status = document.getElementById('status-tag');
            const loader = document.getElementById('active-loader');

            btn.disabled = true; btn.style.opacity = "0.5";
            loader.classList.remove('hidden');
            logs.innerHTML = isDemoMode ? '<div class="text-blue-400 font-bold">> Ejecutando Demo Optimizado...</div>' : "";
            status.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span><span class="mono text-[9px] text-emerald-500 font-bold uppercase tracking-widest">IA_Processing</span>';

            const msgs = isDemoMode ? [
                "> Conectando a Simulación Estocástica...",
                "> Agente Física: Validando movilidad de polímero...",
                "> Physics-Informed ML: Resolviendo Tensors...",
                "> Agente Financiero: Calculando NPV Success Fee...",
                "> DEMO COMPLETADO CON ÉXITO."
            ] : [
                "> Conectando a Data Lake S3 Real...",
                "> Limpiando logs de producción...",
                "> Procesando Ley de Darcy...",
                "> Sincronizando resultados...",
                "> PROCESO COMPLETADO."
            ];

            for (const m of msgs) {
                const div = document.createElement('div');
                div.textContent = m;
                if(m.includes('COMPLETADO')) div.className = "text-white font-bold";
                logs.appendChild(div);
                logs.scrollTop = logs.scrollHeight;
                await new Promise(r => setTimeout(r, 700));
            }

            loader.classList.add('hidden');
            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            status.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span><span class="mono text-[9px] text-emerald-500 font-bold uppercase tracking-widest">Optimized Output</span>';
            setTimeout(drawPlot, 100);
        }

        function drawPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3500 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1200 * Math.exp(-0.028 * (m - 12)));
            const data = [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'}, name: 'Base' },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)', name: 'FlowBio' }
            ];
            const lay = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('main-plot', data, lay, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. RENDERIZADO FINAL
components.html(html_code, height=1200, scrolling=False)
