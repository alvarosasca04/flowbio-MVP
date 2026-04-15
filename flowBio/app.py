import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Agentic OS",
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

# 3. CORE UI (PRESENTACIÓN + PASO 1, 2, 3 Y 4)
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
        
        /* Custom Sliders */
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; width: 100%; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; cursor: pointer; }
    </style>
</head>
<body class="min-h-screen">

    <div id="page-landing" class="h-screen w-full flex flex-col justify-center items-center p-10 text-center relative overflow-hidden bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <div class="relative z-10 max-w-5xl space-y-10">
            <h1 class="text-7xl md:text-9xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">01. Optimización Financiera</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light">Modelo <b>Success Fee</b> basado en producción incremental real. Reducción de OPEX mediante dosificación autónoma.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">02. Ingeniería de Fondo</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light">Simulación de fluidos no-newtonianos integrada con motores de física <b>PIML</b> para recobro optimizado.</p>
                </div>
                <div class="glass p-6">
                    <h3 class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">03. Metrología Avanzada</h3>
                    <p class="text-slate-400 text-xs leading-relaxed font-light">Validación de incertidumbre de medición ±2% según normativas <b>ISO-17025</b> para reportes auditables.</p>
                </div>
            </div>

            <button onclick="goToStep1()" class="btn-deploy px-14 py-5 rounded-xl tracking-widest text-xs"> 
                INICIALIZAR CONSOLA DE COMANDO 
            </button>
        </div>
    </div>

    <div id="step-1" class="hidden max-w-4xl mx-auto space-y-8 py-10 reveal">
        <header class="flex justify-between items-center mb-10">
            <span class="text-xl font-black text-white italic">Flow<span class="text-emerald-500">Bio</span></span>
            <button onclick="location.reload()" class="text-[9px] mono text-slate-500 hover:text-white uppercase">← Regresar</button>
        </header>

        <div class="text-center space-y-2">
            <h2 class="text-3xl font-bold text-white uppercase tracking-tight">Diagnóstico Inicial del Pozo</h2>
            <p class="text-slate-500 mono text-[10px] uppercase tracking-widest italic">PIML Reservoir Radiography Phase</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass p-8 border-dashed border-2 border-slate-700 flex flex-col items-center justify-center space-y-4">
                <i data-lucide="upload-cloud" class="w-12 h-12 text-slate-500"></i>
                <div class="text-center">
                    <p class="text-sm font-bold text-white">Subir Historial de Producción</p>
                    <p class="text-[10px] text-slate-500 italic">Formatos: .csv / .xlsx (2-5 años)</p>
                </div>
                <button class="text-[10px] text-emerald-500 border border-emerald-500/30 px-4 py-2 rounded-lg hover:bg-emerald-500/10">Arrastra o Selecciona</button>
            </div>

            <div class="glass p-8 space-y-6">
                <p class="text-xs font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Parámetros Críticos</p>
                <div class="space-y-4">
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Permeabilidad Absolute ($K$)</span><span class="text-emerald-500">450 mD</span></div>
                        <input type="range" min="10" max="2000" value="450">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Viscosidad del Crudo</span><span class="text-emerald-500">120 cP</span></div>
                        <input type="range" min="1" max="500" value="120">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Saturación Agua ($S_w$)</span><span class="text-emerald-500">0.35</span></div>
                        <input type="range" min="0" max="1" step="0.01" value="0.35">
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-center pt-6">
            <button onclick="runSimulation()" class="btn-deploy px-16 py-5 rounded-xl text-xs tracking-widest shadow-2xl"> ⚡ Desplegar Agentes EOR </button>
        </div>
    </div>

    <div id="step-2" class="hidden max-w-3xl mx-auto py-20">
        <div class="terminal flex flex-col h-[420px] overflow-hidden shadow-2xl">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Agent_Orchestration_Active</span>
                <div class="flex gap-1.5 animate-pulse"><div class="w-2 h-2 rounded-full bg-emerald-500"></div></div>
            </div>
            <div id="terminal-content" class="p-8 flex-1 mono text-[13px] text-emerald-500/80 space-y-4 overflow-y-auto leading-relaxed">
                </div>
        </div>
    </div>

    <div id="step-3" class="hidden space-y-6 reveal p-4">
        <header class="flex justify-between items-center glass px-8 py-4">
            <span class="text-2xl font-black text-white tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="flex gap-4">
                <button onclick="location.reload()" class="text-[10px] mono text-slate-600 uppercase hover:text-white">Reiniciar Sistema</button>
                <button class="bg-white text-black font-extrabold px-6 py-2 rounded text-[10px] uppercase tracking-tighter"> 📄 Descargar Reporte Operativo </button>
            </div>
        </header>

        <div class="glass p-8">
            <div class="flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-xl font-bold text-white uppercase tracking-tight">Pronóstico de Recuperación Incremental</h2>
                    <p class="text-[10px] text-slate-500 mono uppercase">Análisis PIML vs Status Quo</p>
                </div>
                <div class="flex gap-6 text-[10px] mono font-bold">
                    <span class="text-rose-500">● DECLINACIÓN NATURAL</span>
                    <span class="text-emerald-500">● OPTIMIZACIÓN FLOWBIO</span>
                </div>
            </div>
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
                <p class="text-[10px] uppercase text-emerald-500 tracking-widest mb-2 font-bold underline">FlowBio Success Fee</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$75,000 <span class="text-sm font-normal text-emerald-900 italic">USD</span></h3>
                <p class="text-[9px] text-slate-500 mt-2 uppercase mono italic">Pagadero solo contra éxito incremental</p>
            </div>
        </div>

        <div class="glass p-8 space-y-6 mb-10">
            <h4 class="text-xs font-black text-white uppercase tracking-[0.4em] border-b border-white/5 pb-4 flex items-center gap-2 italic">
                <i data-lucide="zap" class="w-4 h-4 text-emerald-500"></i> Dictamen Técnico Operativo
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="space-y-1">
                    <p class="text-[9px] text-slate-500 uppercase">Químico EOR Recomendado</p>
                    <p class="text-sm font-bold text-white uppercase">HPAM (Poliacrilamida Parcialmente Hidrolizada)</p>
                </div>
                <div class="space-y-1">
                    <p class="text-[9px] text-slate-500 uppercase">Concentración de Inyección</p>
                    <p class="text-sm font-bold text-white uppercase">1,500 ppm</p>
                </div>
                <div class="space-y-1">
                    <p class="text-[9px] text-slate-500 uppercase">Presión Crítica de Bombeo</p>
                    <p class="text-sm font-bold text-emerald-500 uppercase">2,450 psi <span class="text-[10px] text-slate-600 font-normal ml-2"> (± 2% Certificado)</span></p>
                </div>
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
                {t: "🤖 Agente de Datos:", m: "Limpiando valores nulos en el CSV y estructurando series de tiempo...", s: "[OK]"},
                {t: "🤖 Agente de Física (PIML):", m: "Simulando inyección. Aplicando Ley de Darcy y restricciones reológicas. Buscando M=1...", s: "[OK]"},
                {t: "🤖 Agente de Mitigación (Skin):", m: "Alerta: Concentración inicial taponaría el poro. Recalibrando presión para evitar daño...", s: "[CORREGIDO]"},
                {t: "🤖 Agente Financiero:", m: "Corriendo Análisis DCA. Calculando línea base vs. producción optimizada...", s: "[OK]"},
                {t: ">", m: "Desplegando resultados financieros y técnicos...", s: "READY"}
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
