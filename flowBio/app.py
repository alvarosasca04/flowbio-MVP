import streamlit as st
import streamlit.components.v1 as components

# 1. SETUP DE ALTA PRIORIDAD
st.set_page_config(
    page_title="FlowBio | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. HACK DE UI PARA PANTALLA COMPLETA
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ REFORZADA
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    
    <style>
        :root { --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }
        body { background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
        #map { height: 350px; width: 100%; border-radius: 12px; border: 1px solid var(--border); }
        .btn-action { background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; }
        .btn-action:hover { filter: brightness(1.2); box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
        .terminal { background: #080a0d; border: 1px solid var(--border); border-radius: 8px; font-family: 'JetBrains Mono'; min-height: 120px; }
        .hidden { display: none !important; }
        .reveal { animation: revealEffect 0.6s ease-out forwards; }
        @keyframes revealEffect { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="p-4 flex flex-col gap-4 overflow-hidden">

    <header class="flex justify-between items-center glass px-8 py-4">
        <span class="text-2xl font-black text-white uppercase tracking-tighter italic">Flow<span class="text-emerald-500">Bio</span></span>
        <button onclick="startAgents()" id="run-btn" class="hidden btn-action px-8 py-2 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Agentes </button>
    </header>

    <div id="main-container" class="flex-1 flex flex-col gap-4 overflow-y-auto pr-2">
        <div id="map-section" class="glass p-2">
            <div id="map"></div>
        </div>

        <div id="meta-panel" class="hidden grid grid-cols-5 gap-4 reveal">
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Well_ID</p><p id="v-id" class="mono text-emerald-500 text-[11px] font-bold">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Infraestructura</p><p id="v-infra" class="mono text-white text-[11px]">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Químico</p><p id="v-chem" class="mono text-white text-[11px]">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Temp</p><p id="v-temp" class="mono text-white text-[11px]">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Presión</p><p id="v-pres" class="mono text-white text-[11px]">--</p></div>
        </div>

        <div id="terminal-view" class="glass terminal p-6 mono text-[12px] text-emerald-500/80">
            <div id="term-content">> Seleccione un activo en el mapa para sincronizar telemetría...</div>
        </div>

        <div id="results-view" class="hidden flex flex-col gap-4 pb-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">Incremental</p><h2 class="mono text-3xl font-bold text-emerald-500">+22,500</h2></div>
                <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">NPV Proyectado</p><h2 class="mono text-4xl font-bold text-white">$1.46M</h2></div>
                <div class="glass p-5"><p class="text-[9px] uppercase tracking-widest text-slate-500">Incertidumbre</p><h2 class="mono text-3xl font-bold text-slate-600">±2.1%</h2></div>
            </div>
            <div class="glass p-6 h-80">
                <div id="main-plot" class="w-full h-full"></div>
            </div>
            <button onclick="location.reload()" class="text-[10px] text-slate-700 hover:text-white mono uppercase">← Reiniciar Simulación</button>
        </div>
    </div>

    <script>
        const DATABASE = [
            { id: "FB-PRD-101", lat: 57.1, lng: 1.2, infra: "Vertical ESP", chem: "HPAM", temp: "84°C", pres: "3240 psi" },
            { id: "FB-PRD-102", lat: 57.15, lng: 1.25, infra: "Horizontal", chem: "Bio-P", temp: "89°C", pres: "3100 psi" },
            { id: "FB-INJ-205", lat: 58.4, lng: 0.5, infra: "Smart Well", chem: "Xanthan", temp: "77°C", pres: "2950 psi" }
        ];

        let map = L.map('map').setView([57.5, 1.0], 6);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);
        let markers = L.markerClusterGroup();

        DATABASE.forEach(w => {
            const m = L.marker([w.lat, w.lng]);
            m.on('click', () => {
                document.getElementById('v-id').textContent = w.id;
                document.getElementById('v-infra').textContent = w.infra;
                document.getElementById('v-chem').textContent = w.chem;
                document.getElementById('v-temp').textContent = w.temp;
                document.getElementById('v-pres').textContent = w.pres;
                document.getElementById('meta-panel').classList.remove('hidden');
                document.getElementById('run-btn').classList.remove('hidden');
                document.getElementById('term-content').innerHTML = `> Activo ${w.id} vinculado. Presione EJECUTAR AGENTES.`;
            });
            markers.addLayer(m);
        });
        map.addLayer(markers);

        async function startAgents() {
            const t = document.getElementById('term-content');
            const btn = document.getElementById('run-btn');
            btn.classList.add('hidden');
            t.innerHTML = "";
            
            const msgs = [
                "> Conectando a Data Lake S3... OK",
                "> Agente Metrología: Validando sensores...",
                "> Agente Física: Resolviendo tensores PIML...",
                "> Ejecutando 10k iteraciones Monte Carlo...",
                "> SIMULACIÓN COMPLETADA EXITOSAMENTE."
            ];

            for (const m of msgs) {
                const d = document.createElement('div');
                d.textContent = m;
                t.appendChild(d);
                await new Promise(r => setTimeout(r, 600));
            }

            // ACCIÓN CRÍTICA: OCULTAR TODO Y MOSTRAR RESULTADOS
            document.getElementById('map-section').classList.add('hidden');
            document.getElementById('meta-panel').classList.add('hidden');
            document.getElementById('terminal-view').classList.add('hidden');
            
            const resView = document.getElementById('results-view');
            resView.classList.remove('hidden');
            resView.classList.add('reveal');
            
            renderPlot();
        }

        function renderPlot() {
            const x = Array.from({length: 36}, (_, i) => i + 1);
            Plotly.newPlot('main-plot', [
                { x: x, y: x.map(m => 3500 * Math.exp(-0.06 * m)), type: 'scatter', line: {color: '#f43f5e', width: 2, dash: 'dot'}, name: 'Base' },
                { x: x, y: x.map((m, i) => m < 12 ? 3500 * Math.exp(-0.06 * m) : 3100 * Math.exp(-0.025 * (m - 12))), type: 'scatter', line: {color: '#10b981', width: 4}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)', name: 'FlowBio' }
            ], {
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40}, showlegend: false,
                xaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} },
                yaxis: { gridcolor: '#1e262f', tickfont: {color: '#4b5563', size: 9} }
            }, {responsive: true, displayModeBar: false});
        }
        lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. LANZAMIENTO
components.html(html_code, height=1200, scrolling=False)
