# Archivo: 05_Evaluacion_MMs.py
import streamlit as st

st.set_page_config(page_title="05 - Evaluación M/M/s", layout="centered")
st.title("✍️ 05. Evaluación del Modelo M/M/s")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Responde esta autoevaluación para comprobar tu comprensión del modelo **M/M/s**.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué significa la 's' en el modelo M/M/s?",
             ("Número de clientes", "Tamaño de la cola", "Cantidad de servidores", "Tiempo de servicio"))
if p1 == "Cantidad de servidores":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Cuál es la fórmula para la utilización en M/M/s?",
             ("λ / μ", "λ / (s × μ)", "s × μ / λ", "1 - (λ / μ)"))
if p2 == "λ / (s × μ)":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué ocurre si ρ ≥ 1 en un sistema M/M/s?",
             ("El sistema es estable", "La utilización es baja", "Se acumulan clientes indefinidamente", "Se reduce el tiempo de espera"))
if p3 == "Se acumulan clientes indefinidamente":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Qué representa Lq en el modelo?",
             ("Clientes en el sistema", "Tiempo de atención", "Clientes promedio en cola", "Número de servidores libres"))
if p4 == "Clientes promedio en cola":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si λ = 10, μ = 5 y s = 3, ¿cuál es la utilización?",
             ("0.67", "0.50", "1.25", "0.33"))
if p5 == "0.67":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/M/s.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes repasar algunos conceptos.")
    else:
        st.error("Te recomendamos revisar nuevamente la teoría del modelo M/M/s.")
