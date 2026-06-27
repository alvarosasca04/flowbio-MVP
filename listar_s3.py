import boto3, os
from dotenv import load_dotenv

load_dotenv('.env')

s3 = boto3.client("s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-2")

r = s3.list_objects_v2(
    Bucket="flowbio-data-lake-v2-627807503177-us-east-2-an",
    Prefix="raw-datak-repository/")

archivos = r.get("Contents", [])
print(f"Total archivos: {len(archivos)}")
for obj in archivos:
    print(f"  {obj['Key']}  ({obj['Size']:,} bytes)")