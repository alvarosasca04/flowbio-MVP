import streamlit as st
import streamlit.components.v1 as components

# 1. ELIMINAR CUALQUIER RASTRO DE STREAMLIT (CONFIGURACIÓN DE PODER)
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK RADICAL DE CSS: Limpia la pantalla totalmente
st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        #MainMenu {visibility: hidden;}
        
        /* Reset de márgenes del contenedor principal */
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important; margin: 0 !important;}
        
        /* Forzar al Iframe a ocupar TODA la ventana del navegador */
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            z-index: 999;
        }
    </style>
""", unsafe_allow_html=True)

# 3. EL CÓDIGO HTML INTEGRAL (DISEÑO MINERSIA + LÓGICA FUNCIONAL)
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; height: 100vh; width: 100vw; margin: 0; overflow: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-action { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; }
        .btn-action:hover { filter: brightness(1.2); box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; font-size: 11px; overflow-y: auto; }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div id="page-home" class="h-screen w-full flex flex-col justify-center items-center text-center p-10">
        <div class="space-y-6">
            <h1 class="text-8xl font-black tracking-tighter uppercase text-white">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-xl text-slate-500 font-light italic">Infrastructure for Intelligent Recovery Optimization</p>
            <button onclick="changePage('dashboard')" class="btn-action px-12 py-4 mt-8 rounded-lg tracking-widest text-xs"> 
                ENTRAR AL COMMAND CENTER 
            </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden h-screen w-full flex flex-col p-6 gap-6">
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-6">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="h-6 w-[1px] bg-slate-800"></div>
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="mono text-[10px] text-emerald-500 font-bold uppercase tracking-widest">S3_LINK: ACTIVE</span>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="startAgents()" class="btn-action px-6 py-2 rounded text-[10px] tracking-tighter">⚡ Desplegar Agentes</button>
                <button onclick="changePage('home')" class="px-4 py-2 text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">Logout</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-6">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental Proyectado</p>
                <h2 class="mono text-4xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-700">bbl</span></h2>
            </div>
            <div class="glass p-6">
                <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Estimado (36m)</p>
                <h2 class="mono text-4xl font-bold text-white">$1.46M <span class="text-xs text-slate-700">USD</span></h2>
            </div>
            <div class="glass p-6 border-emerald-500/20">
                <p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p>
                <h2 class="mono text-4xl font-bold text-white">$73,125 <span class="text-xs text-slate-700">USD</span></h2>
            </div>
        </div>

        <div class="flex-1 grid grid-cols-12 gap-6 min-h-0">
            <div class="col-span-8 glass p-8 flex flex-col">
                <h3 class="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-6">PIML Recovery Forecast</h3>
                <div id="chart-container" class="flex-1 w-full"></div>
            </div>
            <div class="col-span-4 terminal flex flex-col">
                <div class="px-4 py-2 border-b border-slate-900 bg-black/40 text-[9px] mono text-slate-600 uppercase">Agent_Stream</div>
                <div id="terminal-content" class="p-5 flex-1 mono text-[11px] text-emerald-500/80 space-y-2 overflow-y-auto">
                    <div class="text-slate-700 italic">Esperando inicialización...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function changePage(page) {
            if(page === 'dashboard') {
                document.getElementById('page-home').classList.add('hidden');
                document.getElementById('page-dashboard').classList.remove('hidden');
                initChart();
            } else {
                document.getElementById('page-home').classList.remove('hidden');
                document.getElementById('page-dashboard').classList.add('hidden');
            }
            lucide.createIcons();
        }

        async function startAgents() {
            const t = document.getElementById('terminal-content');
            const lines = [
                "> Conectando a AWS S3 Data Lake...",
                "> Agente de Datos: Procesando logs... [OK]",
                "> Agente Física: Resolviendo Tensores de Darcy...",
                "> PIML Engine: Validando movilidad M=1.0...",
                "> Generando proyecciones financieras...",
                "> DASHBOARD SINCRONIZADO."
            ];
            t.innerHTML = "";
            for (const line of lines) {
                const div = document.createElement('div');
                div.textContent = line;
                if(line.includes('OK') || line.includes('SINCRONIZADO')) div.className = "text-white font-bold";
                t.appendChild(div);
                t.scrollTop = t.scrollHeight;
                await new Promise(r => setTimeout(r, 600));
            }
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
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', zeroline: false, tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('chart-container', data, layout, {responsive: true, displayModeBar: false});
        }
        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDERIZADO FINAL SIN BORDES
components.html(html_code, height=1200, scrolling=False)
