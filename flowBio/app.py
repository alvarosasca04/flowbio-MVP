import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Cloud Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. BYPASS UI STREAMLIT
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. CORE UI
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; border: none; }
        .btn-deploy:hover { filter: brightness(1.2); transform: translateY(-2px); box-shadow: 0 0 30px rgba(16, 185, 129, 0.4); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        select { background: #080a0d; border: 1px solid var(--border); color: #f3f4f6; padding: 12px; border-radius: 8px; width: 100%; font-size: 11px; outline: none; }
        .hidden { display: none !important; }
        .reveal { animation: revealEffect 0.5s ease-out forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; width: 100%; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; cursor: pointer; }
    </style>
</head>
<body>

    <div id="page-landing" class="h-screen w-full flex flex-col justify-center items-center p-10 text-center relative bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic mb-10">FlowBio<span class="text-emerald-500">.</span>IA</h1>
        <button id="start-btn" class="btn-deploy px-14 py-5 rounded-xl tracking-widest text-xs"> 
            INICIALIZAR INSTANCIA CLOUD 
        </button>
    </div>

    <div id="step-1" class="hidden max-w-5xl mx-auto py-10 reveal px-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="glass p-8">
                <p class="text-[10px] font-bold text-[#38bdf8] uppercase mb-4 tracking-widest">Químico EOR</p>
                <select id="chem-select">
                    <option value="HPAM">HPAM (Polímero Tradicional)</option>
                    <option value="Bio">FlowBio S3 (Bio-Polímero)</option>
                </select>
            </div>
            <div class="glass p-8">
                <p class="text-[10px] font-bold text-[#38bdf8] uppercase mb-4 tracking-widest">Infraestructura</p>
                <select id="infra-select">
                    <option value="ESP">Vertical ESP (Bomba)</option>
                    <option value="Smart">Smart Completion</option>
                </select>
            </div>
        </div>
        <div class="glass p-8 space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div><div class="flex justify-between text-[10px] mono mb-3 text-slate-400"><span>Permeabilidad</span><span class="text-emerald-500">450 mD</span></div><input type="range" min="10" max="2000" value="450"></div>
                <div><div class="flex justify-between text-[10px] mono mb-3 text-slate-400"><span>Viscosidad</span><span class="text-emerald-500">120 cP</span></div><input type="range" min="1" max="500" value="120"></div>
                <div><div class="flex justify-between text-[10px] mono mb-3 text-slate-400"><span>Saturación Sw</span><span class="text-emerald-500">0.35</span></div><input type="range" min="0" max="1" step="0.01" value="0.35"></div>
            </div>
        </div>
        <div class="flex justify-center pt-8"><button id="simulate-btn" class="btn-deploy px-16 py-5 rounded-xl text-xs"> ⚡ Desplegar Agentes en AWS </button></div>
    </div>

    <div id="step-2" class="hidden max-w-3xl mx-auto py-20 px-6">
        <div class="terminal flex flex-col h-[400px] shadow-2xl overflow-hidden">
            <div id="terminal-content" class="p-8 flex-1 mono text-[13px] text-emerald-500/80 space-y-4 overflow-y-auto leading-relaxed"></div>
        </div>
    </div>

    <div id="step-3" class="hidden space-y-6 p-6">
        <div class="glass p-8"><div id="main-plot" class="w-full h-96"></div></div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-8 border-l-4 border-emerald-500"><p class="text-[10px] uppercase text-slate-500 mb-2 font-bold">Extra</p><h3 class="text-5xl font-black text-emerald-500">+25,000 bbls</h3></div>
            <div class="glass p-8 border-l-4 border-white"><p class="text-[10px] uppercase text-slate-500 mb-2 font-bold">NPV</p><h3 class="text-5xl font-black text-white">$1.72M</h3></div>
            <div class="glass p-8 border-l-4 border-emerald-500 bg-emerald-500/5"><p class="text-[10px] uppercase text-emerald-500 mb-2 font-bold">Fee</p><h3 class="text-5xl font-black text-white">$75,000</h3></div>
        </div>
    </div>

    <script>
        // Manejador del primer botón
        document.getElementById('start-btn').addEventListener('click', () => {
            document.getElementById('page-landing').classList.add('hidden');
            document.getElementById('step-1').classList.remove('hidden');
            lucide.createIcons();
        });

        // Manejador de la simulación
        document.getElementById('simulate-btn').addEventListener('click', async () => {
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.remove('hidden');
            const term = document.getElementById('terminal-content');
            const lines = [
                "AWS Cloud: Sincronizando instancia...",
                "🤖 Agente Física: Procesando leyes de Darcy...",
                "🤖 Agente Financiero: Generando NPV...",
                "SISTEMA LISTO."
            ];
            for (let l of lines) {
                const d = document.createElement('div');
                d.textContent = "> " + l;
                term.appendChild(d);
                await new Promise(r => setTimeout(r, 800));
            }
            document.getElementById('step-2').classList.add('hidden');
            document.getElementById('step-3').classList.remove('hidden');
            renderPlot();
        });

        function renderPlot() {
            const x = Array.from({length: 40}, (_, i) => i);
            const base = x.map(v => 3000 * Math.exp(-0.06 * v));
            const opt = x.map((v, i) => i < 10 ? base[i] : base[i] + 1300 * Math.exp(-0.025 * (i-10)));
            Plotly.newPlot('main-plot', [
                { x: x, y: base, name: 'Status Quo', type: 'scatter', line: {color: '#f43f5e', dash: 'dot'} },
                { x: x, y: opt, name: 'FlowBio', type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.08)' }
            ], { paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', margin: {l: 50, r: 20, t: 10, b: 40}, showlegend: false, xaxis: { gridcolor: '#1e262f' }, yaxis: { gridcolor: '#1e262f' } }, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=False)
