import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="FlowBio | Asset Command", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stHeader"], footer {display: none !important;}
        .stApp {background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .asset-select { background: #080a0d; border: 1px solid var(--border); color: #f3f4f6; cursor: pointer; }
        .asset-select:hover { border-color: var(--primary); }
        .hidden { display: none !important; }
        .btn-run { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }
        .btn-run:hover { filter: brightness(1.2); box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
    </style>
</head>
<body class="p-6 flex flex-col gap-6">

    <header class="flex justify-between items-center glass px-8 py-4">
        <div class="flex items-center gap-6">
            <span class="text-2xl font-black text-white tracking-tighter uppercase">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="h-6 w-[1px] bg-slate-800"></div>
            
            <div class="flex items-center gap-3">
                <label class="mono text-[10px] text-slate-500 uppercase">Seleccionar Activo:</label>
                <select id="asset-picker" onchange="updateAssetInfo()" class="asset-select text-xs px-4 py-1.5 rounded-md mono outline-none">
                    <option value="FB_VER_01">VER-ORIZABA-01</option>
                    <option value="FB_UKCS_04">UKCS-NORTH-04</option>
                    <option value="FB_TX_88">TEXAS-EAGLE-88</option>
                </select>
            </div>
        </div>
        
        <button onclick="runValidation()" id="run-btn" class="btn-run px-8 py-2 rounded text-[10px] tracking-tighter"> 
            ⚡ Iniciar Simulación Agéntica 
        </button>
    </header>

    <div id="asset-metadata" class="grid grid-cols-4 gap-4">
        <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Temperatura</p><p id="meta-temp" class="mono text-white text-sm">85°C</p></div>
        <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Presión Reservoir</p><p id="meta-pres" class="mono text-white text-sm">3200 psi</p></div>
        <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Permeabilidad</p><p id="meta-perm" class="mono text-white text-sm">450 mD</p></div>
        <div class="glass p-4"><p class="text-[9px] text-slate-500 uppercase">Viscosidad Crudo</p><p id="meta-visc" class="mono text-white text-sm">120 cP</p></div>
    </div>

    <div id="main-view" class="flex-1 flex flex-col gap-6 min-h-0">
        <div id="terminal-view" class="flex-1 glass bg-[#080a0d] overflow-hidden flex flex-col">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <span id="term-header" class="mono text-[10px] text-slate-500 uppercase tracking-widest">Awaiting Command...</span>
            </div>
            <div id="logs" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-2 overflow-y-auto">
                <div class="text-slate-600 italic">> Seleccione un activo y presione 'Iniciar Simulación' para procesar con Agentes de IA...</div>
            </div>
        </div>

        <div id="results-view" class="hidden flex flex-col gap-6 h-full overflow-y-auto pb-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental</p><h2 class="mono text-4xl font-bold text-emerald-500">+22.5k <span class="text-xs text-slate-700">bbl</span></h2></div>
                <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Ajustado</p><h2 class="mono text-4xl font-bold text-white">$1.41M <span class="text-xs text-slate-700">USD</span></h2></div>
                <div class="glass p-6 border-emerald-500/30"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-4xl font-bold text-white">$73.1k <span class="text-xs text-slate-700">USD</span></h2></div>
            </div>
            <div class="glass p-8">
                <div id="main-chart" class="w-full h-80"></div>
            </div>
            <button onclick="resetDashboard()" class="text-[10px] mono text-slate-600 hover:text-white uppercase">← Cambiar Activo / Reiniciar</button>
        </div>
    </div>

    <script>
        const assets = {
            "FB_VER_01": { temp: "85°C", pres: "3200 psi", perm: "450 mD", visc: "120 cP" },
            "FB_UKCS_04": { temp: "110°C", pres: "4500 psi", perm: "150 mD", visc: "45 cP" },
            "FB_TX_88": { temp: "95°C", pres: "2800 psi", perm: "800 mD", visc: "210 cP" }
        };

        function updateAssetInfo() {
            const val = document.getElementById('asset-picker').value;
            document.getElementById('meta-temp').textContent = assets[val].temp;
            document.getElementById('meta-pres').textContent = assets[val].pres;
            document.getElementById('meta-perm').textContent = assets[val].perm;
            document.getElementById('meta-visc').textContent = assets[val].visc;
        }

        async function runValidation() {
            const logs = document.getElementById('logs');
            const btn = document.getElementById('run-btn');
            const assetName = document.getElementById('asset-picker').selectedOptions[0].text;
            
            btn.disabled = true; btn.style.opacity = "0.3";
            document.getElementById('term-header').textContent = `RUNNING AGENTS ON ${assetName}...`;
            logs.innerHTML = "";

            const steps = [
                `> Conectando a Data Lake para activo: ${assetName}`,
                "> Agente Física: Validando Ley de Darcy y Reología...",
                "> Agente Metrología: Calculando Incertidumbre P90/P50/P10...",
                "> Ejecutando 10,000 iteraciones Monte Carlo... [OK]",
                "> Generando curvas de recobro incremental...",
                "> SIMULACIÓN EXITOSA."
            ];

            for (const s of steps) {
                const d = document.createElement('div');
                d.textContent = s;
                if(s.includes('OK') || s.includes('EXITOSA')) d.className = "text-white font-bold";
                logs.appendChild(d);
                logs.scrollTop = logs.scrollHeight;
                await new Promise(r => setTimeout(r, 800));
            }

            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('asset-metadata').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            setTimeout(renderPlot, 100);
        }

        function resetDashboard() {
            document.getElementById('results-view').classList.add('hidden');
            document.getElementById('terminal-view').classList.remove('hidden');
            document.getElementById('asset-metadata').classList.remove('hidden');
            document.getElementById('run-btn').disabled = false;
            document.getElementById('run-btn').style.opacity = "1";
            document.getElementById('term-header').textContent = "Awaiting Command...";
            document.getElementById('logs').innerHTML = '<div class="text-slate-600 italic">> Seleccione un activo y presione Iniciar Simulación...</div>';
        }

        function renderPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3000 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
            const data = [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'} },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)' }
            ];
            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('main-chart', data, layout, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
