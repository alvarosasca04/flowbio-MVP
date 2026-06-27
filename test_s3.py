import boto3  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore

load_dotenv('D:\\mis proyectos\\.env', override=True)

print("Variables cargadas:")
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
print(f"AWS_ACCESS_KEY_ID: {aws_key[:10] if aws_key else 'NOT SET'}...")
print(f"AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION')}")
print(f"S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME')}")
print(f"S3_OBJECT_KEY: {os.getenv('S3_OBJECT_KEY')}\n")

s3 = boto3.client(  # type: ignore
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)

bucket_name = os.getenv("S3_BUCKET_NAME")
prefix = "raw-datak-repository/"

try:
    print(f"Listando objetos en s3://{bucket_name}/{prefix}")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=50)  # type: ignore
    
    if "Contents" in response:  # type: ignore
        print(f"\nObjetos encontrados:")
        for obj in response["Contents"]:  # type: ignore
            print(f"  - {obj['Key']}")  # type: ignore    else:
        print("  (no hay objetos en esa ruta)")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
