# Archivo: 18_Casos_Practicos_Aplicados.py
import streamlit as st

st.set_page_config(page_title="18 - Casos Prácticos Aplicados", layout="centered")
st.title("🧪 18. Casos Prácticos Aplicados")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
En esta sección exploraremos aplicaciones reales de la **teoría de colas** en diferentes sectores. Cada caso permite visualizar cómo los modelos se aplican en situaciones concretas de la vida profesional.
""")

st.markdown("---")

st.subheader("🏥 Caso 1: Atención en sala de emergencias")
st.markdown("""
**Situación:** En un hospital llegan en promedio 6 pacientes por hora (λ = 6), y cada médico puede atender a 3 pacientes por hora (μ = 3). Se cuenta con 3 médicos (s = 3).

**Modelo aplicado:** M/M/s

**Objetivo:** Calcular la utilización, número de pacientes en espera y probabilidad de que haya demora.

➡️ Este modelo permite dimensionar recursos humanos para evitar cuellos de botella.
""")

st.markdown("---")

st.subheader("🏦 Caso 2: Atención en ventanillas de banco")
st.markdown("""
**Situación:** Una agencia bancaria tiene 2 ventanillas para atención al cliente. En promedio llegan 20 clientes por hora (λ = 20), y cada cajero atiende 12 clientes por hora (μ = 12).

**Modelo aplicado:** M/M/s

**Objetivo:** Determinar el tiempo promedio que un cliente pasa en el sistema y el tiempo de espera en cola.

➡️ El modelo ayuda a mejorar la experiencia del cliente y reducir el tiempo de permanencia.
""")

st.markdown("---")

st.subheader("🏭 Caso 3: Línea de producción automatizada")
st.markdown("""
**Situación:** En una planta, cada estación recibe piezas cada 4 minutos (T = 4) y tarda 3 minutos en procesarlas (S = 3).

**Modelo aplicado:** D/D/1 (Determinista)

**Objetivo:** Evaluar si se genera cola en la estación o si el flujo es constante y estable.

➡️ Ideal para sistemas automatizados donde los tiempos son perfectamente controlables.
""")

st.markdown("---")

st.info("Recuerda que cada situación puede representarse con distintos modelos según los datos disponibles y el comportamiento del sistema. Puedes usar la simulación en la siguiente sección para experimentar estos casos.")
