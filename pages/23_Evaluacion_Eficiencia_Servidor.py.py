# Archivo: 23_Evaluacion_Eficiencia_Servidor.py
import streamlit as st
import pandas as pd
import math
import plotly.express as px

st.set_page_config(page_title="Eficiencia del Servidor", layout="wide")
st.title("⚙️ 23. Evaluación de la Eficiencia del Servidor")

st.markdown("""
Este módulo te ayuda a determinar el número óptimo de servidores según el nivel de servicio deseado.

📌 **Modelos incluidos:** M/M/1, M/M/s, M/M/s/k  
Solo estos modelos permiten evaluar la eficiencia en función de `s` (número de servidores).  
❌ Modelos como M/M/1/c o M/M/s/c tienen `s` fijo o capacidad limitada y no permiten un análisis de eficiencia dinámica.
""")

modelo = st.selectbox("Selecciona el modelo", ["M/M/1", "M/M/s", "M/M/s/k"])
lambda_ = st.number_input("λ - Tasa de llegada (clientes/hora)", min_value=0.01)
mu = st.number_input("μ - Tasa de servicio (clientes/hora)", min_value=0.01)
s_min = st.number_input("Número mínimo de servidores", value=1, step=1)
s_max = st.number_input("Número máximo de servidores", value=10, step=1)
costo_servidor = st.number_input("Costo por servidor por hora (S/.)", min_value=0.0)
k = None
if modelo == "M/M/s/k":
    k = st.number_input("Capacidad total del sistema (k)", min_value=int(s_max), step=1)

nsc_deseado = st.slider("Nivel de Servicio al Cliente deseado (%)", min_value=50, max_value=100, value=85)

if st.button("Evaluar Eficiencia"):
    resultados = []
    for s in range(int(s_min), int(s_max)+1):
        rho = lambda_ / (s * mu)
        r = lambda_ / mu
        Pc = 0

        if modelo == "M/M/1":
            if rho >= 1:
                continue
            Lq = rho**2 / (1 - rho)
        elif modelo == "M/M/s":
            def P0():
                suma = sum((r**n)/math.factorial(n) for n in range(s))
                parte2 = (r**s)/(math.factorial(s)*(1 - rho))
                return 1 / (suma + parte2)
            P0_val = P0()
            Lq = (P0_val * (r**s) * rho) / (math.factorial(s) * ((1 - rho)**2))
        elif modelo == "M/M/s/k":
            def P0():
                suma = sum((r**n)/math.factorial(n) for n in range(s))
                suma += sum((r**n)/(math.factorial(s) * s**(n-s)) for n in range(s, k+1))
                return 1 / suma
            P0_val = P0()
            Pc = ((r**k)/(math.factorial(s) * s**(k - s))) * P0_val
            Lq = P0_val * ((r**s) / (math.factorial(s) * (1 - rho)**2)) * \
                 (1 - rho**(k - s + 1) - (k - s + 1) * rho**(k - s) * (1 - rho))

        Wq = Lq / (lambda_ * (1 - Pc)) if (modelo == "M/M/s/k") else Lq / lambda_
        NSC = max(0, 100 - (0.6 * (Wq / (Wq + 1) * 100) + 0.4 * Pc * 100))
        costo_total = s * costo_servidor

        resultados.append({
            "Servidores": s,
            "ρ": round(rho, 2),
            "Lq": round(Lq, 2),
            "Wq": round(Wq, 2),
            "NSC": round(NSC, 1),
            "Costo total (S/.)": round(costo_total, 2)
        })

    df = pd.DataFrame(resultados)
    st.markdown("### 📊 Resultados por número de servidores")
    st.dataframe(df, use_container_width=True)

    fig = px.line(df, x="Servidores", y="NSC", markers=True, title="Nivel de Servicio al Cliente vs Servidores")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(df, x="Servidores", y="Costo total (S/.)", title="Costo total por cantidad de servidores")
    st.plotly_chart(fig2, use_container_width=True)

    recomendado = df[df["NSC"] >= nsc_deseado]
    if not recomendado.empty:
        optimo = recomendado.iloc[0]
        st.success(f"✅ Se recomienda usar {int(optimo['Servidores'])} servidores para alcanzar un NSC ≥ {nsc_deseado}% con el menor costo posible.")
        st.caption("📌 Esta recomendación busca equilibrar nivel de servicio deseado con el menor costo operativo.")
    else:
        st.warning("⚠️ No se encontró un número de servidores que cumpla con el NSC deseado en el rango evaluado.")
