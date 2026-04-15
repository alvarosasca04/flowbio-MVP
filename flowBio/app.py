import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE CSS PARA PANTALLA COMPLETA
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ CON LÓGICA DE REVELACIÓN
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
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        
        /* Animación de revelado */
        .reveal { animation: revealEffect 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; transform: translateY(20px); }
        @keyframes revealEffect { to { opacity: 1; transform: translateY(0); } }
        
        .hidden { display: none !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
    </style>
</head>
<body class="p-6 flex flex-col gap-6">

    <header class="flex justify-between items-center glass px-8 py-5">
        <div class="flex items-center gap-6">
            <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="h-6 w-[1px] bg-slate-800"></div>
            <div id="status-tag" class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-slate-600"></span>
                <span class="mono text-[10px] text-slate-500 font-bold uppercase tracking-widest">Awaiting Command</span>
            </div>
        </div>
        <button onclick="startAgentSimulation()" id="main-btn" class="btn-deploy px-8 py-2.5 rounded text-[10px] tracking-tighter"> ⚡ Iniciar Simulación Agéntica </button>
    </header>

    <div id="workspace-initial" class="flex-1 grid grid-cols-12 gap-6 min-h-0">
        <div class="col-span-12 glass flex flex-col terminal overflow-hidden">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Console_Output</span>
                <div id="loader" class="hidden flex gap-1 items-center">
                    <span class="text-[9px] text-emerald-500 mono animate-pulse">PROCESANDO FÍSICA...</span>
                </div>
            </div>
            <div id="terminal-content" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-2 overflow-y-auto leading-relaxed">
                <div class="text-slate-600 italic">SYSTEM_READY: Presione el botón superior para desplegar el enjambre de agentes...</div>
            </div>
        </div>
    </div>

    <div id="results-area" class="hidden flex flex-col gap-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 reveal">
            <div class="glass p-6">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental Proyectado</p>
                <h2 class="mono text-4xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-700">bbl</span></h2>
            </div>
            <div class="glass p-6">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Estimado (36m)</p>
                <h2 class="mono text-4xl font-bold text-white">$1.46M <span class="text-xs text-slate-700">USD</span></h2>
            </div>
            <div class="glass p-6 border-emerald-500/40 bg-emerald-500/5">
                <p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee FlowBio</p>
                <h2 class="mono text-4xl font-bold text-white">$73,125 <span class="text-xs text-slate-700">USD</span></h2>
            </div>
        </div>

        <div class="glass p-8 reveal" style="animation-delay: 0.2s;">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">PIML Recovery Forecast - Active Projection</h3>
            </div>
            <div id="main-chart" class="w-full h-80"></div>
        </div>
    </div>

    <script>
        async function startAgentSimulation() {
            const btn = document.getElementById('main-btn');
            const term = document.getElementById('terminal-content');
            const loader = document.getElementById('loader');
            const statusTag = document.getElementById('status-tag');
            
            // Estado inicial de carga
            btn.disabled = true;
            btn.style.opacity = "0.5";
            loader.classList.remove('hidden');
            term.innerHTML = "";
            statusTag.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span><span class="mono text-[10px] text-emerald-500 font-bold uppercase tracking-widest">Agents Processing</span>`;

            const logs = [
                "> Iniciando handshake con AWS S3...",
                "> Agente de Datos: Limpiando ruidos en sensores... [OK]",
                "> Agente de Física: Calculando tensores de movilidad...",
                "> Physics-Informed ML: Resolviendo ecuaciones de Navier-Stokes...",
                "> Integrando variables financieras ($65/bbl)...",
                "> Generando curvas de declinación optimizadas...",
                "> SIMULACIÓN COMPLETADA CON ÉXITO."
            ];

            for (const line of logs) {
                const div = document.createElement('div');
                div.textContent = line;
                if(line.includes('OK') || line.includes('ÉXITO')) div.className = "text-white font-bold";
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                await new Promise(r => setTimeout(r, 800));
            }

            // REVELAR RESULTADOS
            loader.classList.add('hidden');
            document.getElementById('workspace-initial').classList.add('hidden');
            document.getElementById('results-area').classList.remove('hidden');
            
            // Cambiar tag de estatus
            statusTag.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span class="mono text-[10px] text-emerald-500 font-bold uppercase tracking-widest">Optimization Ready</span>`;
            
            // Renderizar gráfica después de mostrar el div
            setTimeout(initChart, 100);
        }

        function initChart() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3000 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
            const data = [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'}, name: 'Base' },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)', name: 'FlowBio' }
            ];
            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('main-chart', data, layout, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. RENDERIZADO
components.html(html_code, height=1200, scrolling=False)
