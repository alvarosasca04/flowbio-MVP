"""
╔══════════════════════════════════════════════════════════════════════╗
║   FlowBio Intelligence: Subsurface Diagnostic Console               ║
║   Motor PIML · Modelo Ostwald-de Waele · Factor Skin · TEA         ║
║   CEO: Álvaro Noé Sastré Castro · Startup Building WC2026          ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math

# ─────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FlowBio Intelligence | Subsurface Console",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# ESTILOS CSS — DARK MODE CON ACENTOS VERDE ESMERALDA
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Fondo principal ── */
  .stApp { background-color: #0D1B2A; color: #D0E4F8; }
  section[data-testid="stSidebar"] { background-color: #0A1520; border-right: 1px solid #1E3A60; }

  /* ── Header principal ── */
  .main-header {
    background: linear-gradient(135deg, #0a2235 0%, #0d3320 100%);
    border: 1px solid #1E6040;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
  }
  .main-title {
    font-size: 26px;
    font-weight: 800;
    color: #fff;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .main-sub {
    font-size: 13px;
    color: #7ABF8A;
    margin-top: 4px;
    letter-spacing: 1px;
  }
  .version-badge {
    background: rgba(75,174,110,.15);
    border: 1px solid #4BAE6E;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 11px;
    color: #4BAE6E;
    font-weight: 700;
    letter-spacing: 1px;
  }

  /* ── Metric cards ── */
  .metric-card {
    background: #0a1520;
    border: 1px solid #1E3A60;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    height: 100%;
  }
  .metric-card-val {
    font-size: 32px;
    font-weight: 800;
    font-family: 'Courier New', monospace;
    line-height: 1.1;
  }
  .metric-card-lbl {
    font-size: 10px;
    letter-spacing: 1.5px;
    color: #6A8AAA;
    margin-top: 6px;
    font-weight: 600;
  }
  .metric-card-sub {
    font-size: 11px;
    color: #4A8AAA;
    margin-top: 4px;
  }
  .val-green  { color: #4BAE6E; }
  .val-blue   { color: #4A9FD4; }
  .val-amber  { color: #E8A030; }
  .val-red    { color: #E05A5A; }
  .val-purple { color: #9B7FD4; }

  /* ── Section headers ── */
  .section-header {
    font-size: 10px;
    letter-spacing: 2px;
    color: #6A8AAA;
    font-weight: 700;
    margin: 20px 0 12px;
    text-transform: uppercase;
    border-bottom: 1px solid #1E3A60;
    padding-bottom: 8px;
  }

  /* ── Info box ── */
  .info-box {
    background: rgba(74,159,212,.08);
    border: 1px solid rgba(74,159,212,.3);
    border-radius: 10px;
    padding: 14px;
    font-size: 12px;
    color: #A0C4D8;
    line-height: 1.7;
  }
  .warning-box {
    background: rgba(232,160,48,.08);
    border: 1px solid rgba(232,160,48,.3);
    border-radius: 10px;
    padding: 14px;
    font-size: 12px;
    color: #E8C080;
    line-height: 1.7;
  }
  .success-box {
    background: rgba(75,174,110,.1);
    border: 1px solid rgba(75,174,110,.4);
    border-radius: 10px;
    padding: 16px;
    font-size: 13px;
    color: #7ABF8A;
    line-height: 1.7;
  }

  /* ── Sidebar labels ── */
  .sidebar-section {
    font-size: 9px;
    letter-spacing: 1.8px;
    color: #4BAE6E;
    font-weight: 700;
    margin: 16px 0 8px;
    text-transform: uppercase;
  }

  /* ── Streamlit overrides ── */
  .stSlider > div > div > div > div { background: #4BAE6E !important; }
  .stSelectbox > div > div { background: #0a1520 !important; border-color: #1E3A60 !important; }
  .stNumberInput > div > div > input { background: #0a1520 !important; border-color: #1E3A60 !important; color: #D0E4F8 !important; }
  div[data-testid="metric-container"] {
    background: #0a1520;
    border: 1px solid #1E3A60;
    border-radius: 12px;
    padding: 16px;
  }
  .stTabs [data-baseweb="tab"] { background: transparent; color: #6A8AAA; }
  .stTabs [aria-selected="true"] { color: #4BAE6E !important; border-bottom: 2px solid #4BAE6E !important; }
  h1, h2, h3 { color: #D0E4F8 !important; }

  /* ── Formula display ── */
  .formula-box {
    background: #060e18;
    border: 1px solid #1E3A60;
    border-radius: 10px;
    padding: 14px 18px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    color: #9B7FD4;
    text-align: center;
    margin: 8px 0;
  }

  /* ── Success fee highlight ── */
  .fee-card {
    background: linear-gradient(135deg, rgba(75,174,110,.15), rgba(74,159,212,.08));
    border: 1px solid #4BAE6E;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
  }
  .fee-big {
    font-size: 48px;
    font-weight: 900;
    color: #4BAE6E;
    font-family: 'Courier New', monospace;
    letter-spacing: -2px;
  }
  .fee-lbl {
    font-size: 11px;
    letter-spacing: 2px;
    color: #7ABF8A;
    margin-top: 4px;
  }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# MOTOR PIML — MODELO OSTWALD-DE WAELE (Power Law)
# ═════════════════════════════════════════════════════════════════════

class PIMLEngine:
    """
    Motor de Physics-Informed Machine Learning para EOR.

    El modelo de Power Law (Ostwald-de Waele) describe fluidos no-newtonianos:
        τ = K · (γ)ⁿ
    donde:
        τ = esfuerzo cortante (shear stress, Pa)
        K = índice de consistencia (consistency index, mPa·sⁿ)
        γ = tasa de corte (shear rate, s⁻¹)
        n = índice de flujo (flow behavior index, adimensional)
            n < 1 → fluido pseudoplástico (ideal para EOR)
            n = 1 → fluido newtoniano
            n > 1 → fluido dilatante

    El Factor Skin de Van Everdingen-Hurst:
        S = (K/Kd - 1) · ln(rd/rw)
    donde:
        K  = permeabilidad original del yacimiento (mD)
        Kd = permeabilidad dañada en zona de daño (mD)
        rd = radio de zona dañada (ft)
        rw = radio del pozo (ft)
    """

    def __init__(self, T_c: float, sal_ppm: float, conc_pct: float, fluid: str = "Na-CMC"):
        """
        Inicializa el motor con condiciones del yacimiento.

        Args:
            T_c      : Temperatura del yacimiento (°C)
            sal_ppm  : Salinidad del agua de formación (ppm)
            conc_pct : Concentración del biopolímero (% peso)
            fluid    : Tipo de fluido ('Na-CMC' o 'HPAM')
        """
        self.T = T_c
        self.S = sal_ppm
        self.C = conc_pct
        self.fluid = fluid

    def flow_index_n(self) -> float:
        """
        Calcula el índice de flujo n del modelo Power Law.
        Na-CMC produce n más bajo (mayor pseudoplasticidad) que HPAM.
        Rango ideal EOR: 0.3 < n < 0.65
        """
        if self.fluid == "Na-CMC":
            n = 0.65 - (self.T / 1200) - (self.S / 600000) - (self.C * 0.08)
            return float(np.clip(n, 0.28, 0.72))
        else:  # HPAM
            n = 0.78 - (self.T / 900) - (self.S / 500000) - (self.C * 0.05)
            return float(np.clip(n, 0.38, 0.85))

    def consistency_K(self) -> float:
        """
        Calcula el índice de consistencia K (mPa·sⁿ).
        Mayor K = fluido más resistente al flujo.
        """
        if self.fluid == "Na-CMC":
            K = 160 - (self.T * 0.75) + (self.S * 0.001) + (self.C * 12)
        else:
            K = 200 - (self.T * 0.90) + (self.S * 0.0008) + (self.C * 10)
        return float(max(30, K))

    def apparent_viscosity(self, shear_rates: np.ndarray) -> np.ndarray:
        """
        Calcula la viscosidad aparente η = K · γ^(n-1) en función de la tasa de corte.
        Esto modela el comportamiento shear-thinning del Na-CMC,
        crucial para que fluya fácilmente a través de poros pero mantenga
        viscosidad en zonas de bajo flujo para controlar la movilidad.
        """
        n = self.flow_index_n()
        K = self.consistency_K()
        eta = K * np.power(shear_rates, n - 1)
        return np.clip(eta, 1.0, 5000.0)

    def shear_stress(self, shear_rates: np.ndarray) -> np.ndarray:
        """
        Calcula el esfuerzo cortante τ = K · γⁿ (ley de potencia pura).
        """
        n = self.flow_index_n()
        K = self.consistency_K()
        return K * np.power(shear_rates, n)

    def skin_factor(self, K_orig: float, K_damaged: float,
                    r_damage: float, r_well: float) -> float:
        """
        Factor Skin de Van Everdingen-Hurst.
        S = (K/Kd - 1) · ln(rd/rw)

        S > 0 → daño (restricción al flujo) — es malo
        S = 0 → formación virgen
        S < 0 → estimulación (fractura, acidificación)

        Args:
            K_orig    : Permeabilidad original (mD)
            K_damaged : Permeabilidad en zona dañada (mD)
            r_damage  : Radio de zona dañada (ft)
            r_well    : Radio del pozo (ft)
        """
        if K_damaged <= 0 or r_well <= 0 or r_damage <= r_well:
            return 0.0
        ratio_k = (K_orig / K_damaged) - 1.0
        ratio_r = math.log(r_damage / r_well)
        return ratio_k * ratio_r

    def pressure_drop_skin(self, skin: float, flow_bpd: float,
                           viscosity_cp: float, K_md: float,
                           thickness_ft: float, r_well_ft: float) -> float:
        """
        Caída de presión adicional causada por el Factor Skin (psi).
        Ecuación de Darcy modificada:
            ΔP_skin = (141.2 · q · μ · B · S) / (K · h)
        donde B ≈ 1.0 RB/STB (factor volumétrico del crudo).
        """
        if K_md <= 0 or thickness_ft <= 0:
            return 0.0
        q = flow_bpd
        mu = viscosity_cp
        B = 1.05        # Factor volumétrico típico
        delta_p = (141.2 * q * mu * B * skin) / (K_md * thickness_ft)
        return max(0.0, delta_p)

    def mobility_ratio(self, visc_oil_cp: float, shear_rate: float = 10.0) -> float:
        """
        Ratio de movilidad M = λ_agua / λ_aceite.
        Con biopolímero, la viscosidad del fluido inyectado aumenta,
        reduciendo M y mejorando la eficiencia de barrido.
        M < 1 → barrido favorable
        M > 1 → viscous fingering (malo)
        """
        n = self.flow_index_n()
        K = self.consistency_K()
        visc_polymer = K * (shear_rate ** (n - 1))
        k_rel_water = 0.4   # Permeabilidad relativa al agua típica
        k_rel_oil   = 0.8   # Permeabilidad relativa al aceite
        M = (k_rel_water / visc_polymer) / (k_rel_oil / visc_oil_cp)
        return float(np.clip(M, 0.1, 5.0))

    def sweep_efficiency(self, mobility: float) -> float:
        """
        Eficiencia de barrido volumétrico (%).
        Correlación empírica basada en ratio de movilidad.
        """
        if mobility <= 0.5:
            eff = 90.0
        elif mobility <= 1.0:
            eff = 90.0 - (mobility - 0.5) * 20
        elif mobility <= 2.0:
            eff = 80.0 - (mobility - 1.0) * 25
        else:
            eff = max(30.0, 55.0 - (mobility - 2.0) * 10)
        return eff

    def nacmc_thermal_stability(self) -> dict:
        """
        Evaluación de estabilidad térmica del Na-CMC.
        Na-CMC FlowBio es estable hasta ~90-95°C.
        HPAM degrada significativamente sobre 80°C.
        """
        limit = 90.0 if self.fluid == "Na-CMC" else 80.0
        if self.T < limit * 0.80:
            status = "ESTABLE"
            color  = "green"
            pct    = 100.0
        elif self.T < limit:
            margin = (limit - self.T) / (limit * 0.20)
            status = "MARGINAL"
            color  = "amber"
            pct    = 60.0 + margin * 40
        else:
            excess = self.T - limit
            status = f"INESTABLE (+{excess:.0f}°C sobre límite)"
            color  = "red"
            pct    = max(10.0, 100.0 - excess * 5)
        return {"status": status, "color": color, "pct": pct, "limit": limit}

    def fpi_plugging_index(self, perm_md: float, inj_rate_bpd: float) -> float:
        """
        Filtration Plugging Index (FPI) — riesgo de taponamiento.
        FPI < 0.25 → riesgo bajo
        FPI 0.25-0.5 → moderado
        FPI 0.5-0.75 → alto
        FPI > 0.75 → crítico
        """
        perm_f  = 2.5 if perm_md < 50 else (1.5 if perm_md < 150 else (1.0 if perm_md < 400 else 0.7))
        rate_f  = 1.2 if inj_rate_bpd > 300 else (1.0 if inj_rate_bpd > 150 else 0.85)
        sal_f   = 1.0 + max(0, (self.S - 60000) / 20000)
        base    = 0.12 if self.fluid == "Na-CMC" else 0.65
        return float(np.clip(base * perm_f * rate_f * sal_f, 0.0, 1.0))


# ═════════════════════════════════════════════════════════════════════
# MÓDULO ECONÓMICO TEA — MODELO ADÁN RAMÍREZ
# ═════════════════════════════════════════════════════════════════════

class TEAModule:
    """
    Technical-Economic Analysis (TEA) — Modelo Success Fee.
    El cliente paga $5 USD por cada barril EXTRA producido sobre la línea base.
    FlowBio cobra por resultado, no por servicio.
    """

    SUCCESS_FEE_USD = 5.0          # USD por barril extra
    POLYMER_COST_USD_KG = 2.8      # Costo estimado Na-CMC (materia prima local)
    INJECTION_DAYS = 30            # Ciclo típico de inyección

    def __init__(self, baseline_bpd: float, oil_price_usd: float,
                 opex_usd_bbl: float, conc_pct: float, inj_rate_bpd: float):
        self.baseline  = baseline_bpd
        self.oil_price = oil_price_usd
        self.opex      = opex_usd_bbl
        self.conc      = conc_pct
        self.inj_rate  = inj_rate_bpd

    def incremental_production(self, sweep_before: float, sweep_after: float) -> float:
        """
        Barriles adicionales por mejora en eficiencia de barrido.
        ΔQ = Q_base × (E_after - E_before) / E_before
        """
        if sweep_before <= 0:
            return 0.0
        gain_pct = (sweep_after - sweep_before) / sweep_before
        return max(0.0, self.baseline * gain_pct)

    def success_fee_daily(self, extra_bpd: float) -> float:
        """Ingreso diario por Success Fee (USD/día)."""
        return extra_bpd * self.SUCCESS_FEE_USD

    def polymer_cost_daily(self) -> float:
        """Costo diario del biopolímero Na-CMC (USD/día)."""
        # Consumo: (inj_rate bbl/d × 0.159 m³/bbl × conc% × densidad agua ~1000 kg/m³)
        kg_per_day = self.inj_rate * 0.159 * (self.conc / 100) * 1000
        return kg_per_day * self.POLYMER_COST_USD_KG

    def roi(self, extra_bpd: float) -> dict:
        """
        ROI mensual del programa EOR con modelo Success Fee.
        """
        fee_daily  = self.success_fee_daily(extra_bpd)
        poly_daily = self.polymer_cost_daily()
        net_daily  = fee_daily - poly_daily
        net_month  = net_daily * self.INJECTION_DAYS

        opex_saving_daily = extra_bpd * (self.oil_price - self.opex) * 0.19
        annual_saving     = opex_saving_daily * 365

        return {
            "extra_bpd"       : round(extra_bpd, 1),
            "fee_daily"       : round(fee_daily, 2),
            "poly_cost_daily" : round(poly_daily, 2),
            "net_daily"       : round(net_daily, 2),
            "net_monthly"     : round(net_month, 2),
            "opex_saving_yr"  : round(annual_saving, 0),
            "payback_days"    : round(poly_daily * 30 / max(1, fee_daily), 1),
            "roi_pct"         : round((net_daily / max(1, poly_daily)) * 100, 1),
        }

    def production_curve(self, days: int, extra_bpd: float,
                         decline_rate: float = 0.002) -> pd.DataFrame:
        """
        Genera curva de producción Antes vs Después de la inyección.
        Modelo de declinación exponencial:
            Q(t) = Q0 × e^(-d·t)
        Con Na-CMC, la tasa de declinación se reduce significativamente.
        """
        t = np.arange(0, days + 1)

        # Baseline: declinación normal
        Q_base = self.baseline * np.exp(-decline_rate * t)

        # Con Na-CMC: menor declinación + producción incremental
        Q_after = (self.baseline + extra_bpd) * np.exp(-decline_rate * 0.55 * t)

        return pd.DataFrame({
            "Día"                 : t,
            "Baseline (bbl/día)" : np.round(Q_base, 1),
            "Con Na-CMC (bbl/día)": np.round(Q_after, 1),
            "Δ Barriles"          : np.round(Q_after - Q_base, 1),
        })


# ═════════════════════════════════════════════════════════════════════
# GRÁFICAS PLOTLY
# ═════════════════════════════════════════════════════════════════════

COLORS = {
    "bg"     : "#0d1b2a",
    "bg2"    : "#0a1520",
    "green"  : "#4BAE6E",
    "blue"   : "#4A9FD4",
    "red"    : "#E05A5A",
    "amber"  : "#E8A030",
    "purple" : "#9B7FD4",
    "muted"  : "#6A8AAA",
    "border" : "#1E3A60",
    "text"   : "#D0E4F8",
}

LAYOUT_BASE = dict(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor =COLORS["bg2"],
    font         =dict(family="Courier New, monospace", color=COLORS["text"], size=11),
    margin       =dict(l=50, r=20, t=40, b=50),
    legend       =dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLORS["border"],
                       borderwidth=1, font=dict(size=10)),
    xaxis=dict(gridcolor=COLORS["border"], gridwidth=0.5,
               linecolor=COLORS["border"], tickfont=dict(size=10)),
    yaxis=dict(gridcolor=COLORS["border"], gridwidth=0.5,
               linecolor=COLORS["border"], tickfont=dict(size=10)),
)


def plot_skin_gauge(skin: float) -> go.Figure:
    """
    Velocímetro (Gauge) del Factor Skin.
    Verde   S <  3 → daño bajo
    Ámbar   S <  8 → daño moderado
    Rojo    S < 20 → daño severo
    Rojo    S ≥ 20 → daño crítico
    """
    if skin < 3:
        color, label, level = COLORS["green"], "DAÑO BAJO", "green"
    elif skin < 8:
        color, label, level = COLORS["amber"], "DAÑO MODERADO", "amber"
    elif skin < 20:
        color, label, level = "#E05A5A", "DAÑO SEVERO", "red"
    else:
        color, label, level = "#CC0000", "DAÑO CRÍTICO", "red"

    fig = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = skin,
        delta = {"reference": 0, "increasing": {"color": "#E05A5A"}, "decreasing": {"color": "#4BAE6E"}},
        title = {"text": f"FACTOR SKIN (S)<br><span style='font-size:13px;color:{color}'>{label}</span>",
                 "font": {"size": 14, "color": COLORS["text"]}},
        number= {"font": {"size": 40, "color": color, "family": "Courier New"}},
        gauge = {
            "axis"  : {"range": [0, 30], "tickwidth": 1, "tickcolor": COLORS["muted"],
                       "tickfont": {"size": 9, "color": COLORS["muted"]}},
            "bar"   : {"color": color, "thickness": 0.25},
            "bgcolor": COLORS["bg2"],
            "steps" : [
                {"range": [0,  3],  "color": "rgba(75,174,110,.12)"},
                {"range": [3,  8],  "color": "rgba(232,160,48,.12)"},
                {"range": [8,  20], "color": "rgba(224,90,90,.12)"},
                {"range": [20, 30], "color": "rgba(200,0,0,.18)"},
            ],
            "threshold": {"line": {"color": "#fff", "width": 2}, "thickness": 0.75, "value": skin},
        }
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        font=dict(family="Courier New", color=COLORS["text"]),
        margin=dict(l=20, r=20, t=60, b=20),
        height=280,
    )
    return fig


def plot_rheology(engine_nacmc: PIMLEngine, engine_hpam: PIMLEngine) -> go.Figure:
    """
    Curva reológica: Viscosidad aparente vs Tasa de corte.
    Escala log-log — muestra el comportamiento shear-thinning.
    La zona óptima de inyección EOR está entre 10-100 s⁻¹.
    """
    gamma = np.logspace(-1, 3, 200)   # Tasas de corte 0.1 a 1000 s⁻¹

    eta_nacmc = engine_nacmc.apparent_viscosity(gamma)
    eta_hpam  = engine_hpam.apparent_viscosity(gamma)
    tau_nacmc = engine_nacmc.shear_stress(gamma)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Viscosidad Aparente vs Tasa de Corte", "Esfuerzo Cortante vs Tasa de Corte"],
    )

    # Panel 1: Viscosidad
    fig.add_trace(go.Scatter(
        x=gamma, y=eta_nacmc,
        name="Na-CMC FlowBio", mode="lines",
        line=dict(color=COLORS["green"], width=3),
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=gamma, y=eta_hpam,
        name="HPAM (baseline)", mode="lines",
        line=dict(color=COLORS["red"], width=2, dash="dash"),
    ), row=1, col=1)

    # Zona óptima EOR
    fig.add_vrect(x0=10, x1=100, fillcolor="rgba(75,174,110,.08)",
                  line_color="rgba(75,174,110,.4)", line_width=1,
                  annotation_text="Zona óptima EOR", annotation_position="top left",
                  annotation_font_color=COLORS["green"], annotation_font_size=10,
                  row=1, col=1)

    # Panel 2: Esfuerzo cortante (τ = K·γⁿ)
    fig.add_trace(go.Scatter(
        x=gamma, y=tau_nacmc,
        name="τ Na-CMC", mode="lines",
        line=dict(color=COLORS["blue"], width=2.5),
        showlegend=True,
    ), row=1, col=2)

    fig.update_layout(
        **LAYOUT_BASE,
        height=340,
        title_text="",
    )
    fig.update_xaxes(type="log", title_text="Tasa de Corte γ (s⁻¹)",
                     gridcolor=COLORS["border"], linecolor=COLORS["border"])
    fig.update_yaxes(type="log", title_text="Viscosidad Aparente η (mPa·s)",
                     gridcolor=COLORS["border"], linecolor=COLORS["border"], row=1, col=1)
    fig.update_yaxes(title_text="Esfuerzo Cortante τ (Pa)",
                     gridcolor=COLORS["border"], linecolor=COLORS["border"], row=1, col=2)
    fig.update_annotations(font_color=COLORS["muted"], font_size=11)

    return fig


def plot_production_curve(df: pd.DataFrame) -> go.Figure:
    """
    Curva de producción: Baseline vs Con Na-CMC.
    Incluye el área de barriles incrementales como zona sombreada.
    """
    fig = go.Figure()

    # Área de ganancia incremental
    fig.add_trace(go.Scatter(
        x=pd.concat([df["Día"], df["Día"][::-1]]),
        y=pd.concat([df["Con Na-CMC (bbl/día)"], df["Baseline (bbl/día)"][::-1]]),
        fill="toself",
        fillcolor="rgba(75,174,110,.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Barriles Incrementales",
        showlegend=True,
    ))

    fig.add_trace(go.Scatter(
        x=df["Día"], y=df["Baseline (bbl/día)"],
        name="Baseline (Sin tratamiento)",
        mode="lines",
        line=dict(color=COLORS["red"], width=2, dash="dash"),
    ))

    fig.add_trace(go.Scatter(
        x=df["Día"], y=df["Con Na-CMC (bbl/día)"],
        name="Con Na-CMC FlowBio",
        mode="lines",
        line=dict(color=COLORS["green"], width=3),
    ))

    # Marcador de inicio de inyección
    fig.add_vline(x=0, line_dash="dot", line_color=COLORS["blue"], line_width=1,
                  annotation_text="Inicio inyección", annotation_position="top right",
                  annotation_font_color=COLORS["blue"])

    fig.update_layout(
        **LAYOUT_BASE,
        height=340,
        xaxis_title="Días de Producción",
        yaxis_title="Producción (bbl/día)",
        hovermode="x unified",
    )
    return fig


def plot_opex_comparison(opex_base, opex_new, bopd, extra_bpd):
    categories  = ["OPEX Actual", "OPEX FlowBio", "Ganancia/bbl", "Success Fee/bbl"]
    values      = [opex_base, opex_new, opex_base * 0.19, 5.0]
    bar_colors  = [COLORS["red"], COLORS["green"], COLORS["amber"], COLORS["purple"]]

    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=bar_colors,
        text=[f"${v:.2f}" for v in values],
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
    ))

    # ESTE BLOQUE ES EL QUE DEBES REEMPLAZAR TOTALMENTE:
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor =COLORS["bg2"],
        font         =dict(family="Courier New, monospace", color=COLORS["text"], size=11),
        margin       =dict(l=50, r=20, t=40, b=50),
        height=300,
        yaxis_title="USD por barril",
        showlegend=False,
        bargap=0.35,
        yaxis=dict(
            gridcolor=COLORS["border"], 
            gridwidth=0.5,
            linecolor=COLORS["border"], 
            tickprefix="$"
        ),
    )
    return fig


def plot_fpi_bar(fpi: float) -> go.Figure:
    """Barra horizontal de riesgo de taponamiento FPI."""
    color = COLORS["green"] if fpi < 0.25 else COLORS["amber"] if fpi < 0.50 else COLORS["red"]
    label = "BAJO" if fpi < 0.25 else "MODERADO" if fpi < 0.50 else ("ALTO" if fpi < 0.75 else "CRÍTICO")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fpi * 100,
        title={"text": f"Filtration Plugging Index<br><span style='color:{color};font-size:12px'>{label}</span>",
               "font": {"size": 13, "color": COLORS["text"]}},
        number={"suffix": "%", "font": {"size": 32, "color": color, "family": "Courier New"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%",
                     "tickfont": {"size": 9, "color": COLORS["muted"]}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": COLORS["bg2"],
            "steps": [
                {"range": [0, 25],  "color": "rgba(75,174,110,.1)"},
                {"range": [25, 50], "color": "rgba(232,160,48,.1)"},
                {"range": [50, 75], "color": "rgba(224,90,90,.1)"},
                {"range": [75,100], "color": "rgba(200,0,0,.15)"},
            ],
        }
    ))
    fig.update_layout(paper_bgcolor=COLORS["bg"], margin=dict(l=20, r=20, t=60, b=20),
                      font=dict(family="Courier New", color=COLORS["text"]), height=220)
    return fig


# ═════════════════════════════════════════════════════════════════════
# SIDEBAR — INPUTS
# ═════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px'>
      <div style='font-size:20px;font-weight:900;color:#fff'>FlowBio</div>
      <div style='font-size:9px;letter-spacing:2px;color:#4BAE6E;margin-top:2px'>INTELLIGENCE · PIML ENGINE</div>
    </div>
    <hr style='border-color:#1E3A60;margin:8px 0 16px'>
    """, unsafe_allow_html=True)

    # ── Parámetros del yacimiento ──
    st.markdown("<div class='sidebar-section'>🛢 Parámetros del Yacimiento</div>", unsafe_allow_html=True)

    bhp        = st.number_input("Presión de Fondo (BHP) psi", min_value=100, max_value=8000, value=2200, step=50)
    bopd       = st.number_input("Producción actual (bbl/día)", min_value=10,  max_value=5000, value=500,  step=10)
    visc_oil   = st.number_input("Viscosidad del crudo (cP)",  min_value=1,   max_value=2000, value=85,   step=1)
    perm_md    = st.number_input("Permeabilidad (mD)",          min_value=1,   max_value=3000, value=250,  step=10)
    temp_c     = st.slider("Temperatura del yacimiento (°C)", 40, 130, 82, 1)
    sal_ppm    = st.slider("Salinidad agua formación (ppm)",   5000, 100000, 38000, 1000, format="%d")
    thickness  = st.number_input("Espesor neto (ft)",           min_value=5,   max_value=500,  value=45,   step=5)
    r_well     = st.number_input("Radio del pozo (ft)",          min_value=0.1, max_value=2.0,  value=0.35, step=0.05)

    st.markdown("<div class='sidebar-section'>⚗ Parámetros Na-CMC FlowBio</div>", unsafe_allow_html=True)

    conc_pct   = st.slider("Concentración Na-CMC (%wt)", 0.05, 2.0, 0.8, 0.05)
    inj_rate   = st.number_input("Tasa de inyección (bbl/día)", min_value=10, max_value=1000, value=150, step=10)
    r_damage   = st.slider("Radio zona dañada, rd (ft)", 1.0, 50.0, 8.0, 0.5)

    st.markdown("<div class='sidebar-section'>💰 Parámetros Económicos</div>", unsafe_allow_html=True)

    oil_price  = st.number_input("Precio del crudo (USD/bbl)", min_value=20.0, max_value=150.0, value=72.5, step=0.5)
    opex_bbl   = st.number_input("OPEX actual (USD/bbl)",       min_value=2.0,  max_value=60.0,  value=18.5, step=0.5)
    sim_days   = st.slider("Horizonte de simulación (días)",    30, 365, 120, 10)

    st.markdown("<div class='sidebar-section'>📊 Comparativo</div>", unsafe_allow_html=True)
    compare    = st.checkbox("Comparar con HPAM", value=True)

    st.markdown("""
    <hr style='border-color:#1E3A60;margin:16px 0 8px'>
    <div style='font-size:9px;color:#2A4A6A;text-align:center;line-height:1.6'>
      Motor PIML v0.3 · TRL 3<br>
      Calibración pendiente: IMP + CENAM<br>
      Amplifika UAG · WC 2026
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# CÁLCULOS PRINCIPALES
# ═════════════════════════════════════════════════════════════════════

# Instanciar motores PIML
engine_nacmc = PIMLEngine(T_c=temp_c, sal_ppm=sal_ppm, conc_pct=conc_pct, fluid="Na-CMC")
engine_hpam  = PIMLEngine(T_c=temp_c, sal_ppm=sal_ppm, conc_pct=conc_pct, fluid="HPAM")

# Parámetros Power Law
n_nacmc = engine_nacmc.flow_index_n()
K_nacmc = engine_nacmc.consistency_K()
n_hpam  = engine_hpam.flow_index_n()
K_hpam  = engine_hpam.consistency_K()

# Factor Skin (asumiendo Kd = K × 0.25 = daño típico por sólidos)
K_damaged  = perm_md * 0.25      # Permeabilidad dañada (reducción 75%)
skin       = engine_nacmc.skin_factor(perm_md, K_damaged, r_damage, r_well)
skin_nacmc = engine_nacmc.skin_factor(perm_md, perm_md * 0.85, r_damage, r_well)  # Con Na-CMC
dp_skin    = engine_nacmc.pressure_drop_skin(skin, bopd, visc_oil, perm_md, thickness, r_well)
dp_nacmc   = engine_nacmc.pressure_drop_skin(skin_nacmc, bopd, visc_oil, perm_md, thickness, r_well)

# Ratio de movilidad y eficiencia de barrido
mob_nacmc = engine_nacmc.mobility_ratio(visc_oil, shear_rate=10.0)
mob_hpam  = engine_hpam.mobility_ratio(visc_oil, shear_rate=10.0)
eff_base  = engine_nacmc.sweep_efficiency(2.5)   # Sin polímero → mob alto
eff_nacmc = engine_nacmc.sweep_efficiency(mob_nacmc)
eff_hpam  = engine_hpam.sweep_efficiency(mob_hpam)

# Estabilidad térmica
thermal = engine_nacmc.nacmc_thermal_stability()

# FPI
fpi = engine_nacmc.fpi_plugging_index(perm_md, inj_rate)

# TEA
tea = TEAModule(baseline_bpd=bopd, oil_price_usd=oil_price,
                opex_usd_bbl=opex_bbl, conc_pct=conc_pct, inj_rate_bpd=inj_rate)
extra_bpd  = tea.incremental_production(eff_base, eff_nacmc)
roi_data   = tea.roi(extra_bpd)
prod_curve = tea.production_curve(sim_days, extra_bpd)


# ═════════════════════════════════════════════════════════════════════
# UI PRINCIPAL
# ═════════════════════════════════════════════════════════════════════

# Header
st.markdown(f"""
<div class='main-header'>
  <div style='font-size:42px'>🛢️</div>
  <div style='flex:1'>
    <div class='main-title'>FlowBio Intelligence: Subsurface Diagnostic Console</div>
    <div class='main-sub'>PHYSICS-INFORMED MACHINE LEARNING · EOR · NA-CMC · SKIN FACTOR ANALYSIS</div>
  </div>
  <div>
    <div class='version-badge'>PIML v0.3 · TRL 3</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs PRINCIPALES ──
st.markdown("<div class='section-header'>📊 DIAGNÓSTICO DEL POZO — RESULTADOS PIML</div>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    color = "red" if skin > 8 else "amber" if skin > 3 else "green"
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-card-val val-{color}'>{skin:.2f}</div>
      <div class='metric-card-lbl'>FACTOR SKIN (S)</div>
      <div class='metric-card-sub'>S = (K/Kd-1)·ln(rd/rw)</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-card-val val-amber'>{dp_skin:.0f} psi</div>
      <div class='metric-card-lbl'>ΔP POR SKIN DAMAGE</div>
      <div class='metric-card-sub'>Pérdida de presión actual</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-card-val val-blue'>{n_nacmc:.3f}</div>
      <div class='metric-card-lbl'>ÍNDICE DE FLUJO (n)</div>
      <div class='metric-card-sub'>Power Law Na-CMC</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-card-val val-green'>{eff_nacmc:.1f}%</div>
      <div class='metric-card-lbl'>EF. BARRIDO EOR</div>
      <div class='metric-card-sub'>vs {eff_base:.1f}% baseline</div>
    </div>""", unsafe_allow_html=True)

with c5:
    mob_color = "green" if mob_nacmc < 1.0 else "amber" if mob_nacmc < 2.0 else "red"
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-card-val val-{mob_color}'>{mob_nacmc:.3f}</div>
      <div class='metric-card-lbl'>RATIO MOVILIDAD (M)</div>
      <div class='metric-card-sub'>{'Favorable' if mob_nacmc < 1 else 'Desfavorable'}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS PRINCIPALES ──
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Diagnóstico & Skin",
    "⚗ Reología Power Law",
    "📈 Producción & Economía",
    "🔬 Análisis Técnico Detallado",
])


# ──────────────────────────────────────────────────────────────────
# TAB 1: DIAGNÓSTICO & SKIN
# ──────────────────────────────────────────────────────────────────
with tab1:
    col_g, col_info = st.columns([1, 1.3])

    with col_g:
        st.markdown("<div class='section-header'>🎯 FACTOR SKIN — VELOCÍMETRO DE DAÑO</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_skin_gauge(skin), use_container_width=True, key="gauge_skin")

        st.markdown("<div class='section-header'>🚧 RIESGO DE TAPONAMIENTO (FPI)</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_fpi_bar(fpi), use_container_width=True, key="fpi_bar")

    with col_info:
        st.markdown("<div class='section-header'>📋 DIAGNÓSTICO COMPLETO</div>", unsafe_allow_html=True)

        # Estabilidad térmica
        th_icon = "✅" if thermal["color"] == "green" else "⚠️" if thermal["color"] == "amber" else "❌"
        st.markdown(f"""
        <div class='info-box'>
          <strong style='color:#4BAE6E'>⚡ Modelo Power Law (Ostwald-de Waele)</strong><br>
          τ = K · γⁿ → η = K · γ<sup>(n-1)</sup><br><br>
          <strong>Na-CMC FlowBio:</strong><br>
          &nbsp;• n = {n_nacmc:.4f} (pseudoplástico {'óptimo' if n_nacmc < 0.65 else 'aceptable'})<br>
          &nbsp;• K = {K_nacmc:.1f} mPa·sⁿ<br><br>
          {'<strong>HPAM (baseline):</strong><br>&nbsp;• n = ' + str(round(n_hpam,4)) + '<br>&nbsp;• K = ' + str(round(K_hpam,1)) + ' mPa·sⁿ<br><br>' if compare else ''}
          <strong>Interpretación:</strong> n &lt; 1 indica fluido pseudoplástico. El Na-CMC
          presenta mayor reducción de viscosidad bajo esfuerzo cortante, facilitando
          la inyección pero manteniendo alta viscosidad en zonas de bajo flujo.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='info-box'>
          <strong style='color:#4A9FD4'>🌡 Estabilidad Térmica Na-CMC</strong><br>
          Temperatura actual: <strong>{temp_c}°C</strong> | Límite: <strong>{thermal['limit']}°C</strong><br>
          {th_icon} Estado: <strong>{thermal['status']}</strong><br><br>
          El Na-CMC FlowBio mantiene integridad estructural hasta {thermal['limit']}°C,
          superando al HPAM (límite 80°C). A temperaturas mayores el HPAM
          se hidroliza y pierde efectividad de viscosificación.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Factor Skin con y sin Na-CMC
        skin_reduction = ((skin - skin_nacmc) / max(0.01, skin)) * 100
        st.markdown(f"""
        <div class='success-box'>
          <strong>📉 Reducción de Skin con Na-CMC FlowBio</strong><br><br>
          Skin actual (HPAM):    <strong>{skin:.2f}</strong><br>
          Skin con Na-CMC:       <strong>{skin_nacmc:.2f}</strong><br>
          Reducción:             <strong>{skin_reduction:.1f}%</strong><br>
          ΔP recuperado:         <strong>{dp_skin - dp_nacmc:.0f} psi</strong><br><br>
          <strong>Fórmula:</strong> S = (K/Kd - 1) · ln(rd/rw)<br>
          &nbsp;K  = {perm_md} mD (original)<br>
          &nbsp;Kd = {K_damaged:.0f} mD (dañada) → {perm_md * 0.85:.0f} mD (con Na-CMC)<br>
          &nbsp;rd = {r_damage} ft | rw = {r_well} ft
        </div>
        """, unsafe_allow_html=True)

    # Tabla comparativa OR
    st.markdown("<div class='section-header'>⚙ OPERATIONAL READINESS</div>", unsafe_allow_html=True)

    or_data = {
        "Indicador"            : ["Estab. térmica", "Compat. salina", "Skin Damage", "Ratio movilidad", "Riesgo tapon. (FPI)", "Biodegradabilidad", "HSE Factor"],
        "Estado actual"        : [
            f"{'✅' if thermal['color']=='green' else '⚠️'} {thermal['status']}",
            f"{'✅' if sal_ppm < 70000 else '⚠️'} {'OK' if sal_ppm < 70000 else 'Límite'}",
            f"{'❌' if skin > 8 else '⚠️' if skin > 3 else '✅'} S = {skin:.2f}",
            f"{'✅' if mob_nacmc < 1 else '⚠️'} M = {mob_nacmc:.3f}",
            f"{'✅' if fpi < 0.25 else '⚠️' if fpi < 0.5 else '❌'} {fpi:.3f}",
            "❌ No biodegradable",
            "❌ Tóxico (HPAM)",
        ],
        "Con Na-CMC FlowBio"  : [
            f"✅ {thermal['status']} (límite {thermal['limit']}°C)",
            f"✅ Compatible hasta 80,000 ppm",
            f"✅ S = {skin_nacmc:.2f} (reducción {skin_reduction:.0f}%)",
            f"{'✅' if mob_nacmc < 1 else '⚠️'} M = {mob_nacmc:.3f}",
            f"✅ FPI = {engine_nacmc.fpi_plugging_index(perm_md, inj_rate):.3f}",
            "✅ 100% biodegradable",
            "✅ Cero toxicidad",
        ],
    }
    df_or = pd.DataFrame(or_data)
    st.dataframe(df_or, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────
# TAB 2: REOLOGÍA
# ──────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("<div class='section-header'>⚗ CURVAS REOLÓGICAS — MODELO POWER LAW</div>", unsafe_allow_html=True)
    st.plotly_chart(plot_rheology(engine_nacmc, engine_hpam if compare else engine_nacmc),
                    use_container_width=True, key="rheology")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.markdown(f"""
        <div class='formula-box'>
          τ = K · γⁿ<br>
          <span style='color:#6A8AAA;font-size:11px'>Ley de Potencia · Power Law</span>
        </div>""", unsafe_allow_html=True)
    with col_r2:
        st.markdown(f"""
        <div class='formula-box'>
          η = K · γ<sup>(n-1)</sup><br>
          <span style='color:#6A8AAA;font-size:11px'>Viscosidad Aparente</span>
        </div>""", unsafe_allow_html=True)
    with col_r3:
        st.markdown(f"""
        <div class='formula-box'>
          n = {n_nacmc:.3f} | K = {K_nacmc:.1f}<br>
          <span style='color:#6A8AAA;font-size:11px'>Parámetros Na-CMC FlowBio</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>📊 TABLA DE VISCOSIDAD — NA-CMC vs HPAM</div>", unsafe_allow_html=True)
    gammas = [0.1, 1, 5, 10, 50, 100, 200, 500, 1000]
    df_rheo = pd.DataFrame({
        "γ (s⁻¹)"              : gammas,
        "η Na-CMC (mPa·s)"    : [f"{engine_nacmc.apparent_viscosity(np.array([g]))[0]:.1f}" for g in gammas],
        "η HPAM (mPa·s)"      : [f"{engine_hpam.apparent_viscosity(np.array([g]))[0]:.1f}" for g in gammas],
        "τ Na-CMC (Pa)"        : [f"{engine_nacmc.shear_stress(np.array([g]))[0]:.2f}" for g in gammas],
        "Zona"                 : ["Reposo"] * 2 + ["Baja"] + ["Óptima EOR"] * 2 + ["Media"] + ["Alta"] * 2 + ["Muy alta"][:2],
    })
    st.dataframe(df_rheo, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────
# TAB 3: PRODUCCIÓN & ECONOMÍA
# ──────────────────────────────────────────────────────────────────
with tab3:
    # SUCCESS FEE HERO
    st.markdown(f"""
    <div class='fee-card'>
      <div class='fee-lbl'>INGRESO POR SUCCESS FEE (MENSUAL)</div>
      <div class='fee-big'>${roi_data['net_monthly']:,.0f} USD</div>
      <div class='fee-lbl' style='margin-top:6px'>
        {extra_bpd:.1f} bbl/día extra × $5 USD × 30 días — costo polímero
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs económicos
    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-card-val val-green'>+{extra_bpd:.1f}</div>
          <div class='metric-card-lbl'>BARRILES EXTRA / DÍA</div>
          <div class='metric-card-sub'>Sobre línea base {bopd} bbl/d</div>
        </div>""", unsafe_allow_html=True)
    with ec2:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-card-val val-purple'>${roi_data['fee_daily']:,.0f}</div>
          <div class='metric-card-lbl'>SUCCESS FEE / DÍA</div>
          <div class='metric-card-sub'>${TEAModule.SUCCESS_FEE_USD}/bbl extra</div>
        </div>""", unsafe_allow_html=True)
    with ec3:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-card-val val-amber'>${roi_data['poly_cost_daily']:,.0f}</div>
          <div class='metric-card-lbl'>COSTO POLÍMERO / DÍA</div>
          <div class='metric-card-sub'>Na-CMC local · Orizaba</div>
        </div>""", unsafe_allow_html=True)
    with ec4:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-card-val val-green'>{roi_data['roi_pct']:.0f}%</div>
          <div class='metric-card-lbl'>ROI INMEDIATO</div>
          <div class='metric-card-sub'>Payback: {roi_data['payback_days']:.0f} días</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Curvas
    col_prod, col_opex = st.columns([1.6, 1])
    with col_prod:
        st.markdown("<div class='section-header'>📈 CURVA DE PRODUCCIÓN (ANTES vs DESPUÉS)</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_production_curve(prod_curve), use_container_width=True, key="prod_curve")
    with col_opex:
        st.markdown("<div class='section-header'>💰 COMPARATIVA COST-PER-BARREL</div>", unsafe_allow_html=True)
        opex_new = opex_bbl * (1 - 0.19)
        st.plotly_chart(plot_opex_comparison(opex_bbl, opex_new, bopd, extra_bpd),
                        use_container_width=True, key="opex_chart")

    # Tabla de producción
    st.markdown("<div class='section-header'>📋 DATOS DE PRODUCCIÓN (PRIMEROS 30 DÍAS)</div>", unsafe_allow_html=True)
    st.dataframe(prod_curve.head(31), use_container_width=True, hide_index=True)

    # Ahorro anual
    st.markdown(f"""
    <div class='success-box'>
      <strong>💰 Modelo Económico TEA — Modelo Adán Ramírez</strong><br><br>
      <strong>Success Fee:</strong> El cliente paga <strong>${TEAModule.SUCCESS_FEE_USD} USD</strong>
      por cada barril extra producido sobre su línea base de <strong>{bopd} bbl/día</strong>.<br><br>
      &nbsp;• Producción incremental: <strong>{extra_bpd:.1f} bbl/día</strong>
        ({((extra_bpd/bopd)*100):.1f}% sobre baseline)<br>
      &nbsp;• Ingreso bruto diario FlowBio: <strong>${roi_data['fee_daily']:,.2f} USD/día</strong><br>
      &nbsp;• Costo biopolímero Na-CMC: <strong>${roi_data['poly_cost_daily']:,.2f} USD/día</strong><br>
      &nbsp;• Margen neto FlowBio: <strong>${roi_data['net_daily']:,.2f} USD/día</strong><br>
      &nbsp;• <strong>Ahorro OPEX anual para el cliente: ${roi_data['opex_saving_yr']:,.0f} USD/año</strong><br><br>
      Materia prima local (jacinto de agua · Orizaba, Veracruz) reduce costos vs HPAM importado.
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────
# TAB 4: ANÁLISIS TÉCNICO DETALLADO
# ──────────────────────────────────────────────────────────────────
with tab4:
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("<div class='section-header'>🔬 PARÁMETROS PIML CALCULADOS</div>", unsafe_allow_html=True)

        tech_data = {
            "Parámetro"   : [
                "Índice de flujo n (Na-CMC)",
                "Índice de flujo n (HPAM)",
                "Consistencia K (Na-CMC)",
                "Consistencia K (HPAM)",
                "Viscosidad a 10 s⁻¹ (Na-CMC)",
                "Viscosidad a 10 s⁻¹ (HPAM)",
                "Factor Skin S (actual)",
                "Factor Skin S (con Na-CMC)",
                "ΔP skin actual",
                "ΔP skin con Na-CMC",
                "Ratio movilidad M (Na-CMC)",
                "Ratio movilidad M (HPAM)",
                "Ef. barrido baseline",
                "Ef. barrido Na-CMC",
                "Ef. barrido HPAM",
                "FPI (taponamiento)",
                "Estab. térmica Na-CMC",
            ],
            "Valor"       : [
                f"{n_nacmc:.4f}",
                f"{n_hpam:.4f}",
                f"{K_nacmc:.2f} mPa·sⁿ",
                f"{K_hpam:.2f} mPa·sⁿ",
                f"{engine_nacmc.apparent_viscosity(np.array([10.0]))[0]:.1f} mPa·s",
                f"{engine_hpam.apparent_viscosity(np.array([10.0]))[0]:.1f} mPa·s",
                f"{skin:.3f}",
                f"{skin_nacmc:.3f}",
                f"{dp_skin:.1f} psi",
                f"{dp_nacmc:.1f} psi",
                f"{mob_nacmc:.4f}",
                f"{mob_hpam:.4f}",
                f"{eff_base:.1f}%",
                f"{eff_nacmc:.1f}%",
                f"{eff_hpam:.1f}%",
                f"{fpi:.4f}",
                f"{thermal['status']}",
            ],
            "Estado"      : [
                "✅ Óptimo" if n_nacmc < 0.65 else "⚠️ Aceptable",
                "⚠️ Menos óptimo",
                "✅ OK",
                "⚠️ Mayor",
                "✅ Alta viscosidad",
                "⚠️ Menor",
                "❌ Daño severo" if skin > 8 else "⚠️ Moderado" if skin > 3 else "✅ Bajo",
                "✅ Reducido",
                "❌ Alta pérdida" if dp_skin > 200 else "⚠️ Moderada",
                "✅ Recuperado",
                "✅ Favorable" if mob_nacmc < 1 else "⚠️ Desfavorable",
                "⚠️ Menos favorable",
                "—",
                "✅ Mejor",
                "⚠️ Menor",
                "✅ Bajo" if fpi < 0.25 else "⚠️ Moderado" if fpi < 0.5 else "❌ Alto",
                "✅" if thermal["color"] == "green" else "⚠️" if thermal["color"] == "amber" else "❌",
            ],
        }
        df_tech = pd.DataFrame(tech_data)
        st.dataframe(df_tech, use_container_width=True, hide_index=True)

    with col_t2:
        st.markdown("<div class='section-header'>📐 FÍSICA DEL YACIMIENTO</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='info-box'>
          <strong style='color:#4BAE6E'>Ley de Potencia (Ostwald-de Waele)</strong><br>
          <code>τ = K · γⁿ</code><br>
          <code>η_aparente = K · γ^(n-1)</code><br><br>
          n &lt; 1 → pseudoplástico (shear-thinning)<br>
          n = 1 → newtoniano (agua, crudo ligero)<br>
          n &gt; 1 → dilatante (raro en EOR)<br><br>
          <strong>Na-CMC:</strong> n = {n_nacmc:.4f} → altamente pseudoplástico.<br>
          Se inyecta con facilidad (baja viscosidad bajo alto esfuerzo)
          pero controla la movilidad en el yacimiento (alta viscosidad
          en zonas de bajo flujo).
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='info-box'>
          <strong style='color:#4A9FD4'>Factor Skin (Van Everdingen-Hurst)</strong><br>
          <code>S = (K/Kd - 1) · ln(rd/rw)</code><br><br>
          K  = {perm_md} mD (permeabilidad original)<br>
          Kd = {K_damaged:.0f} mD (zona dañada, -75%)<br>
          rd = {r_damage} ft (radio zona dañada)<br>
          rw = {r_well} ft (radio del pozo)<br><br>
          <strong>S = ({perm_md}/{K_damaged:.0f} - 1) · ln({r_damage}/{r_well})</strong><br>
          S = {skin:.3f} → {'daño severo que restringe la producción' if skin > 8 else 'daño moderado' if skin > 3 else 'daño bajo'}<br><br>
          Caída de presión adicional: <strong>{dp_skin:.1f} psi</strong><br>
          Con Na-CMC → Kd mejora a {perm_md*0.85:.0f} mD → ΔP = {dp_nacmc:.1f} psi
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='warning-box'>
          <strong>⚗ Biopolímero Na-CMC FlowBio</strong><br>
          Fuente: Eichhornia crassipes (jacinto de agua · Orizaba, Ver.)<br>
          Grado de sustitución DS: 0.7-1.2 (objetivo)<br>
          Estabilidad térmica: hasta {thermal['limit']}°C<br>
          Compatibilidad salina: hasta 80,000 ppm NaCl<br>
          Biodegradabilidad: 100% (DNSH compliant)<br>
          HSE Risk Factor: Nulo (no tóxico, no persistente)<br><br>
          ⚠️ Parámetros reológicos reales (n, K) pendientes de
          calibración con viscosímetro rotacional en IMP + CENAM.
          Los valores actuales son estimaciones del modelo PIML.
        </div>
        """, unsafe_allow_html=True)

    # Formulario de exportación
    st.markdown("<div class='section-header'>📄 RESUMEN EJECUTIVO</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='success-box'>
      <strong>FlowBio Intelligence — Diagnóstico EOR</strong> | Generado: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}<br><br>
      <strong>Pozo evaluado:</strong> T={temp_c}°C | K={perm_md}mD | Sal={sal_ppm:,}ppm | Q={bopd}bbl/día<br><br>
      <strong>Diagnóstico:</strong> Factor Skin S={skin:.2f} indica {'daño severo' if skin > 8 else 'daño moderado' if skin > 3 else 'daño bajo'}
      con caída de presión adicional de {dp_skin:.0f} psi. El modelo Power Law predice que el Na-CMC FlowBio
      (n={n_nacmc:.3f}) mejorará la eficiencia de barrido de {eff_base:.1f}% a {eff_nacmc:.1f}%,
      generando <strong>{extra_bpd:.1f} bbl/día adicionales</strong>.<br><br>
      <strong>Impacto económico (Modelo Success Fee):</strong><br>
      &nbsp;• Ingreso FlowBio: ${roi_data['fee_daily']:,.2f}/día | ${roi_data['net_monthly']:,.0f}/mes<br>
      &nbsp;• Ahorro OPEX cliente: ${roi_data['opex_saving_yr']:,.0f}/año<br>
      &nbsp;• ROI: {roi_data['roi_pct']:.0f}% | Payback: {roi_data['payback_days']:.0f} días<br><br>
      <strong>Recomendación:</strong> {'✅ PROCEDER con inyección Na-CMC FlowBio. Condiciones óptimas.' if eff_nacmc > 65 and thermal['color'] != 'red' and fpi < 0.5 else '⚠️ CONDICIONAL. Revisar condiciones antes de inyectar.'}<br>
      Concentración recomendada: {conc_pct}%wt | Tasa: {inj_rate} bbl/día | Ciclo: 30 días
    </div>
    """, unsafe_allow_html=True)


# ── FOOTER ──
st.markdown("""
<hr style='border-color:#1E3A60;margin:32px 0 16px'>
<div style='text-align:center;font-size:10px;color:#2A4A6A;line-height:1.8'>
  <strong style='color:#4BAE6E'>FlowBio Intelligence</strong> · Motor PIML v0.3 · TRL 3<br>
  Na-CMC desde <em>Eichhornia crassipes</em> · Orizaba, Veracruz, MX<br>
  Startup Building Beyond the World Cup 2026 · Amplifika UAG<br>
  Calibración pendiente: IMP + CENAM · Los resultados son estimaciones del modelo
</div>
""", unsafe_allow_html=True)
