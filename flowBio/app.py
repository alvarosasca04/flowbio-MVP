import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="FlowBio Intelligence", layout="wide", initial_sidebar_state="expanded")

# Título principal
st.title("📊 FlowBio Intelligence Dashboard")
st.markdown("---")

# Función para conectar a S3
@st.cache_resource
def conectar_s3():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets["aws"]["AWS_DEFAULT_REGION"]
        )
        return s3_client
    except Exception as e:
        st.error(f"❌ Error de conexión AWS: {e}")
        return None

# Función para cargar CSV desde S3
@st.cache_data(ttl=3600)
def cargar_csv_s3(nombre_bucket, ruta_archivo):
    s3 = conectar_s3()
    if s3 is None:
        return None
    
    try:
        obj = s3.get_object(Bucket=nombre_bucket, Key=ruta_archivo)
        df = pd.read_csv(obj['Body'])
        st.success(f"✅ Datos cargados desde S3 a las {datetime.now().strftime('%H:%M:%S')}")
        return df
    except s3.exceptions.NoSuchKey:
        st.warning(f"⚠️ Archivo no encontrado en S3: {ruta_archivo}")
        return crear_datos_demo()
    except Exception as e:
        st.error(f"❌ Error al leer S3: {e}")
        return crear_datos_demo()

# Función para crear datos de demostración
def crear_datos_demo():
    st.info("📌 Usando datos de demostración (modo fallback)")
    return pd.DataFrame({
        'fecha': pd.date_range('2026-01-01', periods=30),
        'valor': [100 + i*2.5 for i in range(30)],
        'categoria': ['Demo'] * 30
    })

# CONFIGURACIÓN - CAMBIA ESTOS VALORES
nombre_bucket = "flowbio-data-lake-v2"  # Tu nombre de bucket S3
ruta_archivo = "resultados/datos.csv"   # Ruta exacta donde guarda SageMaker el CSV

# Cargar datos
df = cargar_csv_s3(nombre_bucket, ruta_archivo)

if df is not None:
    # Pestañas del dashboard
    tab1, tab2, tab3 = st.tabs(["📊 Datos", "📈 Gráficos", "📋 Información"])
    
    with tab1:
        st.subheader("Tabla de Datos")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Botón para descargar CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name="datos_flowbio.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Visualización de Datos")
        
        # Detectar columnas numéricas
        columnas_numericas = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(columnas_numericas) > 0:
            col_y = st.selectbox("Selecciona columna para graficar:", columnas_numericas)
            
            # Gráfico de línea
            fig = px.line(df, y=col_y, markers=True, title=f"Evolución de {col_y}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay columnas numéricas para graficar")
    
    with tab3:
        st.subheader("Información del Dataset")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📌 Total de Registros", len(df))
        with col2:
            st.metric("📋 Columnas", len(df.columns))
        with col3:
            st.metric("💾 Tamaño (MB)", round(df.memory_usage(deep=True).sum() / 1024**2, 2))
        
        st.write("**Columnas del dataset:**")
        st.write(df.dtypes)
else:
    st.error("❌ No se pudo cargar ningún dato")
