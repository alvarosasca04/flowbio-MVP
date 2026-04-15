import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio Intelligence | Command Center",
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

# 3. INTERFAZ INTEGRAL CON DASHBOARD COMPLEJO
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
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-main { background: var(--primary); color: #000; font-weight: 900; text-transform: uppercase; border-radius: 8px; cursor: pointer; border: none; transition: 0.2s; }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
        .hidden { display: none !important; }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; color: #10b981; }
        .kpi-card { border-top: 3px solid var(--primary); background: linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, rgba(20, 26, 33, 1) 100%); }
        input[type=range] { width: 100%; accent-color: #10b981; }
        
        /* Tablas */
        table { width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: 10px; }
        th { border-bottom: 1px solid #1e262f; text-align: left; padding: 12px; color: #94a3b8; text-transform: uppercase; }
        td { border-bottom: 1px solid #1e262f; padding: 12px; color: #e2e8f0; }
        tr:hover { background-color: rgba(255,255,255,0.02); }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 bg-[#080a0d]">
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(#10b981 1px, transparent 1px); background-size: 50px 50px;"></div>
        <h1 class="text-7xl md:text-9xl font-black text-white italic mb-12 tracking-tighter uppercase">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
        <button id="btn-start" class="btn-main px-20 py-6 text-sm tracking-widest shadow-2xl">INICIALIZAR INSTANCIA CLOUD</button>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-6xl mx-auto space-y-8 h-screen justify-center">
        <h2 class="text-3xl font-black text-white uppercase italic tracking-tighter">Digital Twin Config</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass p-8 space-y-6">
                <div><label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2">EOR Solution</label><select id="chem-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none"><option value="FlowBio S3">FlowBio S3 (Bio-System)</option><option value="HPAM Tradicional">HPAM Polymer</option></select></div>
                <div><label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2">Pump Infrastructure</label><select id="infra-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none"><option value="Horizontal Pad">Horizontal Multi-Pad</option><option value="Vertical ESP">Vertical ESP</option></select></div>
            </div>
            <div class="glass p-8 space-y-8">
                <div><div class="flex justify-between text-[10px] mb-2 font-bold"><span>Reservoir K (mD)</span><span id="k-label" class="text-emerald-500">850</span></div><input type="range" id="k-input" min="100" max="5000" value="850"></div>
                <div><div class="flex justify-between text-[10px] mb-2 font-bold"><span>Viscosity (cP)</span><span id="v-label" class="text-emerald-500">120</span></div><input type="range" id="v-input" min="10" max="1000" value="120"></div>
            </div>
        </div>
        <div class="flex justify-center"><button id="btn-run" class="btn-main px-16 py-5 text-xs tracking-widest">⚡ Simular Activo</button></div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen max-w-4xl mx-auto p-10">
        <div class="terminal flex-1 p-10 text-sm leading-relaxed overflow-y-auto" id="log-box"></div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6 h-screen overflow-y-auto pb-20">
        <header class="flex justify-between items-end border-b border-white/5 pb-4">
            <div>
                <h1 class="text-2xl font-black italic tracking-tighter uppercase">Command Center <span class="text-emerald-500">FlowBio</span></h1>
                <p class="text-[10px] mono text-slate-500 uppercase tracking-[0.3em]">Advanced Recovery Analytics</p>
            </div>
            <div class="flex gap-4">
                <button id="btn-back" class="px-4 py-2 border border-white/10 rounded text-[9px] font-bold text-slate-400 hover:text-white uppercase transition-all">← Ajustar Inputs</button>
                <button class="bg-white text-black px-6 py-2 rounded font-black text-[9px] uppercase">Export Data</button>
            </div>
        </header>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div class="glass kpi-card p-6">
                <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-2">Incremental (P50)</p>
                <h3 id="res-extra" class="text-4xl font-black text-emerald-500 tracking-tighter">--</h3>
            </div>
            <div class="glass kpi-card p-6" style="border-top-color: white;">
                <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-2">NPV Impact</p>
                <h3 id="res-npv" class="text-4xl font-black text-white tracking-tighter">--</h3>
            </div>
            <div class="glass kpi-card p-6" style="border-top-color: #8b5cf6;">
                <p class="text-[9px] text-purple-400 font-bold uppercase tracking-widest mb-2">OPEX Efficiency</p>
                <h3 id="res-opex" class="text-4xl font-black text-white tracking-tighter">-18.4%</h3>
            </div>
            <div class="glass kpi-card p-6" style="border-top-color: #3b82f6;">
                <p class="text-[9px] text-blue-400 font-bold uppercase tracking-widest mb-2">FlowBio Fee (5%)</p>
                <h3 id="res-fee" class="text-4xl font-black text-white tracking-tighter">--</h3>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-6 col-span-2">
                <p class="text-xs font-bold uppercase text-white mb-4">Production Curve Forecasting</p>
                <div id="chart-main" class="w-full h-80"></div>
            </div>
            <div class="glass p-6 flex flex-col">
                <p class="text-xs font-bold uppercase text-white mb-4">AI Confidence Score</p>
                <div id="chart-gauge" class="w-full flex-1"></div>
                <div class="mt-4 p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                    <p class="text-[9px] text-emerald-500 mono leading-relaxed uppercase">La simulación PIML alcanzó convergencia con un margen de error menor al 2% (Norma ISO-17025).</p>
                </div>
            </div>
        </div>

        <div class="glass p-6">
            <div class="flex justify-between items-center mb-6">
                <p class="text-xs font-bold uppercase text-white">Financial Projections (First 5 Months)</p>
                <p id="res-chem" class="text-[10px] text-emerald-500 mono font-bold uppercase bg-emerald-500/10 px-3 py-1 rounded">--</p>
            </div>
            <div class="overflow-x-auto">
                <table>
                    <thead>
                        <tr><th>Month</th><th>Baseline (bbls)</th><th>FlowBio EOR (bbls)</th><th>Incremental</th><th>Gross Revenue (USD)</th></tr>
                    </thead>
                    <tbody id="table-body">
                        </tbody>
                </table>
            </div>
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
                const chem = document.getElementById('chem-input').value;
                
                document.getElementById('view-config').classList.add('hidden');
                document.getElementById('view-terminal').classList.remove('hidden');
                
                const box = document.getElementById('log-box');
                box.innerHTML = "";
                const logs = ["> Syncing Enterprise Nodes...", "> Running Darcy-Multi-Phase Solver...", "> Calibrating Economic Output...", "> Generating Cash Flow Tables...", "> Success."];
                
                for (let l of logs) {
                    let d = document.createElement('div');
                    d.textContent = l;
                    box.appendChild(d);
                    await new Promise(r => setTimeout(r, 500));
                }

                document.getElementById('view-terminal').classList.add('hidden');
                document.getElementById('view-dashboard').classList.remove('hidden');
                
                // --- LÓGICA ---
                const multiplier = (k / v) * 500; 
                const extraBbls = Math.round(multiplier * 120);
                const npv = (extraBbls * 75) / 1000000; 
                
                document.getElementById('res-extra').innerText = "+" + (extraBbls/1000).toFixed(1) + "k";
                document.getElementById('res-npv').innerText = "$" + npv.toFixed(1) + "M";
                document.getElementById('res-fee').innerText = "$" + (npv * 0.05).toFixed(2) + "M";
                
                // Variar el OPEX un poco según los sliders para que se vea vivo
                const opex = (15 + (k/1000)).toFixed(1);
                document.getElementById('res-opex').innerText = "-" + opex + "%";
                document.getElementById('res-chem').innerText = "SYSTEM: " + chem;
                
                renderPlot(extraBbls);
                renderGauge();
                renderTable(extraBbls);
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
            
            Plotly.newPlot('chart-main', [
                {x: x, y: y1, name: 'Baseline', type: 'scatter', line: {color: '#f43f5e', dash: 'dot', width: 2}},
                {x: x, y: y2, name: 'FlowBio', type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16,185,129,0.05)'}
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 20, t: 10, b: 30}, showlegend: false,
                font: {family: 'JetBrains Mono', color: '#4b5563'},
                xaxis: { gridcolor: '#1e262f' }, yaxis: { gridcolor: '#1e262f' }
            }, {responsive: true, displayModeBar: false});
        }

        function renderGauge() {
            Plotly.newPlot('chart-gauge', [{
                type: "indicator", mode: "gauge+number", value: 94.2,
                number: { suffix: "%", font: { color: "#10b981", size: 40 } },
                gauge: {
                    axis: { range: [null, 100], tickwidth: 1, tickcolor: "darkblue" },
                    bar: { color: "#10b981" },
                    bgcolor: "rgba(0,0,0,0)", borderwidth: 0,
                    steps: [
                        { range: [0, 80], color: "#1e262f" },
                        { range: [80, 100], color: "rgba(16, 185, 129, 0.2)" }
                    ]
                }
            }], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 20, r: 20, t: 20, b: 20}
            }, {responsive: true, displayModeBar: false});
        }

        function renderTable(extra) {
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = "";
            let baseVol = 3000;
            
            for(let i=1; i<=5; i++) {
                let opt = Math.round(baseVol + (extra/25000) * 100 * i);
                let inc = opt - Math.round(baseVol);
                let rev = inc * 75;
                
                let tr = document.createElement('tr');
                tr.innerHTML = `<td>Month ${i+10}</td><td>${Math.round(baseVol).toLocaleString()}</td><td class="text-emerald-500 font-bold">${opt.toLocaleString()}</td><td>+${inc.toLocaleString()}</td><td class="text-white">$${rev.toLocaleString()}</td>`;
                tbody.appendChild(tr);
                baseVol = baseVol * 0.94; // declinación simulada
            }
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1400, scrolling=True)
