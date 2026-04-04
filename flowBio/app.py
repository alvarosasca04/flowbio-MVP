"""
FlowBio Intelligence — Subsurface Diagnostic Console v2
Mapa interactivo de pozos · S3 Data Lake · Motor PIML · Gemelo Digital
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math, io, warnings, json
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BUCKET = "flowbio-data-lake-v2-627807503177-us-east-2-an"

# Paleta FlowBio
BG="#0D1B2A"; BG2="#0A1520"; BG3="#071018"; BRD="#1E3A60"
TX="#D0E4F8"; GR="#4BAE6E"; BL="#4A9FD4"; RD="#E05A5A"
AM="#E8A030"; PU="#9B7FD4"; GR2="#3A7D44"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{
  background:{BG};
  color:{TX};
  font-family:'Outfit',sans-serif;
}}
section[data-testid="stSidebar"] {{
  background:{BG2};
  border-right:1px solid {BRD};
}}

/* ── CARDS ── */
.kcard {{
  background:{BG2};
  border:1px solid {BRD};
  border-radius:14px;
  padding:18px 14px;
  text-align:center;
  position:relative;
  overflow:hidden;
}}
.kcard::before {{
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:3px;
  background:linear-gradient(90deg,{BL},{GR});
}}
.kval {{
  font-size:32px;
  font-weight:900;
  font-family:'Space Mono',monospace;
  line-height:1.1;
  margin:6px 0 4px;
}}
.klbl {{
  font-size:9px;
  letter-spacing:2px;
  color:#6A8AAA;
  font-weight:700;
  text-transform:uppercase;
}}
.ksub  {{ font-size:10px; color:#4A7AAA; margin-top:3px; }}
.vg {{ color:{GR}; }}
.vb {{ color:{BL}; }}
.vr {{ color:{RD}; }}
.va {{ color:{AM}; }}
.vp {{ color:{PU}; }}

/* ── SECTION HEADERS ── */
.sec-hdr {{
  font-size:9px;
  letter-spacing:2.5px;
  color:#6A8AAA;
  font-weight:700;
  text-transform:uppercase;
  border-bottom:1px solid {BRD};
  padding-bottom:8px;
  margin:22px 0 14px;
  display:flex;
  align-items:center;
  gap:8px;
}}

/* ── BADGES ── */
.badge-g {{ background:rgba(75,174,110,.15); border:1px solid {GR}; border-radius:20px; padding:3px 12px; font-size:10px; color:{GR}; font-weight:700; display:inline-block; }}
.badge-b {{ background:rgba(74,159,212,.15); border:1px solid {BL}; border-radius:20px; padding:3px 12px; font-size:10px; color:{BL}; font-weight:700; display:inline-block; }}
.badge-r {{ background:rgba(224,90,90,.15);  border:1px solid {RD}; border-radius:20px; padding:3px 12px; font-size:10px; color:{RD}; font-weight:700; display:inline-block; }}
.badge-a {{ background:rgba(232,160,48,.15); border:1px solid {AM}; border-radius:20px; padding:3px 12px; font-size:10px; color:{AM}; font-weight:700; display:inline-block; }}

/* ── INFO BOXES ── */
.box-b {{ background:rgba(74,159,212,.08); border:1px solid rgba(74,159,212,.3); border-radius:10px; padding:14px; font-size:12px; color:#A0C4D8; line-height:1.7; }}
.box-g {{ background:rgba(75,174,110,.1);  border:1px solid rgba(75,174,110,.4); border-radius:10px; padding:14px; font-size:12px; color:#7ABF8A; line-height:1.7; }}
.box-a {{ background:rgba(232,160,48,.08); border:1px solid rgba(232,160,48,.3); border-radius:10px; padding:12px; font-size:12px; color:#E8C080; line-height:1.7; }}

/* ── HERO ── */
.hero-card {{
  background:linear-gradient(135deg,rgba(75,174,110,.18),rgba(74,159,212,.1));
  border:1px solid {GR};
  border-radius:16px;
  padding:24px;
  text-align:center;
  margin-bottom:18px;
}}
.hero-val {{
  font-size:52px;
  font-weight:900;
  color:{GR};
  font-family:'Space Mono',monospace;
  letter-spacing:-2px;
  line-height:1;
}}
.hero-lbl {{
  font-size:9px;
  letter-spacing:2.5px;
  color:{GR};
  font-weight:700;
  margin-bottom:8px;
}}
.hero-sub {{ font-size:12px; color:#7ABF8A; margin-top:6px; }}

/* ── SIDEBAR ── */
.ssc {{
  font-size:9px;
  letter-spacing:2px;
  color:{GR};
  font-weight:700;
  text-transform:uppercase;
  margin:16px 0 8px;
}}

/* ── WELL TABLE ROWS ── */
.well-row {{
  background:{BG2};
  border:1px solid {BRD};
  border-radius:8px;
  padding:10px 14px;
  margin-bottom:6px;
  display:flex;
  align-items:center;
  gap:12px;
  cursor:pointer;
  transition:border-color .2s;
}}
.well-row:hover {{ border-color:{BL}; }}
.well-id {{ font-family:'Space Mono',monospace; font-size:13px; color:{BL}; font-weight:700; min-width:90px; }}
.well-meta {{ font-size:10px; color:#6A8AAA; }}

/* ── OR BADGE ── */
.or-ok   {{ display:inline-block; background:rgba(75,174,110,.15);  border:1px solid {GR}; border-radius:4px; padding:2px 8px; font-size:10px; color:{GR}; font-weight:700; }}
.or-warn {{ display:inline-block; background:rgba(232,160,48,.15); border:1px solid {AM}; border-radius:4px; padding:2px 8px; font-size:10px; color:{AM}; font-weight:700; }}
.or-bad  {{ display:inline-block; background:rgba(224,90,90,.15);  border:1px solid {RD}; border-radius:4px; padding:2px 8px; font-size:10px; color:{RD}; font-weight:700; }}

/* ── TABS ── */
.stTabs [aria-selected="true"] {{ color:{GR} !important; border-bottom:2px solid {GR} !important; }}
.stTabs [data-baseweb="tab"] {{ color:#6A8AAA; font-family:'Outfit',sans-serif; }}

div[data-testid="metric-container"] {{
  background:{BG2};
  border:1px solid {BRD};
  border-radius:10px;
  padding:14px;
}}
</style>
""", unsafe_allow_html=True)

LAY = dict(
    paper_bgcolor=BG, plot_bgcolor=BG2,
    font=dict(family="Space Mono, monospace", color=TX, size=10),
    margin=dict(l=50,r=20,t=40,b=50),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BRD, borderwidth=1),
    xaxis=dict(gridcolor=BRD, gridwidth=0.4, linecolor=BRD),
    yaxis=dict(gridcolor=BRD, gridwidth=0.4, linecolor=BRD),
)

# ═══════════════════════════════════════════════════════════════
# MOTOR PIML
# ═══════════════════════════════════════════════════════════════
class PIML:
    def __init__(self, T=85, S=45000, C=0.8, fluid="Na-CMC"):
        self.T=T; self.S=S; self.C=C; self.fluid=fluid
        self.n = float(np.clip(
            0.65-(T/1200)-(S/600000)-(C*0.08) if fluid=="Na-CMC"
            else 0.78-(T/900)-(S/500000)-(C*0.05), 0.25, 0.90))
        self.K = float(max(30,
            160-(T*0.75)+(S*0.001)+(C*12) if fluid=="Na-CMC"
            else 200-(T*0.90)+(S*0.0008)+(C*10)))

    def visc(self, g=10):  return float(np.clip(self.K*(g**(self.n-1)),1,5000))
    def skin(self, K, Kd, rd=8, rw=0.35): return float((K/Kd-1)*math.log(rd/rw)) if Kd>0 else 0.0
    def mob(self, vo=85, g=10): return float(np.clip((0.4/self.visc(g))/(0.8/vo),0.05,8))
    def sweep(self, M):
        if M<=0.5: return 90.0
        elif M<=1.0: return 90-(M-0.5)*20
        elif M<=2.0: return 80-(M-1.0)*25
        return max(30, 55-(M-2)*10)
    def fpi(self, perm):
        pf=2.5 if perm<50 else 1.5 if perm<150 else 1.0 if perm<400 else 0.7
        return float(np.clip(0.12*pf*(1+max(0,(self.S-60000)/20000)),0,1))
    def roi(self, extra, opex=18.5, oil=74.5):
        fee=extra*5.0*30; cost=(150*0.159*(self.C/100)*1000)*2.8*30
        return round(fee-cost,2), round(extra*(oil-opex)*0.19*365,0)


# ═══════════════════════════════════════════════════════════════
# S3 CONNECTION
# ═══════════════════════════════════════════════════════════════
@st.cache_resource(ttl=300)
def get_s3():
    try:
        import boto3
        c = boto3.client("s3",
            aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["aws"].get("AWS_DEFAULT_REGION","us-east-2"))
        c.list_buckets(); return c, True
    except: return None, False

@st.cache_data(ttl=300)
def cargar_pozos_s3():
    """
    Carga el CSV de pozos desde S3.
    Detecta columnas de coordenadas automáticamente.
    Si no hay S3, genera datos demo con coordenadas del Mar del Norte.
    """
    s3, ok = get_s3()
    WELL_FILES = [
        "UKCS_well_availability_collated_tops_(WGS84)_2454963035769896595 (1).csv",
        "resultados/flowbio_piml_analisis.csv",
        "resultados_piml.csv",
    ]
    if ok:
        # Intentar listar y encontrar CSV de pozos
        try:
            r = s3.list_objects_v2(Bucket=BUCKET)
            keys = [o["Key"] for o in r.get("Contents",[])]
            for fname in WELL_FILES:
                if fname in keys:
                    obj = s3.get_object(Bucket=BUCKET, Key=fname)
                    df  = pd.read_csv(io.BytesIO(obj["Body"].read()),
                                      encoding="latin-1", low_memory=False)
                    df.columns = df.columns.str.replace("ï»¿","").str.strip()
                    return df, fname, True
            # Usar el primer CSV que haya
            csvs = [k for k in keys if k.endswith(".csv")]
            if csvs:
                obj = s3.get_object(Bucket=BUCKET, Key=csvs[0])
                df  = pd.read_csv(io.BytesIO(obj["Body"].read()),
                                  encoding="latin-1", low_memory=False)
                df.columns = df.columns.str.replace("ï»¿","").str.strip()
                return df, csvs[0], True
        except Exception as e:
            st.warning(f"S3 error: {e}")

    # ── DEMO con coordenadas reales del Mar del Norte ──────────
    np.random.seed(42); n=80
    pozos_reales = [
        ("29/10-1","Harbour Energy","Southern N. Sea", 55.82,  2.11, 72, 450, 500, 15.5),
        ("211/18-1","BP","West of Shetland",           61.16, -2.08,125,  75, 280, 26.5),
        ("49/9-1","Perenco","Southern N. Sea",          53.31,  2.85, 58, 720, 800, 13.0),
        ("16/17-14","Equinor","Central N. Sea",          57.83,  1.72,105, 210, 550, 18.2),
        ("21/25-1","CNOOC","Central N. Sea",             57.10,  2.45, 88, 320, 680, 17.5),
        ("9/13-1","Shell","Northern N. Sea",             58.92,  1.28,112, 180, 300, 22.5),
        ("15/17-1","BP","Central N. Sea",                57.50,  1.90, 98,  95, 420, 19.8),
        ("30/13-2","Spirit Energy","Southern N. Sea",    54.10,  2.20, 65, 580, 620, 14.2),
        ("206/8-1","Equinor","West of Shetland",         60.50, -2.40,118,  90, 260, 28.0),
        ("3/14b-7","EnQuest","Northern N. Sea",          58.50,  1.55,108, 160, 340, 23.0),
        ("22/14a-7","Repsol","Central N. Sea",           57.30,  2.15, 94, 140, 380, 21.0),
        ("14/25-1","Shell","Central N. Sea",             57.80,  1.50,101, 115, 350, 22.0),
        ("20/5-1","Dana Petroleum","Central N. Sea",     57.00,  2.80, 82, 380, 590, 16.8),
        ("38/8-1","Ithaca Energy","Southern N. Sea",     54.50,  2.60, 68, 640, 710, 13.8),
        ("12/21-1","TotalEnergies","Northern N. Sea",    58.20,  1.80, 95, 190, 460, 20.5),
    ]
    rows = []
    for (wid,op,basin,lat,lon,T,perm,bopd,opex) in pozos_reales:
        eng  = PIML(T=T, S=40000, C=0.8)
        skin = eng.skin(perm, perm*0.25)
        M    = eng.mob(85)
        eff_b= eng.sweep(2.5)
        eff_n= eng.sweep(M)
        mej  = max(0,(eff_n-eff_b)/max(1,eff_b)*100)
        fpi  = eng.fpi(perm)
        _,aho= eng.roi(bopd*mej/100, opex)
        rows.append({
            "WellName":wid, "Operator":op, "Basin":basin,
            "Latitude":lat, "Longitude":lon,
            "Temperature_C":T, "Permeability_mD":perm,
            "Production_bpd":bopd, "OPEX_bbl":opex,
            "skin":round(skin,3), "n_nacmc":round(eng.n,4),
            "K_nacmc":round(eng.K,2), "mob_ratio":round(M,4),
            "eff_base_pct":round(eff_b,1), "eff_nacmc_pct":round(eff_n,1),
            "mejora_pct":round(mej,2), "fpi":round(fpi,4),
            "ahorro_anual":aho,
            "prioridad":"🔴 CRÍTICO" if skin>15 else "🟠 ALTO" if skin>8 else "🟡 MODERADO" if skin>3 else "🟢 BAJO",
            "recomendacion":"INYECTAR Na-CMC" if fpi<0.4 and T<90 and mej>5 else "EVALUAR" if mej>2 else "MONITOREAR",
        })
    return pd.DataFrame(rows), "Demo (NSTA North Sea)", False


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
    except: return []


# ═══════════════════════════════════════════════════════════════
# DETECTAR COLUMNAS CLAVE
# ═══════════════════════════════════════════════════════════════
def detectar(df, opciones):
    for col in df.columns:
        if any(k in col.lower() for k in opciones):
            return col
    return None

def get_col(df, opciones, default=None):
    c = detectar(df, opciones)
    return df[c] if c else (pd.Series([default]*len(df)) if default is not None else None)


# ═══════════════════════════════════════════════════════════════
# MAPA INTERACTIVO DE POZOS
# ═══════════════════════════════════════════════════════════════
def fig_mapa(df, sel_well=None):
    """
    Mapa interactivo del Mar del Norte con todos los pozos del CSV.
    Color por nivel de daño (skin factor).
    """
    col_lat  = detectar(df, ["lat","latitude"])
    col_lon  = detectar(df, ["lon","long","longitude"])
    col_name = detectar(df, ["wellname","well_name","name","nombre","uwi","wellid"])
    col_skin = detectar(df, ["skin"])
    col_op   = detectar(df, ["operator","operador","company"])
    col_rec  = detectar(df, ["recomendacion","recommendation"])
    col_mej  = detectar(df, ["mejora","improvement"])
    col_aho  = detectar(df, ["ahorro","saving","annual"])

    if not col_lat or not col_lon:
        # Coordenadas del Mar del Norte como fallback
        lat_arr = np.random.uniform(53, 62, len(df))
        lon_arr = np.random.uniform(-3, 4, len(df))
    else:
        lat_arr = pd.to_numeric(df[col_lat], errors="coerce").fillna(57.5).values
        lon_arr = pd.to_numeric(df[col_lon], errors="coerce").fillna(1.5).values

    names  = df[col_name].astype(str).values  if col_name else [f"Pozo-{i}" for i in range(len(df))]
    skins  = pd.to_numeric(df[col_skin], errors="coerce").fillna(5).values if col_skin else np.ones(len(df))*5
    ops    = df[col_op].astype(str).values    if col_op   else ["—"]*len(df)
    recs   = df[col_rec].astype(str).values   if col_rec  else ["EVALUAR"]*len(df)
    mejs   = pd.to_numeric(df[col_mej], errors="coerce").fillna(10).values if col_mej else np.ones(len(df))*10
    ahos   = pd.to_numeric(df[col_aho], errors="coerce").fillna(0).values  if col_aho else np.zeros(len(df))

    # Color por skin
    colors = [GR if s<3 else AM if s<8 else RD for s in skins]
    sizes  = np.clip(8 + skins * 0.8, 8, 22)

    hover = [
        f"<b>{n}</b><br>"
        f"Operadora: {o}<br>"
        f"Skin: <b>{s:.2f}</b><br>"
        f"Mejora EOR: <b>{m:.1f}%</b><br>"
        f"Ahorro: <b>${a:,.0f}/año</b><br>"
        f"Recomendación: <b>{r}</b>"
        for n,o,s,m,a,r in zip(names,ops,skins,mejs,ahos,recs)
    ]

    fig = go.Figure()

    # Fondo del Mar del Norte con Scattergeo
    fig.add_trace(go.Scattergeo(
        lat=lat_arr, lon=lon_arr,
        mode="markers+text",
        marker=dict(
            color=colors,
            size=sizes,
            line=dict(color=BG2, width=1.2),
            opacity=0.88,
        ),
        text=names,
        textposition="top center",
        textfont=dict(size=8, color=TX, family="Space Mono"),
        hovertemplate=hover,
        hoverinfo="text",
        name="Pozos UKCS",
    ))

    # Pozo seleccionado — destacar
    if sel_well is not None and sel_well < len(df):
        fig.add_trace(go.Scattergeo(
            lat=[lat_arr[sel_well]],
            lon=[lon_arr[sel_well]],
            mode="markers",
            marker=dict(
                color=BL, size=20,
                line=dict(color="#fff", width=2.5),
                symbol="star",
            ),
            name=f"Seleccionado: {names[sel_well]}",
            hovertemplate=hover[sel_well],
            hoverinfo="text",
        ))

    fig.update_layout(
        geo=dict(
            scope="europe",
            resolution=50,
            showland=True,
            landcolor="#1A2E1A",
            showocean=True,
            oceancolor="#0A1828",
            showlakes=True,
            lakecolor="#0A1828",
            showcountries=True,
            countrycolor=BRD,
            showcoastlines=True,
            coastlinecolor="#2A4A3A",
            projection_type="natural earth",
            center=dict(lat=57.5, lon=1.0),
            lonaxis=dict(range=[-5, 8]),
            lataxis=dict(range=[50, 63]),
            bgcolor=BG,
        ),
        paper_bgcolor=BG,
        margin=dict(l=0,r=0,t=30,b=0),
        height=460,
        title=dict(
            text=f"<b>Mar del Norte — {len(df)} Pozos UKCS</b>  <span style='font-size:11px;color:{GR}'>● Verde=Bajo  ● Ámbar=Moderado  ● Rojo=Alto/Crítico</span>",
            font=dict(size=13, color=TX),
            x=0.01,
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TX)),
        showlegend=True,
    )
    return fig


# ═══════════════════════════════════════════════════════════════
# OTRAS FIGURAS
# ═══════════════════════════════════════════════════════════════
def fig_gauge(skin):
    c   = GR if skin<3 else AM if skin<8 else RD
    lbl = "BAJO" if skin<3 else "MODERADO" if skin<8 else "SEVERO" if skin<20 else "CRÍTICO"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=skin,
        title={"text":f"FACTOR SKIN (S)<br><span style='font-size:12px;color:{c}'>{lbl}</span>",
               "font":{"size":13,"color":TX}},
        number={"font":{"size":40,"color":c,"family":"Space Mono"}},
        gauge={"axis":{"range":[0,30],"tickfont":{"size":8,"color":"#6A8AAA"}},
               "bar":{"color":c,"thickness":0.28},"bgcolor":BG2,
               "steps":[{"range":[0,3],"color":"rgba(75,174,110,.1)"},
                        {"range":[3,8],"color":"rgba(232,160,48,.1)"},
                        {"range":[8,20],"color":"rgba(224,90,90,.1)"},
                        {"range":[20,30],"color":"rgba(200,0,0,.15)"}]}))
    fig.update_layout(paper_bgcolor=BG,font=dict(family="Space Mono",color=TX),
                      margin=dict(l=20,r=20,t=60,b=20),height=260)
    return fig


def fig_rheo(en, eh):
    g  = np.logspace(-1,3,250)
    vn = [en.visc(x) for x in g]
    vh = [eh.visc(x) for x in g]
    tn = [en.K*(x**en.n) for x in g]
    fig = make_subplots(rows=1,cols=2,
        subplot_titles=["Viscosidad Aparente η vs γ","Esfuerzo Cortante τ = K·γⁿ"])
    fig.add_trace(go.Scatter(x=g,y=vn,name=f"Na-CMC FlowBio (n={en.n:.3f})",
        line=dict(color=GR,width=3)), row=1,col=1)
    fig.add_trace(go.Scatter(x=g,y=vh,name=f"HPAM baseline (n={eh.n:.3f})",
        line=dict(color=RD,width=2,dash="dash")), row=1,col=1)
    fig.add_vrect(x0=10,x1=100,fillcolor="rgba(75,174,110,.07)",
        line_color="rgba(75,174,110,.3)", row=1,col=1)
    fig.add_annotation(x=1.5,y=0.8,xref="x",yref="paper",
        text="Zona óptima EOR",font=dict(size=9,color=GR),
        showarrow=False, row=1,col=1)
    fig.add_trace(go.Scatter(x=g,y=tn,name="τ Na-CMC",
        line=dict(color=BL,width=2.5)), row=1,col=2)
    fig.update_layout(**LAY, height=320)
    fig.update_xaxes(type="log",title_text="Tasa de Corte γ (s⁻¹)",gridcolor=BRD)
    fig.update_yaxes(type="log",title_text="η (mPa·s)",gridcolor=BRD,row=1,col=1)
    fig.update_yaxes(title_text="τ (Pa)",gridcolor=BRD,row=1,col=2)
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
        line=dict(color="rgba(0,0,0,0)"), name="Barriles extra",
        hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=t,y=Qb,name="Baseline sin tratamiento",
        line=dict(color=RD,width=2,dash="dash")))
    fig.add_trace(go.Scatter(x=t,y=Qn,name="Con Na-CMC FlowBio",
        line=dict(color=GR,width=3)))
    fig.add_vline(x=0,line_color=BL,line_dash="dot",line_width=1,
        annotation_text="Inicio inyección",annotation_font_color=BL)
    fig.update_layout(**LAY, height=320,
        xaxis_title="Días de Producción",
        yaxis_title="Producción (bbl/día)",
        hovermode="x unified")
    return fig


def fig_dashboard_skin(df):
    """Histograma Skin + FPI side by side."""
    col_skin = detectar(df,["skin"])
    col_fpi  = detectar(df,["fpi"])
    col_mej  = detectar(df,["mejora"])
    col_perm = detectar(df,["perm"])
    col_eff_b= detectar(df,["eff_base"])
    col_eff_n= detectar(df,["eff_nacmc","eff_n"])

    fig = make_subplots(rows=1,cols=3,
        subplot_titles=["Distribución Factor Skin","Riesgo Taponamiento FPI","Eficiencia Barrido EOR"])

    # Skin
    skins = pd.to_numeric(df[col_skin],errors="coerce").fillna(5).clip(0,30) if col_skin else pd.Series([5.0]*len(df))
    fig.add_trace(go.Histogram(x=skins,nbinsx=20,marker_color=RD,opacity=0.85,name="Skin"),row=1,col=1)
    fig.add_vline(x=skins.mean(),line_dash="dash",line_color=AM,
        annotation_text=f"μ={skins.mean():.1f}",annotation_font_color=AM,row=1,col=1)

    # FPI
    fpis = pd.to_numeric(df[col_fpi],errors="coerce").fillna(0.2) if col_fpi else pd.Series([0.2]*len(df))
    fig.add_trace(go.Histogram(x=fpis,nbinsx=15,marker_color=AM,opacity=0.85,name="FPI"),row=1,col=2)

    # Eficiencia
    perms = pd.to_numeric(df[col_perm],errors="coerce").fillna(250).clip(0,2000) if col_perm else pd.Series([250.0]*len(df))
    eff_b = pd.to_numeric(df[col_eff_b],errors="coerce").fillna(55) if col_eff_b else pd.Series([55.0]*len(df))
    eff_n = pd.to_numeric(df[col_eff_n],errors="coerce").fillna(65) if col_eff_n else pd.Series([65.0]*len(df))
    fig.add_trace(go.Scatter(x=perms,y=eff_b,mode="markers",
        marker=dict(color=RD,size=5,opacity=0.5),name="Sin polímero"),row=1,col=3)
    fig.add_trace(go.Scatter(x=perms,y=eff_n,mode="markers",
        marker=dict(color=GR,size=5,opacity=0.6),name="Na-CMC FlowBio"),row=1,col=3)

    fig.update_layout(**LAY,height=300,showlegend=False)
    fig.update_xaxes(gridcolor=BRD,linecolor=BRD)
    fig.update_yaxes(gridcolor=BRD,linecolor=BRD)
    for ann in fig.layout.annotations: ann.font.color=TX; ann.font.size=10
    return fig


def fig_top_pozos(df):
    """Bar chart horizontal Top 15 pozos."""
    col_mej  = detectar(df,["mejora","improvement","mejora_pct"])
    col_aho  = detectar(df,["ahorro","saving","annual"])
    col_name = detectar(df,["wellname","well_name","name","nombre","wellid"])
    col_rec  = detectar(df,["recomendacion","recommendation"])

    names = df[col_name].astype(str).str[:16].values if col_name else [f"Pozo-{i}" for i in range(len(df))]
    mejs  = pd.to_numeric(df[col_mej],errors="coerce").fillna(0).values if col_mej else np.ones(len(df))*10
    ahos  = pd.to_numeric(df[col_aho],errors="coerce").fillna(0).values if col_aho else np.zeros(len(df))
    recs  = df[col_rec].astype(str).values if col_rec else ["EVALUAR"]*len(df)

    df2 = pd.DataFrame({"name":names,"mej":mejs,"aho":ahos,"rec":recs})
    top = df2.nlargest(15,"mej").sort_values("mej")
    colors = [GR if r=="INYECTAR Na-CMC" else AM if r=="EVALUAR" else BL for r in top["rec"]]

    fig = make_subplots(rows=1,cols=2,
        subplot_titles=["Top 15 — Mejora EOR (%)","Top 15 — Ahorro OPEX Anual"])
    fig.add_trace(go.Bar(x=top["mej"],y=top["name"],orientation="h",
        marker_color=colors,opacity=0.88,name="Mejora%",
        hovertemplate="%{y}<br>Mejora: %{x:.1f}%<extra></extra>"),row=1,col=1)
    top2 = df2.nlargest(15,"aho").sort_values("aho")
    colors2 = [GR if r=="INYECTAR Na-CMC" else AM if r=="EVALUAR" else BL for r in top2["rec"]]
    fig.add_trace(go.Bar(x=top2["aho"]/1000,y=top2["name"],orientation="h",
        marker_color=colors2,opacity=0.88,name="AhorroK$",
        hovertemplate="%{y}<br>Ahorro: $%{x:.0f}K USD/año<extra></extra>"),row=1,col=2)
    fig.update_layout(**LAY,height=380,showlegend=False)
    fig.update_xaxes(gridcolor=BRD,linecolor=BRD)
    fig.update_yaxes(gridcolor=BRD,linecolor=BRD,tickfont=dict(size=9))
    for ann in fig.layout.annotations: ann.font.color=TX; ann.font.size=10
    return fig


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
for k,v in [("simulated",False),("demo_well",None),("sel_well_idx",0)]:
    if k not in st.session_state: st.session_state[k]=v

DEMOS = {
    "29/10-1 · Harbour Energy · Southern N. Sea": dict(T=72,S=33000,visc=88,perm=450,bopd=500,opex=15.5,conc=0.9,dias=120),
    "211/18-1 · BP · West of Shetland":           dict(T=125,S=55000,visc=6, perm=75, bopd=280,opex=26.5,conc=0.6,dias=90),
    "49/9-1 · Perenco · Southern N. Sea":         dict(T=58, S=22000,visc=200,perm=720,bopd=800,opex=13.0,conc=1.1,dias=180),
    "16/17-14 · Equinor · Central N. Sea":        dict(T=105,S=44000,visc=22, perm=210,bopd=550,opex=18.2,conc=0.75,dias=120),
}
_d = st.session_state.demo_well or {}
_, s3_ok = get_s3()


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:14px 0 8px'>
      <div style='font-size:22px;font-weight:900;color:#fff;font-family:Outfit,sans-serif'>🛢️ FlowBio</div>
      <div style='font-size:9px;letter-spacing:2px;color:{GR};margin-top:2px;font-family:Space Mono,monospace'>
        INTELLIGENCE · PIML v0.3
      </div>
    </div>
    <hr style='border-color:{BRD};margin:8px 0 12px'>
    <div style='text-align:center;margin-bottom:10px'>
      <span class='{'badge-g' if s3_ok else 'badge-b'}'>
        {'🟢 S3 Conectado' if s3_ok else '🔵 Modo Demo'}
      </span>
    </div>
    """, unsafe_allow_html=True)

    if not s3_ok:
        st.markdown(f"""
        <div class='box-a' style='font-size:10px;margin-bottom:10px'>
          <b>Conectar S3:</b><br>
          Settings → Secrets:<br>
          <code>[aws]<br>
          AWS_ACCESS_KEY_ID = "..."<br>
          AWS_SECRET_ACCESS_KEY = "..."<br>
          AWS_DEFAULT_REGION = "us-east-2"</code>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"<div class='ssc'>🚀 DEMO — NSTA OPEN DATA</div>", unsafe_allow_html=True)
    demo_sel = st.selectbox("Pozo real", ["— Manual —"]+list(DEMOS.keys()),
                            label_visibility="collapsed")
    if demo_sel != "— Manual —":
        if st.button("▶ Cargar Demo y Simular", use_container_width=True, type="primary"):
            st.session_state.demo_well = DEMOS[demo_sel]
            st.session_state.simulated = True
            st.rerun()

    st.markdown(f"<hr style='border-color:{BRD};margin:10px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div class='ssc'>🛢 YACIMIENTO</div>", unsafe_allow_html=True)
    T    = st.slider("Temperatura (°C)", 40,130, int(_d.get("T",82)))
    S    = st.slider("Salinidad (ppm)", 5000,100000, int(_d.get("S",38000)), 1000, format="%d")
    visc = st.number_input("Viscosidad crudo (cP)", 1,2000, int(_d.get("visc",85)))
    perm = st.number_input("Permeabilidad (mD)",   1,3000, int(_d.get("perm",250)))
    bopd = st.number_input("Producción (bbl/día)", 10,5000, int(_d.get("bopd",500)))

    st.markdown(f"<div class='ssc'>⚗ NA-CMC FLOWBIO</div>", unsafe_allow_html=True)
    conc = st.slider("Concentración (%wt)", 0.05,2.0, float(_d.get("conc",0.8)), 0.05)
    dias = st.slider("Horizonte (días)", 30,365, int(_d.get("dias",120)), 10)

    st.markdown(f"<div class='ssc'>💰 ECONOMÍA</div>", unsafe_allow_html=True)
    opex      = st.number_input("OPEX (USD/bbl)", 2.0,60.0, float(_d.get("opex",18.5)), 0.5)
    oil_price = st.number_input("Precio petróleo (USD/bbl)", 20.0,150.0, 74.5, 0.5)

    st.markdown(f"<hr style='border-color:{BRD};margin:12px 0 8px'>", unsafe_allow_html=True)
    if st.button("▶  EJECUTAR SIMULACIÓN PIML", use_container_width=True, type="primary"):
        st.session_state.simulated = True
        st.session_state.demo_well = None
        st.rerun()
    if st.session_state.simulated:
        if st.button("↺  Limpiar", use_container_width=True):
            st.session_state.simulated = False
            st.session_state.demo_well = None
            st.rerun()

    st.markdown(f"""
    <div style='font-size:9px;color:#2A4A6A;text-align:center;margin-top:10px;line-height:1.7;font-family:Space Mono,monospace'>
      TRL 3 · Calibración pendiente: IMP+CENAM<br>
      Amplifika UAG · WC 2026
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CALCULAR
# ═══════════════════════════════════════════════════════════════
eng_n = PIML(T=T,S=S,C=conc,fluid="Na-CMC")
eng_h = PIML(T=T,S=S,C=conc,fluid="HPAM")
skin_v  = eng_n.skin(perm,perm*0.25)
skin_n2 = eng_n.skin(perm,perm*0.85)
M_v     = eng_n.mob(visc)
eff_b   = eng_n.sweep(2.5)
eff_n   = eng_n.sweep(M_v)
extra   = max(0, bopd*(eff_n-eff_b)/max(1,eff_b))
neto_m, ahorro_yr = eng_n.roi(extra,opex,oil_price)
fpi_v   = eng_n.fpi(perm)
roi_pct = round((neto_m/max(1,(150*0.159*(conc/100)*1000)*2.8*30))*100,1)


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
col_logo, col_title, col_badges = st.columns([0.08, 0.72, 0.20])
with col_logo:
    st.markdown("<div style='font-size:48px;margin-top:6px'>🛢️</div>", unsafe_allow_html=True)
with col_title:
    st.markdown(f"""
    <div style='padding:8px 0'>
      <div style='font-size:20px;font-weight:800;color:#fff;font-family:Outfit,sans-serif'>
        FlowBio Intelligence
      </div>
      <div style='font-size:11px;color:{GR};letter-spacing:.8px;font-family:Space Mono,monospace;margin-top:2px'>
        SUBSURFACE DIAGNOSTIC CONSOLE · PIML · EOR · NA-CMC · S3 DATA LAKE
      </div>
    </div>""", unsafe_allow_html=True)
with col_badges:
    st.markdown(f"""
    <div style='text-align:right;padding:10px 0;display:flex;flex-direction:column;gap:5px;align-items:flex-end'>
      <span class='badge-g'>PIML v0.3 · TRL 3</span><br>
      <span class='{'badge-g' if s3_ok else 'badge-b'}'>{'🟢 S3 Live' if s3_ok else '🔵 Demo'}</span>
    </div>""", unsafe_allow_html=True)

st.markdown(f"<hr style='border-color:{BRD};margin:4px 0 16px'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PANTALLA INICIAL
# ═══════════════════════════════════════════════════════════════
if not st.session_state.simulated:

    # KPIs de contexto
    st.markdown(f"<div class='sec-hdr'>📊 ESTADO DEL MERCADO EOR</div>", unsafe_allow_html=True)
    mc1,mc2,mc3,mc4,mc5 = st.columns(5)
    for col,(val,cls,lbl,sub) in zip([mc1,mc2,mc3,mc4,mc5],[
        ("$44.66B","vb","MERCADO EOR 2032","5.2% CAGR · USD"),
        ("20-40%","vg","RECUPERACIÓN ADICIONAL","pozos maduros con EOR"),
        ("90%","vg","REDUCCIÓN SKIN","Na-CMC vs HPAM"),
        ("+18%","vg","EF. BARRIDO","mejora promedio"),
        ("$5 USD","va","SUCCESS FEE","por barril extra producido"),
    ]):
        with col:
            st.markdown(f"""
            <div class='kcard'>
              <div class='klbl'>{lbl}</div>
              <div class='kval {cls}'>{val}</div>
              <div class='ksub'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mapa principal
    st.markdown(f"<div class='sec-hdr'>🗺️ MAPA DE POZOS — NSTA UK NORTH SEA</div>", unsafe_allow_html=True)

    with st.spinner("Cargando datos de pozos desde S3..."):
        df_wells, fuente_w, es_s3_w = cargar_pozos_s3()

    if es_s3_w:
        st.markdown(f"<div class='box-g'>✅ {fuente_w} · <b>{len(df_wells):,}</b> registros</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='box-a'>🔵 {fuente_w} · {len(df_wells)} pozos de referencia UKCS</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_mapa(df_wells), use_container_width=True)

    # Dashboard de datos
    st.markdown(f"<div class='sec-hdr'>📊 ANÁLISIS PIML — TODOS LOS POZOS</div>", unsafe_allow_html=True)
    st.plotly_chart(fig_dashboard_skin(df_wells), use_container_width=True)
    st.plotly_chart(fig_top_pozos(df_wells), use_container_width=True)

    # Tabla de pozos
    st.markdown(f"<div class='sec-hdr'>📋 TABLA DE POZOS — RANKING POR POTENCIAL EOR</div>", unsafe_allow_html=True)
    show_cols = [c for c in ["WellName","Operator","Basin","Temperature_C","Permeability_mD",
                              "skin","mejora_pct","ahorro_anual","recomendacion","prioridad"]
                 if c in df_wells.columns]
    if not show_cols:
        show_cols = df_wells.columns[:8].tolist()
    sort_c = next((c for c in ["mejora_pct","skin","ahorro_anual"] if c in df_wells.columns), df_wells.columns[0])
    st.dataframe(
        df_wells.sort_values(sort_c, ascending=False)[show_cols]
                .reset_index(drop=True).head(30),
        use_container_width=True, hide_index=True
    )

    # Cómo empezar
    st.markdown(f"<div class='sec-hdr'>🚀 EJECUTAR SIMULACIÓN INDIVIDUAL</div>", unsafe_allow_html=True)
    ia1,ia2,ia3,ia4 = st.columns(4)
    for col,(ico,tit,sub) in zip([ia1,ia2,ia3,ia4],[
        ("⚗","Na-CMC FlowBio","Biopolímero desde<br>jacinto de agua · Orizaba"),
        ("🧮","Power Law PIML","τ = K·γⁿ<br>Ostwald-de Waele"),
        ("🎯","Factor Skin","S = (K/Kd-1)·ln(rd/rw)<br>van Everdingen-Hurst"),
        ("💰","Success Fee","$5 USD por barril<br>extra producido"),
    ]):
        with col:
            st.markdown(f"""
            <div class='kcard' style='padding:20px 14px'>
              <div style='font-size:26px;margin-bottom:8px'>{ico}</div>
              <div style='font-size:12px;font-weight:700;color:{TX};margin-bottom:5px;font-family:Outfit,sans-serif'>{tit}</div>
              <div style='font-size:10px;color:#6A8AAA;line-height:1.6'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.stop()


# ═══════════════════════════════════════════════════════════════
# RESULTADOS — tras simular
# ═══════════════════════════════════════════════════════════════
sk_c = "vr" if skin_v>8 else "va" if skin_v>3 else "vg"
mb_c = "vg" if M_v<1 else "va" if M_v<2 else "vr"

# KPIs principales
st.markdown(f"<div class='sec-hdr'>📊 RESULTADOS PIML — DIAGNÓSTICO DEL POZO</div>",
            unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
for col,(val,cls,lbl,sub) in zip([k1,k2,k3,k4,k5],[
    (f"{skin_v:.2f}", sk_c, "FACTOR SKIN (S)", "S=(K/Kd-1)·ln(rd/rw)"),
    (f"{eng_n.n:.3f}", "vb", "ÍNDICE FLUJO (n)", "Power Law Na-CMC"),
    (f"{eff_n:.1f}%", "vg", "EF. BARRIDO EOR", f"vs {eff_b:.1f}% baseline"),
    (f"{M_v:.3f}", mb_c, "RATIO MOVILIDAD M", "Favorable" if M_v<1 else "Desfavorable"),
    (f"${ahorro_yr:,.0f}", "vg", "AHORRO ANUAL USD", f"+{extra:.0f} bbl/día extra"),
]):
    with col:
        st.markdown(f"""
        <div class='kcard'>
          <div class='klbl'>{lbl}</div>
          <div class='kval {cls}'>{val}</div>
          <div class='ksub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "🗺️ Mapa de Pozos",
    "🎯 Diagnóstico & Skin",
    "⚗ Reología PIML",
    "📈 Producción & ROI",
    "📊 Dashboard S3",
])

# ── TAB 1: MAPA ──────────────────────────────────────────────
with tab1:
    st.markdown(f"<div class='sec-hdr'>🗺️ MAPA INTERACTIVO — POZOS UKCS DEL S3</div>",
                unsafe_allow_html=True)
    with st.spinner("Cargando mapa..."):
        df_wells, fuente_w, es_s3_w = cargar_pozos_s3()

    fuente_lbl = f"✅ {fuente_w}" if es_s3_w else f"🔵 {fuente_w}"
    cls_box = "box-g" if es_s3_w else "box-a"
    st.markdown(f"<div class='{cls_box}'>{fuente_lbl} · <b>{len(df_wells):,}</b> pozos</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Pozo seleccionado
    col_name = detectar(df_wells,["wellname","well_name","name","nombre","uwi","wellid"])
    well_names = df_wells[col_name].astype(str).tolist() if col_name else [f"Pozo-{i}" for i in range(len(df_wells))]
    sel = st.selectbox("Destacar pozo en el mapa", ["— Todos —"] + well_names,
                       label_visibility="visible")
    sel_idx = well_names.index(sel) if sel != "— Todos —" and sel in well_names else None

    st.plotly_chart(fig_mapa(df_wells, sel_idx), use_container_width=True)

    # Mini tabla del pozo seleccionado
    if sel_idx is not None:
        row = df_wells.iloc[sel_idx]
        st.markdown(f"<div class='sec-hdr'>📋 DETALLE DEL POZO SELECCIONADO: {sel}</div>",
                    unsafe_allow_html=True)
        dc1,dc2,dc3 = st.columns(3)
        for col, items in zip([dc1,dc2,dc3],[
            {k:v for i,(k,v) in enumerate(row.items()) if i<4},
            {k:v for i,(k,v) in enumerate(row.items()) if 4<=i<8},
            {k:v for i,(k,v) in enumerate(row.items()) if 8<=i<12},
        ]):
            with col:
                for k,v in items.items():
                    st.markdown(f"""
                    <div style='display:flex;justify-content:space-between;
                                border-bottom:1px solid {BRD};padding:5px 0;
                                font-size:11px'>
                      <span style='color:#6A8AAA'>{k}</span>
                      <span style='color:{TX};font-family:Space Mono,monospace'>{v}</span>
                    </div>""", unsafe_allow_html=True)

    st.plotly_chart(fig_top_pozos(df_wells), use_container_width=True)

# ── TAB 2: DIAGNÓSTICO ───────────────────────────────────────
with tab2:
    cg, ci = st.columns([1, 1.4])
    with cg:
        st.markdown(f"<div class='sec-hdr'>🎯 VELOCÍMETRO — FACTOR SKIN</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_gauge(skin_v), use_container_width=True)

    with ci:
        st.markdown(f"<div class='sec-hdr'>📋 DIAGNÓSTICO TÉCNICO</div>", unsafe_allow_html=True)
        red_pct = ((skin_v-skin_n2)/max(0.01,skin_v))*100
        th_ok   = T < 90
        st.markdown(f"""
        <div class='box-b'>
          <b style='color:{GR}'>⚡ Ostwald-de Waele (Power Law)</b><br>
          Na-CMC: n=<b>{eng_n.n:.4f}</b> | K=<b>{eng_n.K:.1f}</b> mPa·sⁿ<br>
          HPAM:&nbsp;&nbsp; n=<b>{eng_h.n:.4f}</b> | K=<b>{eng_h.K:.1f}</b> mPa·sⁿ<br><br>
          n &lt; 1 → pseudoplástico ✓ (shear-thinning) → ideal EOR
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='box-g'>
          <b>📉 Reducción Skin con Na-CMC FlowBio</b><br>
          Skin actual (HPAM): <b>{skin_v:.2f}</b>
          → Con Na-CMC: <b>{skin_n2:.2f}</b>
          → Reducción: <b>{red_pct:.0f}%</b><br>
          Temperatura: <b>{T}°C</b> {'✅ Estable (< 90°C)' if th_ok else '⚠️ Sobre límite térmico'}<br>
          FPI (taponamiento): <b>{fpi_v:.3f}</b>
          — {'✅ BAJO' if fpi_v<0.25 else '⚠️ MODERADO' if fpi_v<0.5 else '❌ ALTO'}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<div class='sec-hdr'>⚙ OPERATIONAL READINESS</div>", unsafe_allow_html=True)
        df_or = pd.DataFrame({
            "Indicador"    :["Estab. térmica","Compat. salina","Skin Damage","Ratio Movilidad","FPI Taponamiento","Biodegradabilidad","HSE Factor"],
            "Estado actual":[
                "✅ OK" if th_ok else "⚠️ Sobre límite",
                "✅ OK" if S<70000 else "⚠️ Alta",
                "❌ Alto" if skin_v>8 else "⚠️ Mod." if skin_v>3 else "✅ Bajo",
                "✅ Favorable" if M_v<1 else "⚠️ Desfavorable",
                "✅ Bajo" if fpi_v<0.25 else "⚠️ Moderado" if fpi_v<0.5 else "❌ Alto",
                "❌ No biodegradable","❌ Tóxico (HPAM)"],
            "Con Na-CMC FlowBio":[
                "✅ Límite 90°C","✅ Hasta 80K ppm",
                f"✅ Reducción {red_pct:.0f}%","✅ Mejor M",
                "✅ FPI muy bajo","✅ 100% biodegradable","✅ Cero toxicidad"],
        })
        st.dataframe(df_or, use_container_width=True, hide_index=True)

# ── TAB 3: REOLOGÍA ──────────────────────────────────────────
with tab3:
    st.markdown(f"<div class='sec-hdr'>⚗ CURVAS REOLÓGICAS — POWER LAW</div>", unsafe_allow_html=True)
    st.plotly_chart(fig_rheo(eng_n, eng_h), use_container_width=True)
    fc1,fc2,fc3 = st.columns(3)
    for col,txt in zip([fc1,fc2,fc3],[
        f"τ = K·γⁿ\nLey de Potencia",
        f"η = K·γ^(n-1)\nViscosidad Aparente",
        f"n = {eng_n.n:.4f}  K = {eng_n.K:.1f}\nParámetros Na-CMC"]):
        with col:
            st.markdown(f"""
            <div style='background:{BG3};border:1px solid {BRD};border-radius:8px;
                        padding:14px;font-family:Space Mono,monospace;font-size:13px;
                        color:{PU};text-align:center;white-space:pre'>{txt}</div>""",
                        unsafe_allow_html=True)

# ── TAB 4: PRODUCCIÓN & ROI ──────────────────────────────────
with tab4:
    st.markdown(f"""
    <div class='hero-card'>
      <div class='hero-lbl'>SUCCESS FEE MENSUAL NETO — MODELO ADÁN RAMÍREZ</div>
      <div class='hero-val'>${neto_m:,.0f} USD</div>
      <div class='hero-sub'>
        {extra:.1f} bbl/día extra × $5 USD × 30 días — costo Na-CMC
      </div>
    </div>""", unsafe_allow_html=True)

    poly_d = (150*0.159*(conc/100)*1000)*2.8*30
    fee_d  = extra*5*30
    e1,e2,e3,e4 = st.columns(4)
    for col,(val,cls,lbl,sub) in zip([e1,e2,e3,e4],[
        (f"+{extra:.1f}","vg","BARRILES EXTRA/DÍA",f"sobre {bopd} bbl/d"),
        (f"${fee_d:,.0f}","vb","SUCCESS FEE/MES","$5/bbl extra"),
        (f"${poly_d:,.0f}","va","COSTO POLÍMERO/MES","Na-CMC · Orizaba"),
        (f"{roi_pct:.0f}%","vg","ROI INMEDIATO",f"Ahorro: ${ahorro_yr:,.0f}/año"),
    ]):
        with col:
            st.markdown(f"""
            <div class='kcard'>
              <div class='klbl'>{lbl}</div>
              <div class='kval {cls}'>{val}</div>
              <div class='ksub'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_prod(bopd,extra,dias), use_container_width=True)

# ── TAB 5: DASHBOARD S3 ──────────────────────────────────────
with tab5:
    st.markdown(f"<div class='sec-hdr'>📊 DASHBOARD — DATOS REALES DEL S3</div>",
                unsafe_allow_html=True)
    with st.spinner("Cargando datos desde S3..."):
        df_s3, fuente, es_s3 = cargar_pozos_s3()

    cls_s3 = "box-g" if es_s3 else "box-a"
    st.markdown(f"<div class='{cls_s3}'>{'✅' if es_s3 else '🔵'} {fuente} · <b>{len(df_s3):,}</b> pozos</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_sk = detectar(df_s3,["skin"])
    col_mj = detectar(df_s3,["mejora","improvement"])
    col_ah = detectar(df_s3,["ahorro","saving","annual"])

    skin_m = pd.to_numeric(df_s3[col_sk],errors="coerce").mean() if col_sk else 5.0
    mej_m  = pd.to_numeric(df_s3[col_mj],errors="coerce").mean() if col_mj else 10.0
    aho_m  = pd.to_numeric(df_s3[col_ah],errors="coerce").mean() if col_ah else 50000.0

    d1,d2,d3,d4 = st.columns(4)
    for col,(val,cls,lbl) in zip([d1,d2,d3,d4],[
        (f"{len(df_s3):,}","vb","POZOS ANALIZADOS"),
        (f"{skin_m:.2f}","vr" if skin_m>8 else "va","SKIN PROMEDIO"),
        (f"{mej_m:.1f}%","vg","MEJORA EOR PROM."),
        (f"${aho_m:,.0f}","vg","AHORRO ANUAL PROM."),
    ]):
        with col:
            st.markdown(f"""
            <div class='kcard'>
              <div class='klbl'>{lbl}</div>
              <div class='kval {cls}'>{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig_mapa(df_s3), use_container_width=True)
    st.plotly_chart(fig_dashboard_skin(df_s3), use_container_width=True)
    st.plotly_chart(fig_top_pozos(df_s3), use_container_width=True)

    # Tabla completa
    st.markdown(f"<div class='sec-hdr'>📋 TODOS LOS POZOS — DATOS S3</div>", unsafe_allow_html=True)
    sort_c2 = col_mj if col_mj else df_s3.columns[0]
    st.dataframe(
        df_s3.sort_values(sort_c2, ascending=False).head(50).reset_index(drop=True),
        use_container_width=True, hide_index=True
    )

    # Data Lake
    st.markdown(f"<div class='sec-hdr'>📦 DATA LAKE — ARCHIVOS EN S3</div>", unsafe_allow_html=True)
    if s3_ok:
        files = listar_s3()
        if files:
            st.dataframe(pd.DataFrame(files), use_container_width=True, hide_index=True)
    else:
        st.markdown(f"""
        <div class='box-a'>
          Para ver tus archivos reales: Settings → Secrets → agrega [aws]
        </div>""", unsafe_allow_html=True)

# FOOTER
st.markdown(f"""
<hr style='border-color:{BRD};margin:30px 0 14px'>
<div style='text-align:center;font-size:9px;color:#2A4A6A;line-height:1.8;font-family:Space Mono,monospace'>
  <b style='color:{GR}'>FlowBio Intelligence</b> · Motor PIML v0.3 · TRL 3 ·
  Na-CMC desde <i>Eichhornia crassipes</i> · Orizaba, Veracruz, MX<br>
  Startup Building Beyond the World Cup 2026 · Amplifika UAG · IMP + CENAM pendiente
</div>
""", unsafe_allow_html=True)
