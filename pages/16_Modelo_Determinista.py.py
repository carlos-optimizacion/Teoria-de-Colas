# Archivo: 16_Modelo_Determinista.py
import streamlit as st

st.set_page_config(page_title="16 - Modelo Determinista", layout="centered")
st.title("📘 16. Modelo Determinista – Sistema D/D/1")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **Determinista (D/D/1)** es un caso especial de teoría de colas donde:
- Los clientes llegan a intervalos **constantes** (no aleatorios)
- El tiempo de servicio también es **constante**
- Hay **1 servidor**

Este modelo representa un sistema sin variabilidad, útil para entender cómo se comporta un sistema perfectamente controlado.
""")

st.markdown("---")

st.subheader("📐 Fórmulas clave")

st.latex(r"\lambda = \frac{1}{T}, \quad \mu = \frac{1}{S}, \quad \rho = \frac{\lambda}{\mu} = \frac{S}{T}")

st.markdown("""
Donde:
- **λ**: tasa de llegada
- **μ**: tasa de servicio
- **ρ**: utilización del sistema
- **T**: tiempo entre llegadas
- **S**: tiempo de servicio

En este modelo:
- Si **ρ < 1**, no se genera cola.
- Si **ρ > 1**, la cola crece indefinidamente.
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- Tiempo entre llegadas: T = 4 minutos
- Tiempo de servicio: S = 3 minutos

**Donde:**
- **T**: tiempo constante entre llegadas (1 cliente cada T minutos)
- **S**: tiempo constante de servicio por cliente

Calculamos:
""")

T = 4  # tiempo entre llegadas
S = 3  # tiempo de servicio
λ = 1 / T
μ = 1 / S
ρ = λ / μ

st.write(f"**Tasa de llegada (λ):** {λ:.2f} clientes/min")
st.write(f"**Tasa de servicio (μ):** {μ:.2f} clientes/min")
st.write(f"**Utilización del sistema (ρ):** {ρ:.2f}")

if ρ < 1:
    st.success("✅ El sistema es estable. No se genera cola.")
elif ρ == 1:
    st.warning("⚠️ El sistema está en su límite. Puede haber cola mínima.")
else:
    st.error("❌ El sistema es inestable. La cola crecerá indefinidamente.")

st.markdown("---")

st.info("Este modelo es útil para sistemas automatizados con tiempos exactos, como producción en línea o robots industriales.")
