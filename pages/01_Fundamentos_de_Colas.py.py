# Archivo: pages/1. Introducción a la Teoría de Colas.py
import streamlit as st

st.set_page_config(page_title="1. Introducción a la Teoría de Colas", layout="centered")
st.title("📘 Introducción a la Teoría de Colas")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

# Sección 1: ¿Qué es?
st.header("🔍 ¿Qué es la teoría de colas?")
st.markdown("""
La teoría de colas es una rama de las matemáticas aplicadas que estudia el comportamiento de las líneas de espera (colas). 
Se enfoca en analizar cómo se forman, cuánto tiempo esperan los clientes, cuántos recursos se necesitan y cómo optimizar el sistema para reducir esperas y costos.
""")

# Sección 2: Aplicaciones reales
st.header("🏥 Aplicaciones reales")
st.markdown("""
La teoría de colas se aplica en una gran variedad de entornos reales, como:

- Bancos y cajas únicas
- Call centers y soporte técnico
- Hospitales y clínicas
- Supermercados y farmacias
- Fábricas, talleres y servicios logísticos
- Sistemas informáticos y servidores web
""")

# Sección 3: Elementos del sistema de colas
st.header("🔧 Elementos de un sistema de colas")
st.markdown("""
- **Cliente**: quien llega en busca de atención
- **Servidor**: recurso que atiende a los clientes
- **Cola**: espacio donde los clientes esperan
- **Disciplina**: orden en que se atienden (FIFO, prioridad, etc.)
- **Tiempo de llegada**: intervalo entre llegadas de clientes
- **Tiempo de servicio**: cuánto tarda cada atención
""")

# Sección 4: Notación de Kendall
st.header("🧾 Notación de Kendall")
with st.expander("📘 ¿Qué significa A/S/c/K/N/D?"):
    st.markdown("""
    - **A**: distribución del tiempo entre llegadas (M: exponencial, D: determinista, G: general)
    - **S**: distribución del tiempo de servicio (M, D, G)
    - **c**: número de servidores
    - **K**: capacidad del sistema (opcional)
    - **N**: tamaño de la población (opcional)
    - **D**: disciplina de la cola (FIFO, LIFO, prioridad)

    Ejemplos:
    - **M/M/1**: llegadas y servicio exponenciales, 1 servidor
    - **M/M/c**: igual que anterior, pero con c servidores
    - **M/G/1**: llegadas exponenciales, servicio general
    """)

# Sección 5: Parámetros fundamentales
st.header("📐 Parámetros fundamentales")
st.markdown("""
| Símbolo | Significado                  |
|---------|------------------------------|
| λ       | Tasa de llegada               |
| μ       | Tasa de servicio              |
| ρ       | Utilización del sistema       |
| L       | Nº promedio en el sistema     |
| Lq      | Nº promedio en la cola        |
| W       | Tiempo promedio en el sistema |
| Wq      | Tiempo promedio en la cola    |

Ley de Little:

\[ L = \lambda \cdot W \quad ; \quad L_q = \lambda \cdot W_q \]
""", unsafe_allow_html=True)

# Sección 6: Ventajas y limitaciones
st.header("⚖️ Ventajas y limitaciones")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    ### ✅ Ventajas
    - Permite optimizar recursos
    - Reduce tiempos de espera
    - Ayuda a diseñar sistemas eficientes
    - Aplicable a múltiples sectores
    """)

with col2:
    st.markdown("""
    ### ⚠️ Limitaciones
    - Modelos idealizados
    - No siempre representan la realidad
    - Requieren datos precisos
    - Supuestos a veces poco realistas
    """)

# Sección 7: Pregunta de reflexión
st.header("💭 Pregunta de reflexión")
st.info("¿Por qué crees que es importante conocer cómo se comportan las colas en sistemas reales?")

# Cierre
st.markdown("---")
st.success("Continúa con el modelo M/M/1 desde el menú lateral izquierdo para aplicar lo aprendido.")
st.markdown("📧 Contacto: [cnieto@gmail.com](mailto:cnieto@gmail.com)")
st.markdown("© 2025 Mag. Carlos Alberto Nieto Astahuamán")
