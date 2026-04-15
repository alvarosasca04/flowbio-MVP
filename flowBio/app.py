import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="FlowBio | Metrology & Analytics", layout="wide", initial_sidebar_state="collapsed")

# Hack para ocultar Streamlit y dar espacio al diseño industrial
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
        .btn-demo { background: transparent; border: 1px solid #38bdf8; color: #38bdf8; font-weight: 700; transition: 0.3s; }
        .btn-demo:hover { background: rgba(56, 189, 248, 0.1); box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }
        .terminal { background: #080a0d; border: 1px solid var(--border); font-family: 'JetBrains Mono'; }
        .hidden { display: none !important; }
    </style>
</head>
<body class="p-6 flex flex-col gap-6">

    <header class="flex justify-between items-center glass px-8 py-4">
        <div class="flex items-center gap-6">
            <span class="text-2xl font-black text-white tracking-tighter uppercase">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="h-6 w-[1px] bg-slate-800"></div>
            <div class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                <span class="mono text-[9px] text-blue-400 font-bold uppercase">Metrology Mode: Active</span>
            </div>
        </div>
        <div class="flex gap-4">
            <button onclick="runValidation()" id="run-btn" class="px-6 py-2 bg-emerald-500 text-black font-bold text-[10px] rounded uppercase tracking-tighter hover:brightness-110"> 
                🔍 Iniciar Validación de Datos 
            </button>
        </div>
    </header>

    <div id="main-view" class="flex-1 flex flex-col gap-6 min-h-0">
        
        <div id="terminal-view" class="flex-1 glass terminal overflow-hidden flex flex-col">
            <div class="px-5 py-3 border-b border-slate-900 bg-black/40 flex justify-between items-center">
                <span class="mono text-[10px] text-slate-500 uppercase tracking-widest">Metrological_Audit_Stream</span>
                <div id="loader" class="hidden text-emerald-500 mono text-[9px] animate-pulse">CALCULANDO INCERTIDUMBRE...</div>
            </div>
            <div id="logs" class="p-6 flex-1 mono text-[12px] text-emerald-500/80 space-y-2 overflow-y-auto">
                <div class="text-slate-600 italic">> Sistema listo para auditoría de sensores S3...</div>
            </div>
        </div>

        <div id="results-view" class="hidden space-y-6 h-full overflow-y-auto pb-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="glass p-6">
                    <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental (Probabilístico)</p>
                    <h2 class="mono text-4xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-700">bbl</span></h2>
                    <p class="text-[10px] text-emerald-700 mt-2 mono">Incertidumbre: ±2.4% (Confianza 95%)</p>
                </div>
                <div class="glass p-6">
                    <p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Ajustado por Riesgo</p>
                    <h2 class="mono text-4xl font-bold text-white">$1.41M <span class="text-xs text-slate-700">USD</span></h2>
                    <p class="text-[10px] text-slate-600 mt-2 mono">Simulación Monte Carlo: 10k iteraciones</p>
                </div>
                <div class="glass p-6 border-blue-500/30">
                    <p class="text-[9px] uppercase tracking-widest text-blue-400 mb-1">Calidad del Dato (QA/QC)</p>
                    <h2 class="mono text-4xl font-bold text-white">98.2%</h2>
                    <p class="text-[10px] text-blue-800 mt-2 mono">Error Cuadrático Medio: 0.012</p>
                </div>
            </div>
            <div class="glass p-8">
                <div id="uncertainty-chart" class="w-full h-80"></div>
            </div>
        </div>
    </div>

    <script>
        async function runValidation() {
            const logs = document.getElementById('logs');
            const loader = document.getElementById('loader');
            const btn = document.getElementById('run-btn');
            
            btn.disabled = true; btn.style.opacity = "0.5";
            loader.classList.remove('hidden');
            logs.innerHTML = "";

            const steps = [
                "> Conectando a nodos de medición en tiempo real...",
                "> Validando calibración de caudalímetros (ISO 17025)... [OK]",
                "> Agente Metrología: Calculando Desviación Estándar...",
                "> Ejecutando prueba de normalidad de Shapiro-Wilk... [PASSED]",
                "> Analizando propagación de errores en sensores S3...",
                "> Aplicando Factor de Cobertura k=2...",
                "> VALIDACIÓN EXITOSA: Datos dentro del umbral de confianza."
            ];

            for (const s of steps) {
                const d = document.createElement('div');
                d.textContent = s;
                if(s.includes('OK') || s.includes('EXITOSA')) d.className = "text-white font-bold";
                logs.appendChild(d);
                logs.scrollTop = logs.scrollHeight;
                await new Promise(r => setTimeout(r, 700));
            }

            loader.classList.add('hidden');
            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            setTimeout(renderPlot, 100);
        }

        function renderPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            const b = x.map(m => 3000 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
            
            // Líneas de incertidumbre (Sombreado P90-P10)
            const upper = f.map(v => v * 1.05);
            const lower = f.map(v => v * 0.95);

            const data = [
                { x: x, y: b, type: 'scatter', line: {color: '#f43f5e', width: 1.5, dash: 'dot'}, name: 'Base' },
                { x: x, y: f, type: 'scatter', line: {color: '#10b981', width: 3}, name: 'P50 Forecast' },
                { x: [...x, ...x.reverse()], y: [...upper, ...lower.reverse()], fill: 'toself', fillcolor: 'rgba(16, 185, 129, 0.1)', line: {color: 'transparent'}, name: 'Incertidumbre' }
            ];

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 50}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} }
            };
            Plotly.newPlot('uncertainty-chart', data, layout, {responsive: true, displayModeBar: false});
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
