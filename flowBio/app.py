import streamlit as st
import streamlit.components.v1 as components

# Asumiendo que ya cargaste tu JSON en st.session_state.all_data
datos_pozos = st.session_state.all_data
lista_pozos = list(datos_pozos.keys())

# 1. CREAMOS EL MENÚ DESPLEGABLE
pozo_seleccionado = st.selectbox("📍 Seleccione un pozo para Análisis de Declinación:", lista_pozos)

# 2. EXTRAEMOS LOS DATOS SOLO DE ESE POZO
d = datos_pozos[pozo_seleccionado]

# (Opcional) Calculamos valores financieros para ESTE pozo específico
barriles_extra_mes = int(d['eur'] / (5 * 12)) # EUR dividido en 60 meses
valor_extra = barriles_extra_mes * 74.5 # Precio del barril
success_fee = d['fee']

# 3. DIBUJAMOS LOS KPIs DINÁMICOS
k1, k2, k3, k4 = st.columns(4)
with k1: st.metric("CRUDO INCREMENTAL (MES)", f"+{barriles_extra_mes:,} bbls")
with k2: st.metric("VALOR EXTRA GENERADO", f"${valor_extra:,.0f}")
with k3: st.metric("SUCCESS FEE", f"${success_fee:,.0f}")
with k4: st.metric("PAYBACK", f"{d['payback']} Meses")

# 4. LA GRÁFICA PLOTLY DINÁMICA (Inyectamos d['mejora'])
# Asumimos que un pozo individual arranca en ~350 bpd (no 4000 como el global)
script_grafica = f"""
<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>
<div id='plot' style='height:400px; background:#0D1520; border-radius:12px;'></div>
<script>
    var x = Array.from({{length:40}}, (_,i)=>i);
    // Producción base de un pozo (ej. 350 bpd) declinando
    var y_base = x.map(i => 350 * Math.exp(-0.06 * i)); 
    // Inyectamos el % de mejora real calculado por la IA
    var mejora = {d['mejora']} / 100;
    var y_flowbio = x.map(i => i < 5 ? y_base[i] : y_base[i] + (350 * mejora * Math.exp(-0.015 * (i-5))));
    
    var trace1 = {{x: x, y: y_base, name: 'Status Quo', line: {{color: '#EF4444', dash: 'dot'}}}};
    var trace2 = {{x: x, y: y_flowbio, name: 'FlowBio EOR', line: {{color: '#00E5A0', width: 4}}, fill: 'tonexty', fillcolor: 'rgba(0,229,160,0.1)'}};
    
    var layout = {{paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: {{color: '#64748B'}} }};
    Plotly.newPlot('plot', [trace1, trace2], layout);
</script>
"""
components.html(script_grafica, height=420)
