# Archivo: 12_Modelo_MMcc.py
import streamlit as st
import math

st.set_page_config(page_title="12 - Modelo M/M/c/c", layout="centered")
st.title("📘 12. Modelo M/M/c/c – Sistema sin cola (bloqueo puro)")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/M/c/c** describe un sistema con:
- Llegadas **Poisson** (λ)
- Servicios **exponenciales** (μ)
- **c** servidores (todos los que ingresan son atendidos)
- **Sin cola**: si todos los servidores están ocupados, el cliente es **rechazado** (bloqueado)

Es típico en servicios como líneas telefónicas, salas de emergencia, elevadores o cajeros automáticos.
""")

st.markdown("---")

st.subheader("📐 Cálculo de la probabilidad de rechazo (fórmula de Erlang-B)")

st.latex(r"""
P_B = \frac{\frac{(\lambda/\mu)^c}{c!}}{\sum\limits_{n=0}^{c} \frac{(\lambda/\mu)^n}{n!}}
""")

st.markdown("""
Donde:
- λ: tasa de llegada
- μ: tasa de servicio
- c: número de servidores
- \( P_B \): probabilidad de bloqueo (cliente es rechazado)
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- λ = 5 clientes/hora
- μ = 2 clientes/hora
- c = 4 servidores

**Donde:**
- **λ**: tasa de llegada promedio de clientes
- **μ**: tasa de servicio promedio de cada servidor
- **c**: número de servidores disponibles

Calculamos la probabilidad de bloqueo:
""")

# Parámetros del ejemplo
λ = 5
μ = 2
c = 4
A = λ / μ

numerador = (A**c) / math.factorial(c)
denominador = sum([(A**n) / math.factorial(n) for n in range(c + 1)])
P_B = numerador / denominador

st.write(f"**Valores usados:** λ = {λ}, μ = {μ}, c = {c}")
st.write(f"**Carga ofrecida (A = λ / μ):** {A:.2f}")
st.write(f"**Probabilidad de bloqueo (Pᴮ):** {P_B:.4f}")

st.markdown("---")

st.info("Este modelo es útil en contextos donde no se permite espera y el sistema está completamente ocupado o disponible.")
