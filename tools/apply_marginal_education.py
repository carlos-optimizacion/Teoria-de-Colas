"""Mejora visualmente la interpretación y añade análisis marginal s-1/s/s+1.

No modifica fórmulas de los modelos. Reutiliza queue_core para calcular los
escenarios marginales y añade la lectura pedagógica debajo de los resultados.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ensure_import(path: Path, statement: str) -> None:
    text = path.read_text(encoding="utf-8")
    if statement in text:
        return
    anchor = "import streamlit as st\n"
    if anchor not in text:
        raise RuntimeError(f"No se encontró import de Streamlit en {path}")
    text = text.replace(anchor, anchor + statement + "\n", 1)
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
    raise RuntimeError(f"No se encontró marcador para {sentinel} en {path}")


def patch_core() -> None:
    path = ROOT / "interpretation_core.py"
    text = path.read_text(encoding="utf-8")

    start = text.index("def to_markdown(")
    end = text.index("# EDU_INTERPRETATION_COMPARISON_CORE")

    visual_function = r'''def to_markdown(lectura: dict, title: str = "🧠 Interpretación en lenguaje sencillo") -> str:
    """Convierte una interpretación en bloques Markdown visuales y homogéneos."""
    return f"""
### {title}

> 🔎 **1. ¿Qué está pasando?**  
> {lectura['que_pasa']}

> 🧩 **2. ¿Por qué ocurre?**  
> {lectura['por_que']}

> 🏭 **3. ¿Qué significa operativamente?**  
> {lectura['operacion']}

> 🔧 **4. ¿Qué podrías cambiar?**  
> {lectura['accion']}

> 🎓 **5. ¿Qué debes aprender de este escenario?**  
> {lectura['aprendizaje']}
"""


# EDU_MARGINAL_MMS_CORE
def marginal_mms_analysis(t_llegada_min: float, t_atencion_min: float, s_actual: int):
    """Compara s-1, s y s+1 en M/M/s usando el motor matemático compartido."""
    from queue_core import mms_from_minutes

    if s_actual < 1:
        raise ValueError("s_actual debe ser al menos 1.")

    servidores = sorted({max(1, s_actual - 1), s_actual, s_actual + 1})
    rows = []
    for s in servidores:
        r = mms_from_minutes(t_llegada_min, t_atencion_min, s)
        rows.append({
            "s": s,
            "rol": "Actual" if s == s_actual else ("s−1" if s < s_actual else "s+1"),
            "estable": r["estable"],
            "rho": r["rho"],
            "p_wait": r["P_espera"],
            "wq_min": r["Wq"] * 60 if r["estable"] and math.isfinite(r["Wq"]) else float("inf"),
            "lq": r["Lq"] if r["estable"] and math.isfinite(r["Lq"]) else float("inf"),
        })

    actual = next(row for row in rows if row["s"] == s_actual)
    prev = next((row for row in rows if row["s"] == s_actual - 1), None)
    nxt = next(row for row in rows if row["s"] == s_actual + 1)

    mensajes = []
    if prev is not None:
        if not prev["estable"] and actual["estable"]:
            mensajes.append(
                f"Con un servidor menos (s={prev['s']}) el sistema se vuelve inestable; la dotación actual cruza el umbral mínimo de capacidad estable."
            )
        elif prev["estable"] and actual["estable"]:
            aumento = prev["wq_min"] - actual["wq_min"]
            pct = (aumento / actual["wq_min"] * 100) if actual["wq_min"] > 1e-12 else float("inf")
            if math.isfinite(pct):
                mensajes.append(
                    f"Quitar un servidor elevaría Wq en {aumento:.1f} min ({pct:.0f}% respecto al escenario actual)."
                )
            else:
                mensajes.append(f"Quitar un servidor elevaría Wq en {aumento:.1f} min.")

    if not actual["estable"]:
        if nxt["estable"]:
            mensajes.append(
                f"La dotación actual es inestable, pero s+1={nxt['s']} sí alcanza estabilidad con Wq≈{nxt['wq_min']:.1f} min."
            )
        else:
            mensajes.append("Ni la dotación actual ni un servidor adicional logran estabilidad; se requiere revisar un rango mayor de capacidad o el tiempo de servicio.")
    elif nxt["estable"]:
        reduccion = actual["wq_min"] - nxt["wq_min"]
        pct = (reduccion / actual["wq_min"] * 100) if actual["wq_min"] > 1e-12 else 0.0
        mensajes.append(
            f"Agregar un servidor reduce Wq en {reduccion:.1f} min ({pct:.0f}%). Esta es la ganancia marginal de pasar de s={s_actual} a s={nxt['s']}."
        )
        if pct < 20:
            mensajes.append("La mejora adicional es relativamente pequeña: aparece una señal de rendimientos marginales decrecientes en capacidad.")
        elif pct >= 50:
            mensajes.append("La reducción es fuerte: todavía existe una ganancia marginal importante al ampliar capacidad.")

    return {"rows": rows, "insight": " ".join(mensajes)}


def marginal_mms_markdown(t_llegada_min: float, t_atencion_min: float, s_actual: int, title: str = "🔬 Análisis marginal de capacidad") -> str:
    """Presenta s-1/s/s+1 sin sustituir el análisis matemático principal."""
    data = marginal_mms_analysis(t_llegada_min, t_atencion_min, s_actual)

    lines = [
        f"### {title}",
        "",
        "Compara la dotación actual con una unidad menos y una unidad más. La tabla usa exactamente el mismo modelo M/M/s.",
        "",
        "| Escenario | Servidores | Estado | Utilización | P(espera) | Wq | Lq |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in data["rows"]:
        estado = "Estable" if row["estable"] else "Inestable"
        wq = f"{row['wq_min']:.1f} min" if row["estable"] else "∞"
        lq = f"{row['lq']:.2f}" if row["estable"] else "∞"
        lines.append(
            f"| **{row['rol']}** | {row['s']} | {estado} | {row['rho']*100:.1f}% | {row['p_wait']*100:.1f}% | {wq} | {lq} |"
        )

    lines.extend([
        "",
        f"> 📌 **Lectura marginal:** {data['insight']}",
        "",
        "> 💡 **Cómo usarlo:** una gran caída de Wq al pasar a s+1 indica que la capacidad adicional todavía aporta mucho. Si la reducción es pequeña, conviene contrastar el beneficio con el costo antes de agregar recursos.",
    ])
    return "\n".join(lines)


'''

    text = text[:start] + visual_function + text[end:]
    path.write_text(text, encoding="utf-8")


def patch_pages() -> None:
    pages = ROOT / "pages"
    statement = "from interpretation_core import marginal_mms_markdown"

    targets = []

    # 04 - M/M/s
    p = pages / "04_Modelo_MMs_Teoria_Ejemplo.py"
    ensure_import(p, statement)
    targets.append((
        p,
        ['st.markdown("## 6. Reto de destreza: encuentra la dotación")'],
        '''# EDU_MARGINAL_MMS_04
st.markdown(marginal_mms_markdown(t_llegada, t_atencion, servidores))''',
        "EDU_MARGINAL_MMS_04",
    ))

    # 18 - Casos hospital/banca
    p = pages / "18_Casos_Practicos_Aplicados.py"
    ensure_import(p, statement)
    targets.append((
        p,
        ['st.markdown("## 2. Qué debe demostrar el estudiante")'],
        '''# EDU_MARGINAL_MMS_18
if caso in {"🏥 Emergencias hospitalarias", "🏦 Ventanillas bancarias"}:
    st.markdown(marginal_mms_markdown(t_llegada, t_atencion, s, title="🔬 ¿Qué pasa con un recurso menos o uno más?"))''',
        "EDU_MARGINAL_MMS_18",
    ))

    # 19 - laboratorio simple
    p = pages / "19_Modelos_Colas_Simples.py"
    ensure_import(p, statement)
    targets.append((
        p,
        ['st.markdown("## 3. ¿Qué cambia si modificas la dotación?")'],
        '''# EDU_MARGINAL_MMS_19
st.markdown(marginal_mms_markdown(t_llegada, t_atencion, servidores, title="🔬 Efecto marginal de cambiar la dotación"))''',
        "EDU_MARGINAL_MMS_19",
    ))

    # 22 - alternativa económica recomendada
    p = pages / "22_Analisis_Economico.py"
    ensure_import(p, statement)
    targets.append((
        p,
        ['with st.expander("Ver tabla económica completa"):', "with st.expander('Ver tabla económica completa'):"] ,
        '''# EDU_MARGINAL_MMS_22
if not cumple.empty:
    st.markdown(
        marginal_mms_markdown(
            t_llegada,
            t_atencion,
            int(recomendado["Operadores"]),
            title="🔬 Sensibilidad alrededor de la alternativa económica",
        )
    )''',
        "EDU_MARGINAL_MMS_22",
    ))

    # 23 - dimensionamiento
    p = pages / "23_Dimensionamiento_Servidores.py"
    ensure_import(p, statement)
    targets.append((
        p,
        ['st.markdown("## 3. Curva de servicio")'],
        '''# EDU_MARGINAL_MMS_23
st.markdown(marginal_mms_markdown(t_llegada, t_atencion, int(actual), title="🔬 Sensibilidad de la dotación actual"))''',
        "EDU_MARGINAL_MMS_23",
    ))

    # 25 - End-to-End
    p = pages / "25_Analisis_End_to_End.py"
    ensure_import(p, statement)
    targets.append((
        p,
        ['st.markdown("### 2. Curva de espera según capacidad")'],
        '''# EDU_MARGINAL_MMS_25
st.markdown(
    marginal_mms_markdown(
        r["t_llegada"],
        r["t_atencion"],
        int(r["operadores_actuales"]),
        title="🔬 Sensibilidad inmediata de la capacidad actual",
    )
)''',
        "EDU_MARGINAL_MMS_25",
    ))

    for args in targets:
        insert_before(*args)


def main() -> None:
    patch_core()
    patch_pages()
    print("Mejora visual y análisis marginal aplicados correctamente.")


if __name__ == "__main__":
    main()
