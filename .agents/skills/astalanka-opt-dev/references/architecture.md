# Arquitectura y convenciones

Entrada: streamlit_app.py. Repositorio: carlos-optimizacion/Teoria-de-Colas. Render: verificar servicio y URL real; render.yaml es configuración, no prueba de estado. Antes de editar, leer las rutas vigentes y su código.

## Cuatro módulos

- Simulador 3D: streamlit_v3.py y django_app/portal/queue_v3.py; teoría queue_core.py y portal/theory_v3.py; entrada empírica portal/empirical_v3.py; escenarios bank_three_scene.py, sector_scenes_v3.py, visual_quality_v3.py.
- Desafíos gerenciales: streamlit_app.py, portal/challenge_engine.py, sus adaptadores compartidos y tests.
- Red de colas: portal/network_engine.py, portal/network_v3.py y network_three_scene.py; procesos en serie y KPI por nodo.
- Análisis y reportes: experiment_registry_v3.py, report_v3.py, optimizador en motor y streamlit_app.py.

## Contratos

El backend Python es la fuente de verdad para eventos, colas, utilización, clientes, costos y réplicas. WebGL solo representa traza física y controles de cámara/calidad. Un fotograma muestreado no debe confundirse con datos inventados.

Cuatro sectores activos: Banco, Salud, Retail, Logística. No reintroducir Producción/Manufactura en la teoría de colas. Su futuro sistema de flujo continuo tiene un modelo independiente.

Mantener configuración antes de la escena, selección explícita de modelo compatible, validación antes de simular, escena previa sin movimiento, ejecución, comparación y reporte. Historial de sesión no equivale a base de datos persistente.

La README puede estar desactualizada: cotejar contra main, firmas de funciones y tests reales. Los flujos de Challenge, Red y Comparador deben compartir contratos para evitar indicadores contradictorios.