# Decision Lab · Django 6.1

Migración integral de la plataforma educativa de Teoría de Colas. Django convive con Streamlit y reutiliza directamente los motores `queue_core.py` e `interpretation_core.py` de la raíz del repositorio.

## Stack
- Django 6.1.1
- Python 3.12–3.14 (referencia principal: 3.14)
- Django Templates + JavaScript
- Plotly.js para gráficos dinámicos
- MathJax para fórmulas
- SQLite en desarrollo; arquitectura preparada para PostgreSQL

## Ejecutar
```bash
cd django_app
python -m venv .venv
# activar entorno
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`.

## Módulos migrados
1. Fundamentos
2. M/M/1
4. M/M/s
6. M/M/s/K
8. M/M/1 con espera limitada
10. M/M/s con capacidad total
12. Erlang B
14. M/G/1
16. D/D/1
18. Casos aplicados
19. Colas simples
20. Colas complejas
21. Comparador de modelos
22. Análisis económico
23. Dimensionamiento de servidores
24. Validador de supuestos
25. Análisis End-to-End

## Simulación
`simulation_core.py` implementa eventos discretos con réplicas, capacidad finita, bloqueo y distribuciones de servicio exponencial, determinista y Gamma. En M/G/1, la Gamma se usa únicamente como escenario de simulación calibrado al CV; el resultado analítico continúa usando Pollaczek–Khinchine y no presupone que G sea Gamma.

## Convenciones
La capa Django normaliza:
- `s`: número de servidores;
- `K`: capacidad total del sistema;
- `K-s`: plazas máximas de espera.

Cuando un módulo histórico usa `c`, la interfaz conserva el alias para fines pedagógicos, pero lo traduce a K antes de calcular.

## Validación
```bash
python manage.py check
python manage.py test portal
```

GitHub Actions valida Django 6.1.1 en Python 3.12 y 3.14. El workflow matemático original continúa validando Streamlit y el motor compartido.

## Principio de migración
Streamlit no se elimina. Las dos interfaces utilizan la misma fuente matemática para evitar divergencias. Django es la capa preparada para persistencia, autenticación, reportes y evolución hacia una plataforma web completa.
## Arena integral de simulaciones y gamificación (rama feature/decision-lab-challenge-2)

Visita `http://127.0.0.1:8000/challenge/` después de iniciar Django.

### Laboratorio académico integrado
Incluye ocho modelos originales en un panel experimental que utiliza el endpoint existente `/api/model/`. Se conserva el acceso a cada modelo individual y a la animación M/M/s previa desde el menú.

### Misiones gerenciales animadas
Cinco sectores: banco, hospital, supermercado, inspección industrial y despacho logístico. Se programan servidores por hora y el jugador puede introducir intervenciones durante la reproducción; éstas entran en vigor en el siguiente minuto simulado. La partida se recalcula con la misma muestra de llegadas y tiempos de servicio por cliente, para comparar alternativas sin alterar los eventos pasados.

Cada partida muestra clientes identificables, ocupación de puestos, colas, pérdidas por bloqueo, costos laborales, costos de espera, servicio objetivo, puntos, medallas, comparación con la primera estrategia y descarga JSON.

**Precisiones metodológicas:**
- La animación representa la primera réplica de un experimento de horizonte finito, mientras que los promedios y los intervalos de confianza se calculan usando todas las réplicas.
- El nivel de servicio conservador usa como denominador a los clientes admitidos, incluidos pendientes que todavía no iniciaron atención.
- La utilización se calcula respecto de la capacidad disponible efectiva, considerando servicios en curso al reducir dotación.
- Los valores económicos y objetivos de cada misión son supuestos didácticos, no parámetros validados de organizaciones reales.
- Los intervalos de confianza de 95% son aproximaciones exploratorias; pocas réplicas no ofrecen inferencia robusta.
- El mini-reto de modelos es formativo, no reemplaza optimización ni evaluación estadística formal.
- Las puntuaciones personales guardadas en el navegador no son rankings multiusuario.

### Pruebas
```bash
cd django_app
python manage.py check
python manage.py test
node --check static/js/challenge.js
node --check static/js/classic-lab.js
```

Para verificar visualmente en GitHub, el workflow `Vista previa y prueba de navegador` ejecuta pruebas de Playwright y adjunta capturas de escritorio y móvil a sus artefactos. Requiere que ese workflow termine correctamente.

**Estado:** versión beta en rama de trabajo; no fusionar ni considerar lista para producción hasta completar pruebas E2E y capacidades de seguridad/persistencia.
