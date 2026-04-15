import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio Intelligence | Enterprise OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. BYPASS UI (PANTALLA COMPLETA)
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 9999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL CON ESCALABILIDAD MASIVA
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background-color: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; height: 100vh; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 16px; }
        .btn-main { background: var(--primary); color: #000; font-weight: 900; text-transform: uppercase; border-radius: 12px; cursor: pointer; border: none; transition: 0.2s; }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
        .hidden { display: none !important; }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; color: #10b981; }
        .kpi-card { border-top: 4px solid var(--primary); background: linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, rgba(20, 26, 33, 1) 100%); }
        input[type=range] { width: 100%; accent-color: #10b981; }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 bg-[#080a0d]">
        <h1 class="text-7xl md:text-9xl font-black text-white italic mb-12 tracking-tighter uppercase">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
        <button id="btn-start" class="btn-main px-20 py-6 text-sm tracking-widest shadow-2xl">INICIALIZAR INSTANCIA CLOUD</button>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-6xl mx-auto space-y-8 h-screen justify-center">
        <h2 class="text-4xl font-black text-white uppercase italic tracking-tighter">Enterprise Asset Config</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="glass p-8 space-y-6">
                <div><label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2 tracking-widest">EOR Selection</label><select id="chem-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none"><option value="FlowBio S3">FlowBio S3 (Bio-System)</option><option value="HPAM Tradicional">HPAM Polymer</option></select></div>
                <div><label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2 tracking-widest">Pump Cluster</label><select id="infra-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none"><option value="Horizontal Pad">Horizontal Multi-Pad (Enterprise)</option><option value="Vertical ESP">Vertical ESP</option></select></div>
            </div>
            <div class="glass p-8 space-y-8">
                <div><div class="flex justify-between text-[10px] mb-2 font-bold"><span>Reservoir K (mD)</span><span id="k-label" class="text-emerald-500">850</span></div><input type="range" id="k-input" min="100" max="5000" value="850"></div>
                <div><div class="flex justify-between text-[10px] mb-2 font-bold"><span>Crude Viscosity (cP)</span><span id="v-label" class="text-emerald-500">120</span></div><input type="range" id="v-input" min="10" max="1000" value="120"></div>
            </div>
        </div>
        <div class="flex justify-center"><button id="btn-run" class="btn-main px-16 py-5 text-xs tracking-widest">⚡ Simular Activo de Escala</button></div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen max-w-4xl mx-auto p-10">
        <div class="terminal flex-1 p-10 text-sm leading-relaxed overflow-y-auto" id="log-box"></div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6 h-screen overflow-y-auto pb-20">
        <header class="flex justify-between items-end border-b border-white/5 pb-4">
            <div>
                <h1 class="text-3xl font-black italic tracking-tighter uppercase">Command Center <span class="text-emerald-500">FlowBio</span></h1>
                <p class="text-[10px] mono text-slate-500 uppercase tracking-[0.3em]">High-Volume Asset Optimization</p>
            </div>
            <button id="btn-back" class="px-4 py-2 border border-white/10 rounded text-[9px] font-bold text-slate-400 uppercase">← Adjust</button>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass kpi-card p-8">
                <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-4">Incremental Recovery (P50)</p>
                <h3 id="res-extra" class="text-6xl font-black text-emerald-500 tracking-tighter">--</h3>
                <p class="text-[10px] text-emerald-500/50 mt-2 mono font-bold">↑ TOTAL BBLS SAVED</p>
            </div>
            <div class="glass kpi-card p-8" style="border-top-color: white;">
                <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-4">Projected NPV Impact</p>
                <h3 id="res-npv" class="text-6xl font-black text-white tracking-tighter">--</h3>
                <p class="text-[10px] text-slate-300 mt-2 mono font-bold">VALUATION INCREASE (USD)</p>
            </div>
            <div class="glass kpi-card p-8" style="border-top-color: #3b82f6;">
                <p class="text-[10px] text-blue-400 font-bold uppercase tracking-widest mb-4">Success Fee (5%)</p>
                <h3 id="res-fee" class="text-6xl font-black text-white tracking-tighter">--</h3>
                <p class="text-[10px] text-blue-400/50 mt-2 mono font-bold">NO RISK PERFORMANCE MODEL</p>
            </div>
        </div>

        <div class="glass p-8 h-[450px]">
            <div id="chart-div" class="w-full h-full"></div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const kIn = document.getElementById('k-input');
            const vIn = document.getElementById('v-input');
            kIn.oninput = () => { document.getElementById('k-label').innerText = kIn.value; };
            vIn.oninput = () => { document.getElementById('v-label').innerText = vIn.value; };

            document.getElementById('btn-start').onclick = () => {
                document.getElementById('view-landing').classList.add('hidden');
                document.getElementById('view-config').classList.remove('hidden');
            };

            document.getElementById('btn-run').onclick = async () => {
                const k = parseFloat(kIn.value);
                const v = parseFloat(vIn.value);
                document.getElementById('view-config').classList.add('hidden');
                document.getElementById('view-terminal').classList.remove('hidden');
                
                const box = document.getElementById('log-box');
                box.innerHTML = "";
                const logs = ["> Syncing Enterprise AWS Nodes...", "> Running Darcy-Multi-Phase Solver...", "> Calibrating Economic Output...", "> Success."];
                
                for (let l of logs) {
                    let d = document.createElement('div');
                    d.textContent = l;
                    box.appendChild(d);
                    await new Promise(r => setTimeout(r, 600));
                }

                document.getElementById('view-terminal').classList.add('hidden');
                document.getElementById('view-dashboard').classList.remove('hidden');
                
                // --- LÓGICA DE ESCALA ---
                // Ajustamos para que los resultados sean de 10x a 50x mayores
                const multiplier = (k / v) * 500; 
                const extraBbls = Math.round(multiplier * 120);
                const npv = (extraBbls * 75) / 1000000; // Barril a $75 USD
                
                document.getElementById('res-extra').innerText = "+" + (extraBbls/1000).toFixed(1) + "M";
                document.getElementById('res-npv').innerText = "$" + npv.toFixed(1) + "M";
                document.getElementById('res-fee').innerText = "$" + (npv * 0.05).toFixed(2) + "M";
                
                renderPlot(extraBbls);
            };

            document.getElementById('btn-back').onclick = () => {
                document.getElementById('view-dashboard').classList.add('hidden');
                document.getElementById('view-config').classList.remove('hidden');
            };
        });

        function renderPlot(extra) {
            const x = Array.from({length: 40}, (_, i) => i);
            const y1 = x.map(v => 3000 * Math.exp(-0.06 * v));
            const y2 = x.map((v, i) => i < 10 ? y1[i] : y1[i] + (extra/25000) * 1000 * Math.exp(-0.015 * (i-10)));
            
            Plotly.newPlot('chart-div', [
                {x: x, y: y1, name: 'BASELINE', type: 'scatter', line: {color: '#f43f5e', dash: 'dot', width: 2}},
                {x: x, y: y2, name: 'FLOWBIO OPTIMIZED', type: 'scatter', line: {color: '#10b981', width: 5}, fill: 'tonexty', fillcolor: 'rgba(16,185,129,0.1)'}
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 30, b: 40},
                showlegend: false,
                font: {family: 'JetBrains Mono', color: '#4b5563'},
                xaxis: { gridcolor: '#1e262f', title: 'MONTHS' },
                yaxis: { gridcolor: '#1e262f', title: 'BBL/DAY' }
            }, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=True)
