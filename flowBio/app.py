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

# 3. CORE UI (FLUJO COMPLETO CON NARRATIVA AWS)
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
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-deploy { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; }
        .btn-deploy:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(16, 185, 129, 0.4); transform: translateY(-2px); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; }
        .hidden { display: none !important; }
        .reveal { animation: revealEffect 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; width: 100%; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; cursor: pointer; }
    </style>
</head>
<body class="min-h-screen">

    <div id="page-landing" class="h-screen w-full flex flex-col justify-center items-center p-10 text-center relative overflow-hidden bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <div class="relative z-10 max-w-5xl space-y-10">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-slate-500 mono text-sm uppercase tracking-[0.5em]">Cloud-Native PIML Infrastructure</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mt-8">
                <div class="glass p-6 border-t border-emerald-500/30">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">AWS Infrastructure</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light">Procesamiento distribuido en nodos <b>Amazon EC2</b>. Seguridad de datos grado bancario en <b>S3</b>.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">Physics-Agential AI</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light">Modelado multivariante para recobro mejorado mediante redes neuronales informadas por física.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">Zero-Risk CAPEX</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light">Implementación sin costo inicial. FlowBio cobra sobre el éxito del crudo extraído.</p>
                </div>
            </div>

            <button onclick="goToStep1()" class="btn-deploy px-14 py-5 rounded-xl tracking-widest text-xs"> 
                INICIALIZAR INSTANCIA CLOUD 
            </button>
        </div>
    </div>

    <div id="step-1" class="hidden max-w-4xl mx-auto space-y-8 py-10 reveal">
        <header class="flex justify-between items-center mb-10">
            <span class="text-xl font-black text-white italic">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div><span class="text-[9px] mono text-blue-400">AWS_CONNECTED</span></div>
        </header>

        <div class="text-center space-y-2">
            <h2 class="text-3xl font-bold text-white uppercase tracking-tight italic">Diagnóstico del Activo</h2>
            <p class="text-slate-500 mono text-[10px] uppercase tracking-widest">Digital Twin Synchronization</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass p-8 border-dashed border-2 border-slate-700 flex flex-col items-center justify-center space-y-4">
                <i data-lucide="cloud-upload" class="w-12 h-12 text-slate-500"></i>
                <div class="text-center">
                    <p class="text-sm font-bold text-white uppercase">Cargar Data S3</p>
                    <p class="text-[10px] text-slate-500 italic">Suba historial de producción (.csv / .xlsx)</p>
                </div>
                <button class="text-[10px] text-emerald-500 border border-emerald-500/30 px-6 py-2 rounded-lg hover:bg-emerald-500/10">Examinar</button>
            </div>

            <div class="glass p-8 space-y-6">
                <p class="text-xs font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Variables de Yacimiento</p>
                <div class="space-y-5">
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2 text-slate-400"><span>Permeabilidad ($K$)</span><span class="text-emerald-500">450 mD</span></div>
                        <input type="range" min="10" max="2000" value="450">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2 text-slate-400"><span>Viscosidad Líquido</span><span class="text-emerald-500">120 cP</span></div>
                        <input type="range" min="1" max="500" value="120">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2 text-slate-400"><span>Saturación ($S_w$)</span><span class="text-emerald-500">0.35</span></div>
                        <input type="range" min="0" max="1" step="0.01" value="0.35">
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-center pt-6">
            <button onclick="runSimulation()" class="btn-deploy px-16 py-5 rounded-xl text-xs tracking-widest"> ⚡ Desplegar Agentes en la Nube </button>
        </div>
    </div>

    <div id="step-2" class="hidden max-w-3xl mx-auto py-20">
        <div class="terminal flex flex-col h-[420px] shadow-2xl overflow-hidden">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <div class="flex gap-2 items-center"><i data-lucide="cloud" class="w-3 h-3 text-slate-500"></i><span class="mono text-[10px] text-slate-500 uppercase tracking-widest">AWS_US_EAST_1_INSTANCE</span></div>
                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            </div>
            <div id="terminal-content" class="p-8 flex-1 mono text-[13px] text-emerald-500/80 space-y-4 overflow-y-auto leading-relaxed">
                </div>
        </div>
    </div>

    <div id="step-3" class="hidden space-y-6 reveal p-4">
        <header class="flex justify-between items-center glass px-8 py-4">
            <span class="text-2xl font-black text-white tracking-tighter italic">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="flex gap-4">
                <button onclick="location.reload()" class="text-[10px] mono text-slate-600 uppercase">Reset</button>
                <button class="bg-white text-black font-extrabold px-6 py-2 rounded text-[10px] uppercase tracking-tighter"> 📄 Descargar Reporte PDF </button>
            </div>
        </header>

        <div class="glass p-8">
            <h2 class="text-xl font-bold text-white uppercase mb-6 italic tracking-tight">Análisis DCA Optimizado (AWS Instance)</h2>
            <div id="main-plot" class="w-full h-96"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-8 border-l-4 border-emerald-500">
                <p class="text-[10px] uppercase text-slate-500 tracking-widest mb-2 font-bold">Crudo Extra Recuperado</p>
                <h3 class="text-5xl font-black text-emerald-500 tracking-tighter">+25,000 <span class="text-sm font-normal text-slate-700 italic">bbls</span></h3>
            </div>
            <div class="glass p-8 border-l-4 border-white">
                <p class="text-[10px] uppercase text-slate-500 tracking-widest mb-2 font-bold">Valor Generado (NPV)</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$1.72M <span class="text-sm font-normal text-slate-700 italic">USD</span></h3>
            </div>
            <div class="glass p-8 border-l-4 border-emerald-500 bg-emerald-500/5">
                <p class="text-[10px] uppercase text-emerald-500 tracking-widest mb-2 font-bold">FlowBio Success Fee</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$75,000 <span class="text-sm font-normal text-emerald-900 italic">USD</span></h3>
                <p class="text-[9px] text-slate-500 mt-2 uppercase mono italic">Costo 0 si no hay incremental</p>
            </div>
        </div>

        <div class="glass p-8 space-y-6 mb-10">
            <h4 class="text-xs font-black text-white uppercase tracking-[0.4em] border-b border-white/5 pb-4">Dictamen Técnico Final</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="space-y-1"><p class="text-[9px] text-slate-500 uppercase">Químico EOR</p><p class="text-sm font-bold text-white uppercase">HPAM (Poliacrilamida)</p></div>
                <div class="space-y-1"><p class="text-[9px] text-slate-500 uppercase">Concentración</p><p class="text-sm font-bold text-white uppercase">1,500 ppm</p></div>
                <div class="space-y-1"><p class="text-[9px] text-slate-500 uppercase">Presión Crítica</p><p class="text-sm font-bold text-emerald-500 uppercase">2,450 psi <span class="text-[10px] text-slate-600 font-normal ml-2"> (± 2% Cert.)</span></p></div>
            </div>
        </div>
    </div>

    <script>
        function goToStep1() {
            document.getElementById('page-landing').classList.add('hidden');
            document.getElementById('step-1').classList.remove('hidden');
            lucide.createIcons();
        }

        async function runSimulation() {
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.remove('hidden');
            
            const term = document.getElementById('terminal-content');
            const lines = [
                {t: "AWS Cloud:", m: "Sincronizando archivo CSV con S3 Bucket...", s: "UPLOADED"},
                {t: "🤖 Agente de Datos:", m: "Limpiando series de tiempo en instancia EC2...", s: "[OK]"},
                {t: "🤖 Agente de Física (PIML):", m: "Simulando tensores de movilidad. Ejecutando ecuaciones Navier-Stokes...", s: "[OK]"},
                {t: "🤖 Agente de Mitigación:", m: "Recalibrando presión de inyección para evitar daño de formación...", s: "[CORREGIDO]"},
                {t: "🤖 Agente Financiero:", m: "Generando reporte de éxito incremental y NPV...", s: "[OK]"},
                {t: "SYSTEM:", m: "Cerrando instancia de cómputo y enviando resultados al Dashboard...", s: "READY"}
            ];

            for (let l of lines) {
                const div = document.createElement('div');
                div.innerHTML = `<span class="text-white font-bold">${l.t}</span> ${l.m} <span class="text-emerald-400 font-bold">${l.s}</span>`;
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                await new Promise(r => setTimeout(r, 1200));
            }

            setTimeout(() => {
                document.getElementById('step-2').classList.add('hidden');
                document.getElementById('step-3').classList.remove('hidden');
                renderPlot();
                lucide.createIcons();
            }, 800);
        }

        function renderPlot() {
            const x = Array.from({length: 40}, (_, i) => i);
            const base = x.map(v => 3000 * Math.exp(-0.06 * v));
            const opt = x.map((v, i) => i < 10 ? base[i] : base[i] + 1300 * Math.exp(-0.025 * (i-10)));

            Plotly.newPlot('main-plot', [
                { x: x, y: base, name: 'Status Quo', type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'} },
                { x: x, y: opt, name: 'FlowBio', type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.08)' }
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 10}, title: 'Meses' },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 10}, title: 'BBL/D' }
            }, {responsive: true, displayModeBar: false});
        }

        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=True)
