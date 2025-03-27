# Archivo: 03_Evaluacion_MM1.py
import streamlit as st

st.set_page_config(page_title="03 - Evaluación M/M/1", layout="centered")
st.title("✍️ 03. Evaluación del Modelo M/M/1")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Esta autoevaluación tiene como objetivo verificar tu comprensión del modelo **M/M/1**.
Responde las siguientes preguntas y obtendrás tu puntaje al final.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué distribución representa el tiempo entre llegadas en un modelo M/M/1?",
             ("Normal", "Exponencial", "Uniforme", "Gamma"))
if p1 == "Exponencial":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Qué representa la letra ρ (rho) en el modelo M/M/1?",
             ("El tiempo de espera promedio", "La tasa de llegada", "El nivel de utilización", "El número de servidores"))
if p2 == "El nivel de utilización":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Cuál de estas condiciones debe cumplirse para que el sistema M/M/1 sea estable?",
             ("λ = μ", "λ > μ", "λ < μ", "μ = 0"))
if p3 == "λ < μ":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Cuál es la fórmula para calcular el número promedio de clientes en la cola (Lq)?",
             ("ρ / (1 - ρ)", "ρ² / (1 - ρ)", "1 / (μ - λ)", "λ / μ"))
if p4 == "ρ² / (1 - ρ)":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si λ = 4 clientes/hora y μ = 5 clientes/hora, ¿cuál es la utilización (ρ)?",
             ("0.8", "1.25", "0.5", "0.2"))
if p5 == "0.8":
    total += 1

st.markdown("---")

# Mostrar resultado
if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/M/1.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes repasar algunos conceptos para afianzar.")
    else:
        st.error("Te recomendamos revisar nuevamente la teoría del modelo M/M/1.")

