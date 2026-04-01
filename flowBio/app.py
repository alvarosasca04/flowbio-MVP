def _calculate_fpi_factors(perm_md: float, inj_rate_bpd: float, sal_ppm: float) -> tuple:
    """
    Calcula factores individuales del índice FPI.
    Returns: (perm_factor, rate_factor, sal_factor)
    """
    # Factor permeabilidad: menor perm → mayor riesgo
    if perm_md < 50:
        perm_f = 2.5
    elif perm_md < 150:
        perm_f = 1.5
    elif perm_md < 400:
        perm_f = 1.0
    else:
        perm_f = 0.7
    
    # Factor tasa inyección: mayor tasa → mayor riesgo
    if inj_rate_bpd > 300:
        rate_f = 1.2
    elif inj_rate_bpd > 150:
        rate_f = 1.0
    else:
        rate_f = 0.85
    
    # Factor salinidad: mayor salinidad → mayor riesgo (incompatibilidad)
    sal_f = 1.0 + max(0, (sal_ppm - 60000) / 20000)
    
    return perm_f, rate_f, sal_f

def fpi_plugging_index(self, perm_md: float, inj_rate_bpd: float) -> float:
    """
    Filtration Plugging Index (FPI) — riesgo de taponamiento.
    FPI < 0.25 → riesgo bajo
    FPI 0.25-0.5 → moderado
    FPI 0.5-0.75 → alto
    FPI > 0.75 → crítico
    """
    perm_f, rate_f, sal_f = _calculate_fpi_factors(perm_md, inj_rate_bpd, self.S)
    base = 0.12 if self.fluid == "Na-CMC" else 0.65
    return float(np.clip(base * perm_f * rate_f * sal_f, 0.0, 1.0))