import streamlit as st
import streamlit.components.v1 as components

# 1. ESTO DEBE IR PRIMERO (Obligatorio para Streamlit)
st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. OCULTAR ELEMENTOS DE STREAMLIT PARA QUE SE VEA COMO TU WEB
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

# 3. TU CÓDIGO HTML COMPLETO (Inyectado como componente)
# He limpiado los scripts que daban error en la versión anterior
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
        html, body { height: 100%; margin: 0; padding: 0; background: #0d1117; overflow-x: hidden; }
        * { font-family: 'Outfit', sans-serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .gradient-text { background: linear-gradient(90deg, #00E5FF, #39FF14); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .glow-border { box-shadow: 0 0 30px rgba(0,229,255,0.08); }
        .pulse-glow { animation: pulseGlow 3s ease-in-out infinite; }
        @keyframes pulseGlow { 0%,100% { box-shadow: 0 0 20px rgba(0,229,255,0.15); } 50% { box-shadow: 0 0 40px rgba(0,229,255,0.3); } }
        @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        .fade-up { animation: fadeUp 0.6s ease-out forwards; opacity:0; }
        .fade-up-d1 { animation-delay: 0.1s; }
        .fade-up-d2 { animation-delay: 0.2s; }
        .fade-up-d3 { animation-delay: 0.3s; }
        .fade-up-d4 { animation-delay: 0.5s; }
        .hidden { display: none; }
    </style>
</head>
<body class="bg-[#0d1117] text-[#e6edf3]">
    <div id="app" class="h-full w-full">
        <div id="page-home" class="h-full w-full flex flex-col min-h-screen">
            <div class="flex-1 flex flex-col items-center justify-center px-6 py-16 relative overflow-hidden">
                <div class="absolute inset-0" style="background: radial-gradient(ellipse at center, #1a1f2e 0%, #0d1117 70%);"></div>
                <div class="relative z-10 text-center max-w-4xl mx-auto">
                    <div class="fade-up mb-2">
                        <span class="mono text-xs tracking-widest text-[#00E5FF] uppercase border border-[#00E5FF]/30 px-3 py-1 rounded-full">Plataforma Agéntica EOR</span>
                    </div>
                    <h1 class="fade-up fade-up-d1 text-5xl md:text-7xl font-extrabold gradient-text mt-6 mb-4">FlowBio Intelligence</h1>
                    <p class="fade-up fade-up-d2 text-lg md:text-xl text-[#8b949e] mb-10">La primera plataforma de Agentes de IA para Optimización EOR</p>
                    <button onclick="showPage('dashboard')" class="fade-up fade-up-d4 pulse-glow px-8 py-3.5 rounded-xl font-bold text-white text-sm" style="background: linear-gradient(135deg, #00E5FF, #0077FF);"> ✨ ENTRAR AL DASHBOARD DE COMANDO </button>
                </div>
            </div>
            <div class="px-6 pb-16 max-w-6xl mx-auto w-full grid grid-cols-1 md:grid-cols-3 gap-5">
                <div class="fade-up fade-up-d1 rounded-2xl p-6 border border-[#30363d] glow-border" style="background: rgba(22,27,34,0.7);">
                    <h3 class="font-bold text-lg mb-2">Agentes Autónomos</h3>
                    <p class="text-sm text-[#8b949e]">Workflow que limpia datos y calcula ROI sin intervención humana.</p>
                </div>
                <div class="fade-up fade-up-d2 rounded-2xl p-6 border border-[#30363d] glow-border" style="background: rgba(22,27,34,0.7);">
                    <h3 class="font-bold text-lg mb-2">Motor PIML</h3>
                    <p class="text-sm text-[#8b949e]">Modelado de fluidos no newtonianos con leyes termodinámicas.</p>
                </div>
                <div class="fade-up fade-up-d3 rounded-2xl p-6 border border-[#30363d] glow-border" style="background: rgba(22,27,34,0.7);">
                    <h3 class="font-bold text-lg mb-2">Success Fee</h3>
                    <p class="text-sm text-[#8b949e]">Modelo de bajo riesgo basado en producción incremental real.</p>
                </div>
            </div>
        </div>

        <div id="page-dashboard" class="hidden h-full w-full min-h-screen p-8">
            <div class="flex justify-between items-center mb-10">
                <h1 class="gradient-text font-extrabold text-3xl">🧬 FlowBio Dashboard</h1>
                <button onclick="showPage('home')" class="text-sm text-[#8b949e] hover:text-white">← Regresar</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="rounded-xl border border-[#30363d] p-6 bg-[#161b22]">
                    <p class="text-xs text-[#6e7681] uppercase tracking-widest">Incremental</p>
                    <h2 class="text-3xl font-bold text-[#39FF14]">+187 bbl/d</h2>
                </div>
                <div class="rounded-xl border border-[#30363d] p-6 bg-[#161b22]">
                    <p class="text-xs text-[#6e7681] uppercase tracking-widest">ROI</p>
                    <h2 class="text-3xl font-bold text-white">342%</h2>
                </div>
                <div class="md:col-span-2 rounded-xl border border-[#30363d] p-6 bg-[#161b22]">
                    <p class="text-xs text-[#6e7681] uppercase tracking-widest">Estado Terminal</p>
                    <p class="mono text-xs text-[#39FF14] mt-2">> Agentes Sincronizados... OK</p>
                    <p class="mono text-xs text-[#39FF14]">> Ley de Darcy validada... OK</p>
                </div>
            </div>
            <div class="mt-8 rounded-xl border border-[#30363d] p-10 bg-[#010409] text-center border-dashed">
                <p class="text-[#6e7681]">Simulación PIML en tiempo real activa</p>
            </div>
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

# 4. RENDERIZADO
components.html(html_content, height=1000, scrolling=True)
