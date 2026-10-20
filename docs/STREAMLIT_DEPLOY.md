# Despliegue de Decision Lab 2.0 en Streamlit Community Cloud

## Configuración del repositorio

La versión Streamlit usa directamente los motores validados del proyecto:

- `streamlit_app.py`: entrada principal de la aplicación.
- `queue_core.py`: modelos analíticos.
- `django_app/portal/challenge_engine.py`: simulación gerencial avanzada.
- `django_app/portal/network_engine.py`: red de colas multietapa.
- `django_app/static/img/scenarios/`: imágenes SVG de los cinco sectores.
- `requirements.txt`: dependencias Python.
- `runtime.txt`: Python 3.12.
- `.streamlit/config.toml`: tema y configuración headless.
- `.github/workflows/streamlit-smoke.yml`: prueba de arranque y health-check.

No se requieren secretos para ejecutar la versión Streamlit actual.

## Despliegue en Community Cloud

En Streamlit Community Cloud:

1. Conecta tu cuenta de GitHub.
2. Selecciona **Create app**.
3. Elige el repositorio `carlos-optimizacion/Teoria-de-Colas`.
4. Para revisar antes de fusionar:
   - Branch: `feature/decision-lab-challenge-2`
   - Main file path: `streamlit_app.py`
5. Para producción, después de fusionar:
   - Branch: `main`
   - Main file path: `streamlit_app.py`
6. Elige el subdominio deseado y pulsa **Deploy**.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Luego abre `http://localhost:8501`.

## Funciones incluidas en Streamlit

- 5 escenarios gerenciales visuales.
- Simulación de eventos discretos reproducible.
- Clientes, cola y puestos activos por frame.
- Intervenciones de dotación durante la jornada.
- Costos, SLA, utilización, bloqueos y abandonos.
- Distribuciones exponencial, determinista, gamma y lognormal.
- Paciencia/abandono y prioridad no expropiativa.
- 8 modelos académicos.
- Comparador de escenarios.
- Análisis económico.
- Red multietapa de 2 a 4 etapas.
- Progreso y gamificación durante la sesión.
- Exportación JSON y CSV.

## Limitación deliberada de Community Cloud

La versión Streamlit conserva el progreso en `st.session_state`, por lo que no sustituye la persistencia multiusuario de Django/PostgreSQL. Reiniciar el proceso o una sesión puede borrar ese estado. Para usuarios, rankings e historial persistentes, la versión Django/PostgreSQL del mismo repositorio sigue siendo la arquitectura productiva completa.

## Validación

El workflow `Validación Streamlit`:
- instala `requirements.txt`;
- compila los módulos principales;
- ejecuta smoke tests de los motores;
- inicia Streamlit en modo headless;
- comprueba `/_stcore/health`;
- verifica que la página principal responda.
