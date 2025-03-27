# Archivo: 17_Evaluacion_Determinista.py
import streamlit as st

st.set_page_config(page_title="17 - Evaluación Modelo Determinista", layout="centered")
st.title("✍️ 17. Evaluación del Modelo Determinista (D/D/1)")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Pon a prueba tu comprensión del modelo **D/D/1**, un sistema sin variabilidad en llegadas ni servicios.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué caracteriza al modelo determinista D/D/1?",
             ("Llegadas y servicios aleatorios", "Llegadas deterministas, servicio aleatorio", "Llegadas y servicios constantes", "1 cliente en espera máximo"))
if p1 == "Llegadas y servicios constantes":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Cuál es la fórmula de la tasa de llegada λ si el tiempo entre llegadas es T?",
             ("λ = T", "λ = 1 / T", "λ = T / 60", "λ = T²"))
if p2 == "λ = 1 / T":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué sucede si ρ > 1 en un sistema D/D/1?",
             ("La cola desaparece", "El sistema se estabiliza", "La cola crece indefinidamente", "La tasa de llegada disminuye"))
if p3 == "La cola crece indefinidamente":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("Si el tiempo de servicio es S, ¿cuál es la tasa de servicio μ?",
             ("μ = S", "μ = 1 / S", "μ = S × T", "μ = 1 / T"))
if p4 == "μ = 1 / S":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si T = 3 min y S = 2 min, ¿cuál es la utilización ρ?",
             ("0.67", "1.5", "2.0", "0.25"))
if p5 == "0.67":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo D/D/1.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes reforzar algunos puntos.")
    else:
        st.error("Revisa el modelo determinista para mejorar tu comprensión.")
