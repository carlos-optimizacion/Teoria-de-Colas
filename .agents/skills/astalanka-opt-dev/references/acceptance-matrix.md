# Pruebas y evidencias

## Capas de aceptación

1. Sintaxis e imports: py_compile, node --check donde corresponda, validación de entrada y condiciones límite.
2. Motor Python: pytest y conservación de flujo; conteos no negativos, capacidad, ocupación <= servidores, rechazos, abandonos, semilla/horizonte, matriz de modelos que realmente soporta la versión.
3. Configuración UI: Streamlit AppTest y pruebas de cambio reactivo; confirmar que servidores/tiempos/modelos corresponden a parámetros de Python y que la simulación aparece después de los datos.
4. Visualización: Chromium/Playwright WebGL en cuatro sectores y Red 3D; comprobar cargue sin errores, recursos de escena correspondientes, indicadores sincronizados, actores físicos y controles de calidad.
5. Capturas: tomar captura del iframe completo, revisar oclusiones, escala, señalética, densidad, estados y color. Captura de la cabecera de Streamlit no prueba nada sobre la escena.
6. Exportaciones: PDF/XLSX/JSON con modelo, semilla, réplicas, supuestos, métricas y proveniencia idénticos a lo reportado.
7. Rendimiento: escenas grandes, numerosos actores, red de hasta 10 etapas si el código actual lo admite; documentar limitaciones de frames y FPS.
8. Release: revisar tests del SHA exacto del PR, verificar live/commit en Render, chequeo de salud y registros posteriores al deploy.

## Casos matemáticos

Determinístico D/D con 1 y múltiples servidores; M/M/c con y sin capacidad finita; escenarios empíricos Excel válidos/inválidos; por red 2,4,8,10 etapas cuando corresponda; semilla reproducible y conservación etapa a etapa: entradas = completados + cola al corte + en servicio al corte + pérdidas válidas. No inventar cobertura si un modelo no existe.

## Comandos de referencia

- python -m pip install -r requirements-dev.txt
- python -m pytest -q tests/
- python -m py_compile streamlit_app.py streamlit_v3.py bank_three_scene.py network_three_scene.py
- cd django_app && python manage.py check && python manage.py test
- streamlit run streamlit_app.py --server.headless true --server.port 8501
- python tests_browser/v3_streamlit_smoke.py
- python tests_browser/v3_active_sectors_smoke.py
- python tests_browser/v3_network_3d_smoke.py

Ajustar según CI y entorno; pruebas de navegador requieren Streamlit activo y Chromium instalado. No atribuir aprobaciones sin observar código de salida o estado del workflow.