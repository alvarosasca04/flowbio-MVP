import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA
st.set_page_config(
    page_title="FlowBio Intelligence",
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
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background-color: var(--bg); color: #f3f4f6; font-family: sans-serif; margin: 0; overflow: hidden; height: 100vh; width: 100vw; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        .btn-main { background: var(--primary); color: #000; font-weight: 900; text-transform: uppercase; border-radius: 12px; cursor: pointer; border: none; transition: 0.2s; }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
        .hidden { display: none !important; }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: monospace; color: #10b981; }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 bg-[#080a0d]">
        <h1 class="text-7xl md:text-9xl font-black text-white italic mb-12 tracking-tighter">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
        <button id="btn-start" class="btn-main px-20 py-6 text-sm tracking-widest">
            INICIALIZAR INSTANCIA CLOUD
        </button>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-6xl mx-auto space-y-8">
        <h2 class="text-3xl font-bold text-white uppercase italic">Configuración de Activo</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="glass p-8 space-y-6">
                <div>
                    <label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2">Químico EOR</label>
                    <select id="chem-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none">
                        <option value="HPAM Tradicional">HPAM (Polímero Tradicional)</option>
                        <option value="FlowBio S3">FlowBio S3 (Bio-Polímero)</option>
                    </select>
                </div>
                <div>
                    <label class="text-[10px] font-bold text-emerald-500 uppercase block mb-2">Infraestructura</label>
                    <select id="infra-input" class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white text-xs outline-none">
                        <option value="Vertical ESP">Vertical ESP</option>
                        <option value="Horizontal Pad">Horizontal Pad</option>
                    </select>
                </div>
            </div>
            <div class="glass p-8 space-y-6">
                <div>
                    <div class="flex justify-between text-[10px] mb-2 font-bold"><span>Permeabilidad (mD)</span><span id="k-label" class="text-emerald-500">450</span></div>
                    <input type="range" id="k-input" min="50" max="1500" value="450" class="w-full">
                </div>
                <div>
                    <div class="flex justify-between text-[10px] mb-2 font-bold"><span>Viscosidad (cP)</span><span id="v-label" class="text-emerald-500">120</span></div>
                    <input type="range" id="v-input" min="10" max="500" value="120" class="w-full">
                </div>
            </div>
        </div>
        <div class="flex justify-center"><button id="btn-run" class="btn-main px-16 py-5 text-xs">⚡ Desplegar Agentes en AWS</button></div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen max-w-4xl mx-auto p-10">
        <div class="terminal flex-1 p-10 text-sm leading-relaxed overflow-y-auto" id="log-box"></div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6 overflow-y-auto">
        <div class="glass p-8 h-96" id="chart-div"></div>
        <div class="grid grid-cols-3 gap-6">
            <div class="glass p-8 text-center"><p class="text-slate-500 text-[10px] uppercase">Extra</p><h3 id="res-extra" class="text-4xl font-bold text-emerald-500">--</h3></div>
            <div class="glass p-8 text-center"><p class="text-slate-500 text-[10px] uppercase">NPV</p><h3 id="res-npv" class="text-4xl font-bold text-white">--</h3></div>
            <div class="glass p-8 text-center"><p class="text-slate-500 text-[10px] uppercase">Fee</p><h3 id="res-fee" class="text-4xl font-bold text-white">--</h3></div>
        </div>
    </div>

    <script>
        // MANEJO DE EVENTOS (Blindado)
        document.addEventListener('DOMContentLoaded', function() {
            
            // 1. Al mover Sliders
            const kIn = document.getElementById('k-input');
            const vIn = document.getElementById('v-input');
            kIn.oninput = () => { document.getElementById('k-label').innerText = kIn.value; };
            vIn.oninput = () => { document.getElementById('v-label').innerText = vIn.value; };

            // 2. Botón Entrar
            document.getElementById('btn-start').onclick = function() {
                document.getElementById('view-landing').classList.add('hidden');
                document.getElementById('view-config').classList.remove('hidden');
            };

            // 3. Botón Simular
            document.getElementById('btn-run').onclick = async function() {
                const k = parseFloat(kIn.value);
                const v = parseFloat(vIn.value);
                
                document.getElementById('view-config').classList.add('hidden');
                document.getElementById('view-terminal').classList.remove('hidden');
                
                const box = document.getElementById('log-box');
                const logs = ["> Conectando AWS...", "> Agente Física (PIML): Analizando K=" + k + "...", "> Agente Financiero: ROI ready...", "> SISTEMA LISTO."];
                
                for (let l of logs) {
                    let d = document.createElement('div');
                    d.textContent = l;
                    box.appendChild(d);
                    await new Promise(r => setTimeout(r, 800));
                }

                document.getElementById('view-terminal').classList.add('hidden');
                document.getElementById('view-dashboard').classList.remove('hidden');
                
                // CÁLCULOS DINÁMICOS
                const extra = Math.round((k / v) * 2000);
                const npv = (extra * 68) / 1000000;
                document.getElementById('res-extra').innerText = "+" + extra.toLocaleString() + " bbls";
                document.getElementById('res-npv').innerText = "$" + npv.toFixed(2) + "M";
                document.getElementById('res-fee').innerText = "$" + Math.round(npv * 1000000 * 0.05).toLocaleString();
                
                renderPlot(extra);
            };
        });

        function renderPlot(extra) {
            const x = Array.from({length: 40}, (_, i) => i);
            const y1 = x.map(v => 3000 * Math.exp(-0.06 * v));
            const y2 = x.map((v, i) => i < 10 ? y1[i] : y1[i] + (extra/50) * Math.exp(-0.02 * (i-10)));
            Plotly.newPlot('chart-div', [
                {x: x, y: y1, type: 'scatter', line: {color: '#f43f5e', dash: 'dot'}},
                {x: x, y: y2, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16,185,129,0.1)'}
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 20, t: 20, b: 40}, showlegend: false,
                font: {color: '#64748b'}, xaxis: { gridcolor: '#1e262f' }, yaxis: { gridcolor: '#1e262f' }
            }, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=True)
