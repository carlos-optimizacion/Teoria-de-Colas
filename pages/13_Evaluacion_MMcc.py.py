# Archivo: 13_Evaluacion_MMcc.py
import streamlit as st

st.set_page_config(page_title="13 - Evaluación M/M/c/c", layout="centered")
st.title("✍️ 13. Evaluación del Modelo M/M/c/c")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Evalúa tu comprensión del modelo **M/M/c/c**, caracterizado por un sistema sin cola donde los clientes son bloqueados si todos los servidores están ocupados.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Cuál es la principal característica del modelo M/M/c/c?",
             ("Permite cola infinita", "Solo hay un servidor", "No permite espera (bloqueo)", "Todos los clientes son atendidos"))
if p1 == "No permite espera (bloqueo)":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Qué sucede si todos los servidores están ocupados y llega un cliente?",
             ("Se queda esperando", "Es rechazado", "Pasa a otro sistema", "Se atiende igual"))
if p2 == "Es rechazado":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué fórmula se usa para calcular la probabilidad de bloqueo en M/M/c/c?",
             ("Erlang-C", "Little", "Erlang-B", "Pollaczek-Khinchine"))
if p3 == "Erlang-B":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Qué representa la variable A = λ / μ en este modelo?",
             ("Tiempo de atención", "Número de servidores", "Clientes bloqueados", "Carga ofrecida"))
if p4 == "Carga ofrecida":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si λ = 8 y μ = 2, ¿cuál es la carga ofrecida A?",
             ("4", "0.25", "16", "10"))
if p5 == "4":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/M/c/c.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes reforzar algunos puntos.")
    else:
        st.error("Revisa la teoría del modelo sin cola para mejorar tu comprensión.")
