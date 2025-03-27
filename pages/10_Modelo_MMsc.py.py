# Archivo: 10_Modelo_MMsc.py
import streamlit as st
import math

st.set_page_config(page_title="10 - Modelo M/M/s/c", layout="centered")
st.title("📘 10. Modelo M/M/s/c – Capacidad de sistema con múltiples servidores")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/M/s/c** considera:
- Llegadas **Poisson** (λ)
- Servicios **exponenciales** (μ)
- Número de servidores (s)
- **Capacidad máxima del sistema: (c) clientes** (incluye a los que esperan y a los que están siendo atendidos)

Este modelo es útil cuando tanto el número de servidores como el espacio del sistema son limitados.
""")

st.markdown("---")

st.subheader("📐 Cálculo de la probabilidad de rechazo (P₍c₎)")

st.latex(r"""
P_c = \frac{\frac{(\lambda/\mu)^c}{s! \cdot s^{c-s}}}
{\sum\limits_{n=0}^{s-1} \frac{(\lambda/\mu)^n}{n!} +
 \sum\limits_{n=s}^{c} \frac{(\lambda/\mu)^n}{s! \cdot s^{n-s}}}
""")

st.markdown("""
Donde:
- λ: tasa de llegada
- μ: tasa de servicio
- s: número de servidores
- c: capacidad total del sistema
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- λ = 6 (clientes por hora)
- μ = 4 (clientes por hora)
- s = 2 (servidores disponibles)
- c = 5 (capacidad máxima del sistema incluyendo en cola y en servicio)

**Donde:**
- **λ**: tasa de llegada promedio de clientes
- **μ**: tasa de servicio promedio de cada servidor
- **s**: número total de servidores que atienden en paralelo
- **c**: número máximo de clientes que el sistema puede contener (en cola y atendidos)

Calculamos la probabilidad de rechazo:
""")

# Parámetros del ejemplo
λ = 6
μ = 4
s = 2
c = 5

ρ = λ / μ

# Sumatoria
parte1 = sum([(ρ**n) / math.factorial(n) for n in range(s)])
parte2 = sum([(ρ**n) / (math.factorial(s) * (s**(n - s))) for n in range(s, c + 1)])
P_c = ((ρ**c) / (math.factorial(s) * (s**(c - s)))) / (parte1 + parte2)

st.write(f"**Valores usados:** λ = {λ}, μ = {μ}, s = {s}, c = {c}")
st.write(f"**Utilización del sistema (ρ):** {ρ:.2f}")
st.write(f"**Probabilidad de rechazo (P₍c₎):** {P_c:.4f}")

st.markdown("---")

st.info("Este modelo es útil para evaluar sistemas donde tanto el número de recursos como el espacio total son limitados, como en salas de emergencia o call centers con límite de líneas.")
