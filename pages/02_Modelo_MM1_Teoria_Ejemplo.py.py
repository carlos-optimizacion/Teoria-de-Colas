# Archivo: 02_Modelo_MM1_Teoria_Ejemplo.py
import streamlit as st

st.set_page_config(page_title="02 - Modelo M/M/1", layout="centered")
st.title("📘 02. Modelo M/M/1 – Teoría y Ejemplo")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/M/1** es el más básico en la teoría de colas. Se caracteriza por:

- Llegadas aleatorias con distribución **Poisson** (tasa \( \lambda \))
- Tiempos de servicio con distribución **exponencial** (tasa \( \mu \))
- **Un solo servidor**
- Capacidad infinita y disciplina FIFO

Este modelo es muy útil para entender la lógica básica de los sistemas de espera y para estimar tiempos promedio y uso del sistema.
""")

st.markdown("---")

st.subheader("📐 Fórmulas principales del modelo M/M/1")

st.latex(r"\rho = \frac{\lambda}{\mu}")
st.latex(r"L = \frac{\rho}{1 - \rho}")
st.latex(r"L_q = \frac{\rho^2}{1 - \rho}")
st.latex(r"W = \frac{1}{\mu - \lambda}")
st.latex(r"W_q = \frac{\lambda}{\mu(\mu - \lambda)}")

st.markdown("""
Donde:
- \( \lambda \): tasa media de llegada de clientes
- \( \mu \): tasa media de servicio
- \( \rho \): utilización del sistema
- \( L \): número promedio en el sistema
- \( L_q \): número promedio en la cola
- \( W \): tiempo promedio en el sistema
- \( W_q \): tiempo promedio en la cola
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- Llegan 5 clientes por hora (\( \lambda = 5 \))
- El servidor puede atender 8 clientes por hora (\( \mu = 8 \))

Veamos los resultados:
""")

lambda_ = 5
mu = 8
rho = lambda_ / mu
L = rho / (1 - rho)
Lq = rho**2 / (1 - rho)
W = 1 / (mu - lambda_)
Wq = lambda_ / (mu * (mu - lambda_))

st.write(f"**Utilización (ρ):** {rho:.2f}")
st.write(f"**Número promedio en el sistema (L):** {L:.2f}")
st.write(f"**Número promedio en la cola (Lq):** {Lq:.2f}")
st.write(f"**Tiempo promedio en el sistema (W):** {W:.2f} horas")
st.write(f"**Tiempo promedio en la cola (Wq):** {Wq:.2f} horas")

st.markdown("---")

st.success("Ahora que conoces la teoría, puedes avanzar al siguiente módulo para resolver una autoevaluación interactiva.")
