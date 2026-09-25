"""Inserta la capa de interpretación educativa en los laboratorios existentes.

El script trabaja sobre la rama de mejora dentro de GitHub Actions. No modifica
fórmulas: solo añade imports del motor pedagógico y paneles debajo de los
resultados interactivos.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def ensure_import(path: Path, names: str) -> None:
    text = path.read_text(encoding="utf-8")
    statement = f"from interpretation_core import {names}\n"
    if statement in text:
        return
    anchor = "import streamlit as st\n"
    if anchor not in text:
        raise RuntimeError(f"No se encontró import de Streamlit en {path}")
    text = text.replace(anchor, anchor + statement, 1)
    path.write_text(text, encoding="utf-8")


def insert_before(path: Path, markers: list[str], block: str, sentinel: str) -> None:
    text = path.read_text(encoding="utf-8")
    if sentinel in text:
        return
    for marker in markers:
        if marker in text:
            text = text.replace(marker, block.rstrip() + "\n\n" + marker, 1)
            path.write_text(text, encoding="utf-8")
            return
    raise RuntimeError(f"No se encontró marcador para insertar {sentinel} en {path}")


def append_if_missing(path: Path, block: str, sentinel: str) -> None:
    text = path.read_text(encoding="utf-8")
    if sentinel in text:
        return
    path.write_text(text.rstrip() + "\n\n\n" + block.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    pages = ROOT / "pages"

    # Función comparativa compartida.
    core = ROOT / "interpretation_core.py"
    append_if_missing(
        core,
        '''# EDU_INTERPRETATION_COMPARISON_CORE
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
    )''',
        "EDU_INTERPRETATION_COMPARISON_CORE",
    )

    # 02 - M/M/1
    p = pages / "02_Modelo_MM1_Teoria_Ejemplo.py"
    ensure_import(p, "interpret_mm1, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 8. Reto de destreza")'],
        '''# EDU_INTERPRETATION_MM1
st.markdown(to_markdown(interpret_mm1(r_lab)))''',
        "EDU_INTERPRETATION_MM1",
    )

    # 04 - M/M/s
    p = pages / "04_Modelo_MMs_Teoria_Ejemplo.py"
    ensure_import(p, "interpret_mms, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 6. Reto de destreza: encuentra la dotación")'],
        '''# EDU_INTERPRETATION_MMS
st.markdown(to_markdown(interpret_mms(r_lab, servidores)))''',
        "EDU_INTERPRETATION_MMS",
    )

    # 06 - M/M/s/K
    p = pages / "06_Modelo_MMsk.py"
    ensure_import(p, "interpret_mmsk, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 6. Reto de destreza")'],
        '''# EDU_INTERPRETATION_MMSK
r_interpretacion = dict(r)
r_interpretacion.setdefault("lambda_efectiva", r.get("lambda_eff", r.get("lambda", 0.0)))
st.markdown(to_markdown(interpret_mmsk(r_interpretacion)))''',
        "EDU_INTERPRETATION_MMSK",
    )

    # 08 - M/M/1/c
    p = pages / "08_Modelo_MM1c.py"
    ensure_import(p, "interpret_mmsk, to_markdown")
    insert_before(
        p,
        ["st.markdown('## 6. Reto de destreza')", 'st.markdown("## 6. Reto de destreza")'],
        '''# EDU_INTERPRETATION_MM1C
r_interpretacion = dict(r)
r_interpretacion.setdefault("s", 1)
r_interpretacion.setdefault("lambda_efectiva", r.get("lambda_eff", r.get("lambda", 0.0)))
st.markdown(to_markdown(interpret_mmsk(r_interpretacion), title="🧠 Interpretación de tu M/M/1 con espera limitada"))''',
        "EDU_INTERPRETATION_MM1C",
    )

    # 10 - M/M/s/c (capacidad total)
    p = pages / "10_Modelo_MMsc.py"
    ensure_import(p, "interpret_mmsk, to_markdown")
    insert_before(
        p,
        ["st.markdown('## 5. Reto de destreza')", 'st.markdown("## 5. Reto de destreza")'],
        '''# EDU_INTERPRETATION_MMSC
r_interpretacion = dict(r)
r_interpretacion.setdefault("s", s)
r_interpretacion.setdefault("K", cap)
r_interpretacion.setdefault("lambda_efectiva", r.get("lambda_eff", r.get("lambda", 0.0)))
st.markdown(to_markdown(interpret_mmsk(r_interpretacion), title="🧠 Interpretación de tu sistema con capacidad total limitada"))''',
        "EDU_INTERPRETATION_MMSC",
    )

    # 12 - Erlang B / M/M/c/c
    p = pages / "12_Modelo_MMcc.py"
    ensure_import(p, "interpret_erlang_b, to_markdown")
    insert_before(
        p,
        ["st.markdown('## 6. Reto de destreza')", 'st.markdown("## 6. Reto de destreza")'],
        '''# EDU_INTERPRETATION_ERLANG_B
st.markdown(to_markdown(interpret_erlang_b(r, cs), title="🧠 Interpretación de tu sistema sin cola"))''',
        "EDU_INTERPRETATION_ERLANG_B",
    )

    # 14 - M/G/1
    p = pages / "14_Modelo_MG1.py"
    ensure_import(p, "interpret_mg1, to_markdown")
    insert_before(
        p,
        ["st.markdown('## 6. Reto de destreza')", 'st.markdown("## 6. Reto de destreza")'],
        '''# EDU_INTERPRETATION_MG1
st.markdown(to_markdown(interpret_mg1(r, cv, time_unit="minutes"), title="🧠 Interpretación: capacidad + variabilidad"))''',
        "EDU_INTERPRETATION_MG1",
    )

    # 16 - D/D/1
    p = pages / "16_Modelo_Determinista.py"
    ensure_import(p, "interpret_dd1, to_markdown")
    insert_before(
        p,
        ["st.markdown('## 6. Reto de destreza')", 'st.markdown("## 6. Reto de destreza")'],
        '''# EDU_INTERPRETATION_DD1
st.markdown(
    to_markdown(
        interpret_dd1(
            T,
            S,
            float(df["Espera"].mean()),
            float(df.iloc[-1]["Espera"]),
        ),
        title="🧠 Interpretación del flujo determinista",
    )
)''',
        "EDU_INTERPRETATION_DD1",
    )

    # 18 - Casos prácticos aplicados
    p = pages / "18_Casos_Practicos_Aplicados.py"
    ensure_import(p, "interpret_dd1, interpret_mms, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 2. Qué debe demostrar el estudiante")'],
        '''# EDU_INTERPRETATION_CASES
if caso in {"🏥 Emergencias hospitalarias", "🏦 Ventanillas bancarias"}:
    st.markdown(
        to_markdown(
            interpret_mms(r, s),
            title=f"🧠 Interpretación del caso: {caso}",
        )
    )
else:
    st.markdown(
        to_markdown(
            interpret_dd1(
                T,
                S,
                float(df["Espera (min)"].mean()),
                float(df.iloc[-1]["Espera (min)"]),
            ),
            title="🧠 Interpretación del caso de producción",
        )
    )''',
        "EDU_INTERPRETATION_CASES",
    )

    # 19 - Colas simples aplicadas
    p = pages / "19_Modelos_Colas_Simples.py"
    ensure_import(p, "interpret_mm1, interpret_mms, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 3. ¿Qué cambia si modificas la dotación?")'],
        '''# EDU_INTERPRETATION_SIMPLE_APPLIED
lectura_simple = interpret_mm1(r) if servidores == 1 else interpret_mms(r, servidores)
st.markdown(to_markdown(lectura_simple, title="🧠 Interpretación completa del escenario"))''',
        "EDU_INTERPRETATION_SIMPLE_APPLIED",
    )

    # 20 - Capacidad finita aplicada
    p = pages / "20_Modelos_Colas_Complejas.py"
    ensure_import(p, "interpret_mmsk, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 3. ¿Dónde pasa el tiempo el sistema?")'],
        '''# EDU_INTERPRETATION_COMPLEX
st.markdown(to_markdown(interpret_mmsk(r), title="🧠 Interpretación operativa de tu escenario"))''',
        "EDU_INTERPRETATION_COMPLEX",
    )

    # 21 - Comparador de modelos
    p = pages / "21_Comparador_Modelos.py"
    ensure_import(p, "interpret_comparison, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 4. Interpreta la decisión")'],
        '''# EDU_INTERPRETATION_COMPARISON
if len(df) == 2:
    st.markdown(
        to_markdown(
            interpret_comparison(
                df.iloc[0].to_dict(),
                df.iloc[1].to_dict(),
                meta_wq,
                meta_bloqueo,
            ),
            title="🧠 Cómo comparar correctamente las dos alternativas",
        )
    )''',
        "EDU_INTERPRETATION_COMPARISON",
    )

    # 22 - Análisis económico
    p = pages / "22_Analisis_Economico.py"
    ensure_import(p, "interpret_economic, to_markdown")
    insert_before(
        p,
        ['with st.expander("Ver tabla económica completa"):', "with st.expander('Ver tabla económica completa'):"] ,
        '''# EDU_INTERPRETATION_ECONOMIC
if not cumple.empty:
    st.markdown(
        to_markdown(
            interpret_economic(
                float(recomendado["Costo personal"]),
                float(recomendado["Costo espera"]),
                float(recomendado["Costo total"]),
                int(recomendado["Operadores"]),
                float(recomendado["Espera (min)"]),
            ),
            title="🧠 ¿Por qué esta alternativa resulta conveniente?",
        )
    )''',
        "EDU_INTERPRETATION_ECONOMIC",
    )

    # 23 - Dimensionamiento de servidores
    p = pages / "23_Dimensionamiento_Servidores.py"
    ensure_import(p, "interpret_mms, to_markdown")
    insert_before(
        p,
        ['st.markdown("## 3. Curva de servicio")'],
        '''# EDU_INTERPRETATION_DIMENSIONING
st.markdown(to_markdown(interpret_mms(r_actual, int(actual)), title="🧠 Interpretación de la dotación actual"))''',
        "EDU_INTERPRETATION_DIMENSIONING",
    )

    # 25 - End-to-End: interpretación de la situación actual y de la alternativa elegida
    p = pages / "25_Analisis_End_to_End.py"
    ensure_import(p, "interpret_economic, interpret_mms, to_markdown")
    insert_before(
        p,
        ['st.markdown("### 2. Curva de espera según capacidad")'],
        '''# EDU_INTERPRETATION_END_TO_END_CURRENT
st.markdown(
    to_markdown(
        interpret_mms(actual, r["operadores_actuales"]),
        title="🧠 Cómo leer la situación actual",
    )
)''',
        "EDU_INTERPRETATION_END_TO_END_CURRENT",
    )
    insert_before(
        p,
        ['with st.expander("Ver todas las alternativas"):', "with st.expander('Ver todas las alternativas'):"] ,
        '''# EDU_INTERPRETATION_END_TO_END_RECOMMENDED
r_recomendado = mms_from_minutes(r["t_llegada"], r["t_atencion"], int(rec["servers"]))
st.markdown(
    to_markdown(
        interpret_mms(r_recomendado, int(rec["servers"])),
        title="🧠 Qué cambia con la configuración seleccionada",
    )
)
if math.isfinite(rec["cost_total"]):
    st.markdown(
        to_markdown(
            interpret_economic(
                rec["cost_staff"],
                rec["cost_wait"],
                rec["cost_total"],
                int(rec["servers"]),
                rec["Wq_min"],
            ),
            title="💰 Cómo interpretar el resultado económico",
        )
    )''',
        "EDU_INTERPRETATION_END_TO_END_RECOMMENDED",
    )

    print("Capa educativa aplicada correctamente.")


if __name__ == "__main__":
    main()
