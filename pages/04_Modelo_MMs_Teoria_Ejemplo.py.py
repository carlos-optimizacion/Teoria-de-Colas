# Archivo: 04_Modelo_MMs_Teoria_Ejemplo.py
import streamlit as st
import math

st.set_page_config(page_title="04 - Modelo M/M/s", layout="centered")
st.title("📘 04. Modelo M/M/s – Teoría y Ejemplo")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/M/s** amplía el clásico M/M/1 para considerar múltiples servidores. Se caracteriza por:

- Llegadas aleatorias con distribución **Poisson** (\( \lambda \))
- Servicios con distribución **exponencial** (\( \mu \))
- **s servidores en paralelo**
- Capacidad infinita y disciplina FIFO

Este modelo permite analizar centros de atención con varios servidores, como bancos, hospitales, call centers, etc.
""")

st.markdown("---")

st.subheader("📐 Fórmulas principales del modelo M/M/s")

st.latex(r"\rho = \frac{\lambda}{s \cdot \mu}")

st.markdown("Para calcular el promedio de clientes en el sistema se requieren fórmulas más complejas basadas en probabilidades estacionarias."
            " Se suele calcular la probabilidad de que no haya clientes en el sistema (\( P_0 \)) como base para las demás métricas.")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- Llegan 6 clientes por hora (\( \lambda = 6 \))
- Cada servidor atiende 4 clientes por hora (\( \mu = 4 \))
- Hay 2 servidores (\( s = 2 \))

Calculamos:
""")

# Parámetros de entrada
lambda_ = 6
mu = 4
s = 2
rho = lambda_ / (s * mu)

# Cálculo de P0
sumatoria = sum([(lambda_/mu)**n / math.factorial(n) for n in range(s)])
ultimo = ((lambda_/mu)**s) / (math.factorial(s) * (1 - rho))
P0 = 1 / (sumatoria + ultimo)

# Lq (número promedio en la cola)
Lq = (P0 * ((lambda_/mu)**s) * rho) / (math.factorial(s) * (1 - rho)**2)
L = Lq + (lambda_ / mu)
Wq = Lq / lambda_
W = Wq + (1 / mu)

# Resultados
st.write(f"**Utilización del sistema (ρ):** {rho:.2f}")
st.write(f"**Probabilidad de sistema vacío (P₀):** {P0:.4f}")
st.write(f"**Número promedio en la cola (Lq):** {Lq:.2f}")
st.write(f"**Número promedio en el sistema (L):** {L:.2f}")
st.write(f"**Tiempo promedio en la cola (Wq):** {Wq:.2f} horas")
st.write(f"**Tiempo promedio en el sistema (W):** {W:.2f} horas")

st.markdown("---")

st.success("Has completado la explicación y ejemplo del modelo M/M/s. Puedes continuar con la evaluación del módulo.")
