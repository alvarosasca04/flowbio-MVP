import streamlit as st
import streamlit.components.v1 as components

# 1. Configuración de la página de Streamlit
st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Definición del código HTML/CSS/JS (Tu código original)
# Nota: He envuelto tu código en una variable de Python.
html_code = """
<!doctype html>
<html lang="es" class="h-full">
 <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FlowBio Intelligence</title>
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&amp;family=Outfit:wght@300;400;600;700;800&amp;display=swap" rel="stylesheet">
  <style>
  html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; background: #0d1117; }
  * { font-family: 'Outfit', sans-serif; }
  .mono { font-family: 'JetBrains Mono', monospace; }
  .gradient-text { background: linear-gradient(90deg, #00E5FF, #39FF14); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .glow-border { box-shadow: 0 0 30px rgba(0,229,255,0.08); }
  .terminal-line { animation: typeLine 0.4s ease-out forwards; opacity: 0; }
  @keyframes typeLine { to { opacity: 1; } }
  @keyframes pulseGlow { 0%,100% { box-shadow: 0 0 20px rgba(0,229,255,0.15); } 50% { box-shadow: 0 0 40px rgba(0,229,255,0.3); } }
  .pulse-glow { animation: pulseGlow 3s ease-in-out infinite; }
  @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
  .fade-up { animation: fadeUp 0.6s ease-out forwards; opacity:0; }
  .fade-up-d1 { animation-delay: 0.1s; }
  .fade-up-d2 { animation-delay: 0.2s; }
  .fade-up-d3 { animation-delay: 0.3s; }
  .fade-up-d4 { animation-delay: 0.5s; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0d1117; }
  ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
  .chart-bar { transition: height 0.8s ease-out; }
  
  /* Ajuste para Streamlit iframe */
  #app { height: 100vh; width: 100vw; }
</style>
 </head>
 <body class="bg-[#0d1117] text-[#e6edf3]">
  <div id="app">
    <div id="page-home" class="h-full w-full flex flex-col">
        <div class="flex-1 flex flex-col items-center justify-center px-6 py-16 relative overflow-hidden">
            <div class="absolute inset-0" style="background: radial-gradient(ellipse at center, #1a1f2e 0%, #0d1117 70%);"></div>
            <div class="relative z-10 text-center max-w-4xl mx-auto">
                <div class="fade-up mb-2">
                    <span class="mono text-xs tracking-widest text-[#00E5FF] uppercase border border-[#00E5FF]/30 px-3 py-1 rounded-full">Plataforma Agéntica EOR</span>
                </div>
                <h1 class="fade-up fade-up-d1 text-5xl md:text-7xl font-extrabold gradient-text mt-6 mb-4 leading-tight">FlowBio Intelligence</h1>
                <p class="fade-up fade-up-d2 text-lg md:text-xl text-[#8b949e] mb-10">La primera plataforma de Agentes de IA para Optimización EOR</p>
                <button onclick="showPage('dashboard')" class="fade-up fade-up-d4 pulse-glow px-8 py-3.5 rounded-xl font-bold text-white text-sm tracking-wide" style="background: linear-gradient(135deg, #00E5FF, #0077FF);"> ✨ ENTRAR AL DASHBOARD DE COMANDO </button>
            </div>
        </div>
    </div>

    <div id="page-dashboard" class="h-full w-full hidden">
        </div>
  </div>

  <script>
    // PEGAR AQUÍ TODO EL CONTENIDO DE TU <script> ORIGINAL
    // (Funciones showPage, showTab, renderChart, renderWells, runPipeline, etc.)
    function showPage(page) {
        document.getElementById('page-home').classList.toggle('hidden', page !== 'home');
        document.getElementById('page-dashboard').classList.toggle('hidden', page !== 'dashboard');
        if (page === 'dashboard') { showTab('overview'); lucide.createIcons(); }
    }
    // ... resto del script
    lucide.createIcons();
  </script>
 </body>
</html>
"""

# 3. Inyección en Streamlit
# Usamos un contenedor que ocupe todo el ancho y alto disponible
st.markdown("""
    <style>
        .stApp { margin: 0; padding: 0; }
        iframe { position: fixed; top: 0; left: 0; width: 100%; height: 100%; border: none; }
        [data-testid="stHeader"] { display: none; }
    </style>
""", unsafe_allow_html=True)

components.html(html_code, height=2000, scrolling=False)
