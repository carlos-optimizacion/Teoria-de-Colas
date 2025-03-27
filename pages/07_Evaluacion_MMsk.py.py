# Archivo: 07_Evaluacion_MMsk.py
import streamlit as st

st.set_page_config(page_title="07 - Evaluación M/M/s/k", layout="centered")
st.title("✍️ 07. Evaluación del Modelo M/M/s/k")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Evalúa tu comprensión del modelo **M/M/s/k**, que considera un número máximo de clientes en el sistema.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué representa la 'k' en el modelo M/M/s/k?",
             ("Cantidad de servidores", "Clientes en la cola", "Capacidad total del sistema", "Tasa de llegada"))
if p1 == "Capacidad total del sistema":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Qué sucede cuando un cliente llega y el sistema está lleno (n = k)?",
             ("Se queda esperando", "Se va sin ser atendido", "Se atiende por otro canal", "Aumenta el tiempo de servicio"))
if p2 == "Se va sin ser atendido":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué tipo de sistemas suele modelarse con M/M/s/k?",
             ("Sistemas infinitos", "Almacenes de gran capacidad", "Centros con espacio limitado", "Redes sin límite de usuarios"))
if p3 == "Centros con espacio limitado":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Qué representa Pₖ en el modelo?",
             ("Probabilidad de espera", "Probabilidad de que no haya clientes", "Probabilidad de rechazo", "Utilización"))
if p4 == "Probabilidad de rechazo":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si λ = 6, μ = 3, s = 2, k = 5, ¿cuál es ρ (rho)?",
             ("0.75", "1.00", "1.50", "0.50"))
if p5 == "1.00":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/M/s/k.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes repasar algunos puntos.")
    else:
        st.error("Te recomendamos revisar nuevamente el módulo de capacidad finita.")
