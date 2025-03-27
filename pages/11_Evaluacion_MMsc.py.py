# Archivo: 11_Evaluacion_MMsc.py
import streamlit as st

st.set_page_config(page_title="11 - Evaluación M/M/s/c", layout="centered")
st.title("✍️ 11. Evaluación del Modelo M/M/s/c")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Responde esta autoevaluación para verificar tu comprensión del modelo **M/M/s/c**, que incluye múltiples servidores y una capacidad total limitada del sistema.
""")

st.markdown("---")

# Variables de puntaje
total = 0
preguntas = 5

# Pregunta 1
st.subheader("📌 Pregunta 1")
p1 = st.radio("¿Qué representa la letra 'c' en el modelo M/M/s/c?",
             ("Cantidad de servidores", "Capacidad máxima del sistema", "Clientes promedio en cola", "Tasa de servicio"))
if p1 == "Capacidad máxima del sistema":
    total += 1

# Pregunta 2
st.subheader("📌 Pregunta 2")
p2 = st.radio("¿Qué ocurre cuando el sistema ya tiene c clientes y llega uno más?",
             ("Es atendido por un nuevo servidor", "Se queda esperando fuera del sistema", "Es rechazado", "Ingresa igual al sistema"))
if p2 == "Es rechazado":
    total += 1

# Pregunta 3
st.subheader("📌 Pregunta 3")
p3 = st.radio("¿Qué representa la fórmula de 𝑃₍c₎ en este modelo?",
             ("La utilización total", "El número de servidores activos", "La probabilidad de que el sistema esté vacío", "La probabilidad de rechazo por capacidad"))
if p3 == "La probabilidad de rechazo por capacidad":
    total += 1

# Pregunta 4
st.subheader("📌 Pregunta 4")
p4 = st.radio("¿Qué condición debe cumplirse para que el sistema sea estable?",
             ("λ < μ × s", "λ > μ × s", "μ = λ", "λ = 0"))
if p4 == "λ < μ × s":
    total += 1

# Pregunta 5
st.subheader("📌 Pregunta 5")
p5 = st.radio("Si λ = 6, μ = 3 y s = 2, ¿cuál es ρ?",
             ("1.0", "0.5", "0.25", "2.0"))
if p5 == "1.0":
    total += 1

st.markdown("---")

if st.button("Ver mi puntaje"):
    st.success(f"Tu puntaje es: {total} de {preguntas}")
    if total == preguntas:
        st.balloons()
        st.info("¡Excelente! Dominaste el modelo M/M/s/c.")
    elif total >= 3:
        st.warning("¡Buen trabajo! Puedes repasar algunos conceptos.")
    else:
        st.error("Te recomendamos revisar nuevamente el modelo M/M/s/c.")
