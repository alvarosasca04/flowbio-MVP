"""
FlowBio EOR Agentic Pipeline — Unificado
=========================================
Combina:
  • agente_eor.py  → carga de .env, lectura S3, LangChain + ChatGroq
  • main.py        → motor PIML, pipeline multi-agente, escritura S3

Uso:
  python flowbio_pipeline.py
"""

from __future__ import annotations
import os, io, json, math, warnings, pathlib
from typing import Any, Optional
from datetime import datetime

import boto3          # type: ignore
import pandas as pd   # type: ignore
import numpy as np    # type: ignore
from langchain_groq import ChatGroq   # type: ignore
from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# 1. CARGA DE CREDENCIALES (.env con soporte BOM y rutas relativas/absolutas)
# ══════════════════════════════════════════════════════════════════════════════
def _cargar_env() -> None:
    """Lee el .env del directorio del script eliminando el BOM de Windows."""
    ruta = pathlib.Path(__file__).parent / ".env"
    if not ruta.exists():
        raise FileNotFoundError(f".env no encontrado en {ruta}")
    with open(ruta, "r", encoding="utf-8-sig") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ[clave.strip()] = valor.strip()

_cargar_env()

# Variables de entorno obligatorias
GROQ_API_KEY  = os.environ["GROQ_API_KEY"]
AWS_KEY_ID    = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET    = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION    = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
BUCKET        = os.environ["S3_BUCKET_NAME"]
S3_JSON_KEY   = os.getenv("S3_OBJECT_KEY", "raw-datak-repository/movilidad.json")

# Constantes de negocio
POZOS_A_SIMULAR  = 100
SUCCESS_FEE_USD  = 5.0
OPEX_BASE_USD    = 18.5
OIL_PRICE_USD    = 74.5
POLYMER_COST_KG  = 2.8
AGENTS_PREFIX    = "agentes/"
GROQ_MODEL       = "llama-3.3-70b-versatile"   # modelo de agente_eor (más capaz)

print(f"✅ Credenciales cargadas — cuenta terminada en ...{AWS_KEY_ID[-4:]}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. CLIENTES GLOBALES
# ══════════════════════════════════════════════════════════════════════════════
s3: Any = boto3.client(
    "s3",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET,
    region_name=AWS_REGION,
)

llm: Any = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
)

# ══════════════════════════════════════════════════════════════════════════════
# 3. MOTOR FÍSICO PIML  (de main.py)
# ══════════════════════════════════════════════════════════════════════════════
class PIMLEngine:
    """Physics-Informed ML Engine para cálculos reológicos y de reservorio."""

    def __init__(self, T: float = 85, S: float = 45000,
                 C: float = 0.8, fluid: str = "Na-CMC") -> None:
        self.T = T; self.S = S; self.C = C; self.fluid = fluid
        if fluid == "Na-CMC":
            self.n = float(np.clip(0.65 - T/1200 - S/600000 - C*0.08, 0.25, 0.90))
            self.K = float(max(30, 160 - T*0.75 + S*0.001 + C*12))
        else:  # HPAM
            self.n = float(np.clip(0.78 - T/900  - S/500000 - C*0.05, 0.25, 0.90))
            self.K = float(max(30, 200 - T*0.90  + S*0.0008 + C*10))

    def visc(self) -> float:
        return float(np.clip(self.K * (10.0 ** (self.n - 1)), 1.0, 5000.0))

    def mob(self, visc_oil: float = 85.0) -> float:
        """Relación de movilidad M = λ_agua / λ_crudo."""
        return float(np.clip((0.4 / self.visc()) / (0.8 / visc_oil), 0.05, 8.0))

    def skin(self, K_orig: float, K_dam: float) -> float:
        return float((K_orig / K_dam - 1) * math.log(8.0 / 0.35)) if K_dam > 0 else 0.0

    def calcular_movilidad_directa(self, visc_agua: float, visc_crudo: float) -> dict[str, Any]:
        """Cálculo directo desde viscosidades (flujo de agente_eor)."""
        if visc_agua <= 0:
            return {"error": "viscosidad_agua debe ser > 0"}
        M = visc_crudo / visc_agua
        return {
            "movilidad": round(M, 4),
            "favorable": M <= 1,
            "recomendacion": (
                "Frente de barrido estable (M ≤ 1). No se requiere tratamiento urgente."
                if M <= 1 else
                f"Digitación viscosa severa (M={M:.2f} > 1). Inyectar biopolímero "
                f"({'Na-CMC' if self.fluid == 'Na-CMC' else 'HPAM'}) para aumentar viscosidad del fluido desplazante."
            ),
        }

    def get_projection(self, base_bpd: float, skin_factor: float,
                       meses: int = 48) -> list[dict[str, float]]:
        """Curva DCA: P50 con FlowBio vs P10 sin tratamiento."""
        resultado = []
        for m in range(1, meses + 1):
            noise = float(np.random.normal(0, 3.5))
            p50 = round(max(base_bpd * math.exp(-(0.025 + skin_factor*0.001)*m) + noise, 10.0), 2)
            p10 = round(max(base_bpd * math.exp(-0.08 * m), 5.0), 2)
            resultado.append({
                "mes": m, "P50": p50, "P10": p10,
                "P90": round(p50 * 1.15, 2),
                "mob": round(1.0 / (1.0 + 0.3 * math.log(m + 1)), 3),
            })
        return resultado

# ══════════════════════════════════════════════════════════════════════════════
# 4. HELPERS S3
# ══════════════════════════════════════════════════════════════════════════════
def s3_read_json(key: str) -> dict[str, Any]:
    body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode("utf-8")
    return json.loads(body)

def s3_read_csv(key: str) -> pd.DataFrame:
    return pd.read_csv(
        io.BytesIO(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()),
        low_memory=False,
    )

def s3_write(key: str, body: str) -> None:
    s3.put_object(Bucket=BUCKET, Key=key, Body=body)

def s3_latest(prefix_filter: str) -> Optional[str]:
    r = s3.list_objects_v2(Bucket=BUCKET, Prefix=AGENTS_PREFIX)
    archivos = [o for o in r.get("Contents", []) if prefix_filter in o["Key"]]
    archivos.sort(key=lambda x: x["LastModified"])
    return archivos[-1]["Key"] if archivos else None

# ══════════════════════════════════════════════════════════════════════════════
# 5. HERRAMIENTAS DE LOS AGENTES
# ══════════════════════════════════════════════════════════════════════════════

def tool_data_engineer(file_key: Optional[str] = None) -> str:
    """
    AGENTE 1 — Ingeniero de Datos
    Lee el Excel de pozos desde S3 y genera un CSV limpio.
    """
    try:
        # Buscar el Excel en el bucket
        r = s3.list_objects_v2(Bucket=BUCKET, Prefix="raw-datak-repository/")
        excels = [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith(".xlsx")]
        if not excels:
            return json.dumps({"status": "error", "error": "No se encontró ningún .xlsx en raw-datak-repository/"})

        target = file_key or excels[0]
        raw = s3.get_object(Bucket=BUCKET, Key=target)["Body"].read()

        df = pd.read_excel(io.BytesIO(raw)).dropna(how="all").reset_index(drop=True)
        df.columns = df.columns.str.strip()

        # Limitar a POZOS_A_SIMULAR filas
        df = df.head(POZOS_A_SIMULAR)

        out_key = f"{AGENTS_PREFIX}agent1_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        s3_write(out_key, buf.getvalue())

        return json.dumps({
            "status": "success", "source": target,
            "output_key": out_key, "pozos": len(df),
            "columnas": list(df.columns[:8]),
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def tool_movilidad_s3() -> str:
    """
    AGENTE 1b — Lector de movilidad (flujo de agente_eor)
    Lee raw-datak-repository/movilidad.json y calcula M directamente.
    """
    try:
        datos = s3_read_json(S3_JSON_KEY)
        va = datos.get("viscosidad_agua")
        vc = datos.get("viscosidad_crudo")
        if va is None or vc is None:
            return json.dumps({"status": "missing_data",
                               "message": "Faltan viscosidad_agua o viscosidad_crudo en el JSON"})
        eng = PIMLEngine()
        resultado = eng.calcular_movilidad_directa(float(va), float(vc))
        resultado.update({
            "pozo": datos.get("pozo", "desconocido"),
            "yacimiento": datos.get("yacimiento", "desconocido"),
            "viscosidad_agua": va, "viscosidad_crudo": vc,
        })
        return json.dumps(resultado, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def tool_piml_simulator(clean_key: Optional[str] = None) -> str:
    """
    AGENTE 2 — Simulador PIML
    Corre el motor físico sobre cada pozo del CSV limpio.
    """
    try:
        key = clean_key or s3_latest("agent1_clean")
        if not key:
            return json.dumps({"status": "error", "error": "No se encontró agent1_clean en S3"})

        df = s3_read_csv(key)
        rows = []

        for i, row in enumerate(df.to_dict(orient="records"), start=1):
            nombre = str(row.get("well_name", f"Pozo_{i}")).strip()
            if nombre.lower() in ("nan", ""):
                nombre = f"Pozo_No_ID"
            nombre = f"{nombre} (#{i})"

            # Producción base
            bpd = 350.0
            for col in df.columns:
                if any(k in col.lower() for k in ["bopd", "rate", "prod", "oil", "q_"]):
                    try:
                        v = float(row[col])
                        if not pd.isna(v) and v > 0:
                            bpd = v; break
                    except Exception:
                        pass

            T    = float(row.get("temperatura", 85.0)) if "temperatura" in df.columns else 85.0
            perm = float(row.get("permeabilidad", 150.0)) if "permeabilidad" in df.columns else 150.0

            eng  = PIMLEngine(T=T)
            sk   = eng.skin(perm, perm * 0.25)
            M    = eng.mob()
            proj = eng.get_projection(base_bpd=bpd, skin_factor=sk)

            p50_prom    = sum(r["P50"] for r in proj) / len(proj)
            p10_prom    = sum(r["P10"] for r in proj) / len(proj)
            bbls_extra  = max(0.0, p50_prom - p10_prom) * 30
            valor_extra = bbls_extra * OIL_PRICE_USD
            fee         = valor_extra * (SUCCESS_FEE_USD / OIL_PRICE_USD)
            eur         = sum(r["P50"] for r in proj) * 30

            rows.append({
                "pozo": nombre, "T": round(T, 1), "permeabilidad": round(perm, 1),
                "skin": round(sk, 3), "M_ratio": round(M, 3),
                "proyeccion": json.dumps(proj),
                "barriles_mes": round(bbls_extra, 1),
                "valor_extra_usd": round(valor_extra, 2),
                "fee_usd": round(fee, 2),
                "payback_meses": round(3.0 if fee > 0 else 0.0, 1),
                "eur_bbls": round(eur, 0),
            })

        out_key = f"{AGENTS_PREFIX}agent3_piml_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        buf = io.StringIO()
        pd.DataFrame(rows).to_csv(buf, index=False)
        s3_write(out_key, buf.getvalue())

        return json.dumps({
            "status": "success", "agent3_key": out_key,
            "pozos_procesados": len(rows),
            "bbls_extra_total_mes": round(sum(r["barriles_mes"] for r in rows), 0),
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def tool_executive_report(agent3_key: Optional[str] = None) -> str:
    """
    AGENTE 3 — Reporte Ejecutivo
    Consolida el CSV de PIML en dashboard_data.json y lo sube a S3.
    """
    try:
        key = agent3_key or s3_latest("agent3_piml")
        if not key:
            return json.dumps({"status": "error", "error": "No se encontró agent3_piml en S3"})

        df = s3_read_csv(key)
        dashboard: dict[str, Any] = {}

        for _, row in df.iterrows():
            nombre = str(row["pozo"])
            dashboard[nombre] = {
                "proyeccion": json.loads(row["proyeccion"]),
                "kpis": {
                    "barriles_mes":   float(row["barriles_mes"]),
                    "valor_extra_usd": float(row["valor_extra_usd"]),
                    "fee_usd":         float(row["fee_usd"]),
                    "payback_meses":   float(row["payback_meses"]),
                    "eur_bbls":        float(row["eur_bbls"]),
                    "M_ratio":         float(row["M_ratio"]),
                },
            }

        # Resumen ejecutivo
        total_bbls  = df["barriles_mes"].sum()
        total_valor = df["valor_extra_usd"].sum()
        total_fee   = df["fee_usd"].sum()
        avg_M       = df["M_ratio"].mean()

        resumen = {
            "_resumen": {
                "pozos_analizados":    len(df),
                "total_bbls_extra_mes": round(total_bbls, 0),
                "ingreso_operadora_usd": round(total_valor, 2),
                "flowbio_fee_usd":       round(total_fee, 2),
                "M_promedio":            round(avg_M, 3),
                "timestamp":             datetime.now().isoformat(),
            },
            **dashboard,
        }

        s3_write(f"{AGENTS_PREFIX}dashboard_data.json",
                 json.dumps(resumen, ensure_ascii=False, indent=2))

        print(f"   ✅ {len(df)} pozos guardados en dashboard_data.json")
        return json.dumps({"status": "success", "pozos": len(df),
                           "resumen": resumen["_resumen"]})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})

# ══════════════════════════════════════════════════════════════════════════════
# 6. ORQUESTADOR CON LangChain + ChatGroq  (de agente_eor.py)
# ══════════════════════════════════════════════════════════════════════════════

TOOL_MAP = {
    "tool_data_engineer":    tool_data_engineer,
    "tool_movilidad_s3":     tool_movilidad_s3,
    "tool_piml_simulator":   tool_piml_simulator,
    "tool_executive_report": tool_executive_report,
}

def ejecutar_agente(
    nombre: str,
    rol_sistema: str,
    tarea: str,
    nombre_herramienta: str,
    contexto: str = "",
) -> str:
    """
    Ejecuta un agente LangChain que:
      1. Razona sobre la tarea con el LLM (ChatGroq)
      2. Llama a su herramienta Python
      3. Devuelve el análisis final
    """
    print(f"\n{'─'*60}")
    print(f"🤖  {nombre}")
    print(f"{'─'*60}")

    # Paso 1: el LLM describe qué va a hacer
    mensajes = [
        SystemMessage(content=rol_sistema),
        HumanMessage(content=(
            f"CONTEXTO DEL PIPELINE:\n{contexto[-600:]}\n\n"
            f"TAREA: {tarea}\n\n"
            f"Describe en 2 oraciones qué harás y por qué es crítico para el EOR."
        )),
    ]
    intencion = llm.invoke(mensajes).content
    print(f"   💬 {intencion[:200]}…")

    # Paso 2: ejecutar herramienta real
    print(f"   🔧 Ejecutando {nombre_herramienta}…")
    resultado_raw = TOOL_MAP[nombre_herramienta]()
    resultado = json.loads(resultado_raw)

    if resultado.get("status") == "error":
        print(f"   ❌ Error: {resultado.get('error')}")
        return resultado_raw

    print(f"   ✅ Herramienta exitosa")

    # Paso 3: el LLM interpreta el resultado
    mensajes_final = [
        SystemMessage(content=rol_sistema),
        HumanMessage(content=(
            f"La herramienta devolvió:\n{json.dumps(resultado, ensure_ascii=False, indent=2)[:800]}\n\n"
            f"Resume el hallazgo en 2 oraciones técnicas para el siguiente agente."
        )),
    ]
    analisis = llm.invoke(mensajes_final).content
    print(f"   📊 {analisis[:250]}…")

    return json.dumps({
        "agente": nombre,
        "herramienta": nombre_herramienta,
        "resultado": resultado,
        "analisis_llm": analisis,
    }, ensure_ascii=False)

# ══════════════════════════════════════════════════════════════════════════════
# 7. PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    print("\n" + "═"*60)
    print("   FlowBio EOR Agentic Pipeline — Unificado")
    print(f"   Bucket : {BUCKET}")
    print(f"   Modelo : {GROQ_MODEL}")
    print("═"*60)

    contexto = ""

    # ── Agente 1a: Lector de movilidad (flujo agente_eor) ──────────────────
    r1b = ejecutar_agente(
        nombre="Agente 1 — Movilidad S3 (agente_eor)",
        rol_sistema=(
            "Eres un especialista en ingeniería de yacimientos EOR. "
            "Tu tarea es leer datos de viscosidad desde S3 y calcular "
            "la relación de movilidad M para diagnóstico inicial."
        ),
        tarea="Lee movilidad.json de S3 y calcula la relación de movilidad M.",
        nombre_herramienta="tool_movilidad_s3",
        contexto=contexto,
    )
    contexto += f"\n[Movilidad S3]: {r1b[:300]}"

    # ── Agente 1b: Ingeniero de Datos ──────────────────────────────────────
    r1 = ejecutar_agente(
        nombre="Agente 1b — Ingeniero de Datos (main)",
        rol_sistema=(
            "Eres un Ingeniero de Datos para proyectos EOR offshore. "
            "Limpias y normalizas datos de producción de pozos para "
            "alimentar el motor de simulación PIML."
        ),
        tarea="Lee el Excel de pozos desde S3, limpia los datos y guarda el CSV en el Data Lake.",
        nombre_herramienta="tool_data_engineer",
        contexto=contexto,
    )
    contexto += f"\n[DataEng]: {r1[:300]}"

    # ── Agente 2: Simulador PIML ────────────────────────────────────────────
    r2 = ejecutar_agente(
        nombre="Agente 2 — Simulador PIML",
        rol_sistema=(
            "Eres un Físico de Reservorios especialista en EOR. "
            "Ejecutas el motor PIML para calcular curvas de declinación, "
            "relaciones de movilidad y proyecciones de barriles incrementales."
        ),
        tarea="Corre el motor PIML sobre el CSV limpio. Calcula proyecciones DCA y KPIs financieros por pozo.",
        nombre_herramienta="tool_piml_simulator",
        contexto=contexto,
    )
    contexto += f"\n[PIML]: {r2[:300]}"

    # ── Agente 3: Reporte Ejecutivo ─────────────────────────────────────────
    r3 = ejecutar_agente(
        nombre="Agente 3 — Reporte Ejecutivo (CFO)",
        rol_sistema=(
            "Eres el CFO y Director de Operaciones de FlowBio. "
            "Consolidas los resultados técnicos en un reporte ejecutivo "
            "con KPIs financieros para presentar a operadoras petroleras."
        ),
        tarea="Consolida el CSV de PIML en dashboard_data.json y súbelo a S3.",
        nombre_herramienta="tool_executive_report",
        contexto=contexto,
    )

    # ── Resumen final ───────────────────────────────────────────────────────
    try:
        resumen_data = json.loads(r3)
        res = resumen_data.get("resultado", {}).get("resumen", {})
        print("\n" + "═"*60)
        print("   PIPELINE COMPLETADO — RESUMEN EJECUTIVO")
        print("═"*60)
        print(f"   Pozos analizados       : {res.get('pozos_analizados', '—')}")
        print(f"   Crudo extra (mes)      : {res.get('total_bbls_extra_mes', '—'):>10,.0f} bbls")
        print(f"   Ingreso operadora      : ${res.get('ingreso_operadora_usd', 0):>12,.2f} USD")
        print(f"   FlowBio success fee    : ${res.get('flowbio_fee_usd', 0):>12,.2f} USD")
        print(f"   Movilidad promedio (M) : {res.get('M_promedio', '—')}")
        print(f"   dashboard_data.json    : s3://{BUCKET}/{AGENTS_PREFIX}dashboard_data.json")
        print("═"*60)
    except Exception:
        print("\n✅ Pipeline completado. Revisa S3 para los resultados.")


if __name__ == "__main__":
    main()
