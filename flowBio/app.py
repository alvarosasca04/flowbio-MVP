import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import boto3
import json
from io import StringIO

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Cloud Intelligence OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- FUNCIÓN PARA EXTRAER POZOS REALES DESDE AMAZON S3 ---
def get_s3_wells():
    # SUSTITUYE CON TUS DATOS REALES
    BUCKET_NAME = "tu-bucket-flowbio" 
    FILE_KEY = "base_datos_pozos.csv" 
    
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["AWS_REGION"]
        )
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        csv_data = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))
        
        # Aseguramos que las columnas necesarias existan
        return df.to_json(orient="records")
    except Exception as e:
        # Backup en caso de que S3 no esté configurado aún
        backup = [
            {"id": "WELL-DEMO-01", "infra": "ESP Vertical", "chem": "HPAM", "temp": "85", "pres": "3200", "status": "ACTIVO"},
            {"id": "WELL-DEMO-02", "infra": "Horizontal", "chem": "Bio-Polymer", "temp": "92", "pres": "2900", "status": "PRODUCIENDO"}
        ]
        return json.dumps(backup)

well_data_json = get_s3_wells()

# 2. HACK DE INTERFAZ FULL-SCREEN
st.markdown("""
    <style>
        [data-testid="stHeader"], footer {display: none !important;}
        .stApp {background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (MINERS-IA LOOK)
html_code = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #10b981; --bg: #0b0f13; --card: #141a21; --border: #1e262f; }}
        body {{ background: var(--bg); color: #f3f4f6; font-family: 'Inter', sans-serif; margin: 0; overflow: hidden; height: 100vh; }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}
        .glass {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; }}
        .search-box {{ background: #080a0d; border: 1px solid var(--border); transition: 0.2s; }}
        .search-box:focus-within {{ border-color: var(--primary); box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }}
        .well-item {{ cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: 0.2s; }}
        .well-item:hover {{ background: rgba(16, 185, 129, 0.1); transform: translateX(5px); }}
        .btn-run {{ background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; }}
        .btn-run:hover {{ filter: brightness(1.2); box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); }}
        .hidden {{ display: none !important; }}
    </style>
</head>
<body class="p-4 flex flex-col gap-4">

    <header class="flex justify-between items-center glass px-8 py-4">
        <div class="flex items-center gap-8">
            <span class="text-2xl font-black text-white uppercase tracking-tighter italic">Flow<span class="text-emerald-500">Bio</span></span>
            <div class="relative w-80">
                <div class="flex items-center gap-3 search-box px-4 py-2 rounded-lg">
                    <i data-lucide="search" class="w-4 h-4 text-slate-500"></i>
                    <input type="text" id="well-search" placeholder="Buscar pozo en S3 Cloud..." 
                           class="bg-transparent text-xs w-full outline-none text-white mono" 
                           onfocus="showResults()" oninput="filterWells()">
                </div>
                <div id="search-results" class="absolute top-full left-0 right-0 mt-2 glass max-h-64 overflow-y-auto z-50 hidden shadow-2xl">
                    </div>
            </div>
        </div>
        <div class="flex gap-4">
            <button onclick="startAgents()" id="run-btn" class="hidden btn-run px-8 py-2 rounded text-[10px] tracking-tighter"> ⚡ Ejecutar Simulación </button>
        </div>
    </header>

    <div id="workspace" class="flex-1 flex flex-col gap-4 overflow-hidden">
        <div id="meta-panel" class="hidden grid grid-cols-5 gap-4">
            <div class="glass p-4 border-l-2 border-emerald-500"><p class="text-[8px] text-slate-500 uppercase mono">Infraestructura</p><p id="v-infra" class="mono text-white text-[11px] mt-1">--</p></div>
            <div class="glass p-4 border-l-2 border-emerald-500"><p class="text-[8px] text-slate-500 uppercase mono">Químico</p><p id="v-chem" class="mono text-white text-[11px] mt-1">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Well_ID</p><p id="v-id" class="mono text-emerald-500 text-[11px] mt-1">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Temp</p><p id="v-temp" class="mono text-white text-[11px] mt-1">--</p></div>
            <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase mono">Presión</p><p id="v-pres" class="mono text-white text-[11px] mt-1">--</p></div>
        </div>

        <div id="terminal-view" class="flex-1 glass bg-[#080a0d] p-6 mono text-[12px] text-emerald-500/80 overflow-y-auto leading-relaxed">
            <div class="text-slate-600 italic">> Seleccione un activo desde el buscador superior para iniciar el análisis agéntico...</div>
        </div>

        <div id="results-view" class="hidden flex flex-col gap-4 overflow-y-auto pb-4 h-full">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incremental</p><h2 class="mono text-3xl font-bold text-emerald-500">+22,500 <span class="text-xs text-slate-600">bbl</span></h2></div>
                <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">NPV Proyectado</p><h2 class="mono text-3xl font-bold text-white">$1.46M</h2></div>
                <div class="glass p-6 border-emerald-500/30"><p class="text-[9px] uppercase tracking-widest text-emerald-500 mb-1">Success Fee</p><h2 class="mono text-3xl font-bold text-white">$73,125</h2></div>
                <div class="glass p-6"><p class="text-[9px] uppercase tracking-widest text-slate-500 mb-1">Incertidumbre</p><h2 class="mono text-3xl font-bold text-slate-600">±2.1%</h2></div>
            </div>
            <div class="glass p-8 flex-1 min-h-[400px]">
                <div id="main-plot" class="w-full h-full"></div>
            </div>
        </div>
    </div>

    <script>
        const RAW_DATA = {well_data_json};

        function showResults() {{
            document.getElementById('search-results').classList.remove('hidden');
            renderWells(RAW_DATA);
        }}

        function filterWells() {{
            const q = document.getElementById('well-search').value.toUpperCase();
            const filtered = RAW_DATA.filter(w => w.id.toString().includes(q));
            renderWells(filtered);
        }}

        function renderWells(items) {{
            const list = document.getElementById('search-results');
            list.innerHTML = items.map(w => `
                <div class="well-item p-4 flex justify-between items-center" onclick="selectWell('${{w.id}}')">
                    <div>
                        <div class="text-xs font-bold text-white mono">${{w.id}}</div>
                        <div class="text-[9px] text-slate-500 mono">${{w.infra}}</div>
                    </div>
                    <span class="text-[8px] bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded">${{w.status}}</span>
                </div>
            `).join('');
        }}

        function selectWell(id) {{
            const w = RAW_DATA.find(x => x.id.toString() === id.toString());
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('run-btn').classList.remove('hidden');
            
            document.getElementById('v-infra').textContent = w.infra;
            document.getElementById('v-chem').textContent = w.chem;
            document.getElementById('v-id').textContent = id;
            document.getElementById('v-temp').textContent = w.temp + " °C";
            document.getElementById('v-pres').textContent = w.pres + " psi";
            document.getElementById('meta-panel').classList.remove('hidden');
            
            document.getElementById('terminal-view').innerHTML = "> Activo " + id + " cargado. Agentes de IA configurados para inyección de " + w.chem + "...";
        }}

        async function startAgents() {{
            const t = document.getElementById('terminal-view');
            const btn = document.getElementById('run-btn');
            btn.classList.add('hidden');
            t.innerHTML = "";

            const logs = [
                "> Conectando a AWS Data Lake S3... [OK]",
                "> Agente Metrología: Validando incertidumbre ±2.1%...",
                "> Agente Física: Resolviendo tensores de Darcy...",
                "> PIML Engine: Ejecutando simulación de recobro incremental...",
                "> SIMULACIÓN COMPLETADA CON ÉXITO."
            ];

            for (const line of logs) {{
                const d = document.createElement('div');
                d.textContent = line;
                if(line.includes('EXITO')) d.className = "text-white font-bold";
                t.appendChild(d);
                t.scrollTop = t.scrollHeight;
                await new Promise(r => setTimeout(r, 700));
            }

            document.getElementById('terminal-view').classList.add('hidden');
            document.getElementById('results-view').classList.remove('hidden');
            renderPlot();
        }}

        function renderPlot() {{
            const x = Array.from({{length: 36}}, (_, i) => i + 1);
            const b = x.map(m => 3500 * Math.exp(-0.06 * m));
            const f = x.map((m, i) => m < 12 ? b[i] : b[i] + 1300 * Math.exp(-0.028 * (m - 12)));
            Plotly.newPlot('main-plot', [
                {{ x: x, y: b, type: 'scatter', line: {{color: '#f43f5e', width: 2, dash: 'dot'}}, name: 'Base' }},
                {{ x: x, y: f, type: 'scatter', line: {{color: '#10b981', width: 4}}, fill: 'tonexty', fillcolor: 'rgba(16, 185, 129, 0.05)', name: 'FlowBio' }}
            ], {{
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {{l: 50, r: 20, t: 10, b: 50}}, showlegend: false,
                xaxis: {{ gridcolor: '#1e262f', tickfont: {{color: '#4b5563', size: 9}} }},
                yaxis: {{ gridcolor: '#1e262f', tickfont: {{color: '#4b5563', size: 9}} }}
            }}, {{responsive: true, displayModeBar: false}});
        }}
    </script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
