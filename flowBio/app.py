import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO)
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. EL "HACK" DE CSS PARA ELIMINAR TODO EL CONTORNO DE STREAMLIT
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        /* Elimina los márgenes de Streamlit */
        .block-container {
            padding: 0rem !important;
            max-width: 100vw !important;
            height: 100vh !important;
        }
        /* Fuerza al Iframe a ser la pantalla completa */
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# 3. CÓDIGO HTML INTEGRAL (Diseño MinersIA + FlowBio)
html_content = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0b0f13; --card: #141a21; --primary: #10b981; --border: #1e262f; }
        body, html { height: 100%; margin: 0; padding: 0; background: var(--bg); color: #f3f4f6; overflow: hidden; font-family: 'Inter', sans-serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); transform: translateY(-1px); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-size: 11px; line-height: 1.6; }
        .hidden { display: none !important; }
        /* Scrollbar interna para la terminal */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col h-full">

    <div id="page-home" class="h-full w-full flex flex-col justify-center items-center text-center p-8">
        <div class="space-y-6">
            <h1 class="text-8xl font-black tracking-tighter uppercase text-white">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-500 font-light italic">Infrastructure for Intelligent Recovery Optimization</p>
            <button onclick="nav('dashboard')" class="btn-deploy px-12 py-4 mt-8 rounded-lg tracking-widest text-xs"> Inicializar Consola de Comando </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-full w-full flex flex-col p-6 space-y-6 overflow-hidden">
        
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-6">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-6 w-[1px] bg-slate-800"></div>
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="mono text-[10px] text-emerald-500 font-bold uppercase tracking-widest">Systems: Online</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="runAgents()" class="btn-deploy px-6 py-2 rounded-md text-[10px] tracking-tighter"> ⚡ Desplegar Agentes </button>
                <button onclick="nav('home')" class="px-4 py-2 text-[10px] mono text-slate-500 hover:text-white transition-all">Logout</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-6">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-2">Producción Incremental</p>
                <h2 class="mono text-4xl font-bold text-emerald-500">+22,500 <span class="text-sm font-normal text-slate-600">bbls</span></h2>
            </div>
            <div class="glass p-6">
                <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-2">EBITDA Proyectado (36m)</p>
                <h2 class="mono text-4xl font-bold text-white">$1.46M <span class="text-sm font-normal text-slate-600">USD</span></h2>
            </div>
            <div class="glass p-6 border-emerald-500/30 bg-emerald-500/5">
                <p class="text-[10px] uppercase tracking-widest text-emerald-500 mb-2">Success Fee Estimado</p>
                <h2 class="mono text-4xl font-bold text-white">$73,125 <span class="text-sm font-normal text-emerald-900">USD</span></h2>
            </div>
        </div>

        <div class="flex-1 grid grid-cols-12 gap-6 min-h-0">
            <div class="col-span-12 lg:col-span-8 glass p-8 flex flex-col">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">PIML Analysis Viewport</h3>
                    <div class="flex gap-6 text-[9px] mono text-slate-500 uppercase">
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span> Status Quo</span>
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> FlowBio Opt.</span>
                    </div>
                </div>
                <div id="chart-main" class="flex-1 w-full"></div>
            </div>

            <div class="col-span-12 lg:col-span-4 terminal flex flex-col">
                <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                    <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Live_Agent_Logs</span>
                    <div class="flex gap-1.5"><div class="w-2 h-2 rounded-full bg-slate-800"></div><div class="w-2 h-2 rounded-full bg-slate-800"></div></div>
                </div>
                <div id="term-logs" class="p-5 flex-1 mono text-[11px] text-emerald-500/80 space-y-2 overflow-y-auto">
                    <div class="text-slate-600 italic">Esperando inicialización de comando...</div>
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
                }, 50);
            }
        }

        async function runAgents() {
            const term = document.getElementById('term-logs');
            const messages = [
                "> Iniciando Handshake con S3 Data Lake...",
                "> Agente Datos: Estructurando series temporales... [OK]",
                "> Agente Física: Validando Ley de Darcy y Reología...",
                "> Optimizando Viscosidad para M=1.0...",
                "> Agente Financiero: Generando proyecciones de EBITDA...",
                "> SISTEMA ACTUALIZADO: Resultados en dashboard."
            ];
            term.innerHTML = "";
            for (const msg of messages) {
                const div = document.createElement('div');
                div.textContent = msg;
                if(msg.includes('OK')) div.className = "text-white font-bold";
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
                { x: months, y: base, name: 'Base', type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'} },
                { x: months, y: flow, name: 'Flow', type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)' }
            ];

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 10, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };

            Plotly.newPlot('chart-main', data, layout, {responsive: true, displayModeBar: false});
        }
        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDERIZADO AL 100%
components.html(html_content, height=2000, scrolling=False)
