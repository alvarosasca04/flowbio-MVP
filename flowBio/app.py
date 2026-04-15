import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE PÁGINA (ESTRICTO)
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
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { background-color: #0b0f13; color: #f3f4f6; font-family: sans-serif; margin: 0; overflow: hidden; height: 100vh; width: 100vw; }
        .glass { background: #141a21; border: 1px solid #1e262f; border-radius: 12px; }
        .btn-main { background: #10b981; color: #000; font-weight: 900; text-transform: uppercase; border-radius: 12px; cursor: pointer; border: none; transition: 0.2s; }
        .btn-main:hover { filter: brightness(1.2); box-shadow: 0 0 30px rgba(16, 185, 129, 0.4); }
        .hidden { display: none !important; }
        .terminal { background: #080a0d; border: 1px solid #1e262f; border-radius: 8px; font-family: monospace; color: #10b981; }
        input[type=range] { width: 100%; cursor: pointer; }
    </style>
</head>
<body>

    <div id="view-landing" class="flex flex-col justify-center items-center h-screen w-screen text-center p-10 bg-[#080a0d] z-50">
        <h1 class="text-7xl md:text-9xl font-black text-white italic mb-12">FLOWBIO<span class="text-emerald-500">.</span>IA</h1>
        <button onclick="startFlow()" class="btn-main px-16 py-6 text-sm tracking-widest shadow-2xl">
            INICIALIZAR INSTANCIA CLOUD
        </button>
    </div>

    <div id="view-config" class="hidden flex flex-col p-10 max-w-5xl mx-auto space-y-8">
        <h2 class="text-3xl font-bold text-white uppercase italic">Configuración de Activo</h2>
        <div class="grid grid-cols-2 gap-6">
            <div class="glass p-8">
                <p class="text-[10px] text-emerald-500 font-bold mb-4 uppercase">Químico EOR</p>
                <select class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white">
                    <option>HPAM (Tradicional)</option>
                    <option>FlowBio S3 (Bio)</option>
                </select>
            </div>
            <div class="glass p-8">
                <p class="text-[10px] text-emerald-500 font-bold mb-4 uppercase">Infraestructura</p>
                <select class="w-full bg-[#080a0d] border border-[#1e262f] p-3 rounded text-white">
                    <option>Vertical ESP</option>
                    <option>Horizontal Pad</option>
                </select>
            </div>
        </div>
        <div class="glass p-10 flex flex-col space-y-6">
            <p class="text-[10px] text-slate-500 uppercase">Parámetros Físicos del Yacimiento</p>
            <input type="range" min="10" max="2000" value="450">
            <input type="range" min="1" max="500" value="120">
            <button onclick="runSimulation()" class="btn-main py-4 text-xs mt-4">⚡ Desplegar Agentes en AWS</button>
        </div>
    </div>

    <div id="view-terminal" class="hidden flex flex-col justify-center h-screen p-20">
        <div class="terminal flex-1 p-10 text-sm leading-relaxed overflow-y-auto" id="log-box"></div>
    </div>

    <div id="view-dashboard" class="hidden flex flex-col p-6 space-y-6 overflow-y-auto">
        <div class="glass p-8 h-96" id="chart-div"></div>
        <div class="grid grid-cols-3 gap-6">
            <div class="glass p-8 text-center"><p class="text-slate-500 text-[10px] uppercase">Extra</p><h3 class="text-4xl font-bold text-emerald-500">+25,000</h3></div>
            <div class="glass p-8 text-center"><p class="text-slate-500 text-[10px] uppercase">NPV</p><h3 class="text-4xl font-bold text-white">$1.7M</h3></div>
            <div class="glass p-8 text-center"><p class="text-slate-500 text-[10px] uppercase">Fee</p><h3 class="text-4xl font-bold text-white">$75K</h3></div>
        </div>
    </div>

    <script>
        // FUNCIÓN DEL PRIMER BOTÓN
        function startFlow() {
            console.log("Clic detectado en Landing");
            document.getElementById('view-landing').classList.add('hidden');
            document.getElementById('view-config').classList.remove('hidden');
        }

        // FUNCIÓN DE SIMULACIÓN
        async function runSimulation() {
            document.getElementById('view-config').classList.add('hidden');
            document.getElementById('view-terminal').classList.remove('hidden');
            const box = document.getElementById('log-box');
            const logs = [
                "> Conectando a AWS US-EAST-1...",
                "> Agente Física: Procesando tensores...",
                "> Agente Financiero: Validando NPV...",
                "> SISTEMA LISTO."
            ];
            for (let l of logs) {
                let d = document.createElement('div');
                d.textContent = l;
                box.appendChild(d);
                await new Promise(r => setTimeout(r, 800));
            }
            document.getElementById('view-terminal').classList.add('hidden');
            document.getElementById('view-dashboard').classList.remove('hidden');
            renderPlot();
        }

        function renderPlot() {
            const x = Array.from({length: 40}, (_, i) => i);
            const y1 = x.map(v => 3000 * Math.exp(-0.06 * v));
            const y2 = x.map((v, i) => i < 10 ? y1[i] : y1[i] + 1200 * Math.exp(-0.02 * (i-10)));
            Plotly.newPlot('chart-div', [
                {x: x, y: y1, type: 'scatter', line: {color: '#f43f5e', dash: 'dot'}},
                {x: x, y: y2, type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16,185,129,0.1)'}
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 20, t: 20, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f' }, yaxis: { gridcolor: '#1e262f' }
            });
        }
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO (SIN SCROLLING PARA EVITAR CONFLICTOS)
components.html(html_code, height=2000, scrolling=False)
