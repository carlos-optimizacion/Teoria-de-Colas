import streamlit as st

st.set_page_config(page_title="Inicio", page_icon="📚", layout="wide")

st.title("📚 Teoría de Colas | Aprendizaje + Análisis")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Esta aplicación integra dos rutas de trabajo:

- **Modo Aprendizaje:** teoría, ejemplos, ejercicios y evaluaciones progresivas.
- **Modo Analista:** resolución End-to-End de un sistema real, desde el diagnóstico AS IS
  hasta escenarios TO BE, evaluación económica y recomendación.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎓 Modo Aprendizaje")
    st.markdown("""
    **Fundamentos**
    - 01. Fundamentos de Colas

    **Modelos simples y evaluaciones**
    - 02–13. M/M/1, M/M/s y modelos con capacidad limitada

    **Modelos complejos**
    - 14–17. M/G/1 y modelo determinista

    **Aplicación y simulación**
    - 18. Casos Prácticos Aplicados
    - 19. Modelos de Colas Simples
    - 20. Modelos de Colas Complejas
    - 21. Comparador de Modelos

    **Evaluación y análisis**
    - 22. Evaluación Económica
    - 23. Eficiencia del Servidor
    - 24. Evaluación Final
    """)

with col2:
    st.subheader("🧭 Modo Analista End-to-End")
    st.success("Nuevo: **25. Análisis End-to-End de Sistemas de Colas**")
    st.markdown("""
    Utiliza este módulo cuando quieras analizar un caso completo:

    **1. Definir el problema real**  
    **2. Seleccionar automáticamente el modelo**  
    **3. Diagnosticar el escenario AS IS**  
    **4. Generar escenarios TO BE**  
    **5. Evaluar tiempos, utilización y costos**  
    **6. Obtener una recomendación operativa**  
    **7. Comparar AS IS vs TO BE y descargar el informe**

    El objetivo es pasar de la fórmula a la **toma de decisiones en Ingeniería Industrial**.
    """)

st.markdown("---")
st.subheader("🧩 Ruta recomendada")
st.markdown("""
Si estás aprendiendo el tema por primera vez, sigue el orden numérico desde el módulo 01.
Si ya conoces la teoría y deseas resolver un problema aplicado, ve directamente al módulo **25**.
""")

st.info("Usa el menú lateral para acceder a los módulos. El módulo 25 integra el flujo completo de análisis.")

st.markdown("---")
st.markdown("""
📩 Contacto: **carlosnias@gmail.com**  
© 2025 - Todos los derechos reservados. Aplicación desarrollada con fines educativos.
No se permite su copia, reproducción o redistribución sin autorización expresa del autor.
""")
