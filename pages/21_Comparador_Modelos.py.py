# Archivo: 21_Comparador_de_Modelos.py
import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Comparador de Modelos", layout="wide")
st.title("📊 21. Comparador de Modelos de Colas")

modelos = {
    "M/M/1": lambda l, m, s=None, c=None, k=None: _mm1(l, m),
    "M/M/s": lambda l, m, s, c=None, k=None: _mms(l, m, s),
    "M/M/1/c": lambda l, m, s=None, c=None, k=None: _mm1c(l, m, c),
    "M/M/s/k": lambda l, m, s, c=None, k=None: _mmsk(l, m, s, k),
    "M/M/s/c": lambda l, m, s, c, k=None: _mmsc(l, m, s, c),
}

# -------------------------------
# Funciones de modelos
# -------------------------------
def _mm1(lambda_, mu):
    rho = lambda_ / mu
    if rho >= 1:
        return rho, float('inf'), float('inf'), float('inf'), float('inf')
    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)
    W = 1 / (mu - lambda_)
    Wq = lambda_ / (mu * (mu - lambda_))
    return rho, L, Lq, W, Wq

def _mms(lambda_, mu, s):
    rho = lambda_ / (s * mu)
    r = lambda_ / mu
    def P0():
        suma = sum((r**n)/math.factorial(n) for n in range(s))
        parte2 = (r**s)/(math.factorial(s)*(1 - rho))
        return 1 / (suma + parte2)
    P0_val = P0()
    Lq = (P0_val * (r**s) * rho) / (math.factorial(s) * ((1 - rho)**2))
    L = Lq + r
    Wq = Lq / lambda_
    W = Wq + 1 / mu
    return rho, L, Lq, W, Wq

def _mm1c(lambda_, mu, c):
    rho = lambda_ / mu
    if rho == 1:
        L = c / 2
    else:
        numerador = rho * (1 - (c + 1) * rho**c + c * rho**(c + 1))
        denominador = (1 - rho) * (1 - rho**(c + 1))
        L = numerador / denominador
    Lq = L - (1 - rho**c) / (1 - rho) + rho * rho**c / (1 - rho)
    W = L / (lambda_ * (1 - rho**c))
    Wq = Lq / (lambda_ * (1 - rho**c))
    return rho, L, Lq, W, Wq

def _mmsk(lambda_, mu, s, k):
    rho = lambda_ / (s * mu)
    r = lambda_ / mu
    def P0():
        suma = sum((r**n)/math.factorial(n) for n in range(s))
        suma += sum((r**n)/(math.factorial(s) * s**(n-s)) for n in range(s, k+1))
        return 1 / suma
    P0_val = P0()
    Lq = P0_val * ((r**s) / (math.factorial(s) * (1 - rho)**2)) * (1 - rho**(k - s + 1) - (k - s + 1) * rho**(k - s) * (1 - rho))
    prob_rechazo = ((r**k)/(math.factorial(s) * s**(k - s))) * P0_val
    L = Lq + r * (1 - prob_rechazo)
    Wq = Lq / (lambda_ * (1 - prob_rechazo))
    W = Wq + 1 / mu
    return rho, L, Lq, W, Wq

def _mmsc(lambda_, mu, s, c):
    rho = lambda_ / (s * mu)
    r = lambda_ / mu
    def P0():
        suma1 = sum((r**n)/math.factorial(n) for n in range(s))
        suma2 = sum((r**n)/(math.factorial(s) * s**(n-s)) for n in range(s, c+1))
        return 1 / (suma1 + suma2)
    P0_val = P0()
    Pc = (r**c) / (math.factorial(s) * s**(c - s)) * P0_val
    L = sum(n * (r**n)/(math.factorial(n)) for n in range(s))
    L += sum(n * (r**n)/(math.factorial(s) * s**(n - s)) for n in range(s, c+1))
    L *= P0_val
    Lq = L - (1 - Pc) * r
    W = L / (lambda_ * (1 - Pc))
    Wq = Lq / (lambda_ * (1 - Pc))
    return rho, L, Lq, W, Wq

# -------------------------------
# UI de comparación
# -------------------------------
cols = st.columns(2)
parametros = []

for i, col in enumerate(cols):
    with col:
        st.markdown(f"### Modelo {i+1}")
        modelo = st.selectbox("Selecciona el modelo", list(modelos.keys()), key=f"modelo_{i}")
        lambda_ = st.number_input("λ (tasa de llegada)", min_value=0.01, key=f"lambda_{i}")
        mu = st.number_input("μ (tasa de servicio)", min_value=0.01, key=f"mu_{i}")
        s = c = k = None
        if "s" in modelo:
            s = st.number_input("s (servidores)", min_value=1, step=1, key=f"s_{i}")
        if "c" in modelo and "k" not in modelo:
            c = st.number_input("c (capacidad)", min_value=1, step=1, key=f"c_{i}")
        if "k" in modelo:
            k = st.number_input("k (capacidad total)", min_value=1, step=1, key=f"k_{i}")
        if "s/c" in modelo:
            c = st.number_input("c (capacidad total)", min_value=1, step=1, key=f"cap_{i}")
        parametros.append((modelo, lambda_, mu, s, c, k))

# -------------------------------
# Comparación
# -------------------------------
if st.button("🔍 Comparar Modelos"):
    resultados = []
    for modelo, l, m, s, c, k in parametros:
        rho, L, Lq, W, Wq = modelos[modelo](l, m, s, c, k)
        resultados.append({
            "Modelo": modelo,
            "ρ": round(rho, 2),
            "L": round(L, 2),
            "Lq": round(Lq, 2),
            "W": round(W, 2),
            "Wq": round(Wq, 2)
        })

    df = pd.DataFrame(resultados)
    st.markdown("### 📋 Resultados Comparativos")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📊 Comparación Gráfica")
    fig = go.Figure()
    for metrica in ["L", "Lq", "W", "Wq"]:
        fig.add_trace(go.Bar(name=metrica, x=df["Modelo"], y=df[metrica]))
    fig.update_layout(barmode='group', title="Comparación de Métricas entre Modelos")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧠 Interpretación Automática")
    mejores = {"W": None, "Lq": None, "ρ": None}
    min_w = min(resultados, key=lambda x: x['W'])
    min_lq = min(resultados, key=lambda x: x['Lq'])
    min_rho = min(resultados, key=lambda x: x['ρ'])

    for row in resultados:
        if row['ρ'] >= 1:
            st.error(f"❌ El modelo {row['Modelo']} tiene ρ = {row['ρ']}, indicando un sistema inestable.")
        else:
            st.info(f"🔸 En el modelo {row['Modelo']}, el sistema tiene una utilización de {row['ρ']} y un promedio de {row['L']} clientes en el sistema.")

    st.markdown("### 🏁 Conclusión Automática")
    st.success(f"✅ El modelo {min_w['Modelo']} ofrece el menor tiempo promedio en el sistema (W = {min_w['W']}).")
    st.success(f"✅ El modelo {min_lq['Modelo']} presenta la menor congestión en cola (Lq = {min_lq['Lq']}).")
    st.success(f"✅ El modelo {min_rho['Modelo']} tiene la mejor capacidad de respuesta (ρ = {min_rho['ρ']}).")
