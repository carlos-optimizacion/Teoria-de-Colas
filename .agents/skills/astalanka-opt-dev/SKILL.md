---
name: astalanka-opt-dev
description: Desarrollar, validar y publicar hitos de ASTALANKA OPT / Decision Lab 3.0 en GitHub y Render; usar para cambios del motor de colas, escenarios 3D, desafíos, red multietapa, análisis, reportes y pruebas.
---

# ASTALANKA OPT · desarrollo integral con evidencia

## Activación y alcance

Usar cuando se solicite implementar, corregir, probar, integrar o publicar código del repositorio carlos-optimizacion/Teoria-de-Colas, incluidos «continúa», «avanza los hitos», «mejora las simulaciones», «valida» y «despliega». Para consultas meramente conceptuales, analizar sin editar. No aplicar a otros proyectos sin adaptar contratos y pruebas.

Se busca una entrega completa, no solo una propuesta. Trabajar únicamente con las herramientas y autorizaciones efectivamente disponibles. Nunca inventar resultados, commits, CI, despliegues ni supuesta actividad de segundo plano.

Consultar referencias según el tipo de trabajo:
- references/architecture.md para arquitectura, matemáticas, UI, módulos o escenas.
- references/acceptance-matrix.md para pruebas, aceptación y visualizaciones.
- references/github-render.md para cambios en GitHub, merge, despliegue y trazabilidad.
- assets/hito-template.md para informes de hitos.

## Protocolo de ejecución

1. Aclarar alcance sin repetir lo ya decidido: error, función nueva, mejora 3D, refactor o despliegue. Definir criterios medibles por hito. Para tarea sustancial, comunicar plan breve y avances con evidencia.
2. Inspeccionar repositorio real y sus instrucciones, SHA actual de main, PR/issues, código y CI; consultar servicio Render real cuando aplique. No fiarse de resúmenes históricos o README desactualizados.
3. Diseñar el cambio mínimo suficiente, con contratos protegidos. Conservar cuatro módulos: Simulador 3D, Desafíos gerenciales, Red de colas, Análisis y reportes. Mantener Producción/Manufactura fuera del simulador de colas. No duplicar fórmulas ni decisiones de eventos.
4. Crear rama para el hito, commits precisos y PR asociada al issue. No experimentar ni sobrescribir main directamente. Evitar cambios ajenos al alcance.
5. Validar sintaxis, pytest, invariantes, Streamlit AppTest, JavaScript y Chromium/WebGL según corresponda. Si cambia una escena 3D, capturar y examinar el contenido real del iframe, no únicamente la cabecera de Streamlit. Verificar la misma configuración y entidades del motor Python.
6. Ante fallos: leer job/log, reparar causa real, rerun en nuevo SHA. No saltar pruebas ni maquillar indicadores. Mantener producción operativa.
7. Integrar cuando el SHA HEAD esté aprobado, sin conflictos ni bloqueos; solo desplegar si la tarea/permiso lo autoriza. Tras desplegar, verificar en Render estado LIVE, SHA exacto, arranque, salud y logs recientes. PR fusionada no demuestra publicación.
8. Informar hito, código entregado, tests con evidencia, PR/commit, Render verificado o pendiente y próximos riesgos. Cerrar un hito solo con criterios satisfechos. Sin prometer seguimiento automático salvo tarea creada.

## Integridad matemática obligatoria

- El motor Python define llegadas, inicio/fin de servicio, cola, recursos, rechazos, abandono y KPI. Three.js reproduce estados y personas/camiones, nunca genera tiempos o clientes de forma autónoma.
- Identificar minutos/horas y tasas por hora; distinguir estacionariedad analítica de estimación sobre horizonte finito y promedio de réplicas.
- Mantener determinístico, paramétrico y empírico cuando correspondan, con semilla reproducible, modelos Kendall coherentes, límites y validación de Excel.
- Capacidad y flujo: ocupación no excede servidores, conteos no negativos, trazas compatibles con colas y estados. En red tándem preservar identidad y conservación etapa a etapa.
- Comparar costos/SLA únicamente bajo condiciones homogéneas, conservando supuestos, fuentes y método. Nunca afirmar óptimo global de un heurístico.
- UI en orden: datos → validación → vista previa sin movimiento → simulación → análisis → informe.
- Cuatro sectores actuales: Banco, Salud, Retail, Logística. La Red 3D es transversal. Producción se reserva para otro módulo.
- Calidad gráfica adaptable a dispositivos; no forzar supermuestreo que bloquee WebGL o altere sincronización de eventos.

## Definición de terminado

Una entrega se considera completada solo si los tests afectados y la regresión necesaria pasan, las imágenes del visor se verifican si corresponde, las exportaciones son consistentes, el SHA de PR está validado y (cuando se pidió publicación) Render reporta LIVE con el commit correcto. Si no se cumple una condición, explicitar pendiente y bloqueo.

Usar scripts/validate_skill.py al modificar esta skill. No incluir secretos ni datos personales en repositorio, logs o capturas.
