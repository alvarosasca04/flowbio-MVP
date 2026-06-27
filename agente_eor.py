from __future__ import annotations
import os
import json
from typing import Any, Dict
import boto3  # type: ignore
from dotenv import load_dotenv  # type: ignore
from langchain_groq import ChatGroq  # type: ignore

# Cargar explícitamente desde la ruta del proyecto
# pyright: reportMissingImports=false, reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false
import pathlib
env_path = pathlib.Path(__file__).parent / '.env'

# Leer el archivo .env manualmente
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig elimina el BOM
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Verificar que GROQ_API_KEY se cargó
if not os.getenv("GROQ_API_KEY"):
    print(f"ERROR: GROQ_API_KEY no se cargó")
    exit(1)


def leer_datos_s3(bucket_name: str, object_key: str) -> Dict[str, Any]:
    """Lee un JSON desde S3 y devuelve sus datos como diccionario."""
    s3: Any = boto3.client(  # type: ignore
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )
    response = s3.get_object(Bucket=bucket_name, Key=object_key)  # type: ignore
    body = response["Body"].read().decode("utf-8")  # type: ignore
    return json.loads(body)  # type: ignore


def calcular_relacion_movilidad(viscosidad_agua: float, viscosidad_crudo: float) -> str:
    """Útil para calcular la relación de movilidad (M) en un yacimiento.
    Requiere la viscosidad del agua (fluido desplazante) y del crudo (fluido desplazado) en cP."""
    if viscosidad_agua == 0:
        return "Error: La viscosidad del agua no puede ser cero."

    movilidad = viscosidad_crudo / viscosidad_agua

    analisis = f"La relación de movilidad calculada es {movilidad:.2f}. "
    if movilidad <= 1:
        analisis += "Es un escenario favorable (M <= 1), el frente de barrido será estable."
    else:
        analisis += "Es un escenario desfavorable (M > 1), alto riesgo de digitación viscosa. Se recomienda inyección de biopolímero para aumentar la viscosidad del agua."

    return analisis


llm: Any = ChatGroq(  # type: ignore
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


def run_agent(prompt: str) -> str:
    bucket_name = os.getenv("S3_BUCKET_NAME")
    object_key = os.getenv("S3_OBJECT_KEY")

    # Inicializar variables para evitar referencias no enlazadas
    pozo = None
    yacimiento = None
    viscosidad_agua = None
    viscosidad_crudo = None

    if bucket_name and object_key:
        try:
            datos = leer_datos_s3(bucket_name, object_key)
            viscosidad_agua = datos.get("viscosidad_agua")
            viscosidad_crudo = datos.get("viscosidad_crudo")
            pozo = datos.get("pozo", "desconocido")
            yacimiento = datos.get("yacimiento", "desconocido")
            
            if viscosidad_agua is not None and viscosidad_crudo is not None:
                # Calcular directamente sin pedir al usuario

                # Construir prompt instructivo pidiendo respuesta en JSON
                prompt = (
                    f"Eres un asistente de ingeniería de yacimientos. Devuelve SOLO un JSON con las claves: pozo, yacimiento, viscosidad_agua, viscosidad_crudo, movilidad, recommendation, notes.\n"
                    f"Datos:\n- pozo: {pozo}\n- yacimiento: {yacimiento}\n- viscosidad_agua: {viscosidad_agua}\n- viscosidad_crudo: {viscosidad_crudo}\n\n"
                    f"Calcula la relación de movilidad (movilidad = viscosidad_crudo / viscosidad_agua) y da una recomendación breve en español.\n"
                    f"Si no puedes calcular, indica error en el campo 'notes'.\n"
                )
            else:
                # Datos incompletos: solicitar viscosidades al usuario
                return json.dumps({
                    "pozo": datos.get("pozo", "desconocido"),
                    "yacimiento": datos.get("yacimiento", "desconocido"),
                    "missing_data": True,
                    "message": "Faltan viscosidades en S3. Proporciona 'viscosidad_agua' y 'viscosidad_crudo' en cP."
                }, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": f"No pude leer el archivo de S3: {exc}"}, ensure_ascii=False)
    # Intentar invocar el LLM y parsear JSON de salida
    try:
        respuesta = llm.invoke(prompt)  # type: ignore
        texto = getattr(respuesta, "content", str(respuesta))  # type: ignore

        # Intentar parsear JSON en la respuesta
        try:
            payload = json.loads(texto)
            # Asegurar campos mínimos
            payload.setdefault("pozo", pozo or "desconocido")
            payload.setdefault("yacimiento", yacimiento or "desconocido")
            return json.dumps(payload, ensure_ascii=False)
        except Exception:
            # Si no es JSON, devolver la respuesta del modelo dentro de 'notes'
            movilidad = None
            if viscosidad_agua is not None and viscosidad_crudo is not None and float(viscosidad_agua) != 0:
                movilidad = float(viscosidad_crudo) / float(viscosidad_agua)
            out = {
                "pozo": pozo or "desconocido",
                "yacimiento": yacimiento or "desconocido",
                "viscosidad_agua": viscosidad_agua,
                "viscosidad_crudo": viscosidad_crudo,
                "movilidad": movilidad,
                "recommendation": None,
                "notes": str(texto),
            }
            return json.dumps(out, ensure_ascii=False)
    except Exception as exc:
        # Devolver error genérico
        return json.dumps({"error": f"Invocación fallida: {type(exc).__name__} - {exc}"}, ensure_ascii=False)


if __name__ == "__main__":
    print("Iniciando simulación del agente...\n")
    prompt_usuario = "¿Cuál es la relación de movilidad y qué sugieres para optimizar la extracción?"
    respuesta = run_agent(prompt_usuario)
    print("\n--- RESPUESTA FINAL ---")
    print(respuesta)
