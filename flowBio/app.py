import streamlit as st
import streamlit.components.v1 as components
import json, math
import boto3
from fpdf import FPDF
from datetime import datetime

# ══════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="FlowBio Subsurface OS",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Syne:wght@700;800&family=DM+Mono&display=swap');
    [data-testid="stHeader"],[data-testid="stSidebar"],footer{display:none!important}
    .stApp{background:#060B11}
    .block-container{padding:2rem 3rem!important}
    
    /* FIX: Fuentes con respaldo del sistema para evitar que cambie la tipografía */
    body, p, div { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    .kpi-value, h1, h2 { font-family: 'Syne', sans-serif !important; }
    .kpi-label, code, pre { font-family: 'DM Mono', monospace !important; }
    
    .kpi-box{background:rgba(13,21,32,0.8);border:1px solid rgba(255,255,255,0.05);
             border-radius:12px;padding:22px;border-top:4px solid #00E5A0;height:100%}
    .kpi-box.cyan{border-top-color:#22D3EE}
    .kpi-box.amber{border-top-color:#F59E0B}
    .kpi-box.red{border-top-color:#EF4444}
    .kpi-label{font-size:11px;color:#64748B;font-weight:600;
               text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
    .kpi-value{font-size:32px;font-weight:800;color:#fff;margin:5px 0}
    .kpi-desc{font-size:10px;color:#8BA8C0;margin-top:5px;line-height:1.3}
    .stButton>button{background:#00E5A0!important;color:#060B11!important;
                     font-family:'Syne', sans-serif !important;font-weight:800!important;
                     border-radius:8px!important;padding:15px 30px!important;width:100%}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 2. S3 — carga dashboard_data.json generado por Jupyter
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def load_dashboard_data():
    """Lee dashboard_data.json del bucket S3. TTL=60s."""
    try:
        try:
            aws_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
        except:
            aws_key = st.secrets["AWS_ACCESS_KEY_ID"]
            aws_sec = st.secrets["AWS_SECRET_ACCESS_KEY"]

        s3  = boto3.client("s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_sec,
            region_name="us-east-2")
        obj = s3.get_object(
            Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an",
            Key="agentes/dashboard_data.json")
        return json.loads(obj["Body"].read().decode("utf-8")), True
    except Exception as e:
        st.warning(f"S3: {e} — usando datos demo")
        return None, False

def demo_data():
    """Datos demo con los campos correctos para cuando S3 no está disponible."""
    return {
        "Well-UKCS-Alpha": {
            "ahorro":12000,"mejora":18.5,"extra_bpd":92.5,"extra_mes":2775,
            "valor_extra":206831,"fee":13875,"eur":135150,"payback":4.2,
            "oil_price_usd":74.5,"visc_p":102.3,"yield_p":18.4,
            "quimico":"Na-CMC FlowBio","ppm":1760,"vol_pv":0.31,"bwpd":478,
            "lim_psi":3240,"wc_red":19.2,"skin":8.4,"temp_c":78.0,
            "recomendacion":"INYECTAR",
        },
        "Well-UKCS-Beta": {
            "ahorro":9500,"mejora":14.2,"extra_bpd":71.0,"extra_mes":2130,
            "valor_extra":158685,"fee":10650,"eur":103880,"payback":5.8,
            "oil_price_usd":74.5,"visc_p":88.7,"yield_p":14.1,
            "quimico":"Goma Xantana","ppm":1320,"vol_pv":0.24,"bwpd":421,
            "lim_psi":2980,"wc_red":15.7,"skin":5.1,"temp_c":62.0,
            "recomendacion":"INYECTAR",
        },
    }


# ══════════════════════════════════════════════════════
# 3. PDF CORPORATIVO
# ══════════════════════════════════════════════════════
def generate_pdf(well, d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6,11,17); pdf.rect(0,0,210,297,'F')
    pdf.set_text_color(255,255,255)
    pdf.set_font('Arial','B',18)
    pdf.cell(0,15,f"FlowBio Executive Report: {well}",0,1)
    pdf.set_font('Arial','',11)
    pdf.set_text_color(0,229,160)
    pdf.cell(0,8,f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | PIML v0.3",0,1)
    pdf.ln(6)
    pdf.set_fill_color(13,21,32); pdf.set_text_color(255,255,255)
    
    rows_pdf = [
        ["Barriles Extra/Día",  f"{d.get('extra_bpd',0):.1f} bbl/día"],
        ["Barriles Extra/Mes",  f"{d.get('extra_mes',0):,} bbl/mes"],
        ["Valor Extra Generado",f"${d.get('valor_extra',0):,} USD/mes"],
        ["Success Fee Mensual", f"${d.get('fee',0):,} USD/mes"],
        ["Payback",             f"{d.get('payback',0)} meses"],
        ["PV (Visc. Plástica)", f"{d.get('visc_p',0)} mPa·s"],
        ["YP (Yield Point)",    f"{d.get('yield_p',0)} lb/ft²"],
        ["EUR Acumulado",       f"{d.get('eur',0):,} bbls"],
        ["Químico EOR",         str(d.get('quimico','—'))],
        ["Concentración",       f"{d.get('ppm',0)} ppm"],
        ["Factor Skin",         f"{d.get('skin',0):.2f}"],
        ["Recomendación",       str(d.get('recomendacion','—'))],
    ]
    for k,v in rows_pdf:
        pdf.cell(95,11,f" {k}",1,0,'L',True)
        pdf.cell(95,11,f" {v}",1,1,'R')
    pdf.ln(8)
    pdf.set_text_color(100,116,139)
    pdf.set_font('Arial','I',9)
    pdf.cell(0,8,"FlowBio Intelligence · PIML v0.3 · TRL 4 · Orizaba, Veracruz, MX",0,1,'C')
    
    # FIX: errors='replace' para que no falle el UnicodeEncodeError
    return pdf.output(dest='S').encode('latin-1', errors='replace')


# ══════════════════════════════════════════════════════
# 4. AUTENTICACIÓN
# ══════════════════════════════════════════════════════
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("""
    <div style='text-align:center;margin-top:18vh'>
      <h1 style='color:white;font-family:Syne;font-size:72px;letter-spacing:-3px'>
        FlowBio<span style='color:#00E5A0'>.</span>
      </h1>
      <p style='color:#4A6580;font-family:DM Mono;font-size:12px;letter-spacing:3px'>
        SUBSURFACE OS · GROQ EDITION
      </p>
    </div>""", unsafe_allow_html=True)
    _, c, _ = st.columns([1,0.7,1])
    with c:
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("SINCRONIZAR CON S3"):
            if pwd == "FlowBio2026":
                raw, ok = load_dashboard_data()
                if raw and "dashboard_data" in raw:
                    raw = raw["dashboard_data"]
                st.session_state.all_data = raw or demo_data()
                st.session_state.s3_ok    = ok
                st.session_state.auth     = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    st.stop()


# ══════════════════════════════════════════════════════
# 5. DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════════════
datos_pozos = st.session_state.all_data

# Header
c_title, c_refresh, c_logout = st.columns([5, 1, 1])
with c_title:
    s3_status = "🟢 S3 Live" if st.session_state.get("s3_ok") else "🔵 Demo"
    st.markdown(f"## Command Center <span style='color:#00E5A0'>FlowBio</span> "
                f"<span style='font-size:12px;color:#4A6580;font-family:monospace'>{s3_status}</span>",
                unsafe_allow_html=True)
with c_refresh:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        raw, ok = load_dashboard_data()
        if raw and "dashboard_data" in raw: raw = raw["dashboard_data"]
        st.session_state.all_data = raw or demo_data()
        st.session_state.s3_ok   = ok
        st.rerun()
with c_logout:
    if st.button("🏠 Salir"):
        st.session_state.auth = False; st.rerun()

# Filtro de pozos
lista_pozos = [k for k in datos_pozos.keys() if any(x in k for x in ["Well","Pozo","well","pozo","UKCS","P-"])]
if not lista_pozos:
    lista_pozos = list(datos_pozos.keys())

if not lista_pozos:
    st.error("⚠️ Sin pozos. Ejecuta el pipeline Jupyter primero.")
    st.stop()

pozo_sel = st.selectbox("📍 Selecciona un pozo:", lista_pozos)
d = datos_pozos[pozo_sel]

# ── KPIs — RESTAURADOS CON FALLBACKS CORRECTOS ─────────────
extra_bpd    = d.get("extra_bpd",    d.get("eur",0)/60/30)  
extra_mes    = d.get("extra_mes",    int(extra_bpd*30))
valor_extra  = d.get("valor_extra",  int(extra_mes * d.get("oil_price_usd",74.5)))
fee_mensual  = d.get("fee",          int(extra_bpd * 5.0 * 30))
payback_val  = d.get("payback",      0)
mejora_val   = d.get("mejora",       0)

st.markdown("<br>", unsafe_allow_html=True)
k1,k2,k3,k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-box">
      <p class="kpi-label">CRUDO INCREMENTAL / MES</p>
      <p class="kpi-value">+{extra_mes:,} <span style="font-size:16px">bbls</span></p>
      <p class="kpi-desc">{extra_bpd:.1f} bbl/día · dato real PIML</p>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-box cyan">
      <p class="kpi-label">VALOR EXTRA GENERADO</p>
      <p class="kpi-value" style="color:#22D3EE">${valor_extra:,}</p>
      <p class="kpi-desc">extra_mes × ${d.get('oil_price_usd',74.5)}/bbl</p>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-box amber">
      <p class="kpi-label">SUCCESS FEE MENSUAL</p>
      <p class="kpi-value" style="color:#F59E0B">${fee_mensual:,}</p>
      <p class="kpi-desc">{extra_bpd:.1f} bbl/día × $5 × 30d</p>
    </div>""", unsafe_allow_html=True)
with k4:
    color = "#EF4444" if payback_val > 6 else "#00E5A0"
    st.markdown(f"""<div class="kpi-box {'red' if payback_val > 6 else ''}">
      <p class="kpi-label">PAYBACK</p>
      <p class="kpi-value" style="color:{color}">{payback_val} <span style="font-size:16px">meses</span></p>
      <p class="kpi-desc">Retorno de inversión real</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráfica + Engineering Insights (RESTAURADOS AL 100%) ────────────────────
cl, cr = st.columns([2.3,1.7])

with cl:
    oil_js  = d.get("oil_price_usd", 74.5)
    bopd_js = 500  

    script_grafica = f"""
    <script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script>
    <div id='plot' style='height:400px;background:#0D1520;
         border-radius:12px;border:1px solid rgba(255,255,255,0.05)'></div>
    <script>
    var x      = Array.from({{length:48}},(_,i)=>i);
    var bopd   = {bopd_js};
    var mejora = {mejora_val} / 100;
    var y_base = x.map(i => bopd * Math.exp(-0.005*i));
    var y_flow = x.map(i => i<5 ? y_base[i] : bopd*(1+mejora)*Math.exp(-0.0025*i));
    var t1={{x:x,y:y_base,name:'Status Quo',type:'scatter',
             line:{{color:'#EF4444',dash:'dot',width:2}}}};
    var t2={{x:x,y:y_flow,name:'FlowBio EOR',type:'scatter',
             line:{{color:'#00E5A0',width:3}},
             fill:'tonexty',fillcolor:'rgba(0,229,160,0.08)'}};
    var layout={{
      paper_bgcolor:'transparent',plot_bgcolor:'transparent',
      font:{{color:'#64748B',family:'DM Mono',size:10}},
      margin:{{t:20,b:40,l:55,r:20}},
      xaxis:{{gridcolor:'#152335',title:{{text:'MESES'}}}},
      yaxis:{{gridcolor:'#152335',title:{{text:'BBL/DÍA'}}}},
      showlegend:true,
      legend:{{bgcolor:'rgba(0,0,0,0)',font:{{color:'#8BA8C0'}}}},
    }};
    Plotly.newPlot('plot',[t1,t2],layout,{{responsive:true,displayModeBar:false}});
    </script>"""
    components.html(script_grafica, height=420)

with cr:
    rec     = d.get("recomendacion","—")
    rec_col = "#00E5A0" if rec=="INYECTAR" else "#F59E0B" if rec=="EVALUAR" else "#64748B"
    skin_v  = d.get("skin",0)
    skin_col= "#EF4444" if skin_v>8 else "#F59E0B" if skin_v>3 else "#00E5A0"

    html_ins = f"""
    <div style='background:#0D1520;padding:24px;border-radius:12px;
                border:1px solid rgba(0,229,160,0.2);height:415px;overflow-y:auto'>
      <p style='color:#00E5A0;font-family:DM Mono;font-size:11px;
                letter-spacing:1.5px;margin-bottom:16px'>🧠 ENGINEERING INSIGHTS</p>

      <p style='font-family:DM Mono;font-size:13px;color:#22D3EE;margin-bottom:2px'>
        QUÍMICO: {d.get('quimico','—')}
      </p>
      <p style='font-size:11px;color:#8BA8C0;margin-top:0;margin-bottom:12px'>
        Concentración: {d.get('ppm',0)} ppm · PV: {d.get('vol_pv',0)}
      </p>

      <p style='font-family:DM Mono;font-size:13px;color:#22D3EE;margin-bottom:2px'>
        CAUDAL: {d.get('bwpd',0)} bwpd
      </p>
      <p style='font-size:11px;color:#8BA8C0;margin-top:0;margin-bottom:12px'>
        Límite de fractura: max {d.get('lim_psi',0):,} psi
      </p>

      <p style='font-family:DM Mono;font-size:13px;color:#22D3EE;margin-bottom:2px'>
        WC REDUCTION: {d.get('wc_red',0):.1f}%
      </p>
      <p style='font-size:11px;color:#8BA8C0;margin-top:0;margin-bottom:12px'>
        Reducción de corte de agua estimada
      </p>

      <hr style='opacity:0.1;margin:14px 0'>

      <p style='color:#64748B;font-family:DM Mono;font-size:10px;letter-spacing:1px'>
        FACTOR SKIN:
      </p>
      <p style='color:{skin_col};font-family:Syne;font-size:28px;
                font-weight:800;margin:2px 0'>S = {skin_v:.2f}</p>

      <p style='color:#64748B;font-family:DM Mono;font-size:10px;
                letter-spacing:1px;margin-top:12px'>RECOMENDACIÓN PIML:</p>
      <p style='color:{rec_col};font-family:DM Mono;font-size:13px;
                font-weight:500'>{rec}</p>

      <hr style='opacity:0.1;margin:14px 0'>

      <p style='color:#64748B;font-family:DM Mono;font-size:10px'>EUR ACUMULADO (5 años):</p>
      <p style='color:#00E5A0;font-family:Syne;font-size:26px;font-weight:800;margin:0'>
        {d.get('eur',0):,} <span style='font-size:13px;color:#64748B'>bbls</span>
      </p>
    </div>"""
    st.markdown(html_ins, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "📥 DESCARGAR REPORTE PDF",
        data=generate_pdf(pozo_sel, d),
        file_name=f"FlowBio_Report_{pozo_sel.replace(' ','_')}.pdf",
        mime="application/pdf",
    )
