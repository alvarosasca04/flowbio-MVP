import streamlit as st
import streamlit.components.v1 as components

# 1. ESTO DEBE IR PRIMERO Y ES LO QUE CONFIGURA EL ANCHO REAL
st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. CSS PARA ELIMINAR EL MARGEN DE STREAMLIT (EL SECRETO)
st.markdown("""
    <style>
        /* Elimina el padding superior y lateral de Streamlit */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
        /* Oculta el header y footer de Streamlit */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Ajusta el iframe para que no tenga bordes y sea responsive */
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# 3. TU CÓDIGO HTML INTEGRAL
# He optimizado tu código para que el Dashboard no se encime
html_content = """
<!doctype html>
<html lang="es" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body { height: 100%; margin: 0; padding: 0; background: #0d1117; overflow: hidden; }
        * { font-family: 'Outfit', sans-serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .gradient-text { background: linear-gradient(90deg, #00E5FF, #39FF14); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .glass { background: rgba(22, 27, 34, 0.8); backdrop-filter: blur(12px); border: 1px solid #30363d; }
        .hidden { display: none !important; }
        
        /* Animaciones para que se vea premium */
        @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        .fade-up { animation: fadeUp 0.6s ease-out forwards; }
    </style>
</head>
<body class="text-[#e6edf3]">
    <div id="app" class="h-full w-full">
        <div id="page-home" class="h-full w-full flex flex-col justify-center items-center text-center p-6 relative">
            <div class="absolute inset-0" style="background: radial-gradient(circle at center, #1a1f2e 0%, #0d1117 80%);"></div>
            <div class="relative z-10 fade-up">
                <h1 class="text-7xl font-black gradient-text mb-4">FlowBio</h1>
                <p class="text-xl text-[#8b949e] mb-10">Agentes de IA para Optimización EOR</p>
                <button onclick="showPage('dashboard')" class="px-10 py-4 rounded-xl font-bold text-white transition-all hover:scale-105" style="background: linear-gradient(135deg, #00E5FF, #0077FF);"> ✨ ENTRAR AL COMMAND CENTER </button>
            </div>
        </div>

        <div id="page-dashboard" class="hidden h-full w-full flex overflow-hidden">
            <aside class="w-64 border-r border-[#30363d] bg-[#010409] p-6 flex flex-col">
                <h2 class="gradient-text font-black text-2xl mb-10">🧬 FlowBio</h2>
                <nav class="space-y-4 flex-1">
                    <div class="text-[10px] text-[#6e7681] tracking-widest uppercase">Módulos</div>
                    <div class="flex items-center gap-3 p-3 rounded-lg bg-[#161b22] text-[#00E5FF]">
                        <i data-lucide="layout-dashboard" class="w-4 h-4"></i> <span class="text-sm font-bold">Overview</span>
                    </div>
                </nav>
                <button onclick="showPage('home')" class="text-xs text-[#6e7681] hover:text-white mt-auto">← Salir</button>
            </aside>

            <main class="flex-1 p-8 overflow-y-auto">
                <h2 class="text-3xl font-bold mb-8">Dashboard de Comando</h2>
                
                <div class="grid grid-cols-3 gap-6 mb-10">
                    <div class="glass p-6 rounded-2xl">
                        <p class="text-xs text-[#6e7681] uppercase mb-2">Incremental</p>
                        <h3 class="text-4xl font-black text-[#39FF14]">+22.5k <span class="text-sm font-normal">bbl</span></h3>
                    </div>
                    <div class="glass p-6 rounded-2xl">
                        <p class="text-xs text-[#6e7681] uppercase mb-2">NPV USD</p>
                        <h3 class="text-4xl font-black text-white">$1.46M</h3>
                    </div>
                    <div class="glass p-6 rounded-2xl border-[#00E5FF]/30">
                        <p class="text-xs text-[#00E5FF] uppercase mb-2">Success Fee</p>
                        <h3 class="text-4xl font-black text-[#00E5FF]">$67.5k</h3>
                    </div>
                </div>

                <div class="grid grid-cols-12 gap-6">
                    <div class="col-span-8 glass p-6 rounded-2xl h-80 flex flex-col justify-center items-center">
                        <p class="text-xs text-[#6e7681] mono mb-4">[ Visualización de Producción Activa ]</p>
                        <div class="w-full h-full bg-black/20 rounded-lg flex items-end p-4 gap-2">
                            <div class="flex-1 bg-[#39FF14]/40 rounded-t" style="height: 60%"></div>
                            <div class="flex-1 bg-[#39FF14]/60 rounded-t" style="height: 75%"></div>
                            <div class="flex-1 bg-[#39FF14]/80 rounded-t" style="height: 90%"></div>
                        </div>
                    </div>
                    <div class="col-span-4 glass bg-black/50 p-4 rounded-2xl h-80 flex flex-col">
                        <div class="flex gap-1.5 mb-4">
                            <div class="w-2 h-2 rounded-full bg-[#ff5f56]"></div>
                            <div class="w-2 h-2 rounded-full bg-[#ffbd2e]"></div>
                        </div>
                        <div class="mono text-[10px] text-[#39FF14] space-y-2 overflow-y-auto">
                            <div>> INIT AGENT_CORE... OK</div>
                            <div>> SYNC S3_DATA... OK</div>
                            <div>> PIML_SIMULATION RUNNING...</div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script>
        function showPage(page) {
            if(page === 'dashboard') {
                document.getElementById('page-home').classList.add('hidden');
                document.getElementById('page-dashboard').classList.remove('hidden');
            } else {
                document.getElementById('page-home').classList.remove('hidden');
                document.getElementById('page-dashboard').classList.add('hidden');
            }
            lucide.createIcons();
        }
        window.onload = function() { lucide.createIcons(); }
    </script>
</body>
</html>
"""

# 4. RENDER FINAL SIN SCROLL EXTRA
components.html(html_content, height=2000)
