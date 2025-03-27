# Archivo: 20_Modelos_Colas_Complejas.py
import streamlit as st
st.set_page_config(page_title="Modelos Colas Complejas", layout="centered")
import math
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import tempfile
import os
from fpdf import FPDF


st.title("💡 20. Simulación – Modelos de Colas Complejas")

st.markdown("""
Este módulo permite simular los modelos avanzados de teoría de colas:
- **M/M/1/c**: Un solo servidor con capacidad limitada.
- **M/M/s/k**: Varios servidores con capacidad total limitada.
- **M/M/s/c**: Varios servidores con capacidad de espera limitada.
""")

modelo = st.selectbox("Selecciona el modelo complejo:", ["M/M/1/c", "M/M/s/k", "M/M/s/c"])

st.markdown("---")

lambda_ = st.number_input("lambda - Tasa de llegada (clientes/unidad tiempo)", min_value=0.01, step=0.1)
mu = st.number_input("mu - Tasa de servicio (clientes/unidad tiempo)", min_value=0.01, step=0.1)
s = 1
k = 0
c = 0

if modelo == "M/M/1/c":
    c = st.number_input("Capacidad total del sistema (c)", min_value=1, step=1)
    rho = lambda_ / mu
    if rho == 1:
        L = c / 2
        Lq = 0
        W = L / (lambda_ * (1 - pow(rho, c))) if (1 - pow(rho, c)) != 0 else 0
        Wq = 0
    else:
        numerador = rho * (1 - (c + 1) * pow(rho, c) + c * pow(rho, c + 1))
        denominador = (1 - rho) * (1 - pow(rho, c + 1))
        L = numerador / denominador

        if (1 - rho) != 0:
            Lq = L - (1 - pow(rho, c)) / (1 - rho) + rho * pow(rho, c) / (1 - rho)
        else:
            Lq = 0

        if (1 - pow(rho, c)) != 0:
            W = L / (lambda_ * (1 - pow(rho, c)))
            Wq = Lq / (lambda_ * (1 - pow(rho, c)))
        else:
            W = Wq = 0

elif modelo == "M/M/s/k":
    s = st.number_input("s - Número de servidores", min_value=1, step=1)
    k = st.number_input("k - Capacidad total del sistema", min_value=s, step=1)
    rho = lambda_ / (s * mu)
    r = lambda_ / mu

    def P0_mmsk():
        suma = sum((r**n)/math.factorial(n) for n in range(s))
        suma += sum((r**n)/(math.factorial(s) * s**(n-s)) for n in range(s, k+1))
        return 1 / suma

    P0 = P0_mmsk()
    Lq = P0 * ((r**s) / (math.factorial(s) * (1 - rho)**2)) * (1 - rho**(k - s + 1) - (k - s + 1) * rho**(k - s) * (1 - rho))
    prob_rechazo = ((r**k)/(math.factorial(s) * s**(k - s))) * P0
    L = Lq + r * (1 - prob_rechazo)
    Wq = Lq / (lambda_ * (1 - prob_rechazo))
    W = Wq + 1 / mu

elif modelo == "M/M/s/c":
    s = st.number_input("s - Número de servidores", min_value=1, step=1)
    c = st.number_input("c - Capacidad total (incluye servidores y cola)", min_value=s, step=1)
    rho = lambda_ / (s * mu)
    r = lambda_ / mu

    def P0_mmsp():
        suma1 = sum((r**n)/math.factorial(n) for n in range(s))
        suma2 = sum((r**n)/(math.factorial(s) * s**(n-s)) for n in range(s, c+1))
        return 1 / (suma1 + suma2)

    P0 = P0_mmsp()
    Pc = (r**c) / (math.factorial(s) * s**(c - s)) * P0
    L = sum(n * (r**n)/(math.factorial(n)) for n in range(s))
    L += sum(n * (r**n)/(math.factorial(s) * s**(n - s)) for n in range(s, c+1))
    L *= P0
    Lq = L - (1 - Pc) * r
    W = L / (lambda_ * (1 - Pc))
    Wq = Lq / (lambda_ * (1 - Pc))

if lambda_ and mu:
    st.markdown("---")
    st.subheader("📈 Resultados")
    st.write(f"**L - Nº promedio en el sistema:** {L:.2f}")
    st.write(f"**Lq - Nº promedio en la cola:** {Lq:.2f}")
    st.write(f"**W - Tiempo promedio en el sistema:** {W:.2f}")
    st.write(f"**Wq - Tiempo promedio en cola:** {Wq:.2f}")

    st.markdown("---")
    st.subheader("📊 Gráfico Interactivo")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["En sistema"], y=[L], name="L"))
    fig.add_trace(go.Bar(x=["En cola"], y=[Lq], name="Lq"))
    fig.update_layout(title="Número Promedio de Clientes", yaxis_title="Clientes", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Este gráfico de barras compara el número promedio de clientes en el sistema (L) y en la cola (Lq).")

    # Gráfico de pastel
    fig_pie = go.Figure(data=[go.Pie(labels=["En cola", "En servicio"], values=[Lq, max(0, L - Lq)], hole=0.4)])
    fig_pie.update_layout(title="Distribución de Clientes en el Sistema")
    st.plotly_chart(fig_pie, use_container_width=True)
    st.caption("Este gráfico de pastel muestra la proporción entre clientes en espera y en servicio en el sistema.")

    st.markdown("---")
    st.subheader("🧠 Interpretación")
    st.success(f"Este modelo simula un sistema de colas con configuración {modelo}, donde se observa una utilización rho = {rho:.2f}. Con los parámetros ingresados, se espera que haya {L:.2f} clientes en promedio en el sistema, de los cuales {Lq:.2f} están esperando en cola.")

    # Exportar a PDF
    if st.button("📥 Descargar Informe en PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Simulacion - Modelo de Colas Complejas", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Parametros Ingresados", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, f"Modelo: {modelo} - Lambda: {lambda_} - Mu: {mu} - Servidores: {s if modelo != 'M/M/1/c' else 1}".encode('latin1', 'ignore').decode('latin1'))
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Resultados", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, f"L = {L:.2f} - Lq = {Lq:.2f} - W = {W:.2f} - Wq = {Wq:.2f} - Rho = {rho:.2f}".encode('latin1', 'ignore').decode('latin1'))
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Interpretacion", ln=True)
            pdf.set_font("Arial", size=11)
            texto_limpio = f"Este modelo simula un sistema de colas con configuración {modelo}, donde se observa una utilización rho = {rho:.2f}. Con los parámetros ingresados, se espera que haya {L:.2f} clientes en promedio en el sistema, de los cuales {Lq:.2f} están esperando en cola."
            pdf.multi_cell(0, 10, texto_limpio.encode('latin1', 'ignore').decode('latin1'))

            # Guardar gráfico de barras como imagen
            img_path1 = os.path.join(tempfile.gettempdir(), "grafico_barras.png")
            plt.figure()
            plt.bar(["L", "Lq"], [L, Lq], color=['skyblue', 'salmon'])
            plt.title("Número Promedio de Clientes")
            plt.ylabel("Clientes")
            plt.tight_layout()
            plt.savefig(img_path1)
            plt.close()
            pdf.image(img_path1, x=10, w=180)

            # Guardar gráfico de pastel como imagen
            img_path2 = os.path.join(tempfile.gettempdir(), "grafico_pie.png")
            plt.figure()
            plt.pie([Lq, max(0, L - Lq)], labels=["En cola", "En servicio"], autopct='%1.1f%%', colors=['gold', 'lightgreen'])
            plt.title("Distribución de Clientes en el Sistema")
            plt.tight_layout()
            plt.savefig(img_path2)
            plt.close()
            pdf.image(img_path2, x=30, w=150)

            pdf.output(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.download_button("Descargar PDF", f, file_name="simulacion_colas_complejas.pdf")
            try:
                os.remove(img_path1)
                os.remove(img_path2)
                os.remove(tmpfile.name)
            except PermissionError:
                pass
