# Decision Lab · Django

Primera fase de la migración profesional de la plataforma de Teoría de Colas. La aplicación Django convive con Streamlit y reutiliza `queue_core.py` e `interpretation_core.py` desde la raíz del repositorio.

## Stack
- Django 6.1.1
- Python 3.12–3.14 (referencia: 3.14)
- Django Templates + CSS/JavaScript
- Plotly.js para gráficos dinámicos
- SQLite en desarrollo

## Ejecutar localmente
```bash
cd django_app
python -m venv .venv
# activar entorno
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`.

## Alcance de esta fase
- Home y sidebar profesional.
- M/M/1 y M/M/s usando el mismo motor analítico que Streamlit.
- API JSON para cálculo y simulación.
- Simulación de eventos discretos con múltiples réplicas.
- Gráficos dinámicos: espera analítica vs simulada, utilización y evolución de cola.
- Interpretación pedagógica reutilizada desde `interpretation_core.py`.

## Principio de migración
Streamlit no se elimina. Las dos interfaces convivirán mientras se migren y validen módulos. Los motores matemáticos permanecen compartidos para evitar divergencias de resultados.
