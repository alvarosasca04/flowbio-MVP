import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO)
st.set_page_config(
    page_title="FlowBio Intelligence | Command Center",
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

# 3. CÓDIGO HTML/CSS/JS (ESTÉTICA CANVA IA)
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
        .glass { background: rgba(22, 27, 34, 0.85); backdrop-filter: blur(12px); }
        .hidden { display: none !important; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        .fade-up { animation: fadeUp 0.6s ease-out forwards; }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #0d1117; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    </style>
</head>
<body class="text-[#e6edf3]">
    <div id="page-home" class="min-h-screen w-full flex flex-col justify-center items-center relative p-6">
        <div class="absolute inset-0" style="background: radial-gradient(circle at center, #1a1f2e 0%, #0d1117 100%);"></div>
        <div class="relative z-10 text-center fade-up">
            <span class="mono text-[10px] tracking-[0.3em] text-[#00E5FF] uppercase border border-[#00E5FF]/30 px-4 py-1.5 rounded-full">Autonomous EOR Framework</span>
            <h1 class="text-6xl md:text-8xl font-black gradient-text mt-8 mb-4">FlowBio</h1>
            <p class="text-xl text-[#8b949e] max-w-2xl mx-auto mb-12 font-light italic">"Physics-Informed Machine Learning for Subsurface Excellence"</p>
            <button onclick="showPage('dashboard')" class="px-10 py-4 rounded-xl font-bold text-white tracking-widest transition-all hover:scale-105" style="background: linear-gradient(135deg, #00E5FF, #0077FF); box-shadow: 0 0 40px rgba(0,229,255,0.4);">
                ✨ ENTRAR AL DASHBOARD DE COMANDO
            </button>
        </div>
    </div>

    <div id="page-dashboard" class="hidden min-h-screen w-full flex">
        <aside class="w-64 border-r border-[#30363d] flex flex-col p-6 glass h-screen sticky top-0">
            <h2 class="gradient-text text-2xl font-black mb-10">🧬 FlowBio</h2>
            <nav class="space-y-6 flex-1">
                <div class="space-y-2">
                    <p class="text-[10px] text-[#6e7681] uppercase tracking-[0.2em] ml-2">Análisis</p>
                    <div class="flex items-center gap-3 p-3 rounded-xl bg-[#161b22] text-[#00E5FF] border border-[#00E5FF]/20 shadow-lg">
                        <i data-lucide="activity" class="w-4 h-4"></i> <span class="text-sm font-bold">Producción</span>
                    </div>
                </div>
                <div class="space-y-2">
                    <p class="text-[10px] text-[#6e7681] uppercase tracking-[0.2em] ml-2">Entregables</p>
                    <div class="flex items-center gap-3 p-3 rounded-xl text-[#8b949e] hover:bg-[#161b22] transition-all cursor-pointer">
                        <i data-lucide="file-down" class="w-4 h-4"></i> <span class="text-sm">Reporte PDF</span>
                    </div>
                </div>
            </nav>
            <button onclick="showPage('home')" class="flex items-center gap-2 text-xs text-[#6e7681] hover:text-white transition-all">
                <i data-lucide="arrow-left" class="w-3 h-3"></i> Volver al Inicio
            </button>
        </aside>

        <main class="flex-1 p-8 md:p-12 overflow-y-auto">
            <div class="max-w-7xl mx-auto">
                <header class="flex justify-between items-start mb-10">
                    <div>
                        <h1 class="text-4xl font-extrabold text-white">Centro de Comando</h1>
                        <p class="text-[#6e7681] mono text-xs mt-2">Active Asset: s3://flowbio-lake/Field_North_Sea_v4.csv</p>
                    </div>
                    <div class="px-4 py-2 rounded-lg bg-[#161b22] border border-[#30363d]">
                        <span class="w-2 h-2 rounded-full bg-[#39FF14] inline-block mr-2 animate-pulse"></span>
                        <span class="text-xs mono text-[#39FF14]">AGENTS_ONLINE</span>
                    </div>
                </header>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div class="glass p-8 rounded-2xl glow-border">
                        <p class="text-[10px] text-[#6e7681] uppercase tracking-widest mb-3">Producción Incremental</p>
                        <h3 class="text-5xl font-black text-[#39FF14]">+22,500 <span class="text-sm font-light text-[#6e7681]">bbls</span></h3>
                    </div>
                    <div class="glass p-8 rounded-2xl glow-border">
                        <p class="text-[10px] text-[#6e7681] uppercase tracking-widest mb-3">Ebitda Adicional Proyectado</p>
                        <h3 class="text-5xl font-black text-white">$1.5M <span class="text-sm font-light text-[#6e7681]">USD</span></h3>
                    </div>
                    <div class="glass p-8 rounded-2xl border-[#00E5FF]/40 bg-[#00E5FF]/5">
                        <p class="text-[10px] text-[#00E5FF] uppercase tracking-widest mb-3">FlowBio Success Fee (5%)</p>
                        <h3 class="text-5xl font-black text-[#00E5FF]">$67,500 <span class="text-sm font-light text-[#00E5FF]/60">USD</span></h3>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 glass p-8 rounded-2xl glow-border">
                        <div class="flex justify-between items-center mb-6">
                            <h4 class="font-bold flex items-center gap-2 text-[#e6edf3]">
                                <i data-lucide="trending-up" class="w-5 h-5 text-[#00E5FF]"></i> Pronóstico de Recuperación
                            </h4>
                            <div class="flex gap-4 text-[10px] mono">
                                <span class="flex items-center gap-1"><span class="w-2 h-2 bg-[#ff5f56] rounded-full"></span> Status Quo</span>
                                <span class="flex items-center gap-1"><span class="w-2 h-2 bg-[#39FF14] rounded-full"></span> FlowBio EOR</span>
                            </div>
                        </div>
                        <div id="chart-main" class="w-full h-80"></div>
                    </div>

                    <div class="terminal-window flex flex-col h-full min-h-[400px]">
                        <div class="flex items-center justify-between px-5 py-3 border-b border-[#30363d]">
                            <div class="flex gap-1.5">
                                <div class="w-2.5 h-2.5 rounded-full bg-[#ff5f56]"></div>
                                <div class="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]"></div>
                                <div class="w-2.5 h-2.5 rounded-full bg-[#27c93f]"></div>
                            </div>
                            <span class="text-[10px] text-[#6e7681] mono">agent_logs.sh</span>
                        </div>
                        <div class="p-6 mono text-[11px] text-[#39FF14] space-y-2 overflow-y-auto flex-1" id="console">
                            <div class="opacity-50">Initializing agentik_core v4.0...</div>
                            <div>> Accessing S3 Data Lake... [CONNECTED]</div>
                            <div>> Data Agent: Cleaning production logs... [OK]</div>
                            <div>> Physics Agent: Applying Darcy constraints... [OK]</div>
                            <div>> Skin Factor Agent: Optimizing concentration... [OK]</div>
                            <div class="text-white bg-[#39FF14]/20 inline-block px-1">SYSTEM READY: Dashboard updated.</div>
                            <div class="animate-pulse">_</div>
                        </div>
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
                setTimeout(renderChart, 100);
            } else {
                document.getElementById('page-home').classList.remove('hidden');
                document.getElementById('page-dashboard').classList.add('hidden');
            }
            lucide.createIcons();
        }

        function renderChart() {
            const months = Array.from({length: 36}, (_, i) => i + 1);
            const baseline = months.map(m => 3500 * Math.exp(-0.055 * m));
            const optimized = months.map((m, i) => m < 12 ? baseline[i] : baseline[i] + 1350 * Math.exp(-0.025 * (m - 12)));

            const trace1 = {
                x: months, y: baseline, name: 'Baseline',
                type: 'scatter', line: {color: '#ff5f56', width: 2, dash: 'dot'},
                hoverinfo: 'y'
            };
            const trace2 = {
                x: months, y: optimized, name: 'FlowBio',
                type: 'scatter', line: {color: '#39FF14', width: 4},
                fill: 'tonexty', fillcolor: 'rgba(57, 255, 20, 0.08)',
                hoverinfo: 'y'
            };

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 50, r: 20, t: 10, b: 50},
                showlegend: false,
                xaxis: { title: 'Meses', gridcolor: '#1f2937', zeroline: false, tickfont: {color: '#6e7681', size: 10}},
                yaxis: { title: 'BBLS/Mes', gridcolor: '#1f2937', zeroline: false, tickfont: {color: '#6e7681', size: 10}}
            };

            Plotly.newPlot('chart-main', [trace1, trace2], layout, {responsive: true, displayModeBar: false});
        }

        window.onload = () => lucide.createIcons();
    </script>
</body>
</html>
"""

# 4. RENDERIZADO FINAL
components.html(html_content, height=1200, scrolling=False)
