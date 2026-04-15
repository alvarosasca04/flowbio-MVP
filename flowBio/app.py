import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO)
st.set_page_config(
    page_title="FlowBio Intelligence | Agentic OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. LIMPIEZA DE INTERFAZ STREAMLIT
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {display: none;}
        .block-container {padding: 0px; max-width: 100%; height: 100vh;}
        iframe {border: none; width: 100%; height: 100vh;}
    </style>
""", unsafe_allow_html=True)

# 3. CÓDIGO HTML/CSS/JS COMPLETO
html_content = """
<!doctype html>
<html lang="es" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body { height: 100%; margin: 0; padding: 0; background: #0d1117; overflow-x: hidden; scroll-behavior: smooth; }
        * { font-family: 'Outfit', sans-serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .gradient-text { background: linear-gradient(90deg, #00E5FF, #39FF14); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .glow-border { box-shadow: 0 0 30px rgba(0,229,255,0.08); border: 1px solid rgba(48, 54, 61, 0.8); }
        .terminal-window { background: #010409; border: 1px solid #30363d; border-radius: 12px; font-family: 'JetBrains Mono', monospace; }
        .glass { background: rgba(22, 27, 34, 0.75); backdrop-filter: blur(12px); }
        .hidden { display: none !important; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        .fade-up { animation: fadeUp 0.6s ease-out forwards; }
    </style>
</head>
<body class="text-[#e6edf3]">
    <div id="page-home" class="min-h-screen w-full flex flex-col justify-center items-center relative p-6">
        <div class="absolute inset-0" style="background: radial-gradient(circle at center, #1a1f2e 0%, #0d1117 100%);"></div>
        <div class="relative z-10 text-center fade-up">
            <span class="mono text-[10px] tracking-[0.3em] text-[#00E5FF] uppercase border border-[#00E5FF]/30 px-4 py-1.5 rounded-full">PIML Framework v4.0</span>
            <h1 class="text-6xl md:text-8xl font-black gradient-text mt-8 mb-4">FlowBio</h1>
            <p class="text-xl text-[#8b949e] max-w-2xl mx-auto mb-12 font-light">Orquestación de Agentes de IA para Optimización de Recuperación Secundaria</p>
            <button onclick="showPage('dashboard')" class="px-10 py-4 rounded-xl font-bold text-white tracking-widest transition-all hover:scale-105" style="background: linear-gradient(135deg, #00E5FF, #0077FF); box-shadow: 0 0 30px rgba(0,229,255,0.3);">
                ✨ ENTRAR AL DASHBOARD DE COMANDO
            </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden min-h-screen w-full flex">
        <aside class="w-72 border-r border-[#30363d] flex flex-col p-6 glass sticky top-0 h-screen">
            <h2 class="gradient-text text-2xl font-black mb-8">🧬 FlowBio</h2>
            <nav class="space-y-4 flex-1">
                <div class="text-[10px] text-[#6e7681] uppercase tracking-widest mb-4">Módulos de Agente</div>
                <div class="flex items-center gap-3 p-3 rounded-lg bg-[#161b22] text-[#00E5FF] border border-[#00E5FF]/20">
                    <i data-lucide="layout-dashboard" class="w-4 h-4"></i> <span class="text-sm font-bold">Overview</span>
                </div>
                <div class="flex items-center gap-3 p-3 rounded-lg text-[#8b949e] hover:bg-[#161b22] transition-all cursor-not-allowed">
                    <i data-lucide="map" class="w-4 h-4"></i> <span class="text-sm">Geospatial</span>
                </div>
            </nav>
            <button onclick="showPage('home')" class="mt-auto flex items-center gap-2 text-xs text-[#6e7681] hover:text-white transition-all">
                <i data-lucide="log-out" class="w-3 h-3"></i> Salir al Menú Principal
            </button>
        </aside>

        <main class="flex-1 p-8 overflow-y-auto">
            <header class="flex justify-between items-end mb-8">
                <div>
                    <h1 class="text-3xl font-bold">Dashboard de Comando <span class="text-[#00E5FF]">EOR</span></h1>
                    <p class="text-sm text-[#6e7681] mono mt-1">Status: Conectado a AWS S3 Cluster_01</p>
                </div>
                <div class="flex gap-4">
                    <button class="px-4 py-2 border border-[#30363d] rounded-lg text-xs hover:bg-[#161b22] transition-all">📄 Exportar PDF</button>
                    <button class="px-4 py-2 bg-[#00E5FF] text-black font-bold rounded-lg text-xs">🚀 Re-Simular</button>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="glass p-6 rounded-2xl glow-border">
                    <p class="text-[10px] text-[#6e7681] uppercase tracking-widest mb-2">Incremental Estimado</p>
                    <h3 class="text-4xl font-black text-[#39FF14]">+22,500 <span class="text-lg">bbls</span></h3>
                </div>
                <div class="glass p-6 rounded-2xl glow-border">
                    <p class="text-[10px] text-[#6e7681] uppercase tracking-widest mb-2">Ganancia Operativa Adicional</p>
                    <h3 class="text-4xl font-black text-white">$1.5M <span class="text-lg uppercase text-[#6e7681]">usd</span></h3>
                </div>
                <div class="glass p-6 rounded-2xl border-[#00E5FF]/30">
                    <p class="text-[10px] text-[#00E5FF] uppercase tracking-widest mb-2">Success Fee (5%)</p>
                    <h3 class="text-4xl font-black text-[#00E5FF]">$67,500 <span class="text-lg">usd</span></h3>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="glass p-6 rounded-2xl glow-border">
                    <h4 class="text-sm font-bold mb-4 flex items-center gap-2"><i data-lucide="trending-up" class="w-4 h-4"></i> Curva de Declinación vs FlowBio</h4>
                    <div id="chart-dca" class="w-full h-64"></div>
                </div>
                <div class="terminal-window p-6 overflow-hidden flex flex-col">
                    <div class="flex gap-2 mb-4">
                        <div class="w-2 h-2 rounded-full bg-[#ff5f56]"></div>
                        <div class="w-2 h-2 rounded-full bg-[#ffbd2e]"></div>
                        <div class="w-2 h-2 rounded-full bg-[#27c93f]"></div>
                    </div>
                    <div class="mono text-[11px] text-[#39FF14] space-y-1 overflow-y-auto h-48" id="console">
                        <div>> Iniciando Enjambre de Agentes...</div>
                        <div>> Conectando con AWS S3 Data Lake... [OK]</div>
                        <div>> Physics Agent: Aplicando Ley de Darcy... [OK]</div>
                        <div>> Financial Agent: Calculando NPV... [OK]</div>
                        <div>> Skin Factor Agent: Optimización finalizada...</div>
                        <div class="animate-pulse">_</div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        function showPage(page) {
            if(page === 'dashboard') {
                document.getElementById('page-home').classList.add('hidden');
                document.getElementById('page-dashboard').classList.remove('hidden');
                renderChart();
            } else {
                document.getElementById('page-home').classList.remove('hidden');
                document.getElementById('page-dashboard').classList.add('hidden');
            }
            lucide.createIcons();
        }

        function renderChart() {
            const months = Array.from({length: 36}, (_, i) => i + 1);
            const baseline = months.map(m => 3000 * Math.exp(-0.06 * m));
            const optimized = months.map((m, i) => m < 12 ? baseline[i] : baseline[i] + 1200 * Math.exp(-0.03 * (m - 12)));

            const trace1 = {
                x: months, y: baseline, name: 'Status Quo',
                type: 'scatter', line: {color: '#ff5f56', width: 2, dash: 'dot'}
            };
            const trace2 = {
                x: months, y: optimized, name: 'FlowBio',
                type: 'scatter', line: {color: '#39FF14', width: 4},
                fill: 'tonexty', fillcolor: 'rgba(57, 255, 20, 0.1)'
            };

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 10, t: 10, b: 40},
                showlegend: false,
                xaxis: {gridcolor: '#1f2937', zeroline: false, tickfont: {color: '#6e7681'}},
                yaxis: {gridcolor: '#1f2937', zeroline: false, tickfont: {color: '#6e7681'}}
            };

            Plotly.newPlot('chart-dca', [trace1, trace2], layout, {responsive: true, displayModeBar: false});
        }

        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDERIZADO FINAL
components.html(html_content, height=1000, scrolling=True)
