import streamlit as st

st.set_page_config(
    page_title="Teoría de Colas | Decision Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Shell visual compartido por toda la aplicación
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root{
        --navy:#12324F;
        --blue:#1F4E78;
        --blue-2:#2D6A9F;
        --cyan:#2E8AA6;
        --ink:#172033;
        --muted:#667085;
        --line:#E3EAF1;
        --surface:#FFFFFF;
        --soft:#F3F7FA;
    }

    .stApp{
        background:linear-gradient(180deg,#F7F9FC 0%,#F3F6F9 100%);
    }
    .block-container{
        padding-top:1.25rem;
        padding-bottom:2.4rem;
        max-width:1480px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"]{
        background:linear-gradient(180deg,#F8FBFD 0%,#EFF5F9 100%);
        border-right:1px solid #D8E3EC;
        box-shadow:8px 0 24px rgba(23,50,77,.035);
    }
    section[data-testid="stSidebar"] > div{
        padding-top:.7rem;
    }
    [data-testid="stSidebarNav"]{
        padding:.4rem .65rem .2rem .65rem;
    }
    [data-testid="stSidebarNav"] ul{
        gap:.14rem;
    }
    [data-testid="stSidebarNav"] a{
        border-radius:11px;
        min-height:2.45rem;
        transition:all .16s ease;
        border:1px solid transparent;
    }
    [data-testid="stSidebarNav"] a:hover{
        background:#E7F0F6;
        border-color:#D4E3ED;
        transform:translateX(2px);
    }
    [data-testid="stSidebarNav"] a[aria-current="page"]{
        background:linear-gradient(135deg,#173F63 0%,#23618F 100%);
        border-color:#173F63;
        box-shadow:0 6px 15px rgba(31,78,120,.18);
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] *{
        color:#FFFFFF !important;
    }
    .sidebar-panel{
        margin:.75rem .2rem .25rem;
        padding:14px 15px;
        border-radius:15px;
        background:rgba(255,255,255,.78);
        border:1px solid #DCE6EE;
        box-shadow:0 4px 14px rgba(31,78,120,.05);
    }
    .sidebar-panel .sb-kicker{
        font-size:.68rem;
        text-transform:uppercase;
        letter-spacing:.12em;
        font-weight:800;
        color:#2D6A9F;
        margin-bottom:5px;
    }
    .sidebar-panel .sb-title{
        font-size:.97rem;
        font-weight:800;
        color:#17324D;
        margin-bottom:5px;
    }
    .sidebar-panel .sb-text{
        font-size:.78rem;
        line-height:1.45;
        color:#667085;
    }
    .sidebar-chip{
        display:inline-block;
        margin-top:9px;
        padding:4px 8px;
        border-radius:999px;
        background:#E8F2F8;
        color:#1F4E78;
        font-size:.68rem;
        font-weight:800;
    }

    /* Home */
    .hero-modern{
        position:relative;
        overflow:hidden;
        background:linear-gradient(128deg,#102F4A 0%,#1D537E 57%,#2E789F 100%);
        border-radius:24px;
        padding:34px 38px 30px;
        color:#FFFFFF;
        box-shadow:0 16px 36px rgba(22,58,95,.18);
        margin-bottom:1.15rem;
    }
    .hero-modern:after{
        content:"";
        position:absolute;
        width:310px;
        height:310px;
        right:-90px;
        top:-125px;
        border-radius:50%;
        border:52px solid rgba(255,255,255,.06);
    }
    .hero-modern:before{
        content:"";
        position:absolute;
        width:145px;
        height:145px;
        right:155px;
        bottom:-92px;
        border-radius:50%;
        background:rgba(255,255,255,.045);
    }
    .hero-kicker{
        display:inline-flex;
        align-items:center;
        gap:7px;
        padding:6px 10px;
        border-radius:999px;
        background:rgba(255,255,255,.11);
        border:1px solid rgba(255,255,255,.16);
        font-size:.72rem;
        font-weight:800;
        letter-spacing:.08em;
        text-transform:uppercase;
    }
    .hero-modern h1{
        margin:15px 0 8px;
        font-size:2.55rem;
        line-height:1.08;
        letter-spacing:-.025em;
    }
    .hero-modern p{
        margin:0;
        max-width:920px;
        font-size:1.03rem;
        line-height:1.62;
        color:rgba(255,255,255,.90);
    }
    .hero-foot{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        margin-top:20px;
    }
    .hero-tag{
        padding:6px 10px;
        border-radius:9px;
        background:rgba(255,255,255,.09);
        font-size:.77rem;
        font-weight:700;
        color:rgba(255,255,255,.92);
    }

    .metric-strip{
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:12px;
        margin:8px 0 22px;
    }
    .metric-tile{
        background:rgba(255,255,255,.92);
        border:1px solid #E0E8EF;
        border-radius:16px;
        padding:15px 17px;
        box-shadow:0 5px 16px rgba(31,78,120,.045);
    }
    .metric-value{
        color:#173F63;
        font-size:1.55rem;
        line-height:1;
        font-weight:850;
        margin-bottom:6px;
    }
    .metric-label{
        color:#667085;
        font-size:.78rem;
        line-height:1.35;
    }

    .section-title{
        margin:4px 0 5px;
        color:#17324D;
        font-size:1.35rem;
        font-weight:850;
        letter-spacing:-.01em;
    }
    .section-subtitle{
        color:#667085;
        margin-bottom:14px;
        font-size:.92rem;
    }

    .mode-card{
        background:rgba(255,255,255,.96);
        border:1px solid #E0E7EE;
        border-radius:19px;
        padding:22px 22px 20px;
        min-height:300px;
        box-shadow:0 7px 20px rgba(31,78,120,.055);
        transition:transform .16s ease,box-shadow .16s ease;
    }
    .mode-card:hover{
        transform:translateY(-2px);
        box-shadow:0 12px 26px rgba(31,78,120,.085);
    }
    .mode-icon{
        width:42px;
        height:42px;
        border-radius:13px;
        display:flex;
        align-items:center;
        justify-content:center;
        background:#E9F2F8;
        font-size:1.25rem;
        margin-bottom:13px;
    }
    .mode-pill{
        display:inline-block;
        background:#EEF4F8;
        color:#1F4E78;
        border-radius:999px;
        padding:5px 9px;
        font-size:.68rem;
        font-weight:850;
        letter-spacing:.06em;
        text-transform:uppercase;
        margin-bottom:8px;
    }
    .mode-card h3{
        margin:2px 0 7px;
        color:#17324D;
        font-size:1.18rem;
    }
    .mode-card p,.mode-card li{
        color:#5F6B7A;
        font-size:.88rem;
        line-height:1.5;
    }
    .mode-card ul{
        padding-left:1.1rem;
        margin-bottom:0;
    }

    .route-grid{
        display:grid;
        grid-template-columns:repeat(5,minmax(0,1fr));
        gap:10px;
        margin-top:5px;
    }
    .route-step{
        position:relative;
        background:#FFFFFF;
        border:1px solid #E1E8EF;
        border-radius:15px;
        padding:16px 14px 15px;
        min-height:116px;
        box-shadow:0 4px 14px rgba(31,78,120,.04);
    }
    .route-n{
        width:27px;
        height:27px;
        border-radius:9px;
        display:flex;
        align-items:center;
        justify-content:center;
        background:#173F63;
        color:#FFFFFF;
        font-size:.73rem;
        font-weight:850;
        margin-bottom:10px;
    }
    .route-step strong{
        display:block;
        color:#17324D;
        font-size:.89rem;
        margin-bottom:3px;
    }
    .route-step span{
        color:#75808D;
        font-size:.76rem;
        line-height:1.35;
    }

    .start-card{
        background:linear-gradient(135deg,#FFFFFF 0%,#F2F7FA 100%);
        border:1px solid #DCE7EF;
        border-radius:18px;
        padding:19px 21px;
        margin-top:17px;
    }
    .start-card strong{color:#17324D}
    .start-card p{color:#667085;margin:.35rem 0 0;font-size:.87rem}

    #MainMenu{visibility:hidden}
    footer{visibility:hidden}

    @media(max-width:900px){
        .metric-strip{grid-template-columns:repeat(2,minmax(0,1fr));}
        .route-grid{grid-template-columns:1fr;}
        .hero-modern{padding:28px 24px;}
        .hero-modern h1{font-size:2.05rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Definición explícita de navegación
# -----------------------------------------------------------------------------
def render_home():
    st.markdown(
        """
        <div class="hero-modern">
            <div class="hero-kicker">▦ Investigación de Operaciones · Ingeniería Industrial</div>
            <h1>Teoría de Colas · Decision Lab</h1>
            <p>
                Aprende la matemática, interpreta los indicadores en lenguaje sencillo y convierte escenarios de espera
                en decisiones de capacidad, nivel de servicio y costo.
            </p>
            <div class="hero-foot">
                <span class="hero-tag">Matemática + interpretación</span>
                <span class="hero-tag">Laboratorios interactivos</span>
                <span class="hero-tag">Decisiones operativas</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="metric-strip">
            <div class="metric-tile"><div class="metric-value">17</div><div class="metric-label">módulos de aprendizaje, aplicación y análisis</div></div>
            <div class="metric-tile"><div class="metric-value">3</div><div class="metric-label">modos de trabajo según el objetivo del usuario</div></div>
            <div class="metric-tile"><div class="metric-value">5</div><div class="metric-label">etapas para pasar de teoría a decisión sustentada</div></div>
            <div class="metric-tile"><div class="metric-value">2 capas</div><div class="metric-label">resultado matemático + interpretación operativa</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Elige tu ruta de trabajo</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">La plataforma está organizada por intención: aprender, aplicar o analizar un sistema real.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown(
            """
            <div class="mode-card">
                <div class="mode-icon">🎓</div>
                <span class="mode-pill">Modo aprendizaje</span>
                <h3>Comprender antes de calcular</h3>
                <p>Ruta progresiva para dominar la lógica de los modelos y aprender a interpretar cada indicador.</p>
                <ul>
                    <li>Fundamentos y notación</li>
                    <li>Ejemplos matemáticos paso a paso</li>
                    <li>Laboratorios con parámetros modificables</li>
                    <li>Interpretación en lenguaje sencillo</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page_fundamentos, label="Empezar por Fundamentos", icon=":material/school:", use_container_width=True)

    with c2:
        st.markdown(
            """
            <div class="mode-card">
                <div class="mode-icon">🧪</div>
                <span class="mode-pill">Laboratorio aplicado</span>
                <h3>Experimentar con decisiones</h3>
                <p>Evalúa cómo cambia el sistema cuando modificas demanda, servidores, capacidad, variabilidad o costos.</p>
                <ul>
                    <li>Casos de hospital, banca y producción</li>
                    <li>Comparación de escenarios</li>
                    <li>Análisis económico</li>
                    <li>Dimensionamiento de capacidad</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page_cases, label="Ir a Casos Aplicados", icon=":material/science:", use_container_width=True)

    with c3:
        st.markdown(
            """
            <div class="mode-card">
                <div class="mode-icon">📈</div>
                <span class="mode-pill">Modo analista</span>
                <h3>Trabajar con un sistema real</h3>
                <p>Valida si el modelo es razonable para tus datos y construye una recomendación técnica y económica.</p>
                <ul>
                    <li>Diagnóstico de supuestos</li>
                    <li>Lectura de utilización y espera</li>
                    <li>Selección de capacidad</li>
                    <li>Resultado ejecutivo documentable</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page_validator, label="Validar datos primero", icon=":material/fact_check:", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cómo avanza el análisis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Cada etapa responde una pregunta distinta; no conviene saltar directamente al resultado final.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="route-grid">
            <div class="route-step"><div class="route-n">01</div><strong>Comprende</strong><span>¿Qué representa el modelo y cuáles son sus supuestos?</span></div>
            <div class="route-step"><div class="route-n">02</div><strong>Valida</strong><span>¿Los datos reales son compatibles con esos supuestos?</span></div>
            <div class="route-step"><div class="route-n">03</div><strong>Experimenta</strong><span>¿Qué cambia cuando modificas λ, μ, s, K o la variabilidad?</span></div>
            <div class="route-step"><div class="route-n">04</div><strong>Compara</strong><span>¿Qué alternativa mejora servicio, capacidad o costo?</span></div>
            <div class="route-step"><div class="route-n">05</div><strong>Decide</strong><span>¿Qué recomendación puedes sustentar técnica y operativamente?</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="start-card">
            <strong>¿No sabes por dónde empezar?</strong>
            <p>Si estás aprendiendo, inicia en Fundamentos. Si ya tienes datos reales, comienza por el Validador de Supuestos antes de usar el análisis End-to-End.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    q1, q2, q3 = st.columns(3)
    with q1:
        st.page_link(page_fundamentos, label="01 · Fundamentos", icon=":material/menu_book:", use_container_width=True)
    with q2:
        st.page_link(page_validator, label="24 · Validar supuestos", icon=":material/fact_check:", use_container_width=True)
    with q3:
        st.page_link(page_end_to_end, label="25 · Análisis End-to-End", icon=":material/analytics:", use_container_width=True)

    st.markdown("---")
    st.caption(
        "Mag. Carlos Alberto Nieto Astahuamán · Aplicación educativa con fines académicos. "
        "Los resultados dependen de los supuestos del modelo y deben contrastarse con el comportamiento real del proceso."
    )


page_home = st.Page(render_home, title="Inicio", icon=":material/home:", default=True)

page_fundamentos = st.Page("pages/01_Fundamentos_de_Colas.py", title="01 · Fundamentos", icon=":material/menu_book:")
page_mm1 = st.Page("pages/02_Modelo_MM1_Teoria_Ejemplo.py", title="02 · M/M/1", icon=":material/person:")
page_mms = st.Page("pages/04_Modelo_MMs_Teoria_Ejemplo.py", title="04 · M/M/s", icon=":material/groups:")
page_mmsk = st.Page("pages/06_Modelo_MMsk.py", title="06 · M/M/s/K", icon=":material/queue:")
page_mm1k = st.Page("pages/08_Modelo_MM1c.py", title="08 · M/M/1/K", icon=":material/filter_1:")
page_finite_multi = st.Page("pages/10_Modelo_MMsc.py", title="10 · Capacidad finita", icon=":material/view_week:")
page_erlang = st.Page("pages/12_Modelo_MMcc.py", title="12 · Erlang B", icon=":material/block:")
page_mg1 = st.Page("pages/14_Modelo_MG1.py", title="14 · M/G/1", icon=":material/show_chart:")
page_dd1 = st.Page("pages/16_Modelo_Determinista.py", title="16 · D/D/1", icon=":material/straighten:")

page_cases = st.Page("pages/18_Casos_Practicos_Aplicados.py", title="18 · Casos aplicados", icon=":material/science:")
page_simple = st.Page("pages/19_Modelos_Colas_Simples.py", title="19 · Colas simples", icon=":material/tune:")
page_complex = st.Page("pages/20_Modelos_Colas_Complejas.py", title="20 · Colas complejas", icon=":material/account_tree:")
page_compare = st.Page("pages/21_Comparador_Modelos.py", title="21 · Comparador", icon=":material/compare_arrows:")
page_economic = st.Page("pages/22_Analisis_Economico.py", title="22 · Análisis económico", icon=":material/payments:")
page_dimension = st.Page("pages/23_Dimensionamiento_Servidores.py", title="23 · Dimensionamiento", icon=":material/groups_2:")

page_validator = st.Page("pages/24_Validador_Supuestos.py", title="24 · Validador de supuestos", icon=":material/fact_check:")
page_end_to_end = st.Page("pages/25_Analisis_End_to_End.py", title="25 · End-to-End", icon=":material/analytics:")

navigation = {
    "DECISION LAB": [page_home],
    "APRENDER · MODELOS": [
        page_fundamentos,
        page_mm1,
        page_mms,
        page_mmsk,
        page_mm1k,
        page_finite_multi,
        page_erlang,
        page_mg1,
        page_dd1,
    ],
    "APLICAR · DECISIONES": [
        page_cases,
        page_simple,
        page_complex,
        page_compare,
        page_economic,
        page_dimension,
    ],
    "ANALIZAR · DATOS": [
        page_validator,
        page_end_to_end,
    ],
}

pg = st.navigation(navigation, position="sidebar", expanded=True)

st.sidebar.markdown(
    """
    <div class="sidebar-panel">
        <div class="sb-kicker">Decision Lab</div>
        <div class="sb-title">Matemática que se interpreta</div>
        <div class="sb-text">Usa el menú por etapas. Cada laboratorio conserva fórmulas y añade una lectura operativa del resultado.</div>
        <span class="sidebar-chip">17 módulos · 3 rutas</span>
    </div>
    """,
    unsafe_allow_html=True,
)

pg.run()
