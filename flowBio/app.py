import streamlit as st
import boto3
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Configuración de la página
st.set_page_config(page_title="FlowBio Intelligence", layout="wide", initial_sidebar_state="expanded")

# Título principal
st.title("🧬 FlowBio Intelligence - PIML Dashboard")
st.markdown("**Análisis Predictivo de Inyección Mejorada (EOR) - Na-CMC**")
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
        # Mismo encoding que tu SageMaker
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='latin-1', low_memory=False)
        # Limpiar columnas (por si acaso)
        df.columns = df.columns.str.replace('ï»¿', '').str.replace('Ã¯Â»Â¿', '')
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
        'pozo': ['Demo-Pozo-1', 'Demo-Pozo-2', 'Demo-Pozo-3', 'Demo-Pozo-4', 'Demo-Pozo-5'],
        'skin': [8.5, 12.3, 5.1, 15.8, 3.2],
        'mejora_pct': [12.5, 18.3, 8.5, 22.1, 5.3],
        'ahorro_anual': [45000, 65000, 28000, 78000, 15000],
        'estado': ['ESTABLE', 'CRÍTICO', 'ESTABLE', 'CRÍTICO', 'ESTABLE']
    })

# CONFIGURACIÓN - VALORES REALES
nombre_bucket = "flowbio-data-lake-v2-627807503177-us-east-2-an"
ruta_archivo = "resultados_piml.csv"  # SageMaker debe guardar aquí

# Cargar datos
df = cargar_csv_s3(nombre_bucket, ruta_archivo)

if df is not None and not df.empty:
    # Pestañas del dashboard
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Datos", "📈 Gráficos", "🎯 Top Candidatos", "📋 Información"])
    
    with tab1:
        st.subheader("Tabla de Resultados PIML")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Botón para descargar CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name="resultados_flowbio_piml.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Visualización de Métricas PIML")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico: Distribución de Skin Factor
            if 'skin' in df.columns:
                fig1 = px.histogram(df, x='skin', nbins=20, 
                                   title='Distribución de Daño de Formación (Skin)',
                                   labels={'skin': 'Skin Factor', 'count': 'Cantidad de Pozos'})
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Gráfico: Mejora EOR
            if 'mejora_pct' in df.columns:
                fig2 = px.histogram(df, x='mejora_pct', nbins=20,
                                   title='Distribución de Mejora EOR (%)',
                                   labels={'mejora_pct': 'Mejora (%)', 'count': 'Cantidad de Pozos'})
                st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.subheader("Top 10 Candidatos - Mayor Ahorro Anual")
        
        if 'ahorro_anual' in df.columns and 'pozo' in df.columns:
            top10 = df.nlargest(10, 'ahorro_anual')
            fig3 = px.bar(top10, x='ahorro_anual', y='pozo', orientation='h',
                         title='Top 10 Pozos - Ahorro OPEX Anual (USD)',
                         labels={'ahorro_anual': 'Ahorro Anual (USD)', 'pozo': 'Pozo'})
            fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
            
            st.write("**Detalles:**")
            st.dataframe(top10[['pozo', 'skin', 'mejora_pct', 'ahorro_anual', 'estado']], 
                        use_container_width=True)
    
    with tab4:
        st.subheader("Resumen Ejecutivo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📌 Total Pozos", len(df))
        with col2:
            st.metric("💰 Ahorro Promedio", f"${df['ahorro_anual'].mean():,.0f}")
        with col3:
            st.metric("📈 Mejora EOR Prom.", f"{df['mejora_pct'].mean():.1f}%")
        with col4:
            estado_critico = len(df[df['estado'] == 'CRÍTICO'])
            st.metric("⚠️ Pozos Críticos", estado_critico)
        
        st.markdown("---")
        st.write("**Columnas del dataset:**")
        st.write(df.dtypes)
        
        st.write("**Estadísticas Descriptivas:**")
        st.dataframe(df.describe(), use_container_width=True)
else:
    st.error("❌ No se pudo cargar ningún dato")
