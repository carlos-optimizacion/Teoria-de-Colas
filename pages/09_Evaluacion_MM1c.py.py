# Archivo: 09_Evaluacion_MM1c.py
import streamlit as st

st.set_page_config(page_title="09 - Evaluación M/M/1/c", layout="centered")
st.title("✍️ 09. Evaluación del Modelo M/M/1/c")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Responde esta autoevaluación para medir tu comprensión del modelo **M/M/1/c**, que incluye una cola con capacidad limitada.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué representa la letra 'c' en el modelo M/M/1/c?",
             ("Número de clientes atendidos", "Tasa de llegada", "Capacidad de la cola", "Cantidad de servidores"))
if p1 == "Capacidad de la cola":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Qué sucede si un cliente llega cuando ya hay c personas en cola?",
             ("Se va sin ser atendido", "Ingresa igual", "Es atendido de inmediato", "Disminuye \( \lambda \)"))
if p2 == "Se va sin ser atendido":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué distribución tiene el tiempo entre llegadas?",
             ("Normal", "Exponencial (\( \lambda \))", "Uniforme", "Binomial"))
if p3 == "Exponencial (\( \lambda \))":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Cuál es el significado de \( \rho \) en el modelo?",
             ("Clientes promedio", "Tiempo de espera", "Utilización del sistema", "Probabilidad de rechazo"))
if p4 == "Utilización del sistema":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si \( \lambda = 2 \) y \( \mu = 4 \), ¿cuál es \( \rho \)?",
             ("0.25", "0.5", "1.5", "2"))
if p5 == "0.5":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/M/1/c.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes repasar algunos puntos.")
    else:
        st.error("Te recomendamos revisar nuevamente el modelo de cola limitada.")
