import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE CSS PARA PANTALLA COMPLETA Y OCULTAR STREAMLIT
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ CON BOTÓN DE REGRESO
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
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
        .btn-outline { border: 1px solid var(--border); color: #6e7681; font-size: 10px; transition: all 0.2s; }
        .btn-outline:hover { border-color: #fff; color: #fff; background: rgba(255,255,255,0.05); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        .reveal { animation: revealEffect 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(20px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
    </style>
</head>
<body class="h-full w-full">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center p-8 text-center relative">
        <div class="absolute inset-0 opacity-20" style="background-image: radial-gradient(#1e293b 1px, transparent 1px); background-size: 40px 40px;"></div>
        <div class="relative z-10 space-y-6 max-w-3xl">
            <span class="mono text-[10px] tracking-[0.4em] text-emerald-500 uppercase">FlowBio Intelligence</span>
            <h1 class="text-7xl md:text-8xl font-black text-white tracking-tighter uppercase">Agentic<span class="text-emerald-500">.</span>EOR</h1>
            <p class="text-lg text-slate-400 font-light leading-relaxed">
                Plataforma autónoma que utiliza <b class="text-white">Physics-Informed Machine Learning</b> para optimizar la inyección de químicos, 
                reducir el factor de daño y maximizar el recobro incremental en tiempo real.
            </p>
            <div class="pt-8">
                <button onclick="showDashboard()" class="btn-deploy px-12 py-4 rounded-lg tracking-widest text-xs"> 
                    Abrir Consola de Operaciones 
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
                    <span class="mono text-[9px] text-slate-500 font-bold uppercase tracking-widest">Awaiting Command</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="resetSystem()" class="btn-outline px-4 py-2 rounded uppercase font-bold tracking-tighter"> 
                    ← Reiniciar Sistema 
                </button>
                <button onclick="startSimulation()" id="run-btn" class="btn-deploy px-6 py-2 rounded text-[10px] tracking-tighter"> 
                    ⚡ Desplegar Agentes 
                </button>
            </div>
        </header>

        <div id="main-content" class="flex-1 flex flex-col gap-6 min-h-0">
            
            <div id="terminal-container" class="flex-1 glass terminal overflow-hidden flex flex-col">
                <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                    <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Agent_Core_Stream</span>
                    <div id="loading-indicator" class="hidden text-emerald-500 mono text-[9px] animate-pulse">PROCESANDO FÍSICA...</div>
                </div>
                <div id="logs" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-2 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600 italic">CONSOLA: Listo para recibir parámetros de inyección...</div>
                </div>
            </div>

            <div id="results" class="hidden space-y-6 h-full overflow-y-auto pr-2">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 reveal">
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental</p><h2 class="mono text-4xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-700">bbl</span></h2></div>
                    <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV (36m)</p><h2 class="mono text-4xl font-bold text-white">$1.46M <span class="text-xs text-slate-700">USD</span></h2></div>
                    <div class="glass p-6 border-emerald-500/30"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Fee FlowBio</p><h2 class="mono text-4xl font-bold text-white">$73,125 <span class="text-xs text-slate-700">USD</span></h2></div>
                </div>
                <div class="glass p-8 reveal" style="animation-delay: 0.2s;">
                    <h3 class="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-6">PIML Recovery Forecast</h3>
                    <div id="plotly-chart" class="w-full h-80"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showDashboard() {
            document.getElementById('page-home').classList.add('hidden');
            document.getElementById('page-dashboard').classList.remove('hidden');
            lucide.createIcons();
        }

        function resetSystem() {
            // Limpiar todo y volver al inicio
            document.getElementById('page-dashboard').classList.add('hidden');
            document.getElementById('page-home').classList.remove('hidden');
            document.getElementById('results').classList.add('hidden');
            document.getElementById('terminal-container').classList.remove('hidden');
            document.getElementById('logs').innerHTML = '<div class="text-slate-600 italic">CONSOLA: Listo para recibir parámetros de inyección...</div>';
            document.getElementById('run-btn').disabled = false;
            document.getElementById('run-btn').style.opacity = "1";
            document.getElementById('status-tag').innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-slate-600"></span><span class="mono text-[9px] text-slate-500 font-bold uppercase tracking-widest">Awaiting Command</span>';
        }

        async function startSimulation() {
            const btn = document.getElementById('run-btn');
            const logs = document.getElementById('logs');
            const status = document.getElementById('status-tag');
            const indicator = document.getElementById('loading-indicator');

            btn.disabled = true; btn.style.opacity = "0.5";
            indicator.classList.remove('hidden');
            logs.innerHTML = "";
            status.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span><span class="mono text-[9px] text-emerald-500 font-bold uppercase tracking-widest">Processing PIML</span>';

            const msgs = [
                "> Conectando a Data Lake S3...",
                "> Validando integridad de sensores...",
                "> Agente Física: Resolviendo Navier-Stokes...",
                "> Agente Datos: Aplicando regresión no-lineal...",
                "> Optimizando concentración de polímero...",
                "> Sincronizando resultados con el Dashboard...",
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

            indicator.classList.add('hidden');
            document.getElementById('terminal-container').classList.add('hidden');
            document.getElementById('results').classList.remove('hidden');
            status.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span><span class="mono text-[9px] text-emerald-500 font-bold uppercase tracking-widest">System Optimized</span>';
            setTimeout(renderPlot, 100);
        }

        function renderPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3500 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
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
            Plotly.newPlot('plotly-chart', data, lay, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. RENDER FINAL
components.html(html_code, height=1200, scrolling=False)
