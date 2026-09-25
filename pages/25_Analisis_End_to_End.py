import streamlit as st
import math
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="25 - Análisis End-to-End", page_icon="🧭", layout="wide")

st.title("🧭 25. Análisis End-to-End de Sistemas de Colas")
st.caption("Del problema real a una recomendación operativa y económica en una sola experiencia.")

st.info(
    "Este módulo integra selección del modelo, diagnóstico AS IS, generación de escenarios TO BE, "
    "evaluación económica y recomendación. Está pensado para conectar la teoría de colas con la "
    "toma de decisiones en Ingeniería Industrial."
)

# -------------------------------------------------------------------
# Funciones de cálculo
# -------------------------------------------------------------------
def _safe_div(a, b):
    if b == 0:
        return float("inf")
    return a / b


def mm1(lam, mu):
    rho = lam / mu
    if rho >= 1:
        return {
            "modelo": "M/M/1",
            "estable": False,
            "rho": rho,
            "L": float("inf"),
            "Lq": float("inf"),
            "W": float("inf"),
            "Wq": float("inf"),
            "P_bloqueo": 0.0,
            "lambda_efectiva": lam,
        }

    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)
    W = 1 / (mu - lam)
    Wq = lam / (mu * (mu - lam))
    return {
        "modelo": "M/M/1",
        "estable": True,
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_bloqueo": 0.0,
        "lambda_efectiva": lam,
    }


def mms(lam, mu, s):
    rho = lam / (s * mu)
    if rho >= 1:
        return {
            "modelo": "M/M/s",
            "estable": False,
            "rho": rho,
            "L": float("inf"),
            "Lq": float("inf"),
            "W": float("inf"),
            "Wq": float("inf"),
            "P_bloqueo": 0.0,
            "lambda_efectiva": lam,
        }

    r = lam / mu
    suma = sum((r**n) / math.factorial(n) for n in range(s))
    parte = (r**s) / (math.factorial(s) * (1 - rho))
    p0 = 1 / (suma + parte)
    Lq = (p0 * (r**s) * rho) / (math.factorial(s) * ((1 - rho) ** 2))
    L = Lq + r
    Wq = Lq / lam
    W = Wq + 1 / mu

    return {
        "modelo": "M/M/s",
        "estable": True,
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_bloqueo": 0.0,
        "lambda_efectiva": lam,
    }


def mm1k(lam, mu, k):
    rho_nominal = lam / mu

    if abs(rho_nominal - 1.0) < 1e-12:
        probs = [1 / (k + 1)] * (k + 1)
    else:
        p0 = (1 - rho_nominal) / (1 - rho_nominal ** (k + 1))
        probs = [p0 * (rho_nominal**n) for n in range(k + 1)]

    p_bloqueo = probs[-1]
    lam_eff = lam * (1 - p_bloqueo)
    L = sum(n * probs[n] for n in range(k + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = _safe_div(L, lam_eff)
    Wq = _safe_div(Lq, lam_eff)
    rho_efectiva = ocupados

    return {
        "modelo": "M/M/1/K",
        "estable": True,
        "rho": rho_efectiva,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_bloqueo": p_bloqueo,
        "lambda_efectiva": lam_eff,
    }


def mmsk(lam, mu, s, k):
    if k < s:
        raise ValueError("La capacidad total K debe ser mayor o igual al número de servidores.")

    r = lam / mu
    terms = []
    for n in range(k + 1):
        if n < s:
            term = (r**n) / math.factorial(n)
        else:
            term = (r**n) / (math.factorial(s) * (s ** (n - s)))
        terms.append(term)

    p0 = 1 / sum(terms)
    probs = [p0 * t for t in terms]
    p_bloqueo = probs[-1]
    lam_eff = lam * (1 - p_bloqueo)
    L = sum(n * probs[n] for n in range(k + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = _safe_div(L, lam_eff)
    Wq = _safe_div(Lq, lam_eff)
    rho_efectiva = _safe_div(ocupados, s)

    return {
        "modelo": "M/M/s/K",
        "estable": True,
        "rho": rho_efectiva,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_bloqueo": p_bloqueo,
        "lambda_efectiva": lam_eff,
    }


def seleccionar_modelo(s, capacidad_limitada):
    if s == 1 and not capacidad_limitada:
        return "M/M/1"
    if s > 1 and not capacidad_limitada:
        return "M/M/s"
    if s == 1 and capacidad_limitada:
        return "M/M/1/K"
    return "M/M/s/K"


def calcular_modelo(lam, mu, s, capacidad_limitada=False, k=None):
    modelo = seleccionar_modelo(s, capacidad_limitada)
    if modelo == "M/M/1":
        return mm1(lam, mu)
    if modelo == "M/M/s":
        return mms(lam, mu, s)
    if modelo == "M/M/1/K":
        return mm1k(lam, mu, int(k))
    return mmsk(lam, mu, int(s), int(k))


def costo_escenario(resultado, s, costo_servidor, costo_espera, costo_perdido):
    if not resultado["estable"] or not math.isfinite(resultado["Lq"]):
        return float("inf")

    costo_capacidad = s * costo_servidor
    costo_espera_total = resultado["Lq"] * costo_espera
    if resultado["P_bloqueo"] < 1:
        lambda_original = resultado["lambda_efectiva"] / max(1e-12, 1 - resultado["P_bloqueo"])
        clientes_perdidos_h = max(0.0, lambda_original - resultado["lambda_efectiva"])
    else:
        clientes_perdidos_h = float("inf")
    costo_perdida_total = clientes_perdidos_h * costo_perdido
    return costo_capacidad + costo_espera_total + costo_perdida_total


def diagnostico(resultado, max_rho, max_wq_min):
    if not resultado["estable"] or not math.isfinite(resultado["Wq"]):
        return "Crítico", "El sistema es inestable con la configuración actual: la demanda supera la capacidad de servicio."

    rho_pct = resultado["rho"] * 100
    wq_min = resultado["Wq"] * 60

    if rho_pct > max_rho or wq_min > max_wq_min:
        return (
            "Atención",
            f"El sistema opera con {rho_pct:.1f}% de utilización y una espera promedio de "
            f"{wq_min:.1f} min. Se recomienda evaluar capacidad o velocidad de servicio.",
        )

    return (
        "Adecuado",
        f"El sistema cumple los umbrales definidos: utilización {rho_pct:.1f}% y "
        f"espera promedio {wq_min:.1f} min.",
    )


def clean_pdf_text(text):
    return str(text).encode("latin-1", "ignore").decode("latin-1")


def generar_pdf(datos, asis, escenarios_df, recomendado, diagnostico_texto):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_pdf_text("Análisis End-to-End de Teoría de Colas"), ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        clean_pdf_text(
            f"Contexto: {datos['contexto']}\n"
            f"Sistema analizado: {datos['nombre']}\n"
            f"Descripción: {datos['descripcion']}"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("1. Modelo seleccionado"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        clean_pdf_text(
            f"Modelo: {asis['modelo']}\n"
            f"Lambda: {datos['lambda']:.2f} clientes/hora\n"
            f"Mu: {datos['mu']:.2f} clientes/hora por servidor\n"
            f"Servidores: {datos['servidores']}\n"
            f"Capacidad limitada: {'Sí' if datos['capacidad_limitada'] else 'No'}"
            + (f"\nCapacidad total K: {datos['K']}" if datos["capacidad_limitada"] else "")
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("2. Diagnóstico AS IS"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        clean_pdf_text(
            f"Utilización: {asis['rho']*100:.2f}%\n"
            f"L: {asis['L']:.2f}\n"
            f"Lq: {asis['Lq']:.2f}\n"
            f"W: {asis['W']*60:.2f} min\n"
            f"Wq: {asis['Wq']*60:.2f} min\n"
            f"Probabilidad de bloqueo: {asis['P_bloqueo']*100:.2f}%\n"
            f"Diagnóstico: {diagnostico_texto}"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("3. Escenarios evaluados"), ln=True)
    pdf.set_font("Arial", "", 9)

    top = escenarios_df.sort_values("Costo total (S//h)").head(8)
    for _, row in top.iterrows():
        pdf.multi_cell(
            0,
            5,
            clean_pdf_text(
                f"- s={int(row['Servidores'])}, mejora mu={row['Mejora servicio']}: "
                f"rho={row['Utilización %']:.1f}%, Wq={row['Wq (min)']:.2f} min, "
                f"costo={row['Costo total (S//h)']:.2f}"
            ),
        )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("4. Recomendación"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        clean_pdf_text(
            f"Configuración recomendada: {int(recomendado['Servidores'])} servidor(es), "
            f"mejora de servicio {recomendado['Mejora servicio']}.\n"
            f"Utilización: {recomendado['Utilización %']:.1f}%\n"
            f"Wq: {recomendado['Wq (min)']:.2f} min\n"
            f"Costo total: S/ {recomendado['Costo total (S//h)']:.2f} por hora."
        ),
    )

    return bytes(pdf.output(dest="S").encode("latin-1"))


# -------------------------------------------------------------------
# Entrada del problema
# -------------------------------------------------------------------
with st.expander("1️⃣ Definir el problema real", expanded=True):
    col_a, col_b = st.columns(2)

    with col_a:
        contexto = st.selectbox(
            "Contexto de aplicación",
            ["Banco", "Hospital / clínica", "Call center", "Logística", "Producción", "Servicios", "Otro"],
        )
        nombre = st.text_input("Nombre del sistema", value="Sistema de atención")
        descripcion = st.text_area(
            "Descripción breve del problema",
            value="Se desea evaluar el desempeño actual del sistema y determinar una configuración de servicio más conveniente.",
            height=100,
        )

    with col_b:
        lam = st.number_input("λ - Tasa de llegada (clientes/hora)", min_value=0.01, value=12.0, step=0.5)
        mu = st.number_input(
            "μ - Tasa de servicio por servidor (clientes/hora)",
            min_value=0.01,
            value=8.0,
            step=0.5,
        )
        s_actual = st.number_input("Número actual de servidores", min_value=1, value=2, step=1)
        capacidad_limitada = st.checkbox("El sistema tiene capacidad total limitada")
        K = None
        if capacidad_limitada:
            K = st.number_input(
                "K - Capacidad total del sistema (en servicio + en espera)",
                min_value=int(s_actual),
                value=max(int(s_actual), 10),
                step=1,
            )

with st.expander("2️⃣ Criterios económicos y de desempeño", expanded=True):
    c1, c2, c3 = st.columns(3)

    with c1:
        costo_servidor = st.number_input("Costo por servidor (S/ por hora)", min_value=0.0, value=20.0, step=1.0)
        costo_espera = st.number_input(
            "Costo de espera (S/ por cliente-hora)",
            min_value=0.0,
            value=12.0,
            step=1.0,
            help="Costo económico estimado por mantener un cliente esperando durante una hora.",
        )

    with c2:
        costo_perdido = st.number_input(
            "Costo por cliente perdido (S/)",
            min_value=0.0,
            value=30.0,
            step=1.0,
            help="Se aplica en sistemas con capacidad limitada cuando existe bloqueo.",
        )
        objetivo_wq = st.number_input(
            "Espera máxima deseada Wq (min)",
            min_value=0.0,
            value=10.0,
            step=1.0,
        )

    with c3:
        max_rho = st.slider("Utilización máxima deseada (%)", min_value=50, max_value=99, value=90)
        max_extra_servers = st.slider(
            "Servidores adicionales a explorar",
            min_value=1,
            max_value=6,
            value=3,
        )

st.markdown("---")
ejecutar = st.button("🚀 Ejecutar análisis End-to-End", type="primary", use_container_width=True)

if ejecutar:
    try:
        asis = calcular_modelo(
            lam=lam,
            mu=mu,
            s=int(s_actual),
            capacidad_limitada=capacidad_limitada,
            k=K,
        )

        modelo_sugerido = seleccionar_modelo(int(s_actual), capacidad_limitada)

        st.subheader("3️⃣ Selección del modelo")
        st.success(f"Modelo sugerido automáticamente: **{modelo_sugerido}**")
        if capacidad_limitada:
            st.caption(
                "Se selecciona un modelo con capacidad finita porque el sistema admite un máximo total de clientes."
            )
        else:
            st.caption(
                "Se selecciona un modelo con capacidad de espera no limitada dentro del supuesto analítico."
            )

        st.subheader("4️⃣ Diagnóstico AS IS")
        if not asis["estable"] or not math.isfinite(asis["Wq"]):
            st.error(
                "La configuración actual es inestable. Para modelos con capacidad infinita, "
                "la utilización debe ser menor que 100%."
            )
        else:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Utilización", f"{asis['rho']*100:.1f}%")
            m2.metric("L", f"{asis['L']:.2f}")
            m3.metric("Lq", f"{asis['Lq']:.2f}")
            m4.metric("W", f"{asis['W']*60:.2f} min")
            m5.metric("Wq", f"{asis['Wq']*60:.2f} min")

            if capacidad_limitada:
                st.metric("Probabilidad de bloqueo", f"{asis['P_bloqueo']*100:.2f}%")

        estado, texto_diag = diagnostico(asis, max_rho=max_rho, max_wq_min=objetivo_wq)
        if estado == "Crítico":
            st.error(texto_diag)
        elif estado == "Atención":
            st.warning(texto_diag)
        else:
            st.success(texto_diag)

        st.subheader("5️⃣ Escenarios TO BE")
        escenarios = []
        mejoras_servicio = [1.00, 1.10, 1.20]

        inicio_s = max(1, int(s_actual) - 1)
        fin_s = int(s_actual) + int(max_extra_servers)

        for s_eval in range(inicio_s, fin_s + 1):
            for factor in mejoras_servicio:
                mu_eval = mu * factor
                k_eval = None
                if capacidad_limitada:
                    k_eval = max(int(K), s_eval)

                resultado = calcular_modelo(
                    lam=lam,
                    mu=mu_eval,
                    s=s_eval,
                    capacidad_limitada=capacidad_limitada,
                    k=k_eval,
                )

                costo_total = costo_escenario(
                    resultado,
                    s=s_eval,
                    costo_servidor=costo_servidor,
                    costo_espera=costo_espera,
                    costo_perdido=costo_perdido,
                )

                if resultado["estable"] and math.isfinite(resultado["Wq"]) and math.isfinite(costo_total):
                    escenarios.append(
                        {
                            "Servidores": s_eval,
                            "Mejora servicio": f"+{int(round((factor-1)*100))}%",
                            "μ": round(mu_eval, 3),
                            "Utilización %": round(resultado["rho"] * 100, 2),
                            "L": round(resultado["L"], 3),
                            "Lq": round(resultado["Lq"], 3),
                            "W (min)": round(resultado["W"] * 60, 3),
                            "Wq (min)": round(resultado["Wq"] * 60, 3),
                            "Bloqueo %": round(resultado["P_bloqueo"] * 100, 3),
                            "Costo total (S//h)": round(costo_total, 2),
                        }
                    )

        if not escenarios:
            st.error("No fue posible generar escenarios factibles con los parámetros ingresados.")
            st.stop()

        df = pd.DataFrame(escenarios)
        st.dataframe(df, use_container_width=True, hide_index=True)

        graf1 = px.line(
            df,
            x="Servidores",
            y="Wq (min)",
            color="Mejora servicio",
            markers=True,
            title="Tiempo promedio de espera por configuración",
        )
        st.plotly_chart(graf1, use_container_width=True)

        graf2 = px.line(
            df,
            x="Servidores",
            y="Costo total (S//h)",
            color="Mejora servicio",
            markers=True,
            title="Costo total estimado por configuración",
        )
        st.plotly_chart(graf2, use_container_width=True)

        st.subheader("6️⃣ Recomendación TO BE")

        factibles = df[
            (df["Wq (min)"] <= objetivo_wq)
            & (df["Utilización %"] <= max_rho)
        ].copy()

        if not factibles.empty:
            recomendado = factibles.sort_values(
                ["Costo total (S//h)", "Wq (min)", "Servidores"]
            ).iloc[0]
            criterio = (
                "cumple el objetivo de espera y el límite de utilización definidos, "
                "con el menor costo total entre los escenarios factibles"
            )
        else:
            recomendado = df.sort_values(
                ["Wq (min)", "Costo total (S//h)", "Servidores"]
            ).iloc[0]
            criterio = (
                "ningún escenario cumplió simultáneamente todos los umbrales; "
                "se muestra la alternativa con menor espera"
            )
            st.warning(
                "No se encontró una configuración que cumpla simultáneamente todos los objetivos. "
                "La recomendación prioriza el menor tiempo de espera."
            )

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Servidores", int(recomendado["Servidores"]))
        r2.metric("Mejora μ", recomendado["Mejora servicio"])
        r3.metric("Wq", f"{recomendado['Wq (min)']:.2f} min")
        r4.metric("Costo", f"S/ {recomendado['Costo total (S//h)']:.2f}/h")

        st.success(
            f"**Recomendación:** evaluar una configuración con "
            f"**{int(recomendado['Servidores'])} servidor(es)** y una mejora de capacidad de servicio "
            f"de **{recomendado['Mejora servicio']}**. Esta alternativa {criterio}."
        )

        st.subheader("7️⃣ Comparación AS IS vs TO BE")
        if asis["estable"] and math.isfinite(asis["Wq"]):
            costo_asis = costo_escenario(
                asis,
                s=int(s_actual),
                costo_servidor=costo_servidor,
                costo_espera=costo_espera,
                costo_perdido=costo_perdido,
            )
            comp = pd.DataFrame(
                [
                    {
                        "Escenario": "AS IS",
                        "Servidores": int(s_actual),
                        "Utilización %": round(asis["rho"] * 100, 2),
                        "Wq (min)": round(asis["Wq"] * 60, 2),
                        "Lq": round(asis["Lq"], 2),
                        "Costo total (S//h)": round(costo_asis, 2),
                    },
                    {
                        "Escenario": "TO BE",
                        "Servidores": int(recomendado["Servidores"]),
                        "Utilización %": recomendado["Utilización %"],
                        "Wq (min)": recomendado["Wq (min)"],
                        "Lq": recomendado["Lq"],
                        "Costo total (S//h)": recomendado["Costo total (S//h)"],
                    },
                ]
            )
            st.dataframe(comp, use_container_width=True, hide_index=True)

            delta_wq = asis["Wq"] * 60 - float(recomendado["Wq (min)"])
            delta_costo = costo_asis - float(recomendado["Costo total (S//h)"])
            st.caption(
                f"Variación estimada: Wq cambia en {delta_wq:+.2f} min y el costo total "
                f"en S/ {delta_costo:+.2f} por hora (positivo = ahorro)."
            )

        datos_reporte = {
            "contexto": contexto,
            "nombre": nombre,
            "descripcion": descripcion,
            "lambda": lam,
            "mu": mu,
            "servidores": int(s_actual),
            "capacidad_limitada": capacidad_limitada,
            "K": int(K) if K is not None else None,
        }

        if asis["estable"] and math.isfinite(asis["Wq"]):
            pdf_bytes = generar_pdf(
                datos=datos_reporte,
                asis=asis,
                escenarios_df=df,
                recomendado=recomendado,
                diagnostico_texto=texto_diag,
            )
            st.download_button(
                "📄 Descargar informe End-to-End en PDF",
                data=pdf_bytes,
                file_name="analisis_end_to_end_teoria_colas.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📊 Descargar escenarios en CSV",
            data=csv_data,
            file_name="escenarios_teoria_colas.csv",
            mime="text/csv",
            use_container_width=True,
        )

        with st.expander("📚 Supuestos y uso pedagógico"):
            st.markdown(
                """
                - Las tasas de llegada y servicio se expresan por hora.
                - Para M/M/1 y M/M/s se requiere estabilidad (utilización menor que 1).
                - En modelos con capacidad finita se considera bloqueo cuando el sistema alcanza K.
                - Los costos son parámetros de decisión y deben ser definidos o estimados por el estudiante.
                - La recomendación automática es un apoyo al análisis; debe complementarse con el contexto operativo real.
                - El estudiante debe justificar si los supuestos probabilísticos del modelo representan adecuadamente el sistema estudiado.
                """
            )

    except Exception as exc:
        st.error(f"No fue posible completar el análisis: {exc}")
        st.caption("Revisa que λ, μ, servidores y capacidad K sean coherentes.")
