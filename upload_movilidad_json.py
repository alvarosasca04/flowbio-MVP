import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv('D:\\mis proyectos\\.env', override=True)

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)

bucket_name = os.getenv("S3_BUCKET_NAME")
object_key = "raw-datak-repository/movilidad.json"

datos = {
    "viscosidad_agua": 1.5,
    "viscosidad_crudo": 120,
    "pozo": "Pozo Maduro",
    "yacimiento": "Arenal Profundo",
    "fecha": "2026-06-27"
}

json_content = json.dumps(datos, indent=2)

try:
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=json_content)
    print(f"✓ Archivo {object_key} creado y subido a S3")
    print(f"Contenido:\n{json_content}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
