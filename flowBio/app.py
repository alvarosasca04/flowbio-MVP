import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import boto3
import json
from io import StringIO

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="FlowBio | Cloud Asset Manager",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- FUNCIÓN PARA CARGAR DATOS DESDE AMAZON S3 ---
def load_data_from_s3():
    bucket_name = "tu-bucket-nombre" # <--- CAMBIA ESTO
    file_key = "base_datos_pozos.csv"   # <--- CAMBIA ESTO
    
    try:
        # Usamos las secretas de Streamlit para mayor seguridad
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["AWS_REGION"]
        )
        
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        
        # Mapeo de columnas para asegurar compatibilidad con el JS
        return df.to_json(orient="records")
    except Exception as e:
        # Si falla S3, cargamos un backup para que la UI no muera
        backup = [{"id": f"ERROR-S3-{i}", "infra": "N/A", "chem": "N/A", "temp": "0", "pres": "0", "status": "Error AWS"} for i in range(1)]
        return json.dumps(backup)

# Cargamos los datos de S3 al iniciar
well_json_data = load_data_from_s3()

# 2. HACK DE UI (BYPASS STREAMLIT)
st.markdown("""
    <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        .stApp {margin: 0; padding: 0; background-color: #0b0f13;}
        .block-container {padding: 0 !important; max-width: 100vw !important;}
        iframe {position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; z-index: 999;}
    </style>
""", unsafe_allow_html=True)

# 3. INTERFAZ INTEGRAL (HTML/JS)
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
        .search-box {{ background: #080a0d; border: 1px solid var(--border); transition: 0.3s; }}
        .search-box:focus-within {{ border-color: var(--primary); box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }}
        .suggestion-card {{ cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: 0.2s; }}
        .suggestion-card:hover {{ background: rgba(16, 185, 129, 0.15); transform: translateX(5px); }}
        .btn-action {{ background: var(--primary); color: #000; font-weight: 800; text-transform: uppercase; transition: 0.3s; cursor: pointer; }}
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>

    <div id="page-home" class="h-screen w-full flex flex-col justify-center items-center text-center p-10 bg-[#080a0d]">
        <h1 class="text-8xl font-black text-white tracking-tighter uppercase italic">FlowBio<span class="text-emerald-500">.</span>IA</h1>
        <p class="text-xl text-slate-500 font-light mt-4">Cloud Native EOR Intelligence System</p>
        <button onclick="nav('dashboard')" class="btn-action mt-10 px-12 py-4 rounded-md tracking-widest text-xs"> Inicializar Centro de Comando </button>
    </div>

    <div id="page-dashboard" class="hidden h-screen w-full flex flex-col p-6 gap-6">
        <header class="flex justify-between items-center glass px-8 py-5">
            <div class="flex items-center gap-8">
                <span class="text-2xl font-black text-white uppercase tracking-tighter">Flow<span class="text-emerald-500">Bio</span></span>
                <div class="relative w-96">
                    <div class="flex items-center gap-3 search-box px-4 py-2 rounded-lg">
                        <i data-lucide="search" class="w-4 h-4 text-slate-500"></i>
                        <input type="text" id="well-search" placeholder="Buscando en S3..." 
                               class="bg-transparent text-xs w-full outline-none text-white mono" 
                               onfocus="showAll()" oninput="filter()">
                    </div>
                    <div id="search-results" class="absolute top-full left-0 right-0 mt-2 glass max-h-64 overflow-y-auto z-50 hidden">
                        <div id="results-list"></div>
                    </div>
                </div>
            </div>
            <button onclick="nav('home')" class="text-[10px] mono text-slate-500 hover:text-white uppercase transition-all">Cerrar Sesión</button>
        </header>

        <div id="workspace" class="flex-1 flex flex-col gap-6">
            <div id="meta-panel" class="hidden grid grid-cols-5 gap-4">
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Infraestructura</p><p id="v-infra" class="mono text-white text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Químico</p><p id="v-chem" class="mono text-white text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Well_ID</p><p id="v-id" class="mono text-emerald-500 text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Temp</p><p id="v-temp" class="mono text-white text-[11px]">--</p></div>
                <div class="glass p-4"><p class="text-[8px] text-slate-500 uppercase">Presión</p><p id="v-pres" class="mono text-white text-[11px]">--</p></div>
            </div>
            <div id="terminal" class="flex-1 glass bg-[#080a0d] p-6 mono text-[12px] text-emerald-500/80 overflow-y-auto leading-relaxed">
                > Sistema conectado a Amazon S3. Listo para búsqueda de activos...
            </div>
        </div>
    </div>

    <script>
        const DATABASE = {well_json_data};

        function nav(p) {{
            document.getElementById('page-home').classList.toggle('hidden', p !== 'home');
            document.getElementById('page-dashboard').classList.toggle('hidden', p !== 'dashboard');
            lucide.createIcons();
        }}

        function showAll() {{
            document.getElementById('search-results').classList.remove('hidden');
            render(DATABASE);
        }}

        function filter() {{
            const q = document.getElementById('well-search').value.toUpperCase();
            const fil = DATABASE.filter(w => w.id.toString().includes(q));
            render(fil);
        }}

        function render(items) {{
            const list = document.getElementById('results-list');
            list.innerHTML = items.map(w => `
                <div class="suggestion-card p-4 flex justify-between items-center" onclick="select('${{w.id}}')">
                    <div>
                        <div class="text-xs font-bold text-white mono">${{w.id}}</div>
                        <div class="text-[9px] text-slate-500 mono">${{w.infra}}</div>
                    </div>
                </div>
            `).join('');
        }}

        function select(id) {{
            const w = DATABASE.find(x => x.id.toString() === id.toString());
            document.getElementById('search-results').classList.add('hidden');
            document.getElementById('well-search').value = id;
            document.getElementById('v-id').textContent = id;
            document.getElementById('v-infra').textContent = w.infra;
            document.getElementById('v-chem').textContent = w.chem;
            document.getElementById('v-temp').textContent = w.temp;
            document.getElementById('v-pres').textContent = w.pres;
            document.getElementById('meta-panel').classList.remove('hidden');
            document.getElementById('terminal').innerHTML = "> Activo " + id + " validado desde S3 Cloud.";
        }}
    </script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)
