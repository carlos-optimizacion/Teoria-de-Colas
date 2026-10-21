# Teoría de Colas | Decision Lab

Aplicación educativa y de apoyo a decisiones para cursos de **Investigación de Operaciones e Ingeniería Industrial**. La plataforma combina teoría, experimentación interactiva, validación preliminar de supuestos, comparación de escenarios, análisis económico y dimensionamiento de capacidad mediante Streamlit.

## Objetivo

Transformar los modelos de teoría de colas en una herramienta que permita:

1. comprender los supuestos de cada modelo;
2. experimentar con tasas de llegada, servicio, capacidad y variabilidad;
3. medir utilización, espera, longitud de cola y probabilidad de espera;
4. contrastar preliminarmente los supuestos con datos observados;
5. comparar alternativas de capacidad;
6. incorporar costo de servidores, espera y clientes perdidos;
7. sustentar una recomendación operativa con métricas cuantitativas.

## Modos de trabajo

### Modo aprendizaje
Ruta conceptual para estudiar los modelos y experimentar con parámetros.

### Laboratorio aplicado
Casos y comparaciones orientados a decisiones de capacidad y servicio.

### Modo analista
Análisis End-to-End para convertir datos operativos en una recomendación de dotación y costo-beneficio.

## Modelos y módulos incluidos

- M/M/1
- M/M/s (Erlang C)
- M/M/1/K
- M/M/s/K
- M/G/1 mediante Pollaczek-Khinchine
- D/D/1 con secuencia determinista
- comparación de alternativas
- análisis económico
- dimensionamiento de servidores
- validador preliminar de supuestos con CSV
- análisis End-to-End

## Arquitectura

```text
home.py
│
├── pages/                  # Interfaz, teoría, laboratorios y análisis
│   └── 24_Validador_Supuestos.py
│
├── queue_core.py           # Motor matemático compartido
│   ├── M/M/1 y M/M/s
│   ├── M/M/s/K
│   ├── M/G/1
│   ├── D/D/1
│   ├── P(Wq > t)
│   └── costos y dimensionamiento
│
├── tests/                  # Validación matemática automatizada
│
└── .github/workflows/      # Integración continua
```

La interfaz no debe duplicar fórmulas. Los cálculos reutilizables deben vivir en `queue_core.py` para evitar resultados inconsistentes entre páginas.

## Convenciones del motor

- `lambda` y `mu`: eventos por hora.
- `W` y `Wq`: horas.
- `L` y `Lq`: clientes/unidades promedio.
- funciones `*_from_minutes`: reciben datos operativos en minutos.
- `rho`: utilización del sistema.

## Validador preliminar de supuestos

El módulo 24 permite cargar un CSV con tiempos entre llegadas y tiempos de servicio. Calcula, entre otros indicadores:

- media y desviación estándar;
- coeficiente de variación (CV);
- autocorrelación lag 1;
- histogramas descriptivos;
- orientación preliminar sobre el uso de M/M/s, M/G/1 o simulación.

**Importante:** CV≈1 y baja autocorrelación son señales descriptivas, no una prueba formal de proceso Poisson ni de distribución exponencial.

## Supuestos principales

Los resultados de los modelos analíticos son válidos bajo los supuestos correspondientes. Por ejemplo, M/M/s supone llegadas Poisson, tiempos de servicio exponenciales, servidores equivalentes y una cola común. Cuando estos supuestos no representan adecuadamente el proceso real, se recomienda utilizar modelos más generales o simulación de eventos discretos.

## Instalación

Se recomienda Python 3.11 o 3.12.

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar la aplicación:

```bash
streamlit run home.py
```

## Pruebas matemáticas

Instalar dependencias de desarrollo:

```bash
pip install -r requirements-dev.txt
```

Ejecutar:

```bash
pytest -q
```

Las pruebas validan, entre otros puntos:

- resultados conocidos de M/M/1;
- Erlang C para M/M/s;
- estabilidad del sistema;
- consistencia de probabilidades en M/M/s/K;
- Ley de Little;
- efecto de la variabilidad en M/G/1;
- costo de sistemas inestables;
- dimensionamiento automático de servidores.

GitHub Actions ejecuta estas pruebas automáticamente en cada cambio relevante.

## Interpretación responsable

La herramienta es un apoyo analítico. Una recomendación real debe contrastarse con:

- distribución observada de llegadas;
- distribución y variabilidad del servicio;
- estacionalidad por hora/día;
- abandonos y rechazos;
- prioridades de atención;
- descansos y disponibilidad efectiva de servidores;
- habilidades no equivalentes;
- restricciones físicas y de turnos;
- costos reales de capacidad y espera.

## Próxima evolución propuesta

1. **Simulación de eventos discretos** con distribuciones empíricas, lognormal, gamma, Weibull, horarios variables, abandonos y prioridades.
2. **Optimización de capacidad** para minimizar costo total sujeto a metas de servicio y restricciones operativas.
3. **Análisis de sensibilidad** sobre demanda, servicio, costo de espera y disponibilidad.
4. **Importación avanzada de CSV/Excel** con cálculo automático de interarribos, segmentación por franja y depuración de datos.
5. **Pruebas estadísticas formales** y gráficos Q-Q para reforzar la selección del modelo.
6. **Comparación analítico vs. simulación** para validación cruzada.
7. **Redes de colas** para procesos con varias etapas y rutas.
8. **Abandono y paciencia del cliente** mediante modelos Erlang A / M/M/s+M.
9. **SLA probabilístico**: dimensionar por P(Wq≤t), no solo por espera promedio.
10. **Reportes ejecutivos reproducibles** con supuestos, escenarios, riesgos y recomendación.

## Autor

**Mag. Carlos Alberto Nieto Astahuamán**  
Aplicación educativa desarrollada con fines académicos.


---

## Aplicativo App 2.0 — Frontend unificado (rama de revisión)

La experiencia integrada utiliza **Django**, en lugar de mantener una segunda copia del sistema. Se accede a la misma aplicación mediante `/aplicativo-app/` y `/challenge/`.

**Para evaluarla localmente:**
- **Windows:** ejecutar `Iniciar_Aplicativo_App.bat`.
- **Linux/macOS:** ejecutar `sh Iniciar_Aplicativo_App.sh`.
- Abre `http://127.0.0.1:8000/aplicativo-app/`.

El frontend reúne el laboratorio de los ocho modelos originales, el simulador M/M/s, el comparador y análisis económico del portal, y las cinco misiones gerenciales gamificadas. Las escenas SVG de cada sector se ubican en `django_app/static/img/scenarios/`. Los avatares y ocupaciones mostrados en estas escenas se alimentan de datos de los eventos simulados, no de animaciones aleatorias independientes.

**Control de calidad:** las pruebas matemáticas y Django se ejecutan en GitHub Actions. Playwright verifica la página unificada, imágenes, eventos, decisiones, simulador clásico y anchura de pantalla móvil; sus capturas se adjuntan como artefactos de CI. La aplicación no está publicada en un servidor público y la rama `main` permanece sin modificar.

**Limitaciones:** esta es una beta de desarrollo. Aún faltan, para una versión productiva: perfiles persistentes, rankings multiusuario, gestión de partidas guardadas, validación de simulaciones de múltiples etapas y controles de despliegue/seguridad de producción.


## Decision Lab 2.0 en Streamlit

La versión integrada puede ejecutarse también con Streamlit usando el mismo motor matemático y de simulación validado.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Entrada principal: `streamlit_app.py`.

Incluye cinco escenarios, simulación dinámica, decisiones de dotación, costos, SLA, abandonos, prioridades, distribuciones de servicio, ocho modelos matemáticos, comparación, análisis económico y red multietapa.

Para Streamlit Community Cloud usa:
- Repositorio: `carlos-optimizacion/Teoria-de-Colas`
- Rama de revisión: `feature/decision-lab-challenge-2`
- Archivo principal: `streamlit_app.py`

Consulta `docs/STREAMLIT_DEPLOY.md` para el procedimiento completo. La persistencia multiusuario completa permanece en Django/PostgreSQL; la versión Streamlit conserva el progreso de gamificación de forma temporal en la sesión.


## Escenario Banco 3D — Three.js

En **Simulación** selecciona **Banco** y sigue el recorrido: **Configurar → Guardar y validar → Abrir simulación → Iniciar simulación**. Solo se construye la escena después de guardar los parámetros.

- La previsualización muestra exactamente las ventanillas configuradas y no reproduce eventos.
- En ejecución, Three.js dibuja la agencia, ventanillas, cajeros, personas, recorrido, cola y salida. Cámara orbitable con ratón/táctil, zoom, controles de pausa, reproducción, paso y velocidad.
- El motor Python (django_app/portal/challenge_engine.py) genera todos los eventos y métricas. El navegador solo reproduce esos cuadros y suaviza el movimiento; no recalcula llegadas ni servicios.
- Se dibujan hasta 42 personas en espera por rendimiento. El contador siempre muestra el total de la cola.
- Las intervenciones programadas reconstruyen la trayectoria desde Python; al aplicarlas se reinicia el reproductor con el nuevo resultado.
- Requiere navegador con WebGL y acceso a cdn.jsdelivr.net para cargar Three.js y OrbitControls. La interfaz avisa si falla la carga.
- Esta es una primera versión 3D procedimental: todavía no usa personajes o mobiliario de alta fidelidad importados desde Blender.
- Los otros escenarios mantienen sus vistas existentes hasta la incorporación de sus módulos 3D.

**Pruebas**: pytest -q tests/test_bank_three_scene.py verifica configuración, eventos, escape de datos y sintaxis JS cuando Node está disponible. La CI de Streamlit valida también la integración.
