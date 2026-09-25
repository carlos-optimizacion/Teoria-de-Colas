"""Motor pedagógico para interpretar resultados de teoría de colas.

Este módulo NO reemplaza el motor matemático. Recibe resultados ya calculados
por los modelos y los traduce a lenguaje operativo y educativo.

Cada función devuelve cinco capas:
- que_pasa: lectura directa del resultado;
- por_que: explicación causal vinculada al modelo;
- operacion: significado para un proceso real;
- accion: variable que conviene evaluar;
- aprendizaje: concepto que el estudiante debe retener.
"""

import math


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def _clientes_cada_100(p: float) -> int:
    return int(round(max(0.0, min(1.0, p)) * 100))


def _holgura(rho: float) -> float:
    return max(0.0, 1.0 - rho)


def _base(que_pasa: str, por_que: str, operacion: str, accion: str, aprendizaje: str):
    return {
        "que_pasa": que_pasa,
        "por_que": por_que,
        "operacion": operacion,
        "accion": accion,
        "aprendizaje": aprendizaje,
    }


def interpret_mm1(r: dict):
    rho = r["rho"]
    if not r.get("estable", False):
        return _base(
            f"La utilización requerida es {_pct(rho)}. La demanda promedio iguala o supera la capacidad del único servidor, por lo que el modelo no alcanza un estado estable.",
            "En M/M/1 la estabilidad exige λ < μ. Cuando esa condición no se cumple, los clientes llegan al menos tan rápido como pueden ser atendidos y la cola tiende a crecer.",
            "No es correcto interpretar Wq o Lq como promedios finitos en este escenario. El problema principal es capacidad insuficiente, no el tamaño físico de la sala de espera.",
            "Evalúa reducir el tiempo de servicio, reducir el ritmo de llegada o incorporar capacidad adicional. Si agregas servidores, el modelo deja de ser M/M/1 y pasa a M/M/s.",
            "Primero se verifica estabilidad; después se interpretan tiempos y longitudes promedio de cola.",
        )

    wq = r["Wq"] * 60
    w = r["W"] * 60
    p = r["P_espera"]
    holg = _holgura(rho)
    return _base(
        f"El servidor está ocupado {_pct(rho)} del tiempo. Aproximadamente {_clientes_cada_100(p)} de cada 100 clientes encuentran el servidor ocupado y deben esperar. La espera promedio es {wq:.1f} min y el tiempo total promedio en el sistema es {w:.1f} min.",
        f"La capacidad media supera la demanda, pero solo queda una holgura aproximada de {_pct(holg)}. En un sistema aleatorio, una holgura pequeña hace que coincidencias temporales de llegadas generen cola aunque λ < μ.",
        f"En promedio hay {r['Lq']:.2f} clientes esperando. Este valor es un promedio de largo plazo: no significa que siempre existan exactamente {r['Lq']:.2f} personas físicamente en la fila.",
        "Si la espera es alta, prueba primero qué ocurre al reducir el tiempo de atención. También puedes analizar un servidor adicional en M/M/s. Aumentar solo el espacio de espera no incrementa la velocidad de servicio.",
        "Un sistema estable puede tener congestión importante. ρ indica uso de capacidad; Wq y Lq indican el efecto de esa carga sobre el cliente.",
    )


def interpret_mms(r: dict, s: int | None = None):
    s = int(s or r.get("s", 1))
    rho = r["rho"]
    if not r.get("estable", False):
        return _base(
            f"Con {s} servidor(es), la utilización requerida es {_pct(rho)} y la capacidad agregada no es suficiente para absorber la demanda promedio.",
            "En M/M/s la condición de estabilidad es λ < s·μ. Lo relevante no es la velocidad de un servidor aislado, sino la capacidad conjunta de todos los servidores.",
            "La cola tenderá a crecer mientras se mantengan estas tasas. Agregar espacio de espera solo permite acumular más clientes; no resuelve la falta de capacidad de atención.",
            "Evalúa aumentar s, reducir el tiempo medio de servicio o gestionar la llegada de demanda por franjas horarias.",
            "En sistemas multicanal, la capacidad se analiza de forma agregada mediante s·μ.",
        )

    p = r["P_espera"]
    wq = r["Wq"] * 60
    holg = _holgura(rho)
    return _base(
        f"Cada servidor presenta una utilización media de {_pct(rho)}. Aproximadamente {_clientes_cada_100(p)} de cada 100 llegadas encuentran todos los servidores ocupados. La espera promedio antes de iniciar servicio es {wq:.1f} min.",
        f"Aunque la capacidad conjunta es suficiente, la variabilidad hace que varios clientes puedan coincidir con todos los servidores ocupados. La holgura media por servidor es aproximadamente {_pct(holg)}.",
        f"La cola promedio es {r['Lq']:.2f} clientes. Una P(espera) alta con Wq moderado significa que muchos clientes pueden esperar, pero durante poco tiempo; ambas métricas deben leerse juntas.",
        "Compara s-1, s y s+1 servidores. Si un servidor adicional reduce mucho Wq, todavía existe una ganancia relevante de capacidad; si la mejora es pequeña, aparecen rendimientos marginales decrecientes.",
        "No existe un porcentaje universal de utilización 'correcto'. La dotación debe relacionar ρ con Wq, P(espera), nivel de servicio y costo.",
    )


def interpret_mmsk(r: dict):
    bloqueo = r.get("P_bloqueo", 0.0)
    lam = r.get("lambda", 0.0)
    lam_eff = r.get("lambda_efectiva", r.get("lambda_eff", lam))
    wq = r.get("Wq", 0.0) * 60
    k = r.get("K", "K")
    s = r.get("s", 1)
    return _base(
        f"Con capacidad total K={k} y {s} servidor(es), aproximadamente {_clientes_cada_100(bloqueo)} de cada 100 llegadas encuentran el sistema lleno y no ingresan. La tasa realmente admitida es {lam_eff:.2f} de {lam:.2f} llegadas por hora.",
        "En un sistema finito la congestión no puede crecer sin límite dentro del sistema. Cuando se ocupa toda la capacidad K, el exceso de demanda se transforma en bloqueo o rechazo.",
        f"Quienes son admitidos esperan en promedio {wq:.1f} min. Aumentar K suele reducir el rechazo, pero permite que más clientes permanezcan dentro del sistema esperando.",
        "Si el problema es bloqueo alto, compara aumentar K y aumentar s. Aumentar K agrega espacio; aumentar s agrega capacidad de servicio. No son la misma decisión.",
        "En capacidad finita existe un intercambio entre clientes perdidos y clientes esperando. La decisión debe observar simultáneamente bloqueo, Wq y λ efectiva.",
    )


def interpret_erlang_b(r: dict, servers: int):
    b = r.get("B", r.get("P_bloqueo", 0.0))
    lam_eff = r.get("lambda_eff", r.get("lambda_efectiva", 0.0))
    ocup = r.get("ocupacion", r.get("rho", 0.0))
    return _base(
        f"No existe cola: aproximadamente {_clientes_cada_100(b)} de cada 100 llegadas encuentran los {servers} servidores ocupados y se pierden o son desviadas. La ocupación media es {_pct(ocup)}.",
        "Erlang B describe un sistema de pérdidas. Una llegada que coincide con todos los servidores ocupados no espera; simplemente no recibe servicio en ese momento.",
        f"La tasa efectiva atendible es aproximadamente {lam_eff:.2f} clientes por hora. Por eso una ocupación aparentemente moderada puede coexistir con bloqueo: las llegadas son aleatorias y pueden concentrarse temporalmente.",
        "Compara el bloqueo con servers-1 y servers+1. El objetivo no es eliminar necesariamente todo bloqueo, sino encontrar una dotación compatible con el nivel de pérdida aceptable.",
        "En sistemas sin sala de espera la congestión se observa como pérdida de demanda, no como Wq.",
    )


def interpret_mg1(r: dict, cv: float, time_unit: str = "hours"):
    rho = r["rho"]
    if not r.get("estable", False):
        return _base(
            f"La utilización requerida es {_pct(rho)}; el único servidor no tiene capacidad promedio suficiente para absorber la demanda.",
            "En M/G/1 la estabilidad también requiere ρ < 1. La forma de la distribución del servicio cambia la espera, pero no puede compensar una capacidad promedio insuficiente.",
            "Antes de estudiar la variabilidad, debe resolverse el déficit de capacidad.",
            "Reduce el tiempo medio de servicio, la tasa de llegada o analiza varios servidores mediante otro modelo o simulación.",
            "La variabilidad importa después de asegurar que la capacidad promedio sea suficiente.",
        )

    if time_unit not in {"hours", "minutes"}:
        raise ValueError("time_unit debe ser 'hours' o 'minutes'.")
    wq = r["Wq"] * 60 if time_unit == "hours" else r["Wq"]
    variabilidad = "baja" if cv < 0.8 else "similar a la exponencial" if cv <= 1.2 else "alta"
    return _base(
        f"La utilización es {_pct(rho)} y el servicio presenta variabilidad {variabilidad} (CV={cv:.2f}). La espera promedio estimada es {wq:.1f} min.",
        "Pollaczek–Khinchine incorpora el segundo momento del tiempo de servicio. Por eso dos procesos con el mismo tiempo medio pueden producir colas muy distintas si su dispersión cambia.",
        f"Con CV={cv:.2f}, la variabilidad es una causa explícita de la espera. Reducir dispersión puede mejorar el servicio incluso sin cambiar el promedio de atención.",
        "Compara el escenario actual con CV=0 y CV=1 manteniendo iguales λ y tiempo medio. Así podrás separar el efecto de capacidad del efecto de variabilidad.",
        "En M/G/1 el promedio de servicio no basta: estandarización, reducción de retrabajos y control de variabilidad pueden ser palancas de mejora.",
    )


def interpret_dd1(intervalo: float, servicio: float, espera_promedio: float, espera_final: float):
    rho = servicio / intervalo
    if servicio <= intervalo:
        return _base(
            f"El servicio ({servicio:.1f} min) termina antes o justo cuando llega la siguiente unidad ({intervalo:.1f} min). La utilización es {_pct(rho)} y no se acumula cola en el sistema ideal determinista.",
            "Al no existir variabilidad, cada llegada encuentra disponible al servidor cuando S ≤ T.",
            "Un nivel alto de utilización no genera necesariamente congestión si el flujo está perfectamente sincronizado.",
            "Mantén S ≤ T o introduce un pequeño margen si el proceso real presenta variabilidad, fallas o microparadas.",
            "D/D/1 muestra que la variabilidad, además de la utilización, es una fuente fundamental de espera.",
        )
    return _base(
        f"El servicio tarda {servicio:.1f} min y las llegadas ocurren cada {intervalo:.1f} min. La utilización requerida es {_pct(rho)}; la espera promedio observada es {espera_promedio:.1f} min y el último cliente espera {espera_final:.1f} min.",
        "Cada ciclo deja trabajo pendiente porque S > T. Ese atraso se suma al siguiente cliente y la espera crece de forma acumulativa.",
        "La cola no se debe a aleatoriedad sino a un desbalance estructural entre ritmo de llegada y tiempo de proceso.",
        "Reduce S hasta S ≤ T, disminuye el ritmo de llegada o agrega capacidad paralela si el proceso lo permite.",
        "En un flujo determinista, un pequeño déficit de capacidad se acumula sistemáticamente cliente tras cliente.",
    )


def interpret_economic(staff_cost: float, wait_cost: float, total_cost: float, servers: int, wq_min: float):
    share_wait = wait_cost / total_cost if total_cost > 0 and math.isfinite(total_cost) else 0.0
    return _base(
        f"Con {servers} servidor(es), el costo estimado es S/ {total_cost:.2f}/h: S/ {staff_cost:.2f}/h corresponden a capacidad y S/ {wait_cost:.2f}/h a espera. La espera promedio es {wq_min:.1f} min.",
        f"El costo de espera representa aproximadamente {_pct(share_wait)} del costo total modelado. Agregar capacidad sube el costo de personal, pero puede reducir el costo asociado a la congestión.",
        "El mínimo económico aparece cuando el ahorro marginal por reducir espera deja de compensar el costo marginal de agregar capacidad.",
        "Revisa escenarios vecinos. Una alternativa ligeramente más cara puede justificarse si mejora de forma importante el nivel de servicio, resiliencia o capacidad ante picos.",
        "El costo de espera es un supuesto de decisión y debe sustentarse con datos reales; no es un costo contable automático.",
    )


def to_markdown(lectura: dict, title: str = "🧠 Interpretación en lenguaje sencillo") -> str:
    """Convierte una interpretación en un bloque Markdown homogéneo."""
    return f"""
### {title}

**1. ¿Qué está pasando?**  
{lectura['que_pasa']}

**2. ¿Por qué ocurre?**  
{lectura['por_que']}

**3. ¿Qué significa operativamente?**  
{lectura['operacion']}

**4. ¿Qué podrías cambiar?**  
{lectura['accion']}

**5. ¿Qué debes aprender de este escenario?**  
{lectura['aprendizaje']}
"""


# EDU_INTERPRETATION_COMPARISON_CORE
def interpret_comparison(a: dict, b: dict, meta_wq: float, meta_bloqueo: float):
    """Interpreta dos alternativas sin ocultar los indicadores técnicos."""
    def espera_txt(row):
        value = row.get("Espera (min)")
        return "inestable/no finita" if value is None or not math.isfinite(float(value)) else f"{float(value):.1f} min"

    nombre_a = str(a.get("Escenario", "Escenario A"))
    nombre_b = str(b.get("Escenario", "Escenario B"))
    cumple_a = str(a.get("Cumple meta", "No")) == "Sí"
    cumple_b = str(b.get("Cumple meta", "No")) == "Sí"
    bloqueo_a = float(a.get("Bloqueo %", 0.0))
    bloqueo_b = float(b.get("Bloqueo %", 0.0))
    servidores_a = int(a.get("Servidores", 0))
    servidores_b = int(b.get("Servidores", 0))

    que_pasa = (
        f"{nombre_a}: espera {espera_txt(a)}, bloqueo {bloqueo_a:.1f}% y {servidores_a} servidor(es). "
        f"{nombre_b}: espera {espera_txt(b)}, bloqueo {bloqueo_b:.1f}% y {servidores_b} servidor(es)."
    )

    if cumple_a and cumple_b:
        operacion = (
            "Ambas alternativas cumplen simultáneamente las metas definidas. La elección final debe incorporar "
            "capacidad requerida, costo, restricciones físicas y sensibilidad ante aumentos de demanda."
        )
    elif cumple_a or cumple_b:
        nombre = nombre_a if cumple_a else nombre_b
        operacion = (
            f"Solo {nombre} cumple simultáneamente la meta de espera ≤ {meta_wq:.1f} min y bloqueo ≤ {meta_bloqueo:.1f}%. "
            "La diferencia debe atribuirse a su combinación de capacidad de servicio y, cuando corresponda, capacidad física."
        )
    else:
        operacion = (
            "Ninguna alternativa cumple simultáneamente las metas. Antes de escoger entre ellas conviene rediseñar capacidad, "
            "velocidad de atención o límite físico y volver a comparar."
        )

    return _base(
        que_pasa,
        "Comparar modelos no consiste solo en buscar el menor Wq. Una alternativa puede reducir espera a costa de más servidores, o reducir bloqueo permitiendo más capacidad física. Por eso deben leerse juntas espera, bloqueo, utilización y recursos.",
        operacion,
        "Modifica una variable a la vez y observa qué indicador responde: s cambia capacidad de servicio; K cambia capacidad física; μ cambia velocidad de atención; λ representa presión de demanda.",
        "Una comparación válida explica qué cambia entre escenarios y por qué cambia el resultado; no se limita a señalar cuál número es menor.",
    )
