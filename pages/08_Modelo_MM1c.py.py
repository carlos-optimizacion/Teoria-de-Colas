# Archivo: 08_Modelo_MM1c.py
import streamlit as st
import math

st.set_page_config(page_title="08 - Modelo M/M/1/c", layout="centered")
st.title("📘 08. Modelo M/M/1/c – Capacidad de Cola Limitada")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/M/1/c** considera:
- Llegadas **Poisson** (\( \lambda \))
- Servicios **exponenciales** (\( \mu \))
- **1 solo servidor**
- **Capacidad máxima de cola: c clientes en espera**

Este modelo permite analizar sistemas donde sólo cierta cantidad de personas puede esperar. Si hay más de c personas, el cliente es rechazado.
""")

st.markdown("---")

st.subheader("📐 Fórmula general para la probabilidad de bloqueo")

st.markdown("""
\[ P_n = \frac{\rho^n (1 - \rho)}{1 - \rho^{c+2}} \quad \text{para } \rho \ne 1 \]

Donde:
- \( \rho = \lambda / \mu \)
- \( P_{c+1} \): probabilidad de que un cliente llegue y no pueda entrar a la cola

> Si \( \rho = 1 \), se usa una fórmula alternativa basada en distribución uniforme.
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- \( \lambda = 2 \), \( \mu = 3 \), \( c = 4 \)

Calculamos:
""")

# Parámetros del ejemplo
lambda_ = 2
mu = 3
c = 4
rho = lambda_ / mu

# Probabilidad de que el cliente número c+1 no pueda ingresar
P_bloqueo = (rho**(c + 1) * (1 - rho)) / (1 - rho**(c + 2))

st.write(f"**Utilización del sistema (ρ):** {rho:.2f}")
st.write(f"**Probabilidad de rechazo (P₍c₊₁₎):** {P_bloqueo:.4f}")

st.markdown("---")

st.info("Este modelo es útil para sistemas como atención en farmacias, consultorios o negocios donde sólo cierta cantidad de clientes pueden hacer fila.")
