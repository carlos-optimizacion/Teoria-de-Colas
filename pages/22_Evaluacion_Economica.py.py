# Archivo: 22_Evaluacion_Economica.py
import streamlit as st
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Evaluación Económica", layout="centered")
st.title("💰 22. Evaluación Económica del Sistema de Colas")

st.markdown("""
En esta herramienta puedes evaluar los costos operativos y el nivel de servicio al cliente de un sistema de colas.
""")

# Entrada de parámetros
modelo = st.selectbox("Selecciona el modelo", ["M/M/1", "M/M/s", "M/M/1/c", "M/M/s/k"])
lambda_ = st.number_input("λ - Tasa de llegada (clientes/hora)", min_value=0.01)
mu = st.number_input("μ - Tasa de servicio (clientes/hora)", min_value=0.01)
s = 1
c = k = None
if "s" in modelo:
    s = st.number_input("s - Número de servidores", min_value=1, step=1)
if "c" in modelo and "k" not in modelo:
    c = st.number_input("c - Capacidad total del sistema", min_value=1, step=1)
if "k" in modelo:
    k = st.number_input("k - Capacidad total del sistema", min_value=s, step=1)

# Costos
costo_servidor = st.number_input("💼 Costo por hora del servidor (S/.)", min_value=0.0)
costo_cliente_perdido = 0
if "c" in modelo or "k" in modelo:
    costo_cliente_perdido = st.number_input("❗ Costo por cliente perdido (opcional) (S/.)", min_value=0.0)

# Cálculos
if st.button("Calcular evaluación económica"):
    rho = lambda_ / (s * mu)
    r = lambda_ / mu
    Pc = 0

    if modelo == "M/M/1":
        if rho >= 1:
            st.error("⚠️ El sistema está inestable. ρ ≥ 1")
            st.stop()
        Lq = rho**2 / (1 - rho)
        L = rho / (1 - rho)
        Wq = Lq / lambda_
        W = Wq + 1 / mu
    elif modelo == "M/M/s":
        def P0():
            suma = sum((r**n)/math.factorial(n) for n in range(s))
            parte2 = (r**s)/(math.factorial(s)*(1 - rho))
            return 1 / (suma + parte2)
        P0_val = P0()
        Lq = (P0_val * (r**s) * rho) / (math.factorial(s) * ((1 - rho)**2))
        L = Lq + r
        Wq = Lq / lambda_
        W = Wq + 1 / mu
    elif modelo == "M/M/1/c":
        def Pc_mm1c():
            return (1 - rho) * rho**c / (1 - rho**(c + 1))
        Pc = Pc_mm1c()
        L = (rho * (1 - (c + 1) * rho**c + c * rho**(c + 1))) / ((1 - rho) * (1 - rho**(c + 1)))
        Lq = L - (1 - rho**c) / (1 - rho) + rho * rho**c / (1 - rho)
        W = L / (lambda_ * (1 - rho**c))
        Wq = Lq / (lambda_ * (1 - rho**c))
    elif modelo == "M/M/s/k":
        def P0():
            suma = sum((r**n)/math.factorial(n) for n in range(s))
            suma += sum((r**n)/(math.factorial(s) * s**(n-s)) for n in range(s, k+1))
            return 1 / suma
        P0_val = P0()
        Pc = ((r**k)/(math.factorial(s) * s**(k - s))) * P0_val
        Lq = P0_val * ((r**s) / (math.factorial(s) * (1 - rho)**2)) * (1 - rho**(k - s + 1) - (k - s + 1) * rho**(k - s) * (1 - rho))
        L = Lq + r * (1 - Pc)
        Wq = Lq / (lambda_ * (1 - Pc))
        W = Wq + 1 / mu

    # Costos
    costo_util = rho * costo_servidor
    costo_ocioso = (1 - rho) * costo_servidor
    costo_total = costo_util + costo_ocioso + Pc * costo_cliente_perdido

    st.markdown("### 📋 Resultados Económicos")
    st.write(f"**Utilización del sistema (ρ):** {rho:.2f}")
    st.caption("🔹 Mide el porcentaje del tiempo que los servidores están ocupados. Idealmente debe estar entre 0.7 y 0.9.")
    st.write(f"**Clientes en cola promedio (Lq):** {Lq:.2f}")
    st.caption("🔹 Indica cuántos clientes, en promedio, están esperando. Un valor alto implica congestión.")
    st.write(f"**Tiempo de espera promedio (Wq):** {Wq:.2f} horas")
    st.caption("🔹 Refleja cuánto espera, en promedio, un cliente antes de ser atendido.")
    st.write(f"**Probabilidad de rechazo (Pc):** {Pc:.4f}")
    st.caption("🔹 Probabilidad de que un cliente no sea atendido por falta de capacidad.")
    st.write(f"**Costo de servicio útil:** S/.{costo_util:.2f}")
    st.caption("🔹 Representa el costo de los servidores cuando están efectivamente atendiendo clientes.")
    st.write(f"**Costo de servidor ocioso:** S/.{costo_ocioso:.2f}")
    st.caption("🔹 Representa el costo de tener servidores disponibles pero sin uso.")
    if Pc > 0 and costo_cliente_perdido > 0:
        st.write(f"**Costo por clientes perdidos:** S/.{Pc * costo_cliente_perdido:.2f}")
        st.caption("🔹 Costo asociado a clientes que no fueron atendidos debido a capacidad limitada.")
    st.success(f"💰 **Costo total por hora:** S/.{costo_total:.2f}")

    # Nivel de Servicio
    Wq_norm = (Wq / (Wq + 1)) * 100
    NSC = max(0, 100 - (0.6 * Wq_norm + 0.4 * Pc * 100))
    st.markdown("### 🧭 Nivel de Servicio al Cliente")
    st.progress(int(NSC))
    st.info(f"🔹 Nivel de Servicio al Cliente estimado: {NSC:.1f} / 100")
    st.caption("🔹 Estimación basada en el tiempo de espera y la probabilidad de rechazo. Cuanto más alto, mejor atención percibida.")

    # Gráfico de torta
    st.markdown("### 🥧 Distribución de Costos")
    labels = ["Servicio útil", "Servidor ocioso"]
    values = [costo_util, costo_ocioso]
    if Pc > 0 and costo_cliente_perdido > 0:
        labels.append("Clientes perdidos")
        values.append(Pc * costo_cliente_perdido)

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(title="Distribución de Costos por Hora")
    st.plotly_chart(fig, use_container_width=True)
