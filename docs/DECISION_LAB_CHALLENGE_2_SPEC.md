# Decision Lab Challenge 2.0 — especificación integral
Estado: rama de trabajo, no publicada ni fusionada. Una plataforma, tres espacios: aprendizaje, laboratorio científico y dirección de operaciones.

## Alcance final (no confundir el motor inicial con producto terminado)
1. Cinco sectores: banca, salud, retail, manufactura y logística.
2. Editor de desafíos parametrizables, importación/exportación de escenarios versionados.
3. Simulación de eventos discretos dinámica: dotación por hora, aperturas/cierres, averías, absentismo, abandono/paciencia, prioridades, descansos, capacidad finita, servicio empírico/gamma/lognormal, demanda por franja, múltiples clases de clientes.
4. Animación de entidad individual con cronología, control pausa/reanudar, salto, velocidades, representación de servidores y clientes; el primer tablero publicado implementa reproducción resumida por eventos.
5. Sistema de decisiones en el curso de la partida con registro de acciones y costo de decisiones. Cada cambio se aplica desde el instante de decisión, no recalcula retrospectivamente.
6. Evaluación con KPIs calculados en horizonte definido: clientes recibidos, iniciados, finalizados, pendientes, rechazados, abandonos, Wq condicionado y censurado, utilización efectiva, probabilidades SLA observadas, Lq ponderado en tiempo, costos laborales, pérdida de demanda, costo de espera, costo de cambio, costo total, intervalos de confianza.
7. Gamificación: misiones, niveles, objetivos obligatorios, scoring normalizado por caso, medallas por consistencia, habilidades demostradas, desafío de resiliencia, tablas clasificatorias con consentimiento.
8. Evaluación académica: sustento del modelo, supuestos, justificación, comparación analítica/simulación, rúbrica y retroalimentación; sin mezclar ranking empresarial con nota teórica.
9. Comparación de estrategias justa: números aleatorios comunes por cliente, misma muestra de demanda, réplicas independientes y semillas conservadas; resultados y sensibilidad.
10. Capa de persistencia: Django auth, partidas, eventos, perfiles, progreso, métricas, leaderboard, reportes, seguimiento; PostgreSQL en producción, migraciones versionadas.
11. Seguridad: secretos ambientales, DEBUG off en producción, HTTPS, auth/autorización, protección CSRF, límites de cómputo y cargas, controles anti-trampa, trazabilidad de evaluaciones.
12. Calidad: benchmarks exactos M/M/1/M/M/s/Erlang B, conservación de flujo, caso sin variabilidad, carga extrema, cierres, empates de eventos, sesgo de censura, CI 95% por réplicas, test E2E UI, accesibilidad y móviles.
13. Exportaciones PDF/CSV/JSON y reporte gerencial con metodología, costos, evaluación frente a metas y limitaciones.
14. Incorporar las reglas de juego como configuración de misión, versionarlas y registrar la versión junto a resultados.

## Primera implementación en esta rama
- challenge_engine.py: cinco sectores, decisiones de dotación horaria, incidente determinista por tipo, bloqueo, colas FIFO, costos, múltiples réplicas, puntuación y línea de eventos.
- challenge_views.py y API: partida sin persistencia, acceso desde menú.
- challenge.html y challenge.js: tablero y reproducción visual resumida, gráfico de cola, exportación JSON.
- test_challenge.py: pruebas básicas.
- NO implementado todavía: decisiones de reproducción en vivo, abandono, múltiples clases, edición de escenarios, autenticación, rankings persistentes, informes PDF, IC 95%, telemetría y pruebas integrales. No describir esta versión como producción.

## Reglas estadísticas
- Los resultados analíticos M/M/s describen estado estacionario, no una jornada inicial vacía.
- En trayectorias de jornada, cada indicador define población, observación y censura.
- En comparaciones, preservar realizaciones base. Actualmente la secuencia de servicio se genera según orden de inicio, no aún por ID de cliente: mejorar antes de certificar comparaciones de estrategias.
- El score inicial es descriptivo: no presentar como función objetivo optimizada; calibrar contra benchmarks factibles por misión.
- Personal programado, tiempo de trabajo real, indisponibilidad y horas extra deben mostrarse por separado.

## Criterio de cierre del producto integral
Pruebas automáticas verdes; consistencia estadística corroborada; interfaz E2E completa en móvil/escritorio; cinco misiones con acciones durante reproducción; partida reproducible y exportable; costos calibrados; rankings opcionales; configuración segura y despliegue verificable.
