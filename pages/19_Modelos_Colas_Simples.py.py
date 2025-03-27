# Archivo: 19_Modelos_Colas_Simples.py
import streamlit as st
import math
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelos Colas Simples", layout="centered")
st.title("💡 19. Simulación – Modelos de Colas Simples")
st.markdown("""
Este módulo permite simular los modelos básicos de teoría de colas:

- **M/M/1**: Un solo servidor.
- **M/M/s**: Varios servidores en paralelo.

Ingresa los parámetros del sistema para obtener resultados, interpretación automática y gráficos.
""")

modelo = st.selectbox("Selecciona el modelo:", ["M/M/1", "M/M/s"])

st.markdown("---")
st.header("🔢 Ingreso de Parámetros")

lambda_ = st.number_input("lambda - Tasa de llegada (clientes por unidad de tiempo)", min_value=0.01, step=0.1)
mu = st.number_input("mu - Tasa de servicio por servidor", min_value=0.01, step=0.1)
s = 1
if modelo == "M/M/s":
    s = st.number_input("s - Número de servidores", min_value=1, step=1)

if lambda_ and mu:
    rho = lambda_ / (s * mu)
    st.markdown(f"**rho - Utilización del sistema:** {rho:.2f}")

    if modelo == "M/M/1":
        if rho >= 1:
            st.error("⚠️ El sistema no es estable. rho debe ser menor que 1.")
        else:
            L = rho / (1 - rho)
            Lq = rho**2 / (1 - rho)
            W = 1 / (mu - lambda_)
            Wq = lambda_ / (mu * (mu - lambda_))

    elif modelo == "M/M/s":
        def calcular_P0(lam, mu, s):
            r = lam / mu
            suma = sum((r**n)/math.factorial(n) for n in range(s))
            parte2 = (r**s) / (math.factorial(s) * (1 - (r/s)))
            return 1 / (suma + parte2)

        r = lambda_ / mu
        P0 = calcular_P0(lambda_, mu, s)
        Lq = (P0 * (r**s) * rho) / (math.factorial(s) * ((1 - rho)**2))
        L = Lq + r
        Wq = Lq / lambda_
        W = Wq + (1 / mu)

    st.markdown("---")
    st.header("📈 Resultados")
    st.markdown(f"**L - Nº promedio en el sistema:** {L:.2f}")
    st.caption("Cantidad esperada de clientes en el sistema (cola + atención).")
    st.markdown(f"**Lq - Nº promedio en la cola:** {Lq:.2f}")
    st.caption("Cantidad esperada de clientes esperando en cola.")
    st.markdown(f"**W - Tiempo promedio en el sistema:** {W:.2f}")
    st.caption("Tiempo total promedio que un cliente pasa en el sistema.")
    st.markdown(f"**Wq - Tiempo promedio en cola:** {Wq:.2f}")
    st.caption("Tiempo promedio que un cliente espera en cola antes de ser atendido.")

    st.markdown("---")
    st.header("🧠 Interpretación Automática")
    interpretacion = f"Con una tasa de llegada de {lambda_:.2f} y una tasa de servicio de {mu:.2f}, el sistema tiene una utilizacion de {rho:.2f}, lo que significa que el servidor{'es' if modelo=='M/M/s' else ''} esta ocupado el {rho*100:.1f}% del tiempo. Se espera que haya en promedio {Lq:.2f} clientes en cola y un total de {L:.2f} en el sistema."
    st.success(interpretacion)

    st.markdown("---")
    st.header("📊 Gráficos Interactivos")
    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=["L"], y=[L], name="En sistema"))
        fig1.add_trace(go.Bar(x=["Lq"], y=[Lq], name="En cola"))
        fig1.update_layout(title="Número Promedio de Clientes", yaxis_title="Clientes", barmode='group')
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("Este gráfico de barras compara el número promedio de clientes en el sistema (L) y en la cola (Lq).")
    with col2:
        fig2 = go.Figure(data=[go.Pie(labels=["En Cola", "En Servicio"], values=[Lq, L - Lq], hole=0.4)])
        fig2.update_layout(title="Distribución de Clientes en el Sistema")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Este gráfico de pastel muestra la proporción de clientes en cola frente a los que están siendo atendidos.")

    # Guardar PDF con gráficos
    if st.button("📥 Descargar Informe en PDF"):
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Simulacion - Modelo de Colas Simples", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Parametros Ingresados", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, f"Modelo: {modelo}\nlambda = {lambda_}\nmu = {mu}\ns = {s if modelo=='M/M/s' else '1'}")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Resultados", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, f"rho = {rho:.2f}\nL = {L:.2f}\nLq = {Lq:.2f}\nW = {W:.2f}\nWq = {Wq:.2f}")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Interpretacion", ln=True)
        pdf.set_font("Arial", size=11)
        texto_limpio = interpretacion.encode('latin1', 'ignore').decode('latin1')
        pdf.multi_cell(0, 10, texto_limpio)

        # Guardar gráficos como imágenes temporales
        img_path1 = os.path.join(tempfile.gettempdir(), "grafico_barras.png")
        img_path2 = os.path.join(tempfile.gettempdir(), "grafico_pie.png")

        # Gráfico de barras
        plt.figure()
        plt.bar(["L", "Lq"], [L, Lq], color=['skyblue', 'salmon'])
        plt.title("Número Promedio de Clientes")
        plt.ylabel("Clientes")
        plt.tight_layout()
        plt.savefig(img_path1)
        plt.close()

        # Gráfico de pastel
        plt.figure()
        plt.pie([Lq, L - Lq], labels=["En Cola", "En Servicio"], autopct='%1.1f%%', colors=['gold', 'lightgreen'])
        plt.title("Distribución de Clientes en el Sistema")
        plt.tight_layout()
        plt.savefig(img_path2)
        plt.close()

        pdf.image(img_path1, x=10, w=180)
        pdf.ln(5)
        pdf.image(img_path2, x=30, w=150)

        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            st.download_button("Descargar PDF", f, file_name="simulacion_colas_simples.pdf")
        try:
            os.remove(tmpfile.name)
            os.remove(img_path1)
            os.remove(img_path2)
        except PermissionError:
            pass
else:
    st.info("Ingresa los valores de lambda y mu para realizar el cálculo.")
