import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Agentic EOR OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. BYPASS DE INTERFAZ STREAMLIT
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. CORE UI (HTML/JS/TAILWIND)
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
        .reveal { animation: revealEffect 0.6s ease-out forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Custom Sliders */
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; cursor: pointer; }
    </style>
</head>
<body class="p-6 min-h-screen">

    <div id="step-1" class="max-w-4xl mx-auto space-y-8 py-10">
        <div class="text-center space-y-2">
            <h1 class="text-5xl font-black text-white uppercase italic tracking-tighter">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            <p class="text-slate-500 mono text-xs uppercase tracking-widest">PIML Reservoir Radiography</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass p-8 border-dashed border-2 border-slate-700 flex flex-col items-center justify-center space-y-4">
                <i data-lucide="upload-cloud" class="w-12 h-12 text-slate-500"></i>
                <div class="text-center">
                    <p class="text-sm font-bold text-white">Subir Historial de Producción</p>
                    <p class="text-[10px] text-slate-500">Arrastra tu .csv o .xlsx (2-5 años)</p>
                </div>
                <input type="file" class="hidden" id="file-input">
                <button onclick="document.getElementById('file-input').click()" class="text-[10px] text-emerald-500 border border-emerald-500/30 px-4 py-2 rounded-lg hover:bg-emerald-500/10">Seleccionar Archivo</button>
            </div>

            <div class="glass p-8 space-y-6">
                <p class="text-xs font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Parámetros Físicos</p>
                <div class="space-y-4">
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Permeabilidad (K)</span><span class="text-emerald-500">450 mD</span></div>
                        <input type="range" class="w-full" min="10" max="2000" value="450">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Viscosidad Crudo</span><span class="text-emerald-500">120 cP</span></div>
                        <input type="range" class="w-full" min="1" max="500" value="120">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Saturación Agua (Sw)</span><span class="text-emerald-500">0.35</span></div>
                        <input type="range" class="w-full" min="0" max="1" step="0.01" value="0.35">
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-center pt-6">
            <button onclick="runSimulation()" class="btn-deploy px-16 py-5 rounded-xl text-xs tracking-widest"> ⚡ Desplegar Agentes EOR </button>
        </div>
    </div>

    <div id="step-2" class="hidden max-w-3xl mx-auto py-20">
        <div class="terminal flex flex-col h-[400px] overflow-hidden">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <span class="mono text-[10px] text-slate-500 uppercase">Agent_Orchestrator_v4</span>
                <div class="flex gap-1.5"><div class="w-2 h-2 rounded-full bg-slate-800 animate-pulse"></div></div>
            </div>
            <div id="terminal-content" class="p-8 flex-1 mono text-[13px] text-emerald-500/90 space-y-3 overflow-y-auto">
                </div>
        </div>
    </div>

    <div id="step-3" class="hidden space-y-6 reveal">
        <header class="flex justify-between items-center glass px-8 py-4">
            <span class="text-2xl font-black text-white italic tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="flex gap-4">
                <button onclick="window.location.reload()" class="text-[10px] mono text-slate-500 uppercase hover:text-white">Reiniciar</button>
                <button class="bg-white text-black font-bold px-6 py-2 rounded text-[10px] uppercase tracking-tighter hover:bg-slate-200"> 📄 Descargar Reporte PDF </button>
            </div>
        </header>

        <div class="glass p-8">
            <div class="flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-xl font-bold text-white uppercase tracking-tight">Pronóstico de Recuperación Incremental</h2>
                    <p class="text-[10px] text-slate-500 mono uppercase">Optimización basada en PIML vs Declinación Natural</p>
                </div>
                <div class="flex gap-6 text-[10px] mono font-bold">
                    <span class="text-rose-500">● STATUS QUO</span>
                    <span class="text-emerald-500">● FLOWBIO EOR</span>
                </div>
            </div>
            <div id="money-chart" class="w-full h-96"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-8 border-l-4 border-emerald-500">
                <p class="text-[10px] uppercase text-slate-500 tracking-widest mb-2 font-bold">Barriles Extra Recuperados</p>
                <h3 class="text-5xl font-black text-emerald-500 tracking-tighter">+25,000 <span class="text-sm font-normal text-slate-700 italic">bbls</span></h3>
            </div>
            <div class="glass p-8 border-l-4 border-white">
                <p class="text-[10px] uppercase text-slate-500 tracking-widest mb-2 font-bold">Valor Generado (NPV)</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$1.7M <span class="text-sm font-normal text-slate-700 italic">USD</span></h3>
            </div>
            <div class="glass p-8 border-l-4 border-blue-500 bg-blue-500/5">
                <p class="text-[10px] uppercase text-blue-400 tracking-widest mb-2 font-bold">FlowBio Success Fee</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$75,000 <span class="text-sm font-normal text-blue-900 italic">USD</span></h3>
                <p class="text-[9px] text-blue-300/50 mt-2 uppercase mono">Pagadero solo sobre éxito incremental</p>
            </div>
        </div>

        <div class="glass p-8 space-y-6 mb-10">
            <h4 class="text-xs font-black text-white uppercase tracking-[0.3em] border-b border-white/5 pb-4 flex items-center gap-2">
                <i data-lucide="clipboard-list" class="w-4 h-4 text-emerald-500"></i> Dictamen Técnico Operativo
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="space-y-1">
                    <p class="text-[9px] text-slate-500 uppercase">Químico Recomendado</p>
                    <p class="text-sm font-bold text-white">HPAM (Poliacrilamida Parcialmente Hidrolizada)</p>
                </div>
                <div class="space-y-1">
                    <p class="text-[9px] text-slate-500 uppercase">Concentración Óptima</p>
                    <p class="text-sm font-bold text-white">1,500 ppm</p>
                </div>
                <div class="space-y-1">
                    <p class="text-[9px] text-slate-500 uppercase">Presión Máxima de Bombeo</p>
                    <p class="text-sm font-bold text-emerald-500">2,450 psi <span class="text-[10px] font-normal text-slate-600">(Límite Fractura)</span></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function runSimulation() {
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.remove('hidden');
            
            const term = document.getElementById('terminal-content');
            const lines = [
                {t: "🤖 Agente de Datos:", m: "Limpiando valores nulos en el CSV y estructurando series de tiempo...", s: "[OK]"},
                {t: "🤖 Agente de Física (PIML):", m: "Simulando inyección. Aplicando Ley de Darcy y restricciones reológicas. Buscando Razón de Movilidad M=1...", s: "[OK]"},
                {t: "🤖 Agente de Mitigación:", m: "Alerta: Concentración inicial taponaría el poro. Recalibrando presión y dosificación química...", s: "[RECALIBRADO]"},
                {t: "🤖 Agente Financiero:", m: "Corriendo Análisis de Curva de Declinación (DCA). Calculando línea base vs. producción optimizada...", s: "[OK]"},
                {t: ">", m: "Sincronizando Dashboard Principal...", s: ""}
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
                renderMoneyChart();
                lucide.createIcons();
            }, 1000);
        }

        function renderMoneyChart() {
            const x = Array.from({length: 48}, (_, i) => i);
            const baseline = x.map(v => 3000 * Math.exp(-0.05 * v));
            const optimized = x.map((v, i) => i < 10 ? baseline[i] : baseline[i] + 1200 * Math.exp(-0.02 * (i-10)));

            const data = [
                {
                    x: x, y: baseline, name: 'Status Quo',
                    type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'}
                },
                {
                    x: x, y: optimized, name: 'FlowBio EOR',
                    type: 'scatter', line: {color: '#10b981', width: 4},
                    fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.1)'
                }
            ];

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 40},
                showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 10}, title: 'Meses' },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 10}, title: 'BBL/D' }
            };

            Plotly.newPlot('money-chart', data, layout, {responsive: true, displayModeBar: false});
        }

        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=True)
