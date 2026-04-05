"""
FlowBio Intelligence — Subsurface Diagnostic Console v3
UX diseñado para: EOR Manager · Reservoir Engineer · ESG Manager
Mapa satelital interactivo · Buscador de pozos · S3 Data Lake
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math, io, warnings, json
from datetime import datetime
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="FlowBio Intelligence",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BUCKET = "flowbio-data-lake-v2-627807503177-us-east-2-an"
BG="#0D1B2A"; BG2="#0A1520"; BG3="#071018"; BRD="#1E3A60"
TX="#D0E4F8"; GR="#4BAE6E"; BL="#4A9FD4"; RD="#E05A5A"
AM="#E8A030"; PU="#9B7FD4"; GR2="#3A7D44"; TEAL="#00C9B1"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');
*{{box-sizing:border-box}}
html,body,.stApp{{background:{BG};color:{TX};font-family:'Outfit',sans-serif}}
section[data-testid="stSidebar"]{{background:{BG2};border-right:1px solid {BRD}}}
.stTabs [aria-selected="true"]{{color:{GR}!important;border-bottom:2px solid {GR}!important}}
.stTabs [data-baseweb="tab"]{{color:#6A8AAA;font-family:'Outfit',sans-serif;font-size:13px}}
div[data-testid="metric-container"]{{background:{BG2};border:1px solid {BRD};border-radius:12px;padding:14px}}

/* ══ KPIS ══ */
.kcard{{background:{BG2};border:1px solid {BRD};border-radius:14px;
       padding:20px 14px;text-align:center;position:relative;overflow:hidden}}
.kcard-eor::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,{BL},{GR})}}
.kcard-res::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,{PU},{BL})}}
.kcard-esg::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,{GR},{TEAL})}}
.klbl{{font-size:9px;letter-spacing:2px;color:#6A8AAA;font-weight:700;text-transform:uppercase;margin-bottom:6px}}
.kval{{font-size:30px;font-weight:900;font-family:'Space Mono',monospace;line-height:1.1}}
.ksub{{font-size:10px;color:#4A7AAA;margin-top:5px}}
.vg{{color:{GR}}}.vb{{color:{BL}}}.vr{{color:{RD}}}.va{{color:{AM}}}.vp{{color:{PU}}}.vt{{color:{TEAL}}}

/* ══ SECTION HEADERS ══ */
.sh{{font-size:10px;letter-spacing:2.5px;color:#6A8AAA;font-weight:700;
     text-transform:uppercase;border-bottom:1px solid {BRD};
     padding-bottom:8px;margin:24px 0 14px;display:flex;align-items:center;gap:8px}}

/* ══ ALERT CARDS (estilo boceto Figma) ══ */
.alert-card{{background:{BG2};border:1px solid {BRD};border-radius:12px;
             padding:14px 16px;margin-bottom:8px;position:relative;overflow:hidden;
             border-left:3px solid {AM}}}
.alert-card.ok{{border-left-color:{GR}}}
.alert-card.crit{{border-left-color:{RD}}}
.alert-title{{font-size:14px;font-weight:700;color:{TX};margin-bottom:4px}}
.alert-body{{font-size:11px;color:#6A8AAA;line-height:1.5}}
.alert-time{{font-size:9px;color:#3A5A7A;float:right;font-family:'Space Mono',monospace}}
.alert-well{{font-size:10px;color:{GR};margin-top:6px}}

/* ══ BADGE ══ */
.bg{{background:rgba(75,174,110,.15);border:1px solid {GR};border-radius:20px;padding:3px 12px;font-size:10px;color:{GR};font-weight:700;display:inline-block}}
.bb{{background:rgba(74,159,212,.15);border:1px solid {BL};border-radius:20px;padding:3px 12px;font-size:10px;color:{BL};font-weight:700;display:inline-block}}
.br{{background:rgba(224,90,90,.15);border:1px solid {RD};border-radius:20px;padding:3px 12px;font-size:10px;color:{RD};font-weight:700;display:inline-block}}
.ba{{background:rgba(232,160,48,.15);border:1px solid {AM};border-radius:20px;padding:3px 12px;font-size:10px;color:{AM};font-weight:700;display:inline-block}}

/* ══ BOXES ══ */
.box-b{{background:rgba(74,159,212,.08);border:1px solid rgba(74,159,212,.3);border-radius:10px;padding:14px;font-size:12px;color:#A0C4D8;line-height:1.7}}
.box-g{{background:rgba(75,174,110,.1);border:1px solid rgba(75,174,110,.4);border-radius:10px;padding:14px;font-size:12px;color:#7ABF8A;line-height:1.7}}
.box-a{{background:rgba(232,160,48,.08);border:1px solid rgba(232,160,48,.3);border-radius:10px;padding:12px;font-size:12px;color:#E8C080;line-height:1.7}}
.box-esg{{background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.3);border-radius:10px;padding:14px;font-size:12px;color:#7AE8DA;line-height:1.7}}

/* ══ HERO ══ */
.hero{{background:linear-gradient(135deg,rgba(75,174,110,.18),rgba(74,159,212,.1));
       border:1px solid {GR};border-radius:16px;padding:24px;text-align:center;margin-bottom:18px}}
.hero-val{{font-size:52px;font-weight:900;color:{GR};font-family:'Space Mono',monospace;letter-spacing:-2px}}
.hero-lbl{{font-size:9px;letter-spacing:2.5px;color:{GR};font-weight:700;margin-bottom:8px}}
.hero-sub{{font-size:12px;color:#7ABF8A;margin-top:6px}}

/* ══ FORMULA ══ */
.formula{{background:{BG3};border:1px solid {BRD};border-radius:8px;
          padding:14px;font-family:'Space Mono',monospace;font-size:13px;
          color:{PU};text-align:center;white-space:pre}}

/* ══ SIDEBAR ══ */
.ssc{{font-size:9px;letter-spacing:2px;color:{GR};font-weight:700;
      text-transform:uppercase;margin:14px 0 8px}}

/* ══ WELL SEARCH ITEM ══ */
.well-item{{background:{BG2};border:1px solid {BRD};border-radius:8px;
            padding:10px 14px;margin-bottom:5px;cursor:pointer}}
.well-item:hover,.well-item.sel{{border-color:{BL};background:rgba(74,159,212,.06)}}
.wid{{font-family:'Space Mono',monospace;font-size:13px;color:{BL};font-weight:700}}
.wmeta{{font-size:10px;color:#6A8AAA;margin-top:2px}}

/* ══ COORD LABEL ══ */
.coord-label{{background:rgba(10,21,32,.85);border:1px solid {BL};border-radius:6px;
              padding:5px 12px;font-family:'Space Mono',monospace;font-size:11px;color:{BL}}}

/* ══ PROFILE CARDS (EOR/RES/ESG) ══ */
.profile-card{{background:{BG2};border:1px solid {BRD};border-radius:14px;
               padding:20px;height:100%}}
.profile-icon{{font-size:32px;margin-bottom:10px}}
.profile-role{{font-size:11px;letter-spacing:1.5px;color:#6A8AAA;font-weight:600;
               text-transform:uppercase;margin-bottom:6px}}
.profile-name{{font-size:16px;font-weight:800;color:{TX};margin-bottom:8px}}
.profile-pain{{font-size:11px;color:#6A8AAA;line-height:1.6;margin-bottom:10px}}
.profile-win{{font-size:11px;color:{GR};line-height:1.6}}
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

# ═══════════════════════════════════════════
# MOTOR PIML
# ═══════════════════════════════════════════
class PIML:
    def __init__(self,T=85,S=45000,C=0.8,fluid="Na-CMC"):
        self.T=T;self.S=S;self.C=C;self.fluid=fluid
        self.n=float(np.clip(0.65-(T/1200)-(S/600000)-(C*0.08) if fluid=="Na-CMC"
                             else 0.78-(T/900)-(S/500000)-(C*0.05),0.25,0.90))
        self.K=float(max(30,160-(T*0.75)+(S*0.001)+(C*12) if fluid=="Na-CMC"
                         else 200-(T*0.90)+(S*0.0008)+(C*10)))
    def visc(self,g=10): return float(np.clip(self.K*(g**(self.n-1)),1,5000))
    def skin(self,K,Kd,rd=8,rw=0.35): return float((K/Kd-1)*math.log(rd/rw)) if Kd>0 else 0.0
    def mob(self,vo=85,g=10): return float(np.clip((0.4/self.visc(g))/(0.8/vo),0.05,8))
    def sweep(self,M):
        if M<=0.5: return 90.0
        elif M<=1.0: return 90-(M-0.5)*20
        elif M<=2.0: return 80-(M-1.0)*25
        return max(30,55-(M-2)*10)
    def fpi(self,perm):
        pf=2.5 if perm<50 else 1.5 if perm<150 else 1.0 if perm<400 else 0.7
        return float(np.clip(0.12*pf*(1+max(0,(self.S-60000)/20000)),0,1))
    def roi(self,extra,opex=18.5,oil=74.5):
        fee=extra*5.0*30; cost=(150*0.159*(self.C/100)*1000)*2.8*30
        return round(fee-cost,2), round(extra*(oil-opex)*0.19*365,0)

# ═══════════════════════════════════════════
# S3
# ═══════════════════════════════════════════
@st.cache_resource(ttl=300)
def get_s3():
    try:
        import boto3
        c=boto3.client("s3",
            aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["aws"].get("AWS_DEFAULT_REGION","us-east-2"))
        c.list_buckets(); return c,True
    except: return None,False

def detectar(df,opts):
    for col in df.columns:
        if any(k in col.lower() for k in opts): return col
    return None

@st.cache_data(ttl=300)
def cargar_pozos():
    s3,ok=get_s3()
    WELL_FILES=[
        "UKCS_well_availability_collated_tops_(WGS84)_2454963035769896595 (1).csv",
        "resultados/flowbio_piml_analisis.csv","resultados_piml.csv",
    ]
    if ok:
        try:
            r=s3.list_objects_v2(Bucket=BUCKET)
            keys=[o["Key"] for o in r.get("Contents",[])]
            for fn in WELL_FILES:
                if fn in keys:
                    obj=s3.get_object(Bucket=BUCKET,Key=fn)
                    df=pd.read_csv(io.BytesIO(obj["Body"].read()),encoding="latin-1",low_memory=False)
                    df.columns=df.columns.str.replace("ï»¿","").str.strip()
                    return enriquecer(df),fn,True
            csvs=[k for k in keys if k.endswith(".csv")]
            if csvs:
                obj=s3.get_object(Bucket=BUCKET,Key=csvs[0])
                df=pd.read_csv(io.BytesIO(obj["Body"].read()),encoding="latin-1",low_memory=False)
                df.columns=df.columns.str.replace("ï»¿","").str.strip()
                return enriquecer(df),csvs[0],True
        except Exception as e:
            st.warning(f"S3: {e}")
    return demo_pozos(),"Demo NSTA North Sea",False

def enriquecer(df):
    """Calcula PIML sobre filas del CSV si no tiene las columnas ya."""
    col_lat=detectar(df,["lat","latitude"]); col_lon=detectar(df,["lon","long","longitude"])
    col_T  =detectar(df,["temp","temperatura"]); col_P=detectar(df,["perm","permeability"])
    if col_lat and "skin" not in df.columns:
        rows=[]
        for _,row in df.iterrows():
            T=float(row[col_T]) if col_T and pd.notna(row.get(col_T)) else 85
            p=float(row[col_P]) if col_P and pd.notna(row.get(col_P)) else 250
            T=min(max(T,10),200); p=max(p,1)
            eng=PIML(T=T)
            skin=eng.skin(p,p*0.25); M=eng.mob(85)
            eff_b=eng.sweep(2.5); eff_n=eng.sweep(M)
            mej=max(0,(eff_n-eff_b)/max(1,eff_b)*100)
            fpi=eng.fpi(p); _,aho=eng.roi(500*mej/100)
            rows.append({
                "skin":round(skin,3),"mejora_pct":round(mej,2),
                "fpi":round(fpi,4),"ahorro_anual":aho,
                "eff_base_pct":round(eff_b,1),"eff_nacmc_pct":round(eff_n,1),
                "prioridad":"🔴 CRÍTICO" if skin>15 else "🟠 ALTO" if skin>8 else "🟡 MODERADO" if skin>3 else "🟢 BAJO",
                "recomendacion":"INYECTAR Na-CMC" if fpi<0.4 and T<90 and mej>5 else "EVALUAR" if mej>2 else "MONITOREAR",
            })
        calc=pd.DataFrame(rows)
        for c in calc.columns:
            if c not in df.columns: df[c]=calc[c].values
    return df

def demo_pozos():
    np.random.seed(42)
    datos=[
        ("29/10-1","Harbour Energy","Southern N.Sea",55.82,2.11,72,450,500,15.5),
        ("211/18-1","BP","West of Shetland",61.16,-2.08,125,75,280,26.5),
        ("49/9-1","Perenco","Southern N.Sea",53.31,2.85,58,720,800,13.0),
        ("16/17-14","Equinor","Central N.Sea",57.83,1.72,105,210,550,18.2),
        ("21/25-1","CNOOC","Central N.Sea",57.10,2.45,88,320,680,17.5),
        ("9/13-1","Shell","Northern N.Sea",58.92,1.28,112,180,300,22.5),
        ("15/17-1","BP","Central N.Sea",57.50,1.90,98,95,420,19.8),
        ("30/13-2","Spirit Energy","Southern N.Sea",54.10,2.20,65,580,620,14.2),
        ("206/8-1","Equinor","West of Shetland",60.50,-2.40,118,90,260,28.0),
        ("3/14b-7","EnQuest","Northern N.Sea",58.50,1.55,108,160,340,23.0),
        ("22/14a-7","Repsol","Central N.Sea",57.30,2.15,94,140,380,21.0),
        ("14/25-1","Shell","Central N.Sea",57.80,1.50,101,115,350,22.0),
        ("20/5-1","Dana","Central N.Sea",57.00,2.80,82,380,590,16.8),
        ("38/8-1","Ithaca","Southern N.Sea",54.50,2.60,68,640,710,13.8),
        ("12/21-1","TotalEnergies","Northern N.Sea",58.20,1.80,95,190,460,20.5),
    ]
    rows=[]
    for wid,op,basin,lat,lon,T,perm,bopd,opex in datos:
        eng=PIML(T=T,S=40000,C=0.8)
        skin=eng.skin(perm,perm*0.25); M=eng.mob(85)
        eff_b=eng.sweep(2.5); eff_n=eng.sweep(M)
        mej=max(0,(eff_n-eff_b)/max(1,eff_b)*100)
        fpi=eng.fpi(perm); _,aho=eng.roi(bopd*mej/100,opex)
        rows.append({
            "WellName":wid,"Operator":op,"Basin":basin,
            "Latitude":lat,"Longitude":lon,
            "Temp_C":T,"Perm_mD":perm,"Prod_bpd":bopd,"OPEX":opex,
            "skin":round(skin,3),"mejora_pct":round(mej,2),
            "fpi":round(fpi,4),"ahorro_anual":aho,
            "eff_base_pct":round(eff_b,1),"eff_nacmc_pct":round(eff_n,1),
            "prioridad":"🔴 CRÍTICO" if skin>15 else "🟠 ALTO" if skin>8 else "🟡 MODERADO" if skin>3 else "🟢 BAJO",
            "recomendacion":"INYECTAR Na-CMC" if fpi<0.4 and T<90 and mej>5 else "EVALUAR" if mej>2 else "MONITOREAR",
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=600)
def listar_s3():
    s3,ok=get_s3()
    if not ok: return []
    try:
        r=s3.list_objects_v2(Bucket=BUCKET)
        return [{"archivo":o["Key"],"KB":round(o["Size"]/1024,1),
                 "fecha":o["LastModified"].strftime("%d/%m/%Y %H:%M")}
                for o in r.get("Contents",[])]
    except: return []

# ═══════════════════════════════════════════
# MAPA SATELITAL INTERACTIVO
# ═══════════════════════════════════════════
def fig_mapa_satelital(df, filtro_nombre=None, zoom_lat=None, zoom_lon=None, zoom_nivel=5):
    """
    Mapa satelital estilo Mapbox.
    - Un solo pozo resaltado cuando hay búsqueda
    - Todos los pozos como puntos pequeños de fondo
    - Zoom automático al pozo buscado
    """
    col_lat  = detectar(df,["lat","latitude"])
    col_lon  = detectar(df,["lon","long","longitude"])
    col_name = detectar(df,["wellname","well_name","name","nombre","uwi","wellid"])
    col_skin = detectar(df,["skin"])
    col_op   = detectar(df,["operator","operador","company"])
    col_mej  = detectar(df,["mejora","improvement","mejora_pct"])
    col_aho  = detectar(df,["ahorro","saving","annual"])
    col_rec  = detectar(df,["recomendacion","recommendation"])
    col_prio = detectar(df,["prioridad","priority"])

    if not col_lat or not col_lon:
        lat_arr=np.random.uniform(53,62,len(df))
        lon_arr=np.random.uniform(-3,4,len(df))
    else:
        lat_arr=pd.to_numeric(df[col_lat],errors="coerce").fillna(57.5).values
        lon_arr=pd.to_numeric(df[col_lon],errors="coerce").fillna(1.5).values

    names  = df[col_name].astype(str).values  if col_name else [f"P-{i}" for i in range(len(df))]
    skins  = pd.to_numeric(df[col_skin],errors="coerce").fillna(5).values if col_skin else np.ones(len(df))*5
    ops    = df[col_op].astype(str).values    if col_op   else ["—"]*len(df)
    mejs   = pd.to_numeric(df[col_mej],errors="coerce").fillna(10).values if col_mej else np.ones(len(df))*10
    ahos   = pd.to_numeric(df[col_aho],errors="coerce").fillna(0).values  if col_aho else np.zeros(len(df))
    recs   = df[col_rec].astype(str).values   if col_rec  else ["EVALUAR"]*len(df)

    # Color por skin
    mcolors=[GR if s<3 else AM if s<8 else RD for s in skins]

    # Centro y zoom del mapa
    if zoom_lat and zoom_lon:
        center=dict(lat=zoom_lat,lon=zoom_lon)
        zoom=zoom_nivel
    else:
        center=dict(lat=57.5,lon=0.5)
        zoom=4.8

    hover=[
        f"<b style='font-size:14px'>{n}</b><br>"
        f"<span style='color:#aaa'>{o}</span><br><br>"
        f"🎯 Skin Factor: <b>{s:.2f}</b><br>"
        f"📈 Mejora EOR: <b>+{m:.1f}%</b><br>"
        f"💰 Ahorro anual: <b>${a:,.0f} USD</b><br>"
        f"🔬 {r}"
        for n,o,s,m,a,r in zip(names,ops,skins,mejs,ahos,recs)
    ]

    fig=go.Figure()

    # Todos los pozos — puntos pequeños de fondo
    if filtro_nombre:
        # Modo búsqueda: fondo tenue
        fig.add_trace(go.Scattermapbox(
            lat=lat_arr,lon=lon_arr,mode="markers",
            marker=dict(size=6,color=mcolors,opacity=0.3),
            hoverinfo="skip",name="Todos los pozos",showlegend=False,
        ))
        # Pozo encontrado: grande y destacado
        mask=[filtro_nombre.lower() in n.lower() for n in names]
        if any(mask):
            idx=[i for i,m in enumerate(mask) if m]
            for i in idx:
                fig.add_trace(go.Scattermapbox(
                    lat=[lat_arr[i]],lon=[lon_arr[i]],mode="markers+text",
                    marker=dict(size=20,color=BL,opacity=1.0),
                    text=[names[i]],textfont=dict(size=11,color=TX),
                    textposition="top right",
                    hovertext=hover[i],hoverinfo="text",
                    name=names[i],showlegend=True,
                ))
                # Círculo pulsante alrededor
                fig.add_trace(go.Scattermapbox(
                    lat=[lat_arr[i]],lon=[lon_arr[i]],mode="markers",
                    marker=dict(size=36,color=BL,opacity=0.2),
                    hoverinfo="skip",showlegend=False,
                ))
    else:
        # Modo exploración: todos con color y tamaño según skin
        sizes=np.clip(8+skins*0.6,8,18)
        fig.add_trace(go.Scattermapbox(
            lat=lat_arr,lon=lon_arr,mode="markers",
            marker=dict(size=list(sizes),color=mcolors,opacity=0.85),
            hovertext=hover,hoverinfo="text",
            name="Pozos UKCS",showlegend=False,
        ))
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# ===== CARGAR VARIABLES DE ENTORNO =====
load_dotenv()
mapbox_token = os.getenv("pk.eyJ1IjoiYWx2YXJpdXMiLCJhIjoiY21ubHV3Mjk0MWY5MTJxcGtsMWR3ajloaSJ9.a0o-DS-Fl5MjEuhK1V84MQ")

# ===== COLORES =====
BG = "rgb(10,21,32)"
BRD = "rgb(100,150,200)"
TX = "rgb(255,255,255)"

# ===== CONFIGURACIÓN DEL MAPA =====
center = dict(lat=55.0, lon=-3.0)  # Cambia según tu región
zoom = 5  # Cambia según necesites (3-8)

# ===== CREAR FIGURA (asume que tienes datos) =====
fig = go.Figure()

# Aquí agrega tus datos/traces si tienes
# fig.add_trace(go.Scattermapbox(...))

# ===== ACTUALIZAR LAYOUT =====
fig.update_layout(
    mapbox=dict(
        style="satellite-streets",
        center=center,
        zoom=zoom,
        accesstoken=mapbox_token,
    ),
    paper_bgcolor=BG,
    margin=dict(l=0, r=0, t=0, b=0),
    height=460,
    legend=dict(
        bgcolor="rgba(10,21,32,.8)",
        bordercolor=BRD,
        borderwidth=1,
        font=dict(color=TX, size=10),
        x=0.01,
        y=0.98,
    ),
    showlegend=True,
)

# ===== MOSTRAR MAPA =====
fig.show()

# ═══════════════════════════════════════════
# OTRAS FIGURAS
# ═══════════════════════════════════════════
def fig_gauge(skin):
    c=GR if skin<3 else AM if skin<8 else RD
    lbl="BAJO" if skin<3 else "MODERADO" if skin<8 else "SEVERO" if skin<20 else "CRÍTICO"
    fig=go.Figure(go.Indicator(
        mode="gauge+number",value=skin,
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

def fig_rheo(en,eh):
    g=np.logspace(-1,3,250)
    vn=[en.visc(x) for x in g]; vh=[eh.visc(x) for x in g]
    tn=[en.K*(x**en.n) for x in g]
    fig=make_subplots(rows=1,cols=2,
        subplot_titles=["η vs γ (Shear-Thinning Behavior)","τ = K·γⁿ (Power Law)"])
    fig.add_trace(go.Scatter(x=g,y=vn,name=f"Na-CMC FlowBio (n={en.n:.3f})",
        line=dict(color=GR,width=3)),row=1,col=1)
    fig.add_trace(go.Scatter(x=g,y=vh,name=f"HPAM baseline (n={eh.n:.3f})",
        line=dict(color=RD,width=2,dash="dash")),row=1,col=1)
    fig.add_vrect(x0=10,x1=100,fillcolor="rgba(75,174,110,.07)",
        line_color="rgba(75,174,110,.3)",row=1,col=1)
    fig.add_trace(go.Scatter(x=g,y=tn,name="τ Na-CMC",
        line=dict(color=BL,width=2.5)),row=1,col=2)
    fig.update_layout(**LAY,height=320)
    fig.update_xaxes(type="log",title_text="Tasa de Corte γ (s⁻¹)",gridcolor=BRD)
    fig.update_yaxes(type="log",title_text="η (mPa·s)",gridcolor=BRD,row=1,col=1)
    fig.update_yaxes(title_text="τ (Pa)",gridcolor=BRD,row=1,col=2)
    for ann in fig.layout.annotations: ann.font.color=TX; ann.font.size=10
    return fig

def fig_prod(bopd,extra,dias):
    t=np.arange(0,dias+1)
    Qb=bopd*np.exp(-0.002*t); Qn=(bopd+extra)*np.exp(-0.0011*t)
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=np.concatenate([t,t[::-1]]),y=np.concatenate([Qn,Qb[::-1]]),
        fill="toself",fillcolor="rgba(75,174,110,.1)",
        line=dict(color="rgba(0,0,0,0)"),name="Barriles extra",hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=t,y=Qb,name="Baseline",
        line=dict(color=RD,width=2,dash="dash")))
    fig.add_trace(go.Scatter(x=t,y=Qn,name="Con Na-CMC FlowBio",
        line=dict(color=GR,width=3)))
    fig.update_layout(**LAY,height=300,
        xaxis_title="Días",yaxis_title="Producción (bbl/día)",hovermode="x unified")
    return fig

def fig_skin_scatter(df):
    col_sk=detectar(df,["skin"]); col_mj=detectar(df,["mejora","mejora_pct"])
    col_n =detectar(df,["wellname","well_name","name"])
    skins =pd.to_numeric(df[col_sk],errors="coerce").fillna(5).clip(0,30) if col_sk else pd.Series([5.0]*len(df))
    mejs  =pd.to_numeric(df[col_mj],errors="coerce").fillna(0) if col_mj else pd.Series([10.0]*len(df))
    names =df[col_n].astype(str) if col_n else pd.Series([f"P-{i}" for i in range(len(df))])
    colors=[GR if s<3 else AM if s<8 else RD for s in skins]
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=skins,y=mejs,mode="markers",
        marker=dict(color=colors,size=8,opacity=0.8,
                    line=dict(color=BG2,width=0.8)),
        hovertemplate="<b>%{text}</b><br>Skin: %{x:.2f}<br>Mejora EOR: %{y:.1f}%<extra></extra>",
        text=names,name="Pozos"))
    fig.add_vrect(x0=0,x1=3,fillcolor="rgba(75,174,110,.05)",line_width=0)
    fig.add_vrect(x0=3,x1=8,fillcolor="rgba(232,160,48,.05)",line_width=0)
    fig.add_vrect(x0=8,x1=30,fillcolor="rgba(224,90,90,.05)",line_width=0)
    fig.update_layout(**LAY,height=300,
        xaxis_title="Factor Skin (S)",yaxis_title="Mejora EOR con Na-CMC (%)",
        title=dict(text="Skin Factor vs Potencial EOR — Todos los Pozos",
                   font=dict(size=12,color=TX),x=0))
    return fig

def fig_top(df):
    col_mj=detectar(df,["mejora","mejora_pct"])
    col_ah=detectar(df,["ahorro","saving","annual"])
    col_n =detectar(df,["wellname","well_name","name","nombre"])
    col_rc=detectar(df,["recomendacion","recommendation"])
    names =df[col_n].astype(str).str[:15] if col_n else pd.Series([f"P-{i}" for i in range(len(df))])
    mejs  =pd.to_numeric(df[col_mj],errors="coerce").fillna(0) if col_mj else pd.Series([10.0]*len(df))
    ahos  =pd.to_numeric(df[col_ah],errors="coerce").fillna(0) if col_ah else pd.Series([0.0]*len(df))
    recs  =df[col_rc].astype(str) if col_rc else pd.Series(["EVALUAR"]*len(df))
    df2=pd.DataFrame({"n":names.values,"mj":mejs.values,"ah":ahos.values,"r":recs.values})
    top=df2.nlargest(12,"mj").sort_values("mj")
    cols=[GR if r=="INYECTAR Na-CMC" else AM if r=="EVALUAR" else BL for r in top["r"]]
    fig=make_subplots(rows=1,cols=2,subplot_titles=["Top 12 — Mejora EOR (%)","Top 12 — Ahorro OPEX (KUSD/año)"])
    fig.add_trace(go.Bar(x=top["mj"],y=top["n"],orientation="h",
        marker_color=cols,opacity=0.88,name="",
        hovertemplate="%{y}: +%{x:.1f}%<extra></extra>"),row=1,col=1)
    top2=df2.nlargest(12,"ah").sort_values("ah")
    cols2=[GR if r=="INYECTAR Na-CMC" else AM if r=="EVALUAR" else BL for r in top2["r"]]
    fig.add_trace(go.Bar(x=top2["ah"]/1000,y=top2["n"],orientation="h",
        marker_color=cols2,opacity=0.88,name="",
        hovertemplate="%{y}: $%{x:.0f}K USD/año<extra></extra>"),row=1,col=2)
    fig.update_layout(**LAY,height=360,showlegend=False)
    fig.update_xaxes(gridcolor=BRD,linecolor=BRD)
    fig.update_yaxes(gridcolor=BRD,linecolor=BRD,tickfont=dict(size=9))
    for ann in fig.layout.annotations: ann.font.color=TX; ann.font.size=10
    return fig

# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
for k,v in [("simulated",False),("demo_well",None),
            ("busqueda",""),("sel_well",None)]:
    if k not in st.session_state: st.session_state[k]=v

DEMOS={
    "29/10-1 · Harbour Energy · S.N.Sea": dict(T=72,S=33000,visc=88,perm=450,bopd=500,opex=15.5,conc=0.9,dias=120),
    "211/18-1 · BP · W.Shetland":         dict(T=125,S=55000,visc=6, perm=75, bopd=280,opex=26.5,conc=0.6,dias=90),
    "49/9-1 · Perenco · S.N.Sea":         dict(T=58, S=22000,visc=200,perm=720,bopd=800,opex=13.0,conc=1.1,dias=180),
    "16/17-14 · Equinor · C.N.Sea":       dict(T=105,S=44000,visc=22, perm=210,bopd=550,opex=18.2,conc=0.75,dias=120),
}
_d=st.session_state.demo_well or {}
_,s3_ok=get_s3()

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:14px 0 8px'>
      <div style='font-size:22px;font-weight:900;color:#fff;font-family:Outfit,sans-serif'>🛢️ FlowBio</div>
      <div style='font-size:9px;letter-spacing:2px;color:{GR};margin-top:2px;font-family:Space Mono,monospace'>INTELLIGENCE · PIML v0.3</div>
    </div>
    <hr style='border-color:{BRD};margin:8px 0 12px'>
    <div style='text-align:center;margin-bottom:10px'>
      <span class='{'bg' if s3_ok else 'bb'}'>{'🟢 S3 Live' if s3_ok else '🔵 Demo'}</span>
    </div>
    """, unsafe_allow_html=True)

    if not s3_ok:
        st.markdown(f"""<div class='box-a' style='font-size:10px;margin-bottom:10px'>
          <b>Settings → Secrets:</b><br>
          <code>[aws]<br>AWS_ACCESS_KEY_ID="..."<br>AWS_SECRET_ACCESS_KEY="..."</code>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"<div class='ssc'>🚀 DEMO — NSTA OPEN DATA</div>", unsafe_allow_html=True)
    ds=st.selectbox("Pozo",["— Manual —"]+list(DEMOS.keys()),label_visibility="collapsed")
    if ds!="— Manual —":
        if st.button("▶ Cargar Demo",use_container_width=True,type="primary"):
            st.session_state.demo_well=DEMOS[ds]
            st.session_state.simulated=True; st.rerun()
    st.markdown(f"<hr style='border-color:{BRD};margin:10px 0'>", unsafe_allow_html=True)

    st.markdown(f"<div class='ssc'>🛢 YACIMIENTO</div>", unsafe_allow_html=True)
    T   =st.slider("Temperatura (°C)",40,130,int(_d.get("T",82)))
    S   =st.slider("Salinidad (ppm)",5000,100000,int(_d.get("S",38000)),1000,format="%d")
    visc=st.number_input("Viscosidad crudo (cP)",1,2000,int(_d.get("visc",85)))
    perm=st.number_input("Permeabilidad (mD)",1,3000,int(_d.get("perm",250)))
    bopd=st.number_input("Producción (bbl/día)",10,5000,int(_d.get("bopd",500)))

    st.markdown(f"<div class='ssc'>⚗ NA-CMC</div>", unsafe_allow_html=True)
    conc=st.slider("Concentración (%wt)",0.05,2.0,float(_d.get("conc",0.8)),0.05)
    dias=st.slider("Horizonte (días)",30,365,int(_d.get("dias",120)),10)

    st.markdown(f"<div class='ssc'>💰 ECONOMÍA</div>", unsafe_allow_html=True)
    opex     =st.number_input("OPEX (USD/bbl)",2.0,60.0,float(_d.get("opex",18.5)),0.5)
    oil_price=st.number_input("Precio petróleo (USD/bbl)",20.0,150.0,74.5,0.5)

    st.markdown(f"<hr style='border-color:{BRD};margin:12px 0 8px'>", unsafe_allow_html=True)
    if st.button("▶  EJECUTAR SIMULACIÓN PIML",use_container_width=True,type="primary"):
        st.session_state.simulated=True; st.session_state.demo_well=None; st.rerun()
    if st.session_state.simulated:
        if st.button("↺  Limpiar",use_container_width=True):
            st.session_state.simulated=False; st.session_state.demo_well=None; st.rerun()

    st.markdown(f"""<div style='font-size:9px;color:#2A4A6A;text-align:center;margin-top:10px;
        line-height:1.7;font-family:Space Mono,monospace'>
      TRL 3 · IMP+CENAM pendiente<br>Amplifika UAG · WC 2026</div>""",unsafe_allow_html=True)

# ═══════════════════════════════════════════
# CALCULAR
# ═══════════════════════════════════════════
en=PIML(T=T,S=S,C=conc,fluid="Na-CMC"); eh=PIML(T=T,S=S,C=conc,fluid="HPAM")
skin_v=en.skin(perm,perm*0.25); skin_n2=en.skin(perm,perm*0.85)
M_v=en.mob(visc); eff_b=en.sweep(2.5); eff_n=en.sweep(M_v)
extra=max(0,bopd*(eff_n-eff_b)/max(1,eff_b))
neto_m,ahorro_yr=en.roi(extra,opex,oil_price); fpi_v=en.fpi(perm)
roi_pct=round((neto_m/max(1,(150*0.159*(conc/100)*1000)*2.8*30))*100,1)

# ═══════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════
hc1,hc2,hc3=st.columns([0.07,0.73,0.20])
with hc1: st.markdown("<div style='font-size:44px;margin-top:6px'>🛢️</div>",unsafe_allow_html=True)
with hc2:
    st.markdown(f"""<div style='padding:6px 0'>
      <div style='font-size:20px;font-weight:800;color:#fff;font-family:Outfit,sans-serif'>
        FlowBio Intelligence</div>
      <div style='font-size:10px;color:{GR};letter-spacing:.8px;font-family:Space Mono,monospace;margin-top:2px'>
        SUBSURFACE DIAGNOSTIC CONSOLE · PIML · EOR · NA-CMC · AWS S3
      </div></div>""",unsafe_allow_html=True)
with hc3:
    st.markdown(f"""<div style='text-align:right;padding:10px 0'>
      <span class='bg'>PIML v0.3 · TRL 3</span><br><br>
      <span class='{'bg' if s3_ok else 'bb'}'>{'🟢 S3 Live' if s3_ok else '🔵 Demo'}</span>
    </div>""",unsafe_allow_html=True)
st.markdown(f"<hr style='border-color:{BRD};margin:4px 0 16px'>",unsafe_allow_html=True)

# ═══════════════════════════════════════════
# PANTALLA INICIAL
# ═══════════════════════════════════════════
if not st.session_state.simulated:
    # KPIs del mercado
    st.markdown(f"<div class='sh'>📊 CONTEXTO DE MERCADO EOR</div>",unsafe_allow_html=True)
    m1,m2,m3,m4,m5=st.columns(5)
    for col,(v,c,l,s,t) in zip([m1,m2,m3,m4,m5],[
        ("$44.66B","vb","MERCADO EOR 2032","5.2% CAGR","kcard-eor"),
        ("+18%","vg","EF. BARRIDO","vs HPAM sintético","kcard-eor"),
        ("−90%","vg","SKIN DAMAGE","Na-CMC FlowBio","kcard-res"),
        ("100%","vt","BIODEGRADABLE","DNSH compliant","kcard-esg"),
        ("$5","va","SUCCESS FEE","USD/bbl extra","kcard-eor"),
    ]):
        with col:
            st.markdown(f"""<div class='kcard {t}'>
              <div class='klbl'>{l}</div>
              <div class='kval {c}'>{v}</div>
              <div class='ksub'>{s}</div>
            </div>""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # ── MAPA + ALERTAS ──────────────────────────────────────────
    st.markdown(f"<div class='sh'>🗺️ MAPA SATELITAL — POZOS UKCS</div>",unsafe_allow_html=True)

    with st.spinner("Cargando datos..."):
        df_wells,fuente,es_s3=cargar_pozos()

    map_col,alert_col=st.columns([0.68,0.32])

    with map_col:
        # Buscador de pozos
        col_name_w=detectar(df_wells,["wellname","well_name","name","nombre","uwi"])
        names_all=df_wells[col_name_w].astype(str).tolist() if col_name_w else []

        busq=st.text_input(
            "🔍  Buscar pozo por nombre, bloque u operadora",
            value=st.session_state.busqueda,
            placeholder="Ej: 29/10-1 · Harbour · Southern...",
            key="input_busqueda",
        )
        st.session_state.busqueda=busq

        # Determinar zoom
        zoom_lat=zoom_lon=None; zoom_n=4.8
        if busq:
            mask=[busq.lower() in n.lower() for n in names_all]
            if any(mask):
                col_lat_=detectar(df_wells,["lat","latitude"])
                col_lon_=detectar(df_wells,["lon","long","longitude"])
                if col_lat_ and col_lon_:
                    idx=[i for i,m in enumerate(mask) if m][0]
                    zoom_lat=pd.to_numeric(df_wells[col_lat_],errors="coerce").iloc[idx]
                    zoom_lon=pd.to_numeric(df_wells[col_lon_],errors="coerce").iloc[idx]
                    zoom_n=8

        st.plotly_chart(
            fig_mapa_satelital(df_wells,
                               filtro_nombre=busq if busq else None,
                               zoom_lat=zoom_lat,zoom_lon=zoom_lon,zoom_nivel=zoom_n),
            use_container_width=True
        )

        # Coordenadas del pozo encontrado
        if busq and zoom_lat:
            st.markdown(f"""<div class='coord-label'>
              📍 {zoom_lat:.4f}°N, {zoom_lon:.4f}°E &nbsp;|&nbsp; Pozo: <b>{busq.upper()}</b>
            </div>""",unsafe_allow_html=True)

    with alert_col:
        st.markdown(f"<div class='sh'>🔔 ALERTAS Y NOTIFICACIONES</div>",unsafe_allow_html=True)

        # Alertas dinámicas según datos
        col_sk=detectar(df_wells,["skin"])
        col_mj=detectar(df_wells,["mejora","mejora_pct"])
        col_n =detectar(df_wells,["wellname","well_name","name"])

        if col_sk and col_n:
            criticos=df_wells[pd.to_numeric(df_wells[col_sk],errors="coerce")>15]
            optimos =df_wells[pd.to_numeric(df_wells[col_mj] if col_mj else pd.Series([0]*len(df_wells)),errors="coerce")>15]

            n_crit=len(criticos); n_opt=len(optimos)

            if n_crit>0:
                w_crit=criticos[col_n].iloc[0] if len(criticos)>0 else "—"
                st.markdown(f"""<div class='alert-card crit'>
                  <span class='alert-time'>Análisis PIML</span>
                  <div class='alert-title'>⚠️ Daño Crítico Detectado</div>
                  <div class='alert-body'>
                    {n_crit} pozos con Skin Factor > 15.<br>
                    Intervención urgente recomendada.
                  </div>
                  <div class='alert-well'>● {w_crit} y {n_crit-1} más</div>
                </div>""",unsafe_allow_html=True)

            if n_opt>0:
                w_opt=optimos[col_n].iloc[0] if len(optimos)>0 else "—"
                st.markdown(f"""<div class='alert-card ok'>
                  <span class='alert-time'>Motor PIML</span>
                  <div class='alert-title'>✅ Candidatos EOR Confirmados</div>
                  <div class='alert-body'>
                    {n_opt} pozos con mejora > 15%.<br>
                    Aptos para inyección Na-CMC FlowBio.
                  </div>
                  <div class='alert-well'>● {w_opt} y otros</div>
                </div>""",unsafe_allow_html=True)

            skin_avg=pd.to_numeric(df_wells[col_sk],errors="coerce").mean()
            st.markdown(f"""<div class='alert-card'>
              <span class='alert-time'>Estadística</span>
              <div class='alert-title'>📊 Skin Promedio: {skin_avg:.1f}</div>
              <div class='alert-body'>
                {'Daño severo en el campo.' if skin_avg>8 else 'Daño moderado detectado.' if skin_avg>3 else 'Campo en condiciones aceptables.'}
              </div>
              <div class='alert-well'>● {len(df_wells)} pozos analizados</div>
            </div>""",unsafe_allow_html=True)

        # Resultados de búsqueda
        if busq:
            st.markdown(f"<div class='sh' style='margin-top:14px'>🔍 RESULTADOS: \"{busq}\"</div>",unsafe_allow_html=True)
            if col_name_w:
                found=df_wells[df_wells[col_name_w].astype(str).str.lower().str.contains(busq.lower())]
                if len(found):
                    show_c=[c for c in ["WellName","Operator","Temp_C","Perm_mD","skin","mejora_pct","recomendacion"] if c in found.columns]
                    st.dataframe(found[show_c[:6]].head(5),use_container_width=True,hide_index=True)
                else:
                    st.info("Sin resultados para esa búsqueda.")

    # ── ANÁLISIS GENERAL ────────────────────────────────────────
    st.markdown(f"<div class='sh'>📈 ANÁLISIS PIML — TODOS LOS POZOS</div>",unsafe_allow_html=True)
    ac1,ac2=st.columns(2)
    with ac1: st.plotly_chart(fig_skin_scatter(df_wells),use_container_width=True)
    with ac2: st.plotly_chart(fig_top(df_wells),use_container_width=True)

    # ── PERFILES DE USUARIOS ─────────────────────────────────────
    st.markdown(f"<div class='sh'>🎯 DISEÑADO PARA TUS CLIENTES OBJETIVO</div>",unsafe_allow_html=True)
    p1,p2,p3=st.columns(3)
    perfiles=[
        ("💼","EOR MANAGER","Gerente de Recuperación EOR",
         "Su bono anual depende de cuántos barriles extra logra sacar.",
         f"✅ 'Aumentamos +18% la eficiencia de barrido sin dañar la formación.<br>Te lo demostramos en tiempo real con datos de tu pozo.'",
         "kcard-eor"),
        ("🔬","RESERVOIR ENGINEER","Ingeniero de Yacimientos",
         "Valida la física: Factor Skin, Ley de Potencia, reología real.",
         f"✅ 'Na-CMC sigue el modelo Ostwald-de Waele. n={en.n:.3f}.<br>Motor PIML con restricción termodinámica — sin alucinaciones.'",
         "kcard-res"),
        ("🌿","ESG MANAGER","Gerente de Sustentabilidad",
         "Debe reducir toxicidad y huella de carbono del campo.",
         "✅ 'Materia prima: lirio acuático invasor. Producto: 100% biodegradable.<br>Cumple DNSH. Elimina HPAM tóxico. Historia de economía circular.'",
         "kcard-esg"),
    ]
    for col,(ico,rol,nombre,pain,win,cls) in zip([p1,p2,p3],perfiles):
        with col:
            st.markdown(f"""<div class='kcard {cls}' style='padding:22px;text-align:left'>
              <div class='profile-icon'>{ico}</div>
              <div class='profile-role'>{rol}</div>
              <div class='profile-name'>{nombre}</div>
              <div class='profile-pain'>{pain}</div>
              <div class='profile-win'>{win}</div>
            </div>""",unsafe_allow_html=True)

    # ── TABLA ────────────────────────────────────────────────────
    st.markdown(f"<div class='sh'>📋 RANKING DE POZOS — MAYOR POTENCIAL EOR</div>",unsafe_allow_html=True)
    sort_c=next((c for c in ["mejora_pct","skin","ahorro_anual"] if c in df_wells.columns),df_wells.columns[0])
    show_c=[c for c in ["WellName","Operator","Basin","Temp_C","Perm_mD","skin","mejora_pct","ahorro_anual","recomendacion","prioridad"] if c in df_wells.columns]
    if not show_c: show_c=df_wells.columns[:8].tolist()
    st.dataframe(df_wells.sort_values(sort_c,ascending=False)[show_c].reset_index(drop=True).head(30),
                 use_container_width=True,hide_index=True)

    st.stop()

# ═══════════════════════════════════════════
# RESULTADOS POST-SIMULACIÓN
# ═══════════════════════════════════════════
sk_c="vr" if skin_v>8 else "va" if skin_v>3 else "vg"
mb_c="vg" if M_v<1 else "va" if M_v<2 else "vr"

st.markdown(f"<div class='sh'>📊 RESULTADOS PIML — DIAGNÓSTICO DEL POZO</div>",unsafe_allow_html=True)
k1,k2,k3,k4,k5=st.columns(5)
for col,(v,c,l,s,t) in zip([k1,k2,k3,k4,k5],[
    (f"{skin_v:.2f}",sk_c,"FACTOR SKIN (S)","S=(K/Kd-1)·ln(rd/rw)","kcard-res"),
    (f"{en.n:.3f}","vb","ÍNDICE FLUJO (n)","Power Law Na-CMC","kcard-res"),
    (f"{eff_n:.1f}%","vg","EF. BARRIDO EOR",f"vs {eff_b:.1f}% baseline","kcard-eor"),
    (f"{M_v:.3f}",mb_c,"RATIO MOVILIDAD M","Favorable" if M_v<1 else "Desfav.","kcard-eor"),
    (f"${ahorro_yr:,.0f}","vg","AHORRO ANUAL USD",f"+{extra:.0f} bbl/día","kcard-eor"),
]):
    with col:
        st.markdown(f"""<div class='kcard {t}'>
          <div class='klbl'>{l}</div>
          <div class='kval {c}'>{v}</div>
          <div class='ksub'>{s}</div>
        </div>""",unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5=st.tabs([
    "🗺️ Mapa de Pozos",
    "🎯 Diagnóstico Skin",
    "⚗ Reología PIML",
    "📈 Producción & ROI",
    "📊 Dashboard S3",
])

with tab1:
    with st.spinner("Cargando mapa..."):
        df_w2,fw2,_=cargar_pozos()
    st.markdown(f"<div class='sh'>🗺️ MAPA SATELITAL — UKCS NORTH SEA</div>",unsafe_allow_html=True)
    busq2=st.text_input("🔍 Buscar pozo",placeholder="Nombre, bloque, operadora...",key="busq2")
    col_n2=detectar(df_w2,["wellname","well_name","name","nombre"])
    col_lat2=detectar(df_w2,["lat","latitude"]); col_lon2=detectar(df_w2,["lon","long","longitude"])
    zl=zo=None; zn=4.8
    if busq2 and col_n2 and col_lat2 and col_lon2:
        mask2=df_w2[col_n2].astype(str).str.lower().str.contains(busq2.lower())
        if mask2.any():
            idx2=mask2.idxmax()
            zl=pd.to_numeric(df_w2[col_lat2],errors="coerce").iloc[idx2]
            zo=pd.to_numeric(df_w2[col_lon2],errors="coerce").iloc[idx2]
            zn=8
    st.plotly_chart(fig_mapa_satelital(df_w2,busq2 if busq2 else None,zl,zo,zn),
                    use_container_width=True)
    if busq2 and zl:
        found2=df_w2[df_w2[col_n2].astype(str).str.lower().str.contains(busq2.lower())]
        if len(found2):
            sh2=[c for c in ["WellName","Operator","Basin","Temp_C","Perm_mD","skin","mejora_pct","recomendacion"] if c in found2.columns]
            st.dataframe(found2[sh2].head(5),use_container_width=True,hide_index=True)

with tab2:
    cg,ci=st.columns([1,1.4])
    with cg:
        st.markdown(f"<div class='sh'>🎯 VELOCÍMETRO — SKIN DAMAGE</div>",unsafe_allow_html=True)
        st.plotly_chart(fig_gauge(skin_v),use_container_width=True)
    with ci:
        st.markdown(f"<div class='sh'>📋 DIAGNÓSTICO TÉCNICO</div>",unsafe_allow_html=True)
        red_pct=((skin_v-skin_n2)/max(0.01,skin_v))*100
        st.markdown(f"""<div class='box-b'>
          <b style='color:{GR}'>⚡ Ostwald-de Waele · Power Law</b><br>
          Na-CMC: n=<b>{en.n:.4f}</b> | K=<b>{en.K:.1f}</b> mPa·sⁿ<br>
          HPAM:&nbsp;&nbsp; n=<b>{eh.n:.4f}</b> | K=<b>{eh.K:.1f}</b> mPa·sⁿ<br><br>
          n &lt; 1 → pseudoplástico ✓ · shear-thinning · ideal EOR
        </div>""",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(f"""<div class='box-g'>
          <b>📉 Impacto Na-CMC FlowBio</b><br>
          Skin actual: <b>{skin_v:.2f}</b> → Con Na-CMC: <b>{skin_n2:.2f}</b>
          (−<b>{red_pct:.0f}%</b>)<br>
          FPI (tapon.): <b>{fpi_v:.3f}</b> —
          {'✅ BAJO' if fpi_v<0.25 else '⚠️ MODERADO' if fpi_v<0.5 else '❌ ALTO'}<br>
          T={T}°C → {'✅ Estable' if T<90 else '⚠️ Sobre límite 90°C'}
        </div>""",unsafe_allow_html=True)
        st.markdown(f"<div class='sh'>⚙ OPERATIONAL READINESS</div>",unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Indicador":["Estab. térmica","Salinidad","Skin Damage","Movilidad M","FPI","Biodegradab.","HSE"],
            "Estado actual":["✅ OK" if T<90 else "⚠️","✅ OK" if S<70000 else "⚠️",
                "❌ Alto" if skin_v>8 else "⚠️ Mod." if skin_v>3 else "✅ Bajo",
                "✅ Fav." if M_v<1 else "⚠️","✅ Bajo" if fpi_v<0.25 else "⚠️" if fpi_v<0.5 else "❌",
                "❌ No","❌ Tóxico"],
            "Con Na-CMC FlowBio":["✅ 90°C","✅ 80Kppm",f"✅ −{red_pct:.0f}%","✅ Mejor","✅ Mín.","✅ 100%","✅ Cero"],
        }),use_container_width=True,hide_index=True)

with tab3:
    st.markdown(f"<div class='sh'>⚗ CURVAS REOLÓGICAS — POWER LAW</div>",unsafe_allow_html=True)
    st.plotly_chart(fig_rheo(en,eh),use_container_width=True)
    fc1,fc2,fc3=st.columns(3)
    for col,txt in zip([fc1,fc2,fc3],[
        f"τ = K·γⁿ\nLey de Potencia",
        f"η = K·γ^(n-1)\nViscosidad Aparente",
        f"n = {en.n:.4f}\nK = {en.K:.1f} mPa·sⁿ"]):
        with col:
            st.markdown(f"<div class='formula'>{txt}</div>",unsafe_allow_html=True)

with tab4:
    st.markdown(f"""<div class='hero'>
      <div class='hero-lbl'>SUCCESS FEE NETO MENSUAL — MODELO ADÁN RAMÍREZ</div>
      <div class='hero-val'>${neto_m:,.0f} USD</div>
      <div class='hero-sub'>{extra:.1f} bbl/día extra × $5 × 30d − costo Na-CMC</div>
    </div>""",unsafe_allow_html=True)
    poly_d=(150*0.159*(conc/100)*1000)*2.8*30; fee_d=extra*5*30
    e1,e2,e3,e4=st.columns(4)
    for col,(v,c,l,s,t) in zip([e1,e2,e3,e4],[
        (f"+{extra:.1f}","vg","BARRILES EXTRA/DÍA",f"sobre {bopd}","kcard-eor"),
        (f"${fee_d:,.0f}","vb","SUCCESS FEE/MES","$5/bbl extra","kcard-eor"),
        (f"${poly_d:,.0f}","va","COSTO POLÍMERO/MES","Na-CMC · Orizaba","kcard-esg"),
        (f"{roi_pct:.0f}%","vg","ROI INMEDIATO",f"${ahorro_yr:,.0f}/año","kcard-eor"),
    ]):
        with col:
            st.markdown(f"""<div class='kcard {t}'>
              <div class='klbl'>{l}</div><div class='kval {c}'>{v}</div>
              <div class='ksub'>{s}</div></div>""",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.plotly_chart(fig_prod(bopd,extra,dias),use_container_width=True)

with tab5:
    st.markdown(f"<div class='sh'>📊 DASHBOARD — DATOS S3</div>",unsafe_allow_html=True)
    with st.spinner("Cargando S3..."):
        df_s3,fuente_s3,es_s3=cargar_pozos()
    cls_b="box-g" if es_s3 else "box-a"
    st.markdown(f"<div class='{cls_b}'>{'✅' if es_s3 else '🔵'} {fuente_s3} · <b>{len(df_s3):,}</b> pozos</div>",
                unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    col_sk2=detectar(df_s3,["skin"]); col_mj2=detectar(df_s3,["mejora","mejora_pct"])
    col_ah2=detectar(df_s3,["ahorro","saving","annual"])
    sm=pd.to_numeric(df_s3[col_sk2],errors="coerce").mean() if col_sk2 else 5.0
    mm=pd.to_numeric(df_s3[col_mj2],errors="coerce").mean() if col_mj2 else 10.0
    am=pd.to_numeric(df_s3[col_ah2],errors="coerce").mean() if col_ah2 else 50000.0
    d1,d2,d3,d4=st.columns(4)
    for col,(v,c,l,t) in zip([d1,d2,d3,d4],[
        (f"{len(df_s3):,}","vb","POZOS","kcard-res"),
        (f"{sm:.2f}","vr" if sm>8 else "va","SKIN PROM.","kcard-res"),
        (f"{mm:.1f}%","vg","MEJORA EOR","kcard-eor"),
        (f"${am:,.0f}","vg","AHORRO PROM.","kcard-eor"),
    ]):
        with col:
            st.markdown(f"""<div class='kcard {t}'>
              <div class='klbl'>{l}</div><div class='kval {c}'>{v}</div>
            </div>""",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.plotly_chart(fig_mapa_satelital(df_s3),use_container_width=True)
    st.plotly_chart(fig_skin_scatter(df_s3),use_container_width=True)
    st.plotly_chart(fig_top(df_s3),use_container_width=True)
    srt=col_mj2 if col_mj2 else df_s3.columns[0]
    shc=[c for c in ["WellName","Operator","Basin","Temp_C","Perm_mD","skin","mejora_pct","ahorro_anual","recomendacion","prioridad"] if c in df_s3.columns]
    if not shc: shc=df_s3.columns[:8].tolist()
    st.dataframe(df_s3.sort_values(srt,ascending=False).head(50).reset_index(drop=True)[shc],
                 use_container_width=True,hide_index=True)
    if s3_ok:
        files=listar_s3()
        if files:
            st.markdown(f"<div class='sh'>📦 ARCHIVOS EN S3</div>",unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(files),use_container_width=True,hide_index=True)

st.markdown(f"""
<hr style='border-color:{BRD};margin:30px 0 14px'>
<div style='text-align:center;font-size:9px;color:#2A4A6A;line-height:1.8;font-family:Space Mono,monospace'>
  <b style='color:{GR}'>FlowBio Intelligence</b> · Motor PIML v0.3 · TRL 3 ·
  Na-CMC desde <i>Eichhornia crassipes</i> · Orizaba, Veracruz, MX<br>
  Startup Building Beyond the World Cup 2026 · Amplifika UAG
</div>""",unsafe_allow_html=True)
