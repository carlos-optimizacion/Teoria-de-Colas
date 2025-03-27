# Archivo: 15_Evaluacion_MG1.py
import streamlit as st

st.set_page_config(page_title="15 - Evaluación M/G/1", layout="centered")
st.title("✍️ 15. Evaluación del Modelo M/G/1")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Responde esta autoevaluación para comprobar tu comprensión del modelo **M/G/1**, que permite tiempos de servicio con distribución general.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué característica distingue al modelo M/G/1 de otros modelos?",
             ("Llegadas con distribución normal", "Servicios exponenciales", "Un solo servidor con servicio general", "Cola con capacidad finita"))
if p1 == "Un solo servidor con servicio general":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Qué fórmula se utiliza para calcular Lq en M/G/1?",
             ("Lq = λ²·σ² / (2·(1−ρ))", "Lq = ρ / (1−ρ)", "Lq = λ / (μ−λ)", "Lq = λ·μ / (μ−λ)"))
if p2 == "Lq = λ²·σ² / (2·(1−ρ))":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué representa σ² en el modelo?",
             ("Media del tiempo de espera", "Tasa de llegada", "Varianza del tiempo de servicio", "Utilización del sistema"))
if p3 == "Varianza del tiempo de servicio":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Cuál es la condición de estabilidad del modelo?",
             ("λ < 1", "μ < λ", "ρ < 1", "σ² < 1"))
if p4 == "ρ < 1":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si λ = 2 y 𝔼[S] = 0.4, ¿cuánto vale ρ?",
             ("0.8", "1.5", "0.4", "2.4"))
if p5 == "0.8":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/G/1.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes reforzar algunos conceptos.")
    else:
        st.error("Revisa nuevamente la teoría del modelo con servicio general.")
