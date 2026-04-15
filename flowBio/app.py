import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA (ESTÁNDAR DE SOFTWARE PROFESIONAL)
st.set_page_config(
    page_title="FlowBio | Agentic EOR Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. INYECCIÓN DE CSS PARA DISEÑO DE ALTA DEFINICIÓN
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        .block-container {padding: 0px; max-width: 100%; height: 100vh;}
        iframe {border: none; width: 100%; height: 100vh;}
    </style>
""", unsafe_allow_html=True)

# 3. CORE UI: COMBINACIÓN MINERS-IA + POWER BI + HIGH-TECH
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
        :root { --primary: #10b981; --accent: #00E5FF; --bg: #05070a; --card: #0d1117; --border: #1f2937; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; transition: all 0.3s; }
        .glass-card:hover { border-color: var(--accent); box-shadow: 0 0 20px rgba(0, 229, 255, 0.1); }
        .btn-main { background: linear-gradient(90deg, #00E5FF, #0077FF); color: white; font-weight: 800; border-radius: 8px; transition: 0.3s; }
        .btn-main:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0, 229, 255, 0.4); }
        .terminal { background: #000; border: 1px solid var(--border); border-radius: 12px; height: 350px; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div id="page-home" class="h-screen w-full flex flex-col justify-center items-center p-6 text-center">
        <div class="space-y-4 fade-in">
            <h1 class="text-7xl font-black tracking-tighter uppercase" style="background: linear-gradient(90deg, #fff, #64748b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">FLOWBIO</h1>
            <p class="text-xl text-slate-500 font-light">EOR AGENTIC OPERATING SYSTEM</p>
            <button onclick="nav('dashboard')" class="btn-main px-12 py-4 mt-8 uppercase tracking-widest text-xs"> Inicializar Terminal de Comando </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden min-h-screen w-full flex flex-col p-6 space-y-6">
        
        <header class="flex justify-between items-center bg-[#0d1117]/80 backdrop-blur-md border border-white/5 p-5 rounded-2xl">
            <div class="flex items-center gap-6">
                <span class="text-2xl font-black text-white italic">🧬 Flow<span class="text-[#00E5FF]">Bio</span></span>
                <div class="h-6 w-[1px] bg-slate-800"></div>
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="mono text-[10px] text-emerald-500 uppercase font-bold tracking-widest">IA-Agents: Ready</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="runAgents()" class="px-6 py-2 bg-emerald-500 text-black text-[10px] font-bold uppercase rounded-md hover:bg-emerald-400 transition-all">Ejecutar Simulación</button>
                <button onclick="nav('home')" class="px-4 py-2 text-[10px] mono text-slate-500 hover:text-white">Cerrar Sesión</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="glass-card p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental Proyectado</p>
                <h2 class="mono text-3xl font-bold text-emerald-500">+22,500 <span class="text-xs font-normal">bbl</span></h2>
            </div>
            <div class="glass-card p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Valor Neto (NPV)</p>
                <h2 class="mono text-3xl font-bold text-white">$1.46M <span class="text-xs font-normal">USD</span></h2>
            </div>
            <div class="glass-card p-5">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Success Fee (5%)</p>
                <h2 class="mono text-3xl font-bold text-[#00E5FF]">$73.1k <span class="text-xs font-normal">USD</span></h2>
            </div>
            <div class="glass-card p-5 border-[#00E5FF]/20">
                <p class="text-[9px] uppercase tracking-widest text-slate-400 mb-1">Efficiency Index</p>
                <h2 class="mono text-3xl font-bold text-white">0.92 <span class="text-xs font-normal">PIML</span></h2>
            </div>
        </div>

        <div class="flex-1 grid grid-cols-12 gap-6 min-h-0">
            <div class="col-span-12 lg:col-span-8 glass-card p-6 flex flex-col">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xs font-bold uppercase tracking-widest text-slate-300">Análisis Predictivo de Producción</h3>
                    <div class="flex gap-4 text-[9px] mono text-slate-500">
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-rose-500 rounded-full"></span> Status Quo</span>
                        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> FlowBio Opt.</span>
                    </div>
                </div>
                <div id="chart-area" class="flex-1 w-full"></div>
            </div>

            <div class="col-span-12 lg:col-span-4 terminal flex flex-col overflow-hidden">
                <div class="px-4 py-2 border-b border-slate-900 bg-white/5 flex justify-between">
                    <span class="mono text-[10px] text-slate-500 uppercase">Agent-Live-Stream</span>
                    <div class="flex gap-1.5"><div class="w-2 h-2 rounded-full bg-slate-800"></div><div class="w-2 h-2 rounded-full bg-slate-800"></div></div>
                </div>
                <div id="term-logs" class="p-6 flex-1 mono text-[10px] text-emerald-500/80 space-y-2 overflow-y-auto leading-relaxed">
                    <div class="text-slate-600 italic">Esperando señal de ejecución...</div>
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
            const term = document.getElementById('term-logs');
            const messages = [
                "> Conectando a AWS S3 Bucket... [OK]",
                "> Extrayendo logs de producción... [OK]",
                "> Agente Física: Validando Ley de Darcy...",
                "> PIML Engine: Procesando tensores de movilidad...",
                "> Agente Financiero: ROI calculado.",
                "> DASHBOARD SINCRONIZADO EXITOSAMENTE."
            ];
            term.innerHTML = "";
            for (const msg of messages) {
                const div = document.createElement('div');
                div.textContent = msg;
                if(msg.includes('EXITOSAMENTE')) div.className = "text-white font-bold bg-emerald-900/30 p-1";
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                await new Promise(r => setTimeout(r, 600));
            }
        }

        function renderChart() {
            const months = Array.from({length: 36}, (_, i) => i + 1);
            const base = months.map(m => 3000 * Math.exp(-0.06 * m));
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

            Plotly.newPlot('chart-area', data, layout, {responsive: true, displayModeBar: false});
        }
        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDER FINAL
components.html(html_content, height=1200, scrolling=False)
