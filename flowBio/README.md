# FlowBio Intelligence: Subsurface Diagnostic Console

Dashboard Streamlit para diagnóstico de pozos maduros y optimización EOR con Na-CMC.

## Correr local (sin Docker)

```bash
pip install -r requirements.txt
streamlit run app.py
```
Abre: http://localhost:8501

## Correr con Docker

```bash
# Build
docker build -t flowbio-console .

# Run
docker run -p 8501:8501 flowbio-console
```
Abre: http://localhost:8501

## Deploy en Streamlit Cloud (gratis)

1. Sube los 3 archivos a un repositorio GitHub
2. Ve a share.streamlit.io → New app
3. Conecta el repo, selecciona `app.py`
4. Deploy → URL pública instantánea

## Módulos del motor PIML

| Módulo | Descripción |
|--------|-------------|
| `PIMLEngine` | Power Law, Skin Factor, FPI, estabilidad térmica |
| `TEAModule` | Success Fee $5/bbl, ROI, curva de producción |
| `plot_*` | Gauge skin, reología, producción, OPEX |
