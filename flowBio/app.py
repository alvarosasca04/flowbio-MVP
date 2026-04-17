with cr:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        
        # Construimos el HTML en una variable para asegurar que se procese como un solo bloque
        tech_content = f"""
        <div style="background:#0D1520; padding:25px; border-radius:12px; border:1px solid rgba(0,229,160,0.3); height:550px; overflow-y:auto;">
            <p style="color:#00E5A0; font-weight:800; font-size:12px; margin-bottom:15px;">🧠 ENGINEERING INSIGHTS (5-AGENT CONSENSUS)</p>
            
            <div class="tech-box">
                <p class="tech-label">VISCOSIDAD PLÁSTICA (PV): {d.get('visc_p', '95.49')} cP</p>
                <p class="reasoning-text"><b>¿Por qué importa?</b> Una viscosidad >90 cP garantiza que el fluido sea lo suficientemente espeso para empujar el crudo pesado sin "dedear" el agua, maximizando la recuperación.</p>
            </div>
            
            <div class="tech-box">
                <p class="tech-label">YIELD POINT (YP): {d.get('yield_p', '28.1')} lb/100ft²</p>
                <p class="reasoning-text"><b>¿Por qué importa?</b> Este valor indica la capacidad del fluido para mantenerse estable bajo presión, evitando que el polímero se rompa en el fondo del pozo.</p>
            </div>
            
            <div class="tech-box">
                <p class="tech-label">PAYBACK: {d.get('payback', '1.0')} MESES</p>
                <p class="reasoning-text"><b>¿Por qué importa?</b> Es un retorno de inversión casi instantáneo; el petróleo extra producido cubre el costo tecnológico en tiempo récord.</p>
            </div>
            
            <p style="color:#64748B; font-size:10px; margin-top:15px;">RECOMENDACIÓN TÉCNICA:</p>
            <p style="color:white; font-size:13px; font-weight:600; border-left:2px solid #00E5A0; padding-left:10px;">{d.get('recomendacion', 'INYECTAR Na-CMC: Verificado por Agentes.')}</p>
            
            <p style="color:#64748B; font-size:10px; margin-top:20px;">INCREMENTAL PROYECTADO (EUR):</p>
            <p style="color:#00E5A0; font-size:32px; font-weight:800; margin:0;">{d.get('eur', 0):,} <span style="font-size:12px; color:#64748B;">bbls</span></p>
        </div>
        """
        
        # Renderizamos TODO el bloque con el permiso de HTML activado
        st.markdown(tech_content, unsafe_allow_html=True)
