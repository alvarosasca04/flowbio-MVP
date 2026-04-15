import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE ALTA PRIORIDAD
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. INYECCIÓN DE INTERFAZ "ZERO-FRICTION"
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

# 3. NÚCLEO HIFI (HTML5 / TAILWIND / PLOTLY / LUCIDE)
html_content = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        body { background: #05070a; color: #e6edf3; font-family: 'Outfit', sans-serif; margin: 0; overflow: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .gradient-bg { background: radial-gradient(circle at 50% -20%, #1a2a44 0%, #05070a 80%); }
        .glass-card { background: rgba(13, 17, 23, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; }
        .neon-cyan { color: #00E5FF; text-shadow: 0 0 15px rgba(0, 229, 255, 0.4); }
        .neon-green { color: #39FF14; text-shadow: 0 0 15px rgba(57, 255, 20, 0.4); }
        .btn-primary { background: linear-gradient(135deg, #00E5FF, #0077FF); transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 119, 255, 0.3); }
        .btn-primary:hover { transform: scale(1.02); box-shadow: 0 0 30px rgba(0, 229, 255, 0.5); letter-spacing: 1px; }
        .terminal { background: #010409; border-radius: 12px; border: 1px solid #21262d; }
        .hidden { display: none !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    </style>
</head>
<body class="gradient-bg min-h-screen">

    <div id="page-home" class="h-screen w-full flex flex-col justify-center items-center p-6 text-center">
        <div class="space-y-6">
            <h1 class="text-7xl md:text-9xl font-extrabold tracking-tighter" style="background: linear-gradient(90deg, #fff, #8b949e); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">FLOWBIO</h1>
            <p class="text-lg md:text-2xl text-[#8b949e] font-light max-w-2xl mx-auto">Sistemas Agénticos de Optimización EOR</p>
            <button onclick="navigate('dashboard')" class="btn-primary mt-8 px-12 py-4 rounded-full font-bold text-white uppercase tracking-widest text-sm"> Iniciar Terminal de Comando </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-screen w-full flex flex-col p-6 space-y-6">
        <header class="flex justify-between items-center bg-[#0d1117] border border-white/5 p-4 rounded-2xl">
            <div class="flex items-center gap-4">
                <span class="text-2xl font-black neon-cyan">🧬 FlowBio</span>
                <div class="h-6 w-[1px] bg-white/10"></div>
                <span class="mono text-[10px] text-[#6e7681]">NODE_ID: VER_ORIZABA_01</span>
            </div>
            <div class="flex items-center gap-6">
                <div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-[#39FF14] animate-pulse"></span><span class="text-xs mono">S3_LAKE_SYNCED</span></div>
                <button onclick="navigate('home')" class="text-xs text-[#6e7681] hover:text-white transition-all">TERMINAR SESIÓN</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass-card p-6 border-l-4 border-l-[#39FF14]">
                <p class="text-[10px] uppercase tracking-widest text-[#6e7681] mb-2">Producción Incremental</p>
                <h2 class="text-4xl font-extrabold neon-green">+22,500 <span class="text-sm font-light text-[#6e7681]">bbls</span></h2>
            </div>
            <div class="glass-card p-6">
                <p class="text-[10px] uppercase tracking-widest text-[#6e7681] mb-2">EBITDA Proyectado (36m)</p>
                <h2 class="text-4xl font-extrabold text-white">$1,462,500 <span class="text-sm font-light text-[#6e7681]">USD</span></h2>
            </div>
            <div class="glass-card p-6 border-l-4 border-l-[#00E5FF]">
                <p class="text-[10px] uppercase tracking-widest text-[#00E5FF] mb-2">Success Fee Estimado</p>
                <h2 class="text-4xl font-extrabold neon-cyan">$73,125 <span class="text-sm font-light text-[#6e7681]">USD</span></h2>
            </div>
        </div>

        <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
            <div class="lg:col-span-8 glass-card p-6 flex flex-col">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold flex items-center gap-2"><i data-lucide="line-chart" class="w-4 h-4 text-[#00E5FF]"></i> Pronóstico de Recuperación Activa</h3>
                    <div class="flex gap-4 text-[10px] mono text-[#6e7681]">
                        <span class="flex items-center gap-1"><span class="w-2 h-2 bg-[#ff5f56] rounded-full"></span> BASELINE</span>
                        <span class="flex items-center gap-1"><span class="w-2 h-2 bg-[#39FF14] rounded-full"></span> FLOWBIO EOR</span>
                    </div>
                </div>
                <div id="main-chart" class="flex-1 w-full"></div>
            </div>

            <div class="lg:col-span-4 terminal flex flex-col">
                <div class="px-4 py-3 border-b border-white/5 flex justify-between items-center">
                    <span class="mono text-[10px] text-[#6e7681]">AGENT_WORKFLOW_MONITOR</span>
                    <div class="flex gap-1.5"><div class="w-2 h-2 rounded-full bg-[#30363d]"></div><div class="w-2 h-2 rounded-full bg-[#30363d]"></div></div>
                </div>
                <div id="terminal-body" class="p-4 flex-1 mono text-[11px] text-[#39FF14] space-y-2 overflow-y-auto leading-relaxed">
                    <div>> CONNECTING TO AWS S3... [OK]</div>
                    <div>> INITIALIZING PHYSICS AGENT...</div>
                    <div class="text-white">> RESOLVING NAVIER-STOKES FOR NON-NEWTONIAN FLUIDS...</div>
                    <div class="text-[#00E5FF]">> OPTIMIZING MOBILITY RATIO (M=1.0)... SUCCESS</div>
                    <div class="text-white">> GENERATING FINANCIAL REPORT...</div>
                    <div class="animate-pulse">_</div>
                </div>
                <div class="p-4 border-t border-white/5">
                    <button class="w-full py-2 rounded-lg bg-[#161b22] border border-white/10 text-[10px] font-bold tracking-widest hover:bg-[#1c212d] transition-all">DESCARGAR REPORTE TÉCNICO PDF</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function navigate(page) {
            document.getElementById('page-home').classList.toggle('hidden', page !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', page !== 'dashboard');
            if(page === 'dashboard') { 
                setTimeout(initDashboard, 100);
            }
        }

        function initDashboard() {
            lucide.createIcons();
            renderChart();
        }

        function renderChart() {
            const months = Array.from({length: 36}, (_, i) => i + 1);
            const base = months.map(m => 3000 * Math.exp(-0.06 * m));
            const flow = months.map((m, i) => m < 12 ? base[i] : base[i] + 1200 * Math.exp(-0.03 * (m - 12)));

            const data = [
                { x: months, y: base, name: 'Baseline', type: 'scatter', line: {color: '#ff5f56', width: 2, dash: 'dot'} },
                { x: months, y: flow, name: 'FlowBio', type: 'scatter', line: {color: '#39FF14', width: 4}, fill: 'tonexty', fillcolor: 'rgba(57, 255, 20, 0.05)' }
            ];

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40},
                showlegend: false,
                xaxis: { gridcolor: '#1f2937', zeroline: false, tickfont: {color: '#6e7681', size: 10} },
                yaxis: { gridcolor: '#1f2937', zeroline: false, tickfont: {color: '#6e7681', size: 10} }
            };

            Plotly.newPlot('main-chart', data, layout, {responsive: true, displayModeBar: false});
        }

        window.onload = () => { lucide.createIcons(); };
    </script>
</body>
</html>
"""

# 4. RENDERIZADO FINAL
components.html(html_content, height=1200, scrolling=False)
