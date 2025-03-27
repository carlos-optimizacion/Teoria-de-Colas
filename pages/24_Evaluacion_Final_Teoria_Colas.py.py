# Archivo: 24_Evaluacion_Final.py
import streamlit as st
import random
import time

st.set_page_config(page_title="Evaluación Final", layout="centered", initial_sidebar_state="collapsed")
st.title("🎓 24. Evaluación Final de Teoría de Colas")

# Configuración inicial
duracion_total = 20 * 60  # 20 minutos en segundos
if "start_time" not in st.session_state or st.session_state.get("reset", False):
    st.session_state.start_time = time.time()
    st.session_state.respuestas = {}
    st.session_state.finalizado = False
    st.session_state.nota_final = 0
    st.session_state.reset = False

# Temporizador con barra de progreso
if not st.session_state.finalizado:
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.start_time
    segundos_restantes = int(duracion_total - tiempo_transcurrido)

    if segundos_restantes <= 0:
        st.warning("⏰ Se acabó el tiempo. Tu evaluación se ha cerrado automáticamente.")
        st.session_state.finalizado = True
        st.rerun()
    else:
        minutos, segundos = divmod(segundos_restantes, 60)
        porcentaje = int((tiempo_transcurrido / duracion_total) * 100)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### ⏱ Tiempo restante: {minutos:02}:{segundos:02}")
        with col2:
            st.progress(100 - porcentaje)

# Banco de preguntas (30 en total, combinadas)
preguntas_totales = [
    {"pregunta": "¿Qué representa la letra λ en teoría de colas?", "opciones": ["Tasa de llegada", "Tiempo de servicio", "Utilización", "Número de servidores"], "respuesta": "Tasa de llegada", "modulo": "02"},
    {"pregunta": "¿Qué representa la letra μ?", "opciones": ["Tasa de servicio", "Tasa de llegada", "Clientes perdidos", "Costo del sistema"], "respuesta": "Tasa de servicio", "modulo": "02"},
    {"pregunta": "¿Qué significa la métrica Lq?", "opciones": ["Número promedio en el sistema", "Clientes en cola", "Tiempo total en cola", "Probabilidad de rechazo"], "respuesta": "Clientes en cola", "modulo": "02"},
    {"pregunta": "¿Qué condición garantiza estabilidad en M/M/1?", "opciones": ["ρ < 1", "λ > μ", "s < 1", "ρ = 1"], "respuesta": "ρ < 1", "modulo": "02"},
    {"pregunta": "¿Cuál es la fórmula de la utilización ρ en M/M/s?", "opciones": ["λ/μ", "s/λ", "λ/(sμ)", "μ/(λs)"], "respuesta": "λ/(sμ)", "modulo": "04"},
    {"pregunta": "¿Qué representa la métrica W?", "opciones": ["Tiempo promedio en el sistema", "Clientes esperando", "Costo total", "Número de servidores"], "respuesta": "Tiempo promedio en el sistema", "modulo": "02"},
    {"pregunta": "¿Qué modelo considera una capacidad máxima limitada?", "opciones": ["M/M/1", "M/M/s", "M/M/1/c", "M/G/1"], "respuesta": "M/M/1/c", "modulo": "10"},
    {"pregunta": "¿Qué representa Pc en M/M/1/c?", "opciones": ["Costo por cliente", "Utilización máxima", "Probabilidad de rechazo", "Clientes atendidos"], "respuesta": "Probabilidad de rechazo", "modulo": "10"},
    {"pregunta": "¿Qué representa s en M/M/s?", "opciones": ["Número de servidores", "Tiempo de espera", "Costo por hora", "Nivel de servicio"], "respuesta": "Número de servidores", "modulo": "04"},
    {"pregunta": "¿Qué indica un valor alto de W?", "opciones": ["Mucho tiempo en sistema", "Cola vacía", "Bajo uso del servidor", "Rechazo total"], "respuesta": "Mucho tiempo en sistema", "modulo": "02"},
    {"pregunta": "Si λ = 4 y μ = 5 en M/M/1, ¿cuál es ρ?", "opciones": ["0.8", "1.25", "0.5", "4"], "respuesta": "0.8", "modulo": "02"},
    {"pregunta": "Con λ = 2 y μ = 4, ¿cuál es W?", "opciones": ["0.5", "0.33", "1.0", "2.0"], "respuesta": "0.5", "modulo": "02"},
    {"pregunta": "Para M/M/s, si λ = 6, μ = 3 y s = 3, ¿cuál es ρ?", "opciones": ["0.67", "0.5", "1.0", "2.0"], "respuesta": "0.67", "modulo": "04"},
    {"pregunta": "Si ρ = 0.75 en M/M/1, ¿qué interpretación es correcta?", "opciones": ["El sistema está estable", "Habrá rechazo", "La tasa de llegada es mayor", "Hay 1 servidor libre todo el tiempo"], "respuesta": "El sistema está estable", "modulo": "02"},
    {"pregunta": "Si λ = 2, μ = 2.5 y c = 3 en M/M/1/c, ¿cuál es ρ?", "opciones": ["0.8", "1.2", "0.6", "2.0"], "respuesta": "0.8", "modulo": "10"},
    {"pregunta": "λ = 5, μ = 6, ¿cuál es W?", "opciones": ["0.2", "1.2", "0.5", "0.67"], "respuesta": "0.2", "modulo": "02"},
    {"pregunta": "Si λ = 3, μ = 4, ¿Wq?", "opciones": ["0.25", "0.75", "1.0", "0.33"], "respuesta": "0.25", "modulo": "02"},
    {"pregunta": "λ = 3, μ = 5, ¿W?", "opciones": ["0.33", "0.5", "0.4", "0.25"], "respuesta": "0.5", "modulo": "02"},
    {"pregunta": "L = 4, λ = 2. ¿W?", "opciones": ["2.0", "0.5", "1.0", "4.0"], "respuesta": "2.0", "modulo": "02"},
    {"pregunta": "Lq = 2, λ = 2. ¿Wq?", "opciones": ["1.0", "0.5", "2.0", "0.25"], "respuesta": "1.0", "modulo": "02"},
    {"pregunta": "W = 1, λ = 2. ¿L?", "opciones": ["2.0", "0.5", "1.0", "3.0"], "respuesta": "2.0", "modulo": "02"},
    {"pregunta": "λ = 4, μ = 5. ¿Wq?", "opciones": ["0.64", "0.8", "0.25", "1.0"], "respuesta": "0.64", "modulo": "02"},
    {"pregunta": "¿Qué representa Wq?", "opciones": ["Tiempo en cola", "Tasa de rechazo", "Clientes atendidos", "Número de servidores"], "respuesta": "Tiempo en cola", "modulo": "02"},
    {"pregunta": "¿Qué pasa si λ > μ en M/M/1?", "opciones": ["Sistema inestable", "Mejor servicio", "Menor tiempo", "Mayor costo"], "respuesta": "Sistema inestable", "modulo": "02"},
    {"pregunta": "¿Cuál es la fórmula para calcular L?", "opciones": ["λ * W", "μ / λ", "Lq + ρ", "ρ * μ"], "respuesta": "λ * W", "modulo": "02"},
    {"pregunta": "¿Qué significa un Lq alto?", "opciones": ["Cola larga", "Poca demanda", "Sistema vacío", "Bajo uso"], "respuesta": "Cola larga", "modulo": "02"},
    {"pregunta": "¿Cuál es la relación entre W y Wq?", "opciones": ["W = Wq + 1/μ", "W = Wq * μ", "W = Wq - 1/μ", "W = Wq + λ"], "respuesta": "W = Wq + 1/μ", "modulo": "02"},
    {"pregunta": "¿Qué indica ρ > 1 en M/M/1?", "opciones": ["Colas infinitas", "Sistema estable", "Uso óptimo", "Bajo costo"], "respuesta": "Colas infinitas", "modulo": "02"},
    {"pregunta": "¿Qué valor de ρ garantiza estabilidad en M/M/s?", "opciones": ["< 1", "= 1", "> 1", "cualquiera"], "respuesta": "< 1", "modulo": "04"}
]

# Selección aleatoria de 10 preguntas
if "preguntas" not in st.session_state:
    st.session_state.preguntas = random.sample(preguntas_totales, 10)
    for pregunta in st.session_state.preguntas:
        random.shuffle(pregunta["opciones"])

# Mostrar preguntas si no está finalizado
if not st.session_state.finalizado:
    for idx, item in enumerate(st.session_state.preguntas):
        st.markdown(f"**Pregunta {idx+1}: {item['pregunta']}**")
        respuesta = st.radio("Selecciona una opción", item['opciones'], key=f"preg_{idx}")
        st.session_state.respuestas[idx] = respuesta

    if st.button("Finalizar Evaluación"):
        correctas = 0
        errores = []
        for idx, item in enumerate(st.session_state.preguntas):
            if st.session_state.respuestas.get(idx) == item['respuesta']:
                correctas += 1
            else:
                errores.append(item['modulo'])

        total_preguntas = len(st.session_state.preguntas)
        st.session_state.nota_final = round((correctas / total_preguntas) * 20, 1)
        st.session_state.finalizado = True
        st.rerun()

# Mostrar resultados si está finalizado
if st.session_state.finalizado:
    nota = st.session_state.nota_final
    st.markdown(f"### 🧾 Tu nota final es: **{nota} / 20**")

    if nota >= 18:
        st.success("🥇 Excelente dominio del tema.")
    elif nota >= 14:
        st.info("👍 Buen manejo, pero hay aspectos por reforzar.")
    elif nota >= 10:
        st.warning("⚠️ Nivel básico. Revisa los módulos clave.")
    else:
        st.error("❌ Necesitas repasar los conceptos fundamentales.")

    if "errores" in locals() and errores:
        st.markdown("### 📘 Recomendaciones de Repaso")
        modulos_unicos = sorted(set(errores))
        for m in modulos_unicos:
            st.markdown(f"🔁 Revisa el módulo **{m}** para mejorar tu comprensión.")

    if st.button("🔁 Intentar nuevamente"):
        st.session_state.reset = True
        st.rerun()

# Refresco visual automático
if not st.session_state.finalizado:
    time.sleep(1)
    st.rerun()
