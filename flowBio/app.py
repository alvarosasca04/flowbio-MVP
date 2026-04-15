import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio Intelligence | Dynamic OS",
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
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ CON CÁLCULOS DINÁMICOS
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
        .btn-main { background: var(--primary); color: #000; font-weight: 900; text-transform: uppercase; border-radius: 12px; cursor: pointer; border: none; transition: 0.3s; }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; color: #10b981; }
        .hidden { display: none !important; }
        input[type=range] { -webkit-appearance: none; background: #1e262f; height: 4px; border-radius: 5px; width: 100%; cursor: pointer; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 16px; width: 16px; border-radius: 50%; background: #10b981; }
        select { background: #080a0d; border: 1px solid var(--border); color: #f3f4f6; padding: 12px; border-radius: 8px; width: 100%; font-size: 11px; outline: none; }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 relative bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <h1 class="text-8xl md:text-9xl font-black text-white italic tracking-tighter mb-12">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
        <button onclick="startFlow()" class="btn-main px-20 py-6 text-xs tracking-[0.3em] shadow-2xl">INICIALIZAR INSTANCIA CLOUD</button>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-6xl mx-auto space-y-8">
        <h2 class="text-3xl font-bold text-white uppercase italic">Configuración de Activo</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-6">
                <div class="glass p-8">
                    <label class="text-[10px] font-bold text-emerald-500 uppercase mb-4 block tracking-widest">Químico EOR Actual</label>
                    <select id="chem-val">
                        <option value="HPAM Tradicional">HPAM (Polímero Convencional)</option>
                        <option value="FlowBio S3">FlowBio S3 (Bio-Polímero)</option>
                    </select>
                </div>
                <div class="glass p-8">
                    <label class="text-[10px] font-bold text-emerald-500 uppercase mb-4 block tracking-widest">Infraestructura</label>
                    <select id="infra-val">
                        <option value="Vertical ESP">Vertical ESP</option>
                        <option value="Horizontal Pad">Horizontal Multi-Zone</option>
                    </select>
                </div>
            </div>

            <div class="glass p-8 space-y-8">
                <p class="text-[10px] font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Variables de Yacimiento</p>
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Permeabilidad (K)</span><span id="k-display" class="text-emerald-500">450 mD</span></div>
                        <input type="range" id="k-slider" min="50" max="1500" value="450" oninput="updateValues()">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Viscosidad Crudo</span><span id="v-display" class="text-emerald-500">120 cP</span></div>
                        <input type="range" id="v-slider" min="10" max="500" value="120" oninput="updateValues()">
                    </div>
                    <div>
                        <div class="flex justify-between text-[10px] mono mb-2"><span>Saturación Agua (Sw)</span><span id="s-display" class="text-emerald-500">0.35</span></div>
                        <input type="range" id="s-slider" min="0.1" max="0.8" step="0.01" value="0.35" oninput="updateValues()">
                    </div>
                </div>
            </div>
        </div>
        <div class="flex justify-center pt-6"><button onclick="runSim()" class="btn-main px-16 py-5 text-xs tracking-widest">⚡ Desplegar Agentes en AWS</button></div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen max-w-4xl mx-auto p-10">
        <div class="terminal flex-1 flex flex-col overflow-hidden shadow-2xl">
            <div id="log-content" class="p-10 flex-1 mono text-[13px] leading-relaxed space-y-4 overflow-y-auto"></div>
        </div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6">
        <header class="flex justify-between items-center glass px-8 py-4">
            <span class="text-2xl font-black italic">FLOW<span class="text-emerald-500">BIO</span></span>
            <button onclick="location.reload()" class="text-[9px] mono text-slate-600 uppercase border border-white/10 px-4 py-2 rounded-lg hover:text-white transition-all">Reiniciar</button>
        </header>

        <div class="glass p-8 h-[450px]">
             <div id="chart-main" class="w-full h-full"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div class="glass p-8 border-l-4 border-emerald-500">
                <p class="text-[10px] text-slate-500 uppercase font-bold">Barriles Extra</p>
                <h3 id="kpi-extra" class="text-5xl font-black text-emerald-500 tracking-tighter">--</h3>
            </div>
            <div class="glass p-8 border-l-4 border-white">
                <p class="text-[10px] text-slate-500 uppercase font-bold">NPV Generado</p>
                <h3 id="kpi-npv" class="text-5xl font-black text-white tracking-tighter">--</h3>
            </div>
            <div class="glass p-8 border-l-4 border-emerald-500 bg-emerald-500/5">
                <p class="text-[10px] text-blue-400 uppercase font-bold">FlowBio Fee</p>
                <h3 id="kpi-fee" class="text-5xl font-black text-white tracking-tighter">--</h3>
            </div>
        </div>

        <div class="glass p-8 grid grid-cols-3 gap-8">
            <div><p class="text-[9px] text-slate-500 uppercase">Químico Recomendado</p><p id="res-chem" class="text-sm font-bold text-white uppercase"></p></div>
            <div><p class="text-[9px] text-slate-500 uppercase">Concentración Óptima</p><p id="res-conc" class="text-sm font-bold text-white uppercase"></p></div>
            <div><p class="text-[9px] text-slate-500 uppercase">Presión de Inyección</p><p id="res-pres" class="text-sm font-bold text-emerald-500 uppercase"></p></div>
        </div>
    </div>

    <script>
        function updateValues() {
            document.getElementById('k-display').innerText = document.getElementById('k-slider').value + " mD";
            document.getElementById('v-display').innerText = document.getElementById('v-slider').value + " cP";
            document.getElementById('s-display').innerText = document.getElementById('s-slider').value;
        }

        function startFlow() {
            document.getElementById('view-landing').classList.add('hidden');
            document.getElementById('view-config').classList.remove('hidden');
        }

        async function runSim() {
            // Guardar inputs para el cálculo
            const K = parseFloat(document.getElementById('k-slider').value);
            const V = parseFloat(document.getElementById('v-slider').value);
            const S = parseFloat(document.getElementById('s-slider').value);
            const chem = document.getElementById('chem-val').value;

            document.getElementById('view-config').classList.add('hidden');
            document.getElementById('view-terminal').classList.remove('hidden');
            
            const logs = [
                {t: "AWS Cloud:", m: "Sincronizando con S3...", s: "[OK]"},
                {t: "🤖 Agente Física:", m: "Resolviendo Darcy para K=" + K + " mD...", s: "[OK]"},
                {t: "🤖 Agente Mitigación:", m: "Optimizando reología para viscosidad de " + V + " cP...", s: "[OK]"},
                {t: "🤖 Agente Financiero:", m: "Calculando NPV para Saturación " + S + "...", s: "[OK]"}
            ];

            const box = document.getElementById('log-content');
            for (let l of logs) {
                let d = document.createElement('div');
                d.innerHTML = `<span class="text-white font-bold">${l.t}</span> ${l.m} <span class="text-emerald-400 font-bold">${l.s}</span>`;
                box.appendChild(d);
                await new Promise(r => setTimeout(r, 800));
            }

            setTimeout(() => {
                document.getElementById('view-terminal').classList.add('hidden');
                document.getElementById('view-dashboard').classList.remove('hidden');
                calculateAndRender(K, V, S, chem);
            }, 800);
        }

        function calculateAndRender(K, V, S, chem) {
            // Lógica Dinámica: A más K y menos V, más recobro.
            const baseFactor = (K / V) * (1 - S);
            const extraBbls = Math.round(baseFactor * 50);
            const npv = (extraBbls * 68) / 1000000; // Barril a $68
            const fee = (npv * 1000000 * 0.05);

            document.getElementById('kpi-extra').innerText = "+" + extraBbls.toLocaleString() + " bbls";
            document.getElementById('kpi-npv').innerText = "$" + npv.toFixed(2) + "M USD";
            document.getElementById('kpi-fee').innerText = "$" + Math.round(fee).toLocaleString();
            document.getElementById('res-chem').innerText = chem;
            document.getElementById('res-conc').innerText = (V * 12) + " PPM";
            document.getElementById('res-pres').innerText = Math.round(2000 + (K/2)) + " PSI";

            const x = Array.from({length: 40}, (_, i) => i);
            const y1 = x.map(v => 3000 * Math.exp(-0.06 * v));
            // La curva verde reacciona al baseFactor
            const y2 = x.map((v, i) => i < 10 ? y1[i] : y1[i] + (baseFactor * 2.5) * Math.exp(-0.02 * (i-10)));

            Plotly.newPlot('chart-main', [
                {x: x, y: y1, name: 'Status Quo', type: 'scatter', line: {color: '#f43f5e', dash: 'dot'}},
                {x: x, y: y2, name: 'FlowBio EOR', type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16,185,129,0.1)'}
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 30, b: 40}, showlegend: true,
                font: { color: '#f3f4f6' },
                xaxis: { gridcolor: '#1e262f', title: 'Meses' },
                yaxis: { gridcolor: '#1e262f', title: 'Producción BBL/D' }
            }, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=True)
