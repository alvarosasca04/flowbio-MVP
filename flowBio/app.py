import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA (ESTRICTO)
st.set_page_config(
    page_title="FlowBio | Agentic EOR",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. FIX DE OVERLAY Y MARGENES
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        /* Forzamos que el contenedor de Streamlit use el 100% del alto real */
        .block-container {padding: 0px; max-width: 100%; height: 100vh;}
        iframe {border: none; width: 100%; height: 100vh; display: block;}
    </style>
""", unsafe_allow_html=True)

# 3. CORE UI (MINERS-IA STYLE + FUNCIONALIDAD)
html_content = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .stat-value { font-family: 'JetBrains Mono', monospace; }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(16, 185, 129, 0.4); transform: translateY(-2px); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-size: 11px; height: 320px; overflow-y: auto; }
        .hidden { display: none !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
    </style>
</head>
<body>

    <div id="page-home" class="h-screen w-full flex flex-col justify-center items-center p-8">
        <div class="text-center space-y-6">
            <h1 class="text-7xl md:text-8xl font-black tracking-tight uppercase">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-500 font-light max-w-xl mx-auto italic">"Advanced Agentic Infrastructure for Recovery Optimization"</p>
            <div class="pt-8">
                <button onclick="nav('dashboard')" class="btn-deploy px-12 py-4 rounded-lg tracking-widest text-xs uppercase"> Inicializar Terminal de Comando </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="hidden min-h-screen w-full flex flex-col p-6 space-y-6">
        
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-6">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-6 w-[1px] bg-slate-800"></div>
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="mono text-xs text-emerald-500 font-bold tracking-widest uppercase">Sistema Activo</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="runAgents()" id="btn-run" class="btn-deploy px-6 py-2 rounded-md text-[10px] uppercase tracking-tighter"> ⚡ Desplegar Agentes EOR </button>
                <button onclick="nav('home')" class="px-4 py-2 text-[10px] mono text-slate-500 hover:text-white transition-all">Logout</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-6">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-2">Producción Incremental</p>
                <h2 class="stat-value text-4xl font-bold text-emerald-500">+22,500 <span class="text-sm font-normal text-slate-600">bbls</span></h2>
            </div>
            <div class="glass p-6">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-2">EBITDA Proyectado (36m)</p>
                <h2 class="stat-value text-4xl font-bold text-white">$1.46M <span class="text-sm font-normal text-slate-600">USD</span></h2>
            </div>
            <div class="glass p-6 border-emerald-500/20">
                <p class="text-[10px] uppercase tracking-widest text-emerald-500 mb-2">Success Fee (5%)</p>
                <h2 class="stat-value text-4xl font-bold text-white">$73,125 <span class="text-sm font-normal text-slate-600">USD</span></h2>
            </div>
        </div>

        <div class="grid grid-cols-12 gap-6 pb-8">
            <div class="col-span-12 lg:col-span-8 glass p-8">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                        <i data-lucide="trending-up" class="w-4 h-4"></i> Pronóstico de Recuperación PIML
                    </h3>
                    <div class="flex gap-6 text-[9px] mono text-slate-500 uppercase tracking-widest">
                        <span class="flex items-center gap-2"><span class="w-2 h-2 bg-rose-500 rounded-full"></span> Status Quo</span>
                        <span class="flex items-center gap-2"><span class="w-2 h-2 bg-emerald-500 rounded-full"></span> FlowBio</span>
                    </div>
                </div>
                <div id="chart-div" class="w-full h-80"></div>
            </div>

            <div class="col-span-12 lg:col-span-4 terminal flex flex-col">
                <div class="px-5 py-3 border-b border-slate-900 flex justify-between items-center bg-black/30">
                    <span class="mono text-[10px] text-slate-500 uppercase tracking-tighter">Terminal de Agentes_</span>
                    <div class="flex gap-1.5"><div class="w-2 h-2 rounded-full bg-slate-800"></div><div class="w-2 h-2 rounded-full bg-slate-800"></div></div>
                </div>
                <div id="term-stream" class="p-6 flex-1 mono text-[11px] text-emerald-500/80 space-y-2 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600">Esperando despliegue de agentes...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function nav(page) {
            document.getElementById('page-home').classList.toggle('hidden', page !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', page !== 'dashboard');
            if(page === 'dashboard') { 
                setTimeout(() => {
                    lucide.createIcons();
                    renderChart();
                }, 100);
            }
        }

        async function runAgents() {
            const term = document.getElementById('term-stream');
            const logs = [
                "> Conectando a Data Lake S3... [OK]",
                "> Agente Datos: Limpiando series de tiempo... [COMPLETADO]",
                "> Agente Física: Resolviendo tensores de Darcy... [PROCESANDO]",
                "> Physics-Informed ML: M=1.0 validado.",
                "> Agente Finanzas: ROI calculado sobre $65/bbl.",
                "> SISTEMA SINCRONIZADO: Dashboard actualizado."
            ];
            
            term.innerHTML = "";
            for (const line of logs) {
                const div = document.createElement('div');
                div.textContent = line;
                if(line.includes('OK')) div.className = "text-white font-bold";
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                await new Promise(r => setTimeout(r, 600));
            }
        }

        function renderChart() {
            const months = Array.from({length: 36}, (_, i) => i + 1);
            const base = months.map(m => 3500 * Math.exp(-0.06 * m));
            const flow = months.map((m, i) => m < 12 ? base[i] : base[i] + 1300 * Math.exp(-0.028 * (m - 12)));

            const data = [
                { x: months, y: base, name: 'Base', type: 'scatter', line: {color: '#f43f5e', width: 1, dash: 'dot'} },
                { x: months, y: flow, name: 'Flow', type: 'scatter', line: {color: '#10b981', width: 3}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)' }
            ];

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };

            Plotly.newPlot('chart-div', data, layout, {responsive: true, displayModeBar: false});
        }

        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDER FINAL
components.html(html_content, height=1200, scrolling=False)
