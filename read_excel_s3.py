import boto3
import os
from dotenv import load_dotenv
from io import BytesIO
import openpyxl

load_dotenv('D:\\mis proyectos\\.env', override=True)

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)

bucket_name = os.getenv("S3_BUCKET_NAME")

try:
    # Listar todos los archivos Excel
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="raw-datak-repository/")
    excel_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.xlsx')]

    
    print(f"Archivos Excel encontrados: {len(excel_files)}\n")
    
    if excel_files:
        # Leer el primer archivo Excel
        first_excel = excel_files[0]
        print(f"Leyendo: {first_excel}")
        
        obj = s3.get_object(Bucket=bucket_name, Key=first_excel)
        excel_content = obj['Body'].read()
        
        # Cargar el libro
        wb = openpyxl.load_workbook(BytesIO(excel_content))
        ws = wb.active
        
        print(f"Hoja activa: {ws.title}")
        print(f"Dimensiones: {ws.dimensions}")
        print("\nPrimeras 5 filas:")
        
        for i, row in enumerate(ws.iter_rows(max_row=5, values_only=True), 1):
            print(f"  Fila {i}: {row[:5]}")  # Mostrar solo las primeras 5 columnas
            
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
