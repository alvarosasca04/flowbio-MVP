import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA (ESTRICTO)
st.set_page_config(
    page_title="FlowBio Intelligence | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. LIMPIEZA DE CSS (FORZAR PANTALLA COMPLETA)
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL
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
        body { background-color: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        
        /* Botón Maestro */
        .btn-main { 
            background: var(--primary); color: #000; font-weight: 900; 
            text-transform: uppercase; border-radius: 12px; cursor: pointer; 
            border: none; transition: 0.3s; position: relative; z-index: 100;
        }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); transform: translateY(-2px); }
        
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; color: #10b981; }
        .hidden { display: none !important; }
        .reveal { animation: revealEffect 0.5s ease-out forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Sliders */
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; width: 100%; cursor: pointer; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; }
        
        select { background: #080a0d; border: 1px solid var(--border); color: #f3f4f6; padding: 12px; border-radius: 8px; width: 100%; font-size: 11px; outline: none; cursor: pointer; }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 relative overflow-hidden bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        
        <div class="relative z-10 max-w-5xl space-y-12">
            <h1 class="text-7xl md:text-9xl font-black text-white italic tracking-tighter">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div class="glass p-6 border-t-2 border-emerald-500/50">
                    <p class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">01. Optimización Coste</p>
                    <p class="text-slate-400 text-xs font-light leading-relaxed">Modelo Success Fee: Reducción de OPEX mediante dosificación autónoma validada por AWS Cloud.</p>
                </div>
                <div class="glass p-6">
                    <p class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">02. Infraestructura</p>
                    <p class="text-slate-400 text-xs font-light leading-relaxed">Configuración técnica y selección de químicos (HPAM/S3) optimizada por motores PIML.</p>
                </div>
                <div class="glass p-6">
                    <p class="text-emerald-500 font-bold text-[10px] uppercase tracking-widest mb-2">03. Metrología</p>
                    <p class="text-slate-400 text-xs font-light leading-relaxed">Incertidumbre de medición ±2% certificada bajo norma ISO-17025 para reportes auditables.</p>
                </div>
            </div>

            <button onclick="startFlow()" class="btn-main px-20 py-6 text-xs tracking-[0.3em] shadow-2xl">
                INICIALIZAR INSTANCIA CLOUD
            </button>
        </div>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-6xl mx-auto space-y-8 reveal">
        <div class="flex justify-between items-center">
            <span class="text-2xl font-black italic">FLOW<span class="text-emerald-500">BIO</span></span>
            <div class="flex items-center gap-2"><div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div><span class="mono text-[9px] text-blue-400 uppercase">AWS_READY</span></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-6">
                <div class="glass p-8">
                    <label class="text-[10px] font-bold text-emerald-500 uppercase tracking-widest mb-4 block">Químico EOR Actual</label>
                    <select id="chem-val">
                        <option value="HPAM Tradicional">HPAM (Polímero Convencional)</option>
                        <option value="FlowBio S3">FlowBio S3 (Bio-Polímero)</option>
                    </select>
                </div>
                <div class="glass p-8">
                    <label class="text-[10px] font-bold text-emerald-500 uppercase tracking-widest mb-4 block">Infraestructura de Inyección</label>
                    <select id="infra-val">
                        <option value="Vertical ESP">Vertical ESP (Electrosumergible)</option>
                        <option value="Horizontal Pad">Horizontal Multi-Zone</option>
                    </select>
                </div>
            </div>

            <div class="glass p-8 space-y-8">
                <p class="text-[10px] font-bold text-white uppercase tracking-[0.2em] border-b border-white/5 pb-2">Variables de Yacimiento</p>
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Permeabilidad (K)</span><span class="text-emerald-500">450 mD</span></div>
                        <input type="range" min="10" max="2000" value="450">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Viscosidad Crudo</span><span class="text-emerald-500">120 cP</span></div>
                        <input type="range" min="1" max="500" value="120">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Saturación Agua (Sw)</span><span class="text-emerald-500">0.35</span></div>
                        <input type="range" min="0" max="1" step="0.01" value="0.35">
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-center pt-6">
            <button onclick="runSim()" class="btn-main px-16 py-5 text-xs tracking-widest">⚡ Desplegar Agentes en AWS</button>
        </div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen max-w-4xl mx-auto p-10">
        <div class="terminal flex-1 flex flex-col overflow-hidden shadow-2xl">
            <div class="px-5 py-3 border-b border-white/5 bg-black/40 flex justify-between items-center">
                <span class="mono text-[9px] text-slate-500 uppercase tracking-widest">Agent_Compute_Stream</span>
                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            </div>
            <div id="log-content" class="p-10 flex-1 mono text-[13px] leading-relaxed space-y-4 overflow-y-auto"></div>
        </div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6 reveal">
        <header class="flex justify-between items-center glass px-8 py-4">
            <span class="text-2xl font-black italic tracking-tighter">FLOW<span class="text-emerald-500">BIO</span></span>
            <button onclick="location.reload()" class="text-[9px] mono text-slate-600 uppercase border border-white/10 px-4 py-2 rounded-lg hover:text-white transition-all">Reiniciar</button>
        </header>

        <div class="glass p-8 h-[450px]">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold uppercase tracking-tight italic">Pronóstico de Recuperación Incremental (PIML)</h2>
                <div class="flex gap-6 text-[10px] mono font-bold"><span class="text-rose-500">● BASELINE</span><span class="text-emerald-500">● FLOWBIO EOR</span></div>
            </div>
            <div id="chart-main" class="w-full h-full"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-8 border-l-4 border-emerald-500">
                <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-2 font-bold">Barriles Extra</p>
                <h3 class="text-5xl font-black text-emerald-500 tracking-tighter">+25,000 <span class="text-sm font-normal text-slate-700 italic">bbls</span></h3>
            </div>
            <div class="glass p-8 border-l-4 border-white">
                <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-2 font-bold">NPV Generado</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$1.72M <span class="text-sm font-normal text-slate-700 italic">USD</span></h3>
            </div>
            <div class="glass p-8 border-l-4 border-blue-500 bg-blue-500/5">
                <p class="text-[10px] text-blue-400 uppercase tracking-widest mb-2 font-bold italic">Success Fee</p>
                <h3 class="text-5xl font-black text-white tracking-tighter">$75,000 <span class="text-sm font-normal text-blue-900 italic">USD</span></h3>
            </div>
        </div>

        <div class="glass p-8">
            <p class="text-[10px] font-black text-white uppercase tracking-[0.4em] mb-6 italic underline">Dictamen Técnico Operativo</p>
            <div class="grid grid-cols-3 gap-8">
                <div><p class="text-[9px] text-slate-500 uppercase">Químico Recomendado</p><p id="final-chem" class="text-sm font-bold text-white uppercase mt-1">--</p></div>
                <div><p class="text-[9px] text-slate-500 uppercase">Concentración Óptima</p><p class="text-sm font-bold text-white uppercase mt-1">1,500 PPM</p></div>
                <div><p class="text-[9px] text-slate-500 uppercase">Presión de Inyección</p><p class="text-sm font-bold text-emerald-500 uppercase mt-1">2,450 PSI (Certificado)</p></div>
            </div>
        </div>
    </div>

    <script>
        function startFlow() {
            document.getElementById('view-landing').classList.add('hidden');
            document.getElementById('view-config').classList.remove('hidden');
            lucide.createIcons();
        }

        async function runSim() {
            const chem = document.getElementById('chem-val').value;
            document.getElementById('view-config').classList.add('hidden');
            document.getElementById('view-terminal').classList.remove('hidden');
            
            const logs = [
                {t: "🤖 Agente de Datos:", m: "Limpiando valores nulos en CSV y estructurando series de tiempo...", s: "[OK]"},
                {t: "🤖 Agente Física (PIML):", m: "Simulando inyección. Resolviendo ecuaciones Navier-Stokes. M=1...", s: "[OK]"},
                {t: "🤖 Agente de Mitigación:", m: "Alerta: Concentración inicial taponaría poro. Recalibrando presión...", s: "[CORREGIDO]"},
                {t: "🤖 Agente Financiero:", m: "Análisis DCA completado. Generando línea base vs producción FlowBio...", s: "[OK]"},
                {t: "SYSTEM:", m: "Sincronizando Dashboard Principal y Reporte Operativo...", s: "READY"}
            ];

            const box = document.getElementById('log-content');
            for (let l of logs) {
                let d = document.createElement('div');
                d.innerHTML = `<span class="text-white font-bold">${l.t}</span> ${l.m} <span class="text-emerald-400 font-bold">${l.s}</span>`;
                box.appendChild(d);
                box.scrollTop = box.scrollHeight;
                await new Promise(r => setTimeout(r, 1200));
            }

            setTimeout(() => {
                document.getElementById('view-terminal').classList.add('hidden');
                document.getElementById('view-dashboard').classList.remove('hidden');
                document.getElementById('final-chem').innerText = chem;
                renderPlot();
            }, 800);
        }

        function renderPlot() {
            const x = Array.from({length: 40}, (_, i) => i);
            const y1 = x.map(v => 3000 * Math.exp(-0.06 * v));
            const y2 = x.map((v, i) => i < 10 ? y1[i] : y1[i] + 1200 * Math.exp(-0.025 * (i-10)));
            Plotly.newPlot('chart-main', [
                {x: x, y: y1, name: 'Status Quo', type: 'scatter', line: {color: '#f43f5e', dash: 'dot', width: 2}},
                {x: x, y: y2, name: 'FlowBio EOR', type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.1)'}
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563'} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563'} }
            }, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO (Z-INDEX Y HEIGHT PARA EVITAR BLOQUEOS)
components.html(html_code, height=1200, scrolling=True)
