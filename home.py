# Archivo: Home.py
import streamlit as st

st.set_page_config(page_title="Inicio", layout="centered")
st.title("📚 Bienvenido a la App de Teoría de Colas")
st.markdown("#### Mag. Carlos Alberto Nieto Astahuamán")

st.markdown("""
Esta aplicación está diseñada para ayudarte a explorar, simular y aprender sobre modelos de teoría de colas de forma práctica e interactiva.

Usa el menú lateral izquierdo para acceder a cada sección.
Se recomienda seguir el orden numérico para un aprendizaje progresivo.
""")

st.markdown("---")

st.subheader("📘 Contenido del Curso")

st.markdown("### 🔹 Fundamentos")
st.markdown("""
📖 01. Fundamentos de Colas
""")

st.markdown("### 🔹 Modelos Simples")
st.markdown("""
🧮 02. Modelo MM1 – Teoría y Ejemplo  
📝 03. Evaluación MM1  
🧮 04. Modelo MMs – Teoría y Ejemplo  
📝 05. Evaluación MMs  
🧮 06. Modelo MMsk  
📝 07. Evaluación MMsk  
🧮 08. Modelo MM1c  
📝 09. Evaluación MM1c  
🧮 10. Modelo MMsc  
📝 11. Evaluación MMsc  
🧮 12. Modelo MMcc  
📝 13. Evaluación MMcc
""")

st.markdown("### 🔹 Modelos Complejos")
st.markdown("""
🧮 14. Modelo MG1  
📝 15. Evaluación MG1  
🧮 16. Modelo Determinista  
📝 17. Evaluación Determinista
""")

st.markdown("### 🔹 Aplicación y Simulación")
st.markdown("""
🔍 18. Casos Prácticos Aplicados  
💡 19. Modelos Colas Simples  
💡 20. Modelos Colas Complejas  
📊 21. Comparador de Modelos
""")

st.markdown("### 🔹 Evaluación y Análisis Final")
st.markdown("""
💰 22. Evaluación Económica  
⚙️ 23. Evaluación Eficiencia Servidor  
🎓 24. Evaluación Final Teoría de Colas
""")

st.markdown("---")
st.info("Usa el menú lateral izquierdo para acceder a cada sección. Se recomienda seguir el orden secuencial para un mejor aprendizaje.")

st.markdown("---")
st.markdown("""
📩 Contacto: **carlosnias@gmail.com**  
© 2025 - Todos los derechos reservados. Esta aplicación ha sido desarrollada con fines educativos. No se permite su copia, reproducción o redistribución sin autorización expresa del autor.
""")
