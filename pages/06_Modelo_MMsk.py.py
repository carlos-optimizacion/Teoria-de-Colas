# Archivo: 06_Modelo_MMsk.py
import streamlit as st
import math

st.set_page_config(page_title="06 - Modelo M/M/s/k", layout="centered")
st.title("📘 06. Modelo M/M/s/k – Capacidad Finita")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
El modelo **M/M/s/k** considera:
- Llegadas **Poisson** (\( \lambda \))
- Servicios **exponenciales** (\( \mu \))
- **s** servidores en paralelo
- **Capacidad máxima del sistema: k clientes** (incluye los atendidos + los que esperan)

Este modelo permite analizar la **probabilidad de pérdida** de clientes debido a una capacidad limitada del sistema.
""")

st.markdown("---")

st.subheader("📐 Cálculo general de la probabilidad de rechazo (Bloqueo)")

st.markdown("""
La probabilidad de que un cliente sea rechazado (por encontrar el sistema lleno) es:

\[ P_k = \frac{\frac{(\lambda/\mu)^k}{s! \cdot s^{k-s}}}{\sum\limits_{n=0}^{s-1} \frac{(\lambda/\mu)^n}{n!} + \sum\limits_{n=s}^{k} \frac{(\lambda/\mu)^n}{s! \cdot s^{n-s}}} \]

Donde:
- \( s \): número de servidores
- \( k \): capacidad total del sistema
""")

st.markdown("---")

st.subheader("🧪 Ejemplo práctico")
st.markdown("""
**Supongamos:**
- \( \lambda = 5 \), \( \mu = 4 \), \( s = 2 \), \( k = 5 \)

Vamos a calcular la probabilidad de pérdida de un cliente:
""")

# Parámetros del ejemplo
lambda_ = 5
mu = 4
s = 2
k = 5

ro = lambda_ / mu

# Sumas para Pk
parte1 = sum([(ro**n) / math.factorial(n) for n in range(s)])
parte2 = sum([(ro**n) / (math.factorial(s) * (s**(n - s))) for n in range(s, k + 1)])
Pk = ((ro**k) / (math.factorial(s) * (s**(k - s)))) / (parte1 + parte2)

st.write(f"**Probabilidad de rechazo (Pₖ):** {Pk:.4f}")

st.markdown("---")

st.info("Este modelo es útil en sistemas con espacio o recursos limitados como ascensores, call centers, o salas de espera pequeñas.")
