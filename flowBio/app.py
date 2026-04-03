"""
FlowBio Intelligence — Subsurface Diagnostic Console
S3 Data Lake · Motor PIML · Gemelo Digital · Streamlit Cloud
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math, io, warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BUCKET = "flowbio-data-lake-v2-627807503177-us-east-2-an"

# Colores FlowBio
BG    = "#0D1B2A"; BG2   = "#0A1520"; BRD = "#1E3A60"
TX    = "#D0E4F8"; GR    = "#4BAE6E"; BL  = "#4A9FD4"
RD    = "#E05A5A"; AM    = "#E8A030"; PU  = "#9B7FD4"

# ═══════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════
st.markdown(f"""
<style>
  .stApp{{background:{BG};color:{TX}}}
  section[data-testid="stSidebar"]{{background:{BG2};border-right:1px solid {BRD}}}
  .mc{{background:{BG2};border:1px solid {BRD};border-radius:12px;padding:16px;text-align:center}}
  .mv{{font-size:28px;font-weight:800;font-family:monospace;line-height:1.1}}
  .ml{{font-size:9px;letter-spacing:1.5px;color:#6A8AAA;margin-top:5px;font-weight:600}}
  .ms{{font-size:10px;color:#4A8AAA;margin-top:3px}}
  .vg{{color:{GR}}}.vb{{color:{BL}}}.vr{{color:{RD}}}.va{{color:{AM}}}
  .sh{{font-size:9px;letter-spacing:2px;color:#6A8AAA;font-weight:700;
       border-bottom:1px solid {BRD};padding-bottom:6px;margin:18px 0 12px}}
  .badge{{background:rgba(75,174,110,.15);border:1px solid {GR};border-radius:20px;
          padding:3px 12px;font-size:10px;color:{GR};font-weight:700;display:inline-block}}
  .badge-b{{background:rgba(74,159,212,.15);border:1px solid {BL};border-radius:20px;
            padding:3px 12px;font-size:10px;color:{BL};font-weight:700;display:inline-block}}
  .hero{{background:linear-gradient(135deg,rgba(75,174,110,.15),rgba(74,159,212,.1));
         border:1px solid {GR};border-radius:14px;padding:22px;text-align:center;margin-bottom:16px}}
  .hv{{font-size:44px;font-weight:900;color:{GR};font-family:monospace;letter-spacing:-2px}}
  .hs{{font-size:12px;color:#7ABF8A;margin-top:4px}}
  .ib{{background:rgba(74,159,212,.08);border:1px solid rgba(74,159,212,.3);
       border-radius:10px;padding:14px;font-size:12px;color:#A0C4D8;line-height:1.7}}
  .sb{{background:rgba(75,174,110,.1);border:1px solid rgba(75,174,110,.4);
       border-radius:10px;padding:14px;font-size:12px;color:#7ABF8A;line-height:1.7}}
  .wb{{background:rgba(232,160,48,.08);border:1px solid rgba(232,160,48,.3);
       border-radius:10px;padding:12px;font-size:12px;color:#E8C080;line-height:1.7}}
  .ssc{{font-size:9px;letter-spacing:1.8px;color:{GR};font-weight:700;margin:14px 0 8px}}
  .stTabs [aria-selected="true"]{{color:{GR} !important;border-bottom:2px solid {GR} !important}}
  .stTabs [data-baseweb="tab"]{{color:#6A8AAA}}
  div[data-testid="metric-container"]{{background:{BG2};border:1px solid {BRD};border-radius:10px;padding:12px}}
</style>
""", unsafe_allow_html=True)

LAY = dict(
    paper_bgcolor=BG, plot_bgcolor=BG2,
    font=dict(family="Courier New", color=TX, size=10),
    margin=dict(l=50,r=20,t=40,b=50),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BRD, borderwidth=1),
    xaxis=dict(gridcolor=BRD, gridwidth=0.5, linecolor=BRD),
    yaxis=dict(gridcolor=BRD, gridwidth=0.5, linecolor=BRD),
)


# ═══════════════════════════════════════════════
# MOTOR PIML — mismo que tienes en SageMaker
# ═══════════════════════════════════════════════
class PIMLEngine:
    def __init__(self, T=85, S=45000, C=0.8, fluid="Na-CMC"):
        self.T=T; self.S=S; self.C=C; self.fluid=fluid
        if fluid=="Na-CMC":
            self.n=float(np.clip(0.65-(T/1200)-(S/600000)-(C*0.08),0.25,0.90))
            self.K=float(max(30, 160-(T*0.75)+(S*0.001)+(C*12)))
        else:
            self.n=float(np.clip(0.78-(T/900)-(S/500000)-(C*0.05),0.30,0.90))
            self.K=float(max(30, 200-(T*0.90)+(S*0.0008)+(C*10)))

    def visc(self, gamma=10):
        return float(np.clip(self.K*(gamma**(self.n-1)), 1, 5000))

    def skin(self, K_orig, K_dam, rd=8.0, rw=0.35):
        if K_dam<=0: return 0.0
        return float((K_orig/K_dam - 1)*math.log(rd/rw))

    def sweep(self, M):
        if M<=0.5:   return 90.0
        elif M<=1.0: return 90.0-(M-0.5)*20
        elif M<=2.0: return 80.0-(M-1.0)*25
        return max(30.0, 55.0-(M-2.0)*10)

    def mob(self, visc_oil=85, gamma=10):
        return float(np.clip((0.4/self.visc(gamma))/(0.8/visc_oil), 0.05, 8.0))

    def fpi(self, perm):
        pf=2.5 if perm<50 else 1.5 if perm<150 else 1.0 if perm<400 else 0.7
        return float(np.clip(0.12*pf*(1+max(0,(self.S-60000)/20000)), 0, 1))

    def roi(self, extra_bpd, opex=18.5, oil=74.5):
        fee   = extra_bpd * 5.0 * 30
        cost  = (150*0.159*(self.C/100)*1000) * 2.8 * 30
        neto  = fee - cost
        ahorro= extra_bpd * (oil-opex) * 0.19 * 365
        return round(neto,2), round(ahorro,0)


# ═══════════════════════════════════════════════
# CONEXIÓN S3
# ═══════════════════════════════════════════════
@st.cache_resource(ttl=300)
def get_s3():
    try:
        import boto3
        c = boto3.client(
            "s3",
            aws_access_key_id     = st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
            region_name           = st.secrets["aws"].get("AWS_DEFAULT_REGION","us-east-2"),
        )
        # Test de conexión
        c.list_buckets()
        return c, True
    except Exception:
        return None, False


@st.cache_data(ttl=300)
def cargar_desde_s3():
    """
    Intenta cargar el último CSV de resultados PIML desde S3.
    Si no hay conexión o no hay archivo, genera datos demo realistas.
    """
    s3, ok = get_s3()
    if ok:
        try:
            r    = s3.list_objects_v2(Bucket=BUCKET, Prefix="resultados/")
            csvs = sorted([
                o["Key"] for o in r.get("Contents",[])
                if o["Key"].endswith(".csv") and "piml" in o["Key"].lower()
            ])
            if csvs:
                obj = s3.get_object(Bucket=BUCKET, Key=csvs[-1])
                df  = pd.read_csv(io.BytesIO(obj["Body"].read()), encoding="latin-1")
                df.columns = df.columns.str.replace("ï»¿","").str.strip()
                return df, f"✅ S3: {csvs[-1].split('/')[-1]}", True
        except Exception as e:
            st.warning(f"Error leyendo S3: {e}")

    # ── DATOS DEMO realistas (mismo motor PIML) ──────────────────
    np.random.seed(42); n=300
    perm = np.random.lognormal(5.5,0.9,n).clip(10,2000)
    temp = np.random.normal(88,22,n).clip(45,130)
    sal  = np.random.normal(45000,15000,n).clip(10000,100000)

    resultados=[]
    for i in range(n):
        eng   = PIMLEngine(T=temp[i], S=sal[i], C=0.8)
        skin  = eng.skin(perm[i], perm[i]*0.25)
        M     = eng.mob(85)
        eff_b = eng.sweep(2.5)
        eff_n = eng.sweep(M)
        mej   = max(0,(eff_n-eff_b)/max(1,eff_b)*100)
        fpi   = eng.fpi(perm[i])
        _,aho = eng.roi(500*mej/100)
        prio  = ("🔴 CRÍTICO" if skin>15 else "🟠 ALTO" if skin>8
                 else "🟡 MODERADO" if skin>3 else "🟢 BAJO")
        rec   = ("INYECTAR Na-CMC" if fpi<0.4 and temp[i]<90 and mej>5
                 else "EVALUAR" if mej>2 else "MONITOREAR")
        resultados.append({
            "pozo"         : f"UK-{['N','S','C','W'][i%4]}-{i:03d}",
            "cuenca"       : ["Northern N.Sea","Central N.Sea","Southern N.Sea","W.Shetland"][i%4],
            "temp_c"       : round(temp[i],1),
            "perm_md"      : round(perm[i],1),
            "skin"         : round(skin,3),
            "n_nacmc"      : round(eng.n,4),
            "K_nacmc"      : round(eng.K,2),
            "mob_ratio"    : round(M,4),
            "eff_base_pct" : round(eff_b,1),
            "eff_nacmc_pct": round(eff_n,1),
            "mejora_pct"   : round(mej,2),
            "fpi"          : round(fpi,4),
            "thermal_ok"   : bool(temp[i]<90),
            "ahorro_anual" : aho,
            "prioridad"    : prio,
            "recomendacion": rec,
        })
    return pd.DataFrame(resultados), "🔵 Demo (configura AWS Secrets para ver datos reales)", False


@st.cache_data(ttl=600)
def listar_s3():
    s3, ok = get_s3()
    if not ok: return []
    try:
        r = s3.list_objects_v2(Bucket=BUCKET)
        return [{"archivo":o["Key"],
                 "tamaño_KB":round(o["Size"]/1024,1),
                 "fecha":o["LastModified"].strftime("%d/%m/%Y %H:%M")}
                for o in r.get("Contents",[])]
    except:
        return []


# ═══════════════════════════════════════════════
# FIGURAS PLOTLY
# ═══════════════════════════════════════════════
def fig_gauge(skin):
    c   = GR if skin<3 else AM if skin<8 else RD
    lbl = "BAJO" if skin<3 else "MODERADO" if skin<8 else "SEVERO" if skin<20 else "CRÍTICO"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=skin,
        title={"text":f"FACTOR SKIN (S)<br><span style='font-size:12px;color:{c}'>{lbl}</span>",
               "font":{"size":14,"color":TX}},
        number={"font":{"size":42,"color":c,"family":"Courier New"}},
        gauge={"axis":{"range":[0,30],"tickfont":{"size":8,"color":"#6A8AAA"}},
               "bar":{"color":c,"thickness":0.25},"bgcolor":BG2,
               "steps":[{"range":[0,3],"color":"rgba(75,174,110,.1)"},
                        {"range":[3,8],"color":"rgba(232,160,48,.1)"},
                        {"range":[8,20],"color":"rgba(224,90,90,.1)"},
                        {"range":[20,30],"color":"rgba(200,0,0,.15)"}]}))
    fig.update_layout(paper_bgcolor=BG, font=dict(family="Courier New",color=TX),
                      margin=dict(l=20,r=20,t=60,b=20), height=260)
    return fig


def fig_rheo(en, eh):
    g  = np.logspace(-1,3,250)
    vn = [en.visc(x) for x in g]
    vh = [eh.visc(x) for x in g]
    tn = [en.K*(x**en.n) for x in g]
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=["Viscosidad vs Tasa de Corte","Esfuerzo Cortante τ = K·γⁿ"])
    fig.add_trace(go.Scatter(x=g,y=vn,name=f"Na-CMC (n={en.n:.3f})",
        line=dict(color=GR,width=3)), row=1,col=1)
    fig.add_trace(go.Scatter(x=g,y=vh,name=f"HPAM (n={eh.n:.3f})",
        line=dict(color=RD,width=2,dash="dash")), row=1,col=1)
    fig.add_vrect(x0=10,x1=100,fillcolor="rgba(75,174,110,.07)",
        line_color="rgba(75,174,110,.3)", row=1,col=1)
    fig.add_trace(go.Scatter(x=g,y=tn,name="τ Na-CMC",
        line=dict(color=BL,width=2.5),showlegend=True), row=1,col=2)
    fig.update_layout(**LAY, height=320)
    fig.update_xaxes(type="log", title_text="γ (s⁻¹)", gridcolor=BRD)
    fig.update_yaxes(type="log", title_text="η (mPa·s)", gridcolor=BRD, row=1,col=1)
    fig.update_yaxes(title_text="τ (Pa)", gridcolor=BRD, row=1,col=2)
    for ann in fig.layout.annotations: ann.font.color=TX; ann.font.size=10
    return fig


def fig_prod(bopd, extra, dias):
    t  = np.arange(0, dias+1)
    Qb = bopd * np.exp(-0.002*t)
    Qn = (bopd+extra) * np.exp(-0.0011*t)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.concatenate([t, t[::-1]]),
        y=np.concatenate([Qn, Qb[::-1]]),
        fill="toself", fillcolor="rgba(75,174,110,.1)",
        line=dict(color="rgba(0,0,0,0)"), name="Barriles extra"))
    fig.add_trace(go.Scatter(x=t,y=Qb,name="Baseline",
        line=dict(color=RD,width=2,dash="dash")))
    fig.add_trace(go.Scatter(x=t,y=Qn,name="Con Na-CMC FlowBio",
        line=dict(color=GR,width=3)))
    fig.update_layout(**LAY, height=320,
        xaxis_title="Días", yaxis_title="Producción (bbl/día)", hovermode="x unified")
    return fig


def fig_dashboard(df):
    """Dashboard 2×3 con datos reales o demo. Columnas opcionales manejadas con .get()."""

    # ── Columnas con fallback seguro ────────────────────────────
    has_perm   = "perm_md"       in df.columns
    has_eff_b  = "eff_base_pct"  in df.columns
    has_eff_n  = "eff_nacmc_pct" in df.columns
    has_mej    = "mejora_pct"    in df.columns
    has_fpi    = "fpi"           in df.columns
    has_aho    = "ahorro_anual"  in df.columns
    has_rec    = "recomendacion" in df.columns
    has_temp   = "temp_c"        in df.columns
    has_skin   = "skin"          in df.columns

    # Columnas de fallback
    x_perm   = df["perm_md"].clip(0,2000)   if has_perm  else np.ones(len(df))*250
    y_eff_b  = df["eff_base_pct"]           if has_eff_b else np.ones(len(df))*55
    y_eff_n  = df["eff_nacmc_pct"]          if has_eff_n else np.ones(len(df))*65
    col_mej  = df["mejora_pct"]             if has_mej   else np.ones(len(df))*10
    col_fpi  = df["fpi"]                    if has_fpi   else np.random.beta(1.5,5,len(df))
    col_aho  = df["ahorro_anual"]           if has_aho   else np.ones(len(df))*50000
    col_skin = df["skin"].clip(0,30)        if has_skin  else np.ones(len(df))*5
    col_temp = df["temp_c"]                 if has_temp  else np.ones(len(df))*85
    col_rec  = df["recomendacion"]          if has_rec   else np.full(len(df),"EVALUAR")
    col_pozo = df["pozo"]                   if "pozo"    in df.columns else df.index.astype(str)

    fig = make_subplots(rows=2,cols=3,
        subplot_titles=["Factor Skin — Distribución","Eficiencia Barrido EOR",
                        "Top 15 Pozos — Mayor Potencial","Riesgo Taponamiento (FPI)",
                        "Ahorro OPEX Anual","Temp. vs Permeabilidad"],
        vertical_spacing=0.18, horizontal_spacing=0.1)

    # 1. Skin histogram
    fig.add_trace(go.Histogram(x=col_skin, nbinsx=25,
        marker_color=RD, opacity=0.85, name="Skin"), row=1,col=1)
    fig.add_vline(x=float(col_skin.mean()), line_dash="dash", line_color=AM,
        annotation_text=f"Media: {col_skin.mean():.1f}", row=1,col=1)

    # 2. Scatter eficiencia
    fig.add_trace(go.Scatter(x=x_perm, y=y_eff_b,
        mode="markers",marker=dict(color=RD,size=4,opacity=0.5),name="Sin polímero"),row=1,col=2)
    fig.add_trace(go.Scatter(x=x_perm, y=y_eff_n,
        mode="markers",marker=dict(color=GR,size=4,opacity=0.6),name="Na-CMC FlowBio"),row=1,col=2)

    # 3. Top 15
    df2 = df.copy()
    df2["_mej"]  = col_mej.values
    df2["_rec"]  = col_rec.values
    df2["_pozo"] = col_pozo.values
    top = df2.nlargest(15,"_mej").sort_values("_mej")
    cols3=[GR if r=="INYECTAR Na-CMC" else AM if r=="EVALUAR" else BL
           for r in top["_rec"]]
    fig.add_trace(go.Bar(x=top["_mej"],y=top["_pozo"].astype(str).str[:14],
        orientation="h",marker_color=cols3,opacity=0.85,name="Mejora%"),row=1,col=3)

    # 4. FPI
    lbs=["Bajo<br><0.25","Mod<br>0.25-0.5","Alto<br>0.5-0.75","Crítico<br>>0.75"]
    fpi_s = pd.Series(col_fpi.values if hasattr(col_fpi,"values") else col_fpi)
    cnts=[len(fpi_s[fpi_s<0.25]),len(fpi_s[(fpi_s>=0.25)&(fpi_s<0.5)]),
          len(fpi_s[(fpi_s>=0.5)&(fpi_s<0.75)]),len(fpi_s[fpi_s>=0.75])]
    fig.add_trace(go.Bar(x=lbs,y=cnts,marker_color=[GR,AM,RD,"#CC0000"],
        opacity=0.85,name="FPI"),row=2,col=1)

    # 5. Ahorro
    df2["_aho"] = col_aho.values
    eco = df2.nlargest(12,"_aho").sort_values("_aho")
    fig.add_trace(go.Bar(x=eco["_aho"]/1000,y=eco["_pozo"].astype(str).str[:14],
        orientation="h",marker_color=BL,opacity=0.85,name="Ahorro K$"),row=2,col=2)

    # 6. Scatter temp vs perm
    fig.add_trace(go.Scatter(x=col_temp, y=x_perm,
        mode="markers",
        marker=dict(color=col_mej.values if hasattr(col_mej,"values") else col_mej,
                    colorscale="Viridis", size=5, opacity=0.7, showscale=True,
                    colorbar=dict(title="Mejora%",x=1.02,thickness=10)),
        name="Pozos"),row=2,col=3)
    fig.add_vline(x=90,line_dash="dot",line_color=AM,row=2,col=3)

    fig.update_layout(**LAY, height=680, showlegend=False,
        title=dict(text=f"FlowBio Intelligence — Dashboard · {len(df):,} pozos",
                   font=dict(size=13,color=GR),x=0.5))
    fig.update_xaxes(gridcolor=BRD,gridwidth=0.4,linecolor=BRD)
    fig.update_yaxes(gridcolor=BRD,gridwidth=0.4,linecolor=BRD)
    for ann in fig.layout.annotations: ann.font.color=TX; ann.font.size=9
    return fig


# ═══════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════
for key,val in [("simulated",False),("demo_well",None)]:
    if key not in st.session_state: st.session_state[key]=val

DEMOS = {
    "29/10-1 · Harbour Energy · Southern N. Sea":
        dict(T=72,S=33000,visc=88,perm=450,bopd=500,opex=15.5,conc=0.9,dias=120),
    "211/18-1 · BP · West of Shetland":
        dict(T=125,S=55000,visc=6, perm=75, bopd=280,opex=26.5,conc=0.6,dias=90),
    "49/9-1 · Perenco · Southern N. Sea":
        dict(T=58, S=22000,visc=200,perm=720,bopd=800,opex=13.0,conc=1.1,dias=180),
    "16/17-14 · Equinor · Central N. Sea":
        dict(T=105,S=44000,visc=22, perm=210,bopd=550,opex=18.2,conc=0.75,dias=120),
}
_d = st.session_state.demo_well or {}

_, s3_ok = get_s3()


# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:14px 0 8px'>
      <div style='font-size:22px;font-weight:900;color:#fff'>🛢️ FlowBio</div>
      <div style='font-size:9px;letter-spacing:2px;color:{GR};margin-top:2px'>
        INTELLIGENCE · PIML ENGINE
      </div>
    </div>
    <hr style='border-color:{BRD};margin:8px 0 12px'>
    <div style='text-align:center;margin-bottom:10px'>
      <span class='{'badge' if s3_ok else 'badge-b'}'>
        {'🟢 S3 Conectado' if s3_ok else '🔵 Modo Demo'}
      </span>
    </div>
    """, unsafe_allow_html=True)

    if not s3_ok:
        st.markdown(f"""
        <div class='wb' style='font-size:10px;margin-bottom:10px'>
          Para conectar tu S3:<br>
          Streamlit → Settings → Secrets<br>
          <code>[aws]<br>
          AWS_ACCESS_KEY_ID = "..."<br>
          AWS_SECRET_ACCESS_KEY = "..."<br>
          AWS_DEFAULT_REGION = "us-east-2"</code>
        </div>""", unsafe_allow_html=True)

    # Demo rápido
    st.markdown(f"<div class='ssc'>🚀 DEMO RÁPIDO — NSTA OPEN DATA</div>", unsafe_allow_html=True)
    demo_sel = st.selectbox("Pozo real", ["— Configuración manual —"]+list(DEMOS.keys()),
                            label_visibility="collapsed")
    if demo_sel != "— Configuración manual —":
        if st.button("▶ Cargar Demo y Simular", use_container_width=True, type="primary"):
            st.session_state.demo_well = DEMOS[demo_sel]
            st.session_state.simulated = True
            st.rerun()

    st.markdown(f"<hr style='border-color:{BRD};margin:10px 0'>", unsafe_allow_html=True)

    # Parámetros
    st.markdown(f"<div class='ssc'>🛢 PARÁMETROS DEL YACIMIENTO</div>", unsafe_allow_html=True)
    T    = st.slider("Temperatura (°C)", 40,130, int(_d.get("T",82)))
    S    = st.slider("Salinidad (ppm)", 5000,100000, int(_d.get("S",38000)), 1000, format="%d")
    visc = st.number_input("Viscosidad crudo (cP)", 1,2000, int(_d.get("visc",85)))
    perm = st.number_input("Permeabilidad (mD)",   1,3000, int(_d.get("perm",250)))
    bopd = st.number_input("Producción (bbl/día)", 10,5000, int(_d.get("bopd",500)))

    st.markdown(f"<div class='ssc'>⚗ NA-CMC FLOWBIO</div>", unsafe_allow_html=True)
    conc = st.slider("Concentración (%wt)", 0.05,2.0, float(_d.get("conc",0.8)), 0.05)
    dias = st.slider("Horizonte simulación (días)", 30,365, int(_d.get("dias",120)), 10)

    st.markdown(f"<div class='ssc'>💰 ECONOMÍA</div>", unsafe_allow_html=True)
    opex      = st.number_input("OPEX actual (USD/bbl)", 2.0,60.0, float(_d.get("opex",18.5)), 0.5)
    oil_price = st.number_input("Precio petróleo (USD/bbl)", 20.0,150.0, 74.5, 0.5)

    st.markdown(f"<hr style='border-color:{BRD};margin:12px 0 8px'>", unsafe_allow_html=True)

    if st.button("▶  EJECUTAR SIMULACIÓN PIML", use_container_width=True, type="primary"):
        st.session_state.simulated = True
        st.session_state.demo_well = None
        st.rerun()

    if st.session_state.simulated:
        if st.button("↺  Limpiar resultados", use_container_width=True):
            st.session_state.simulated = False
            st.session_state.demo_well = None
            st.rerun()

    st.markdown(f"""
    <div style='font-size:9px;color:#2A4A6A;text-align:center;margin-top:10px;line-height:1.7'>
      Motor PIML v0.3 · TRL 3<br>
      Calibración pendiente: IMP + CENAM<br>
      Amplifika UAG · WC 2026
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# CALCULAR CON EL MISMO MOTOR QUE SAGEMAKER
# ═══════════════════════════════════════════════
eng_n = PIMLEngine(T=T, S=S, C=conc, fluid="Na-CMC")
eng_h = PIMLEngine(T=T, S=S, C=conc, fluid="HPAM")

skin_v  = eng_n.skin(perm, perm*0.25, 8.0, 0.35)
skin_n2 = eng_n.skin(perm, perm*0.85, 8.0, 0.35)
M_v     = eng_n.mob(visc)
eff_b   = eng_n.sweep(2.5)
eff_n   = eng_n.sweep(M_v)
extra   = max(0, bopd*(eff_n-eff_b)/max(1,eff_b))
neto_m, ahorro_yr = eng_n.roi(extra, opex, oil_price)
roi_pct = round((neto_m/max(1, (150*0.159*(conc/100)*1000)*2.8*30))*100, 1)
fpi_v   = eng_n.fpi(perm)


# ═══════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════
st.markdown(f"""
<div style='background:linear-gradient(135deg,#0a2235,#0d3320);border:1px solid #1E6040;
            border-radius:14px;padding:20px 26px;margin-bottom:20px;
            display:flex;align-items:center;gap:16px'>
  <div style='font-size:36px'>🛢️</div>
  <div style='flex:1'>
    <div style='font-size:20px;font-weight:800;color:#fff'>
      FlowBio Intelligence: Subsurface Diagnostic Console
    </div>
    <div style='font-size:11px;color:#7ABF8A;margin-top:3px;letter-spacing:.7px'>
      PHYSICS-INFORMED ML · EOR · NA-CMC · SKIN FACTOR · AWS S3 DATA LAKE
    </div>
  </div>
  <div style='display:flex;flex-direction:column;gap:5px;align-items:flex-end'>
    <span class='badge'>PIML v0.3 · TRL 3</span>
    <span class='{'badge' if s3_ok else 'badge-b'}'>{'🟢 S3 Live' if s3_ok else '🔵 Demo'}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PANTALLA INICIAL — antes de simular
# ═══════════════════════════════════════════════
if not st.session_state.simulated:
    st.markdown(f"""
    <div style='text-align:center;padding:36px 0 20px'>
      <div style='font-size:52px;margin-bottom:12px'>🛢️</div>
      <div style='font-size:24px;font-weight:800;color:#fff;margin-bottom:8px'>FlowBio AI Engine</div>
      <div style='font-size:13px;color:#6A8AAA;max-width:480px;margin:0 auto;line-height:1.8'>
        Simulador PIML para diagnóstico de pozos maduros.<br>
        Factor Skin · Na-CMC · AWS S3 · Modelo Success Fee.
      </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    items = [("⚗","Na-CMC FlowBio","Biopolímero desde<br>jacinto de agua · Orizaba"),
             ("🧮","Power Law PIML","τ = K·γⁿ<br>Ostwald-de Waele"),
             ("🎯","Factor Skin","S = (K/Kd-1)·ln(rd/rw)<br>van Everdingen-Hurst"),
             ("💰","Success Fee","$5 USD por barril<br>extra producido")]
    for col,(ico,tit,sub) in zip([c1,c2,c3,c4],items):
        with col:
            st.markdown(f"""
            <div class='mc' style='padding:22px 14px'>
              <div style='font-size:28px;margin-bottom:10px'>{ico}</div>
              <div style='font-size:13px;font-weight:700;color:{TX};margin-bottom:6px'>{tit}</div>
              <div style='font-size:10px;color:#6A8AAA;line-height:1.6'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"<div class='sh' style='margin-top:28px'>🌊 POZOS DEMO — NSTA UK NORTH SEA</div>",
                unsafe_allow_html=True)
    wcols = st.columns(len(DEMOS))
    for col,(wn,wd) in zip(wcols,DEMOS.items()):
        parts = wn.split("·")
        with col:
            st.markdown(f"""
            <div class='mc' style='padding:14px'>
              <div style='font-size:13px;font-weight:700;color:{BL};font-family:monospace'>
                {parts[0].strip()}
              </div>
              <div style='font-size:10px;color:{GR};margin:3px 0'>
                {parts[1].strip() if len(parts)>1 else ''}
              </div>
              <div style='font-size:9px;color:#6A8AAA;margin-bottom:8px'>
                {parts[2].strip() if len(parts)>2 else ''}
              </div>
              <div style='font-size:9px;color:#6A8AAA;line-height:1.8'>
                🌡 {wd['T']}°C · 📊 {wd['perm']} mD<br>
                🛢 {wd['bopd']} bbl/d · 💧 {wd['S']//1000}K ppm
              </div>
            </div>""", unsafe_allow_html=True)

    if s3_ok:
        st.markdown(f"<div class='sh' style='margin-top:28px'>📦 ARCHIVOS EN TU S3</div>",
                    unsafe_allow_html=True)
        files = listar_s3()
        if files:
            st.dataframe(pd.DataFrame(files), use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay archivos de resultados. Ejecuta el notebook en SageMaker primero.")

    st.stop()


# ═══════════════════════════════════════════════
# RESULTADOS — tras pulsar Simular o Demo
# ═══════════════════════════════════════════════
sk_c = "r" if skin_v>8 else "a" if skin_v>3 else "g"
mb_c = "g" if M_v<1 else "a" if M_v<2 else "r"

c1,c2,c3,c4,c5 = st.columns(5)
kpis = [
    (f"{skin_v:.2f}", sk_c, "FACTOR SKIN (S)",      "S=(K/Kd-1)·ln(rd/rw)"),
    (f"{eng_n.n:.3f}", "b", "ÍNDICE FLUJO (n)",     "Power Law Na-CMC"),
    (f"{eff_n:.1f}%",  "g", "EF. BARRIDO EOR",      f"vs {eff_b:.1f}% baseline"),
    (f"{M_v:.3f}",    mb_c, "RATIO MOVILIDAD M",    "Favorable" if M_v<1 else "Desfav."),
    (f"${ahorro_yr:,.0f}", "g", "AHORRO ANUAL USD", f"+{extra:.0f} bbl/día extra"),
]
for col,(val,cls,lbl,sub) in zip([c1,c2,c3,c4,c5],kpis):
    with col:
        st.markdown(f"""
        <div class='mc'>
          <div class='mv v{cls}'>{val}</div>
          <div class='ml'>{lbl}</div>
          <div class='ms'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "🎯 Diagnóstico & Skin",
    "⚗ Reología Power Law",
    "📈 Producción & Economía",
    "📊 Dashboard S3",
    "📦 Data Lake",
])

# ── TAB 1 ────────────────────────────────────
with tab1:
    cg,ci = st.columns([1,1.4])
    with cg:
        st.markdown("<div class='sh'>🎯 FACTOR SKIN — VELOCÍMETRO DE DAÑO</div>",
                    unsafe_allow_html=True)
        st.plotly_chart(fig_gauge(skin_v), use_container_width=True)

    with ci:
        st.markdown("<div class='sh'>📋 DIAGNÓSTICO TÉCNICO</div>", unsafe_allow_html=True)
        red_pct = ((skin_v-skin_n2)/max(0.01,skin_v))*100
        th_ok   = T < 90

        st.markdown(f"""
        <div class='ib'>
          <strong style='color:{GR}'>⚡ Modelo Ostwald-de Waele (Power Law)</strong><br>
          Na-CMC: n={eng_n.n:.4f} | K={eng_n.K:.1f} mPa·sⁿ<br>
          HPAM:   n={eng_h.n:.4f} | K={eng_h.K:.1f} mPa·sⁿ<br><br>
          n &lt; 1 → pseudoplástico ✓ ideal para EOR<br>
          Menor n = mayor shear-thinning = mejor inyección
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='sb'>
          <strong>📉 Impacto Na-CMC FlowBio en este pozo</strong><br>
          Skin actual: <strong>{skin_v:.2f}</strong>
          → Con Na-CMC: <strong>{skin_n2:.2f}</strong>
          (reducción <strong>{red_pct:.0f}%</strong>)<br>
          Temperatura: <strong>{T}°C</strong>
          {'✅ Dentro del límite 90°C' if th_ok else '⚠️ Sobre el límite — usar con precaución'}<br>
          FPI (riesgo taponamiento): <strong>{fpi_v:.3f}</strong>
          — {'✅ BAJO' if fpi_v<0.25 else '⚠️ MODERADO' if fpi_v<0.5 else '❌ ALTO'}
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='sh' style='margin-top:14px'>⚙ OPERATIONAL READINESS</div>",
                    unsafe_allow_html=True)
        df_or = pd.DataFrame({
            "Indicador":["Estab. térmica","Compat. salina","Skin Damage",
                         "Ratio Movilidad","Riesgo FPI","Biodegradabilidad","HSE"],
            "Estado actual":[
                "✅ OK" if th_ok else "⚠️ Sobre límite",
                "✅ OK" if S<70000 else "⚠️ Alta",
                "❌ Alto" if skin_v>8 else "⚠️ Mod." if skin_v>3 else "✅ Bajo",
                "✅ Favorable" if M_v<1 else "⚠️ Desfavorable",
                "✅ Bajo" if fpi_v<0.25 else "⚠️ Moderado" if fpi_v<0.5 else "❌ Alto",
                "❌ No biodegradable","❌ Tóxico (HPAM)"],
            "Con Na-CMC FlowBio":[
                "✅ Límite 90°C","✅ Hasta 80K ppm",
                f"✅ Reducción {red_pct:.0f}%","✅ Mejor control M",
                "✅ FPI muy bajo","✅ 100% biodegradable","✅ Cero toxicidad"],
        })
        st.dataframe(df_or, use_container_width=True, hide_index=True)

# ── TAB 2 ────────────────────────────────────
with tab2:
    st.markdown("<div class='sh'>⚗ CURVAS REOLÓGICAS — POWER LAW</div>", unsafe_allow_html=True)
    st.plotly_chart(fig_rheo(eng_n, eng_h), use_container_width=True)
    fc1,fc2,fc3 = st.columns(3)
    for col,txt in zip([fc1,fc2,fc3],[
        f"τ = K·γⁿ\nLey de Potencia",
        f"η = K·γ^(n-1)\nViscosidad Aparente",
        f"n = {eng_n.n:.4f}  K = {eng_n.K:.1f}\nParámetros Na-CMC"]):
        with col:
            st.markdown(f"""
            <div style='background:#060e18;border:1px solid {BRD};border-radius:8px;
                        padding:12px;font-family:monospace;font-size:13px;
                        color:{PU};text-align:center;white-space:pre'>{txt}</div>""",
                        unsafe_allow_html=True)

# ── TAB 3 ────────────────────────────────────
with tab3:
    st.markdown(f"""
    <div class='hero'>
      <div style='font-size:9px;letter-spacing:2px;color:{GR};margin-bottom:6px;font-weight:700'>
        SUCCESS FEE MENSUAL NETO — MODELO ADÁN RAMÍREZ
      </div>
      <div class='hv'>${neto_m:,.0f} USD</div>
      <div class='hs'>
        {extra:.1f} bbl/día extra × $5 USD × 30 días — costo Na-CMC
      </div>
    </div>""", unsafe_allow_html=True)

    e1,e2,e3,e4 = st.columns(4)
    poly_d = (150*0.159*(conc/100)*1000)*2.8*30
    fee_d  = extra*5*30
    for col,(val,cls,lbl,sub) in zip([e1,e2,e3,e4],[
        (f"+{extra:.1f}","g","BARRILES EXTRA/DÍA",f"sobre {bopd} bbl/d base"),
        (f"${fee_d:,.0f}","b","SUCCESS FEE/MES","$5/bbl extra"),
        (f"${poly_d:,.0f}","a","COSTO POLÍMERO/MES","Na-CMC · Orizaba"),
        (f"{roi_pct:.0f}%","g","ROI INMEDIATO",f"Ahorro: ${ahorro_yr:,.0f}/año"),
    ]):
        with col:
            st.markdown(f"""
            <div class='mc'>
              <div class='mv v{cls}'>{val}</div>
              <div class='ml'>{lbl}</div>
              <div class='ms'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_prod(bopd, extra, dias), use_container_width=True)

# ── TAB 4 — Dashboard S3 ─────────────────────
with tab4:
    st.markdown("<div class='sh'>📊 DASHBOARD — DATOS DESDE S3</div>", unsafe_allow_html=True)
    with st.spinner("Cargando datos desde S3..."):
        df_s3, fuente, es_s3 = cargar_desde_s3()

    if es_s3:
        st.markdown(f"<div class='sb'>{fuente} · {len(df_s3):,} pozos</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='wb'>{fuente}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    d1,d2,d3,d4 = st.columns(4)
    skin_mean = df_s3["skin"].mean() if "skin" in df_s3.columns else 5.0
    mej_mean  = df_s3["mejora_pct"].mean() if "mejora_pct" in df_s3.columns else 10.0
    aho_mean  = df_s3["ahorro_anual"].mean() if "ahorro_anual" in df_s3.columns else 50000.0
    for col,(val,cls,lbl) in zip([d1,d2,d3,d4],[
        (f"{len(df_s3):,}","b","POZOS ANALIZADOS"),
        (f"{skin_mean:.2f}","r" if skin_mean>8 else "a","SKIN PROMEDIO"),
        (f"{mej_mean:.1f}%","g","MEJORA EOR PROM."),
        (f"${aho_mean:,.0f}","g","AHORRO ANUAL PROM."),
    ]):
        with col:
            st.markdown(f"""
            <div class='mc'>
              <div class='mv v{cls}'>{val}</div>
              <div class='ml'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_dashboard(df_s3), use_container_width=True)

    st.markdown("<div class='sh'>🏆 TOP 10 — MAYOR POTENCIAL EOR</div>", unsafe_allow_html=True)
    all_cols = ["pozo","cuenca","temp_c","perm_md","skin",
                "mejora_pct","ahorro_anual","recomendacion","prioridad"]
    cols_show = [c for c in all_cols if c in df_s3.columns]
    sort_col  = "mejora_pct" if "mejora_pct" in df_s3.columns else df_s3.columns[0]
    st.dataframe(df_s3.nlargest(10, sort_col)[cols_show].reset_index(drop=True),
                 use_container_width=True, hide_index=True)

# ── TAB 5 — Data Lake ────────────────────────
with tab5:
    st.markdown("<div class='sh'>📦 AWS S3 DATA LAKE — FLOWBIO</div>", unsafe_allow_html=True)
    if s3_ok:
        st.markdown(f"<div class='sb'>✅ Bucket: <code>{BUCKET}</code></div>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        files = listar_s3()
        if files:
            st.dataframe(pd.DataFrame(files), use_container_width=True, hide_index=True)
        else:
            st.info("Sin archivos todavía. Ejecuta el notebook en SageMaker para generar resultados.")
    else:
        st.markdown(f"""
        <div class='wb'>
          <strong>Para conectar tu S3 a Streamlit Cloud:</strong><br><br>
          1. share.streamlit.io → tu app → <strong>Settings → Secrets</strong><br>
          2. Pega exactamente esto:<br><br>
          <pre>[aws]
AWS_ACCESS_KEY_ID     = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_DEFAULT_REGION    = "us-east-2"</pre>
          3. Reemplaza los valores con tus credenciales reales de AWS IAM<br>
          4. Save → Reboot app
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <br>
    <div class='ib'>
      <strong style='color:{GR}'>🏗️ Arquitectura Gemelo Digital FlowBio</strong><br><br>
      📦 <strong>S3 Data Lake</strong>
         → almacena CSVs UKCS + resultados PIML<br>
      🧠 <strong>SageMaker</strong>
         → ejecuta motor PIML sobre todos los pozos<br>
      📊 <strong>Streamlit Cloud</strong>
         → visualización pública, siempre activa<br>
      ⚗ <strong>Na-CMC FlowBio</strong>
         → biopolímero desde lirio acuático · Orizaba, Ver.<br><br>
      Motor PIML v0.3 · TRL 3 · Calibración pendiente: IMP + CENAM<br>
      Amplifika UAG · Startup Building Beyond World Cup 2026
    </div>""", unsafe_allow_html=True)

# FOOTER
st.markdown(f"""
<hr style='border-color:{BRD};margin:28px 0 14px'>
<div style='text-align:center;font-size:9px;color:#2A4A6A;line-height:1.8'>
  <strong style='color:{GR}'>FlowBio Intelligence</strong> · Motor PIML v0.3 · TRL 3 ·
  Na-CMC desde <em>Eichhornia crassipes</em> · Orizaba, Veracruz, MX<br>
  Startup Building Beyond the World Cup 2026 · Amplifika UAG
</div>
""", unsafe_allow_html=True)
