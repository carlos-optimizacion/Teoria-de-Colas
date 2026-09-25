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