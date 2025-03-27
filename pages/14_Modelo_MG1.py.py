# Archivo: 14_Modelo_MG1.py
import streamlit as st

st.set_page_config(page_title="14 - Modelo M/G/1", layout="centered")
st.title("📘 14. Modelo M/G/1 – Servicio con distribución general")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/G/1** permite que el tiempo de servicio siga **cualquier distribución** (no solo exponencial), manteniendo llegadas Poisson (λ) y un solo servidor.
Es útil para representar entornos con alta variabilidad, como manufactura, salud o trámites.
""")

st.markdown("---")

st.subheader("📐 Fórmulas clave (Ecuaciones de Pollaczek–Khinchine)")

st.latex(r"\rho = \lambda \cdot \mathbb{E}[S]")

st.latex(r"L_q = \frac{\lambda^2 \cdot \sigma_S^2 + \rho^2}{2(1 - \rho)}")

st.latex(r"W_q = \frac{L_q}{\lambda}, \quad W = W_q + \mathbb{E}[S], \quad L = \lambda \cdot W")

st.markdown("""
Donde:
- **λ**: tasa de llegada
- **𝔼[S]**: media del tiempo de servicio
- **σ²ₛ**: varianza del tiempo de servicio
- **ρ**: utilización del sistema
- **L, Lq**: número promedio en el sistema y en la cola
- **W, Wq**: tiempo promedio en el sistema y en la cola
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- λ = 2 clientes/minuto
- 𝔼[S] = 0.4 minutos
- σ²ₛ = 0.09

**Donde:**
- **λ**: tasa de llegada promedio de clientes
- **𝔼[S]**: media del tiempo de servicio
- **σ²ₛ**: varianza del tiempo de servicio

Calculamos:
""")

# Parámetros de entrada
λ = 2  # tasa de llegada
E_S = 0.4  # media del tiempo de servicio
var_S = 0.09  # varianza del tiempo de servicio

# Cálculos
ρ = λ * E_S
Lq = (λ**2 * var_S + ρ**2) / (2 * (1 - ρ))
Wq = Lq / λ
W = Wq + E_S
L = λ * W

# Mostrar resultados
st.write(f"**Utilización (ρ):** {ρ:.2f}")
st.write(f"**Lq (clientes promedio en cola):** {Lq:.2f}")
st.write(f"**L (clientes promedio en el sistema):** {L:.2f}")
st.write(f"**Wq (tiempo promedio en cola):** {Wq:.2f} minutos")
st.write(f"**W (tiempo promedio en el sistema):** {W:.2f} minutos")

st.markdown("---")

st.info("Este modelo es útil cuando los tiempos de servicio no siguen una distribución exponencial, como en ambientes administrativos, salud o manufactura personalizada.")
