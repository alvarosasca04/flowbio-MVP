# ── FASE 3: DASHBOARD COMMAND CENTER (COMPLETO) ──
else:
    c_title, c_logout = st.columns([4, 1])
    with c_title: st.markdown("## Command Center")
    with c_logout:
        if st.button("🏠 SALIR"): st.session_state.auth = False; st.session_state.simulated = False; st.rerun()
    
    # Carga de datos robusta
    db = st.session_state.all_data.get("dashboard_data", st.session_state.all_data)
    pozo = st.selectbox("📍 Seleccione un pozo:", sorted(list(db.keys())))
    d = db[pozo]
    
    # 1. KPIs Financieros y Producción
    ahorro = d.get('ahorro', {})
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-box"><p class="kpi-label">CRUDO INCREMENTAL</p><p class="kpi-value">+{int(ahorro.get("barriles",0)):,}</p><p class="kpi-sub">bbls/mes</p></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-box"><p class="kpi-label">VALOR EXTRA</p><p class="kpi-value">${ahorro.get("valor_extra",0):,.0f}</p></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-box"><p class="kpi-label">SUCCESS FEE</p><p class="kpi-value">${ahorro.get("fee",0):,.0f}</p></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-box"><p class="kpi-label">PAYBACK</p><p class="kpi-value">{ahorro.get("payback",0)}</p><p class="kpi-sub">Meses</p></div>', unsafe_allow_html=True)

    # 2. Gráfica de Declinación
    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([2.3, 1.7])
    with cl:
        proyeccion = d.get('proyeccion', [])
        chart_data = json.dumps({"x": [r['mes'] for r in proyeccion], "p50": [r['P50'] for r in proyeccion], "p10": [r['P10'] for r in proyeccion]})
        script = f"<script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script><div id='plot' style='height:400px; background:#0D1520;'></div><script>var pd = {chart_data}; Plotly.newPlot('plot', [{{x:pd.x, y:pd.p10, name:'Status Quo', line:{{dash:'dot', color:'gray'}}}, {{x:pd.x, y:pd.p50, name:'FlowBio EOR', line:{{color:'#00E5A0', width:3}}}}], {{paper_bgcolor:'#0D1520', plot_bgcolor:'#0D1520', font:{{color:'white'}}, title:'Proyección Técnica'}});</script>"
        components.html(script, height=430)

    # 3. Recomendación Técnica de Inyección (El corazón del MVP)
    with cr:
        st.markdown("<h4 style='color:#00E5A0'>🧪 Recomendación Técnica (Polímero Tradicional)</h4>", unsafe_allow_html=True)
        rec = [
            ("Sistema Químico", d.get('quimico','Na-CMC / Polímero Tradicional')),
            ("Dosificación", f"{d.get('ppm', 1200)} ppm"),
            ("Caudal de Inyección", f"{d.get('bwpd', 300)} BWPD"),
            ("Presión Límite", f"{d.get('lim_psi', 2800)} psi"),
            ("Factor de Ajuste", "Optimizado según viscosidad")
        ]
        for k, v in rec: st.markdown(f"<div class='diag-row'><span class='diag-key'>{k}</span><span class='diag-val'>{v}</span></div>", unsafe_allow_html=True)
        st.download_button("📥 DESCARGAR REPORTE PDF", data=generate_pdf(pozo, ahorro, d), file_name="FlowBio_Report.pdf")
