import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title='Dashboard de Salarios Tech',
    page_icon='✨',
    layout='wide',
    initial_sidebar_state='expanded'
)

# --- Función reutilizable para crear tarjetas con borde neón ---
# Esto reduce la repetición de código HTML en el cuerpo principal.
def card_wrapper(content_html: str, title: str, card_class: str = "kpi-card"):
    """Genera el HTML para una tarjeta con borde neón y contenido personalizado."""
    st.markdown(f"""
    <div class="card-wrapper">
        <div class="{card_class}">
            <h3>{title}</h3>
            {content_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- CARGA DE DATOS (CACHEADO) ---
@st.cache_data
def load_data():
    # Asumiendo que 'salaries.csv' está en el mismo directorio
    df = pd.read_csv('salaries.csv')
    exp_levels = {'EN': 'Entry-level', 'MI': 'Mid-level', 'SE': 'Senior-level', 'EX': 'Executive-level'}
    remote_types = {0: 'No Remoto', 50: 'Parcialmente Remoto', 100: 'Totalmente Remoto'}
    country_map = {
        "US": "Estados Unidos", "GB": "Reino Unido", "CA": "Canadá", "DE": "Alemania",
        "IN": "India", "FR": "Francia", "ES": "España", "BR": "Brasil", "AU": "Australia",
        "JP": "Japón", "CN": "China", "SG": "Singapur", "NL": "Países Bajos"
    }
    job_types = {
        "FT": "Tiempo Completo (FT)",
        "PT": "Medio Tiempo (PT)",
        "CT": "Contrato (CT)",
        "FL": "Freelance (FL)"
    }
    df['exp_level_name'] = df['experience_level'].map(exp_levels)
    df['remote_type'] = df['remote_ratio'].map(remote_types)
    df['country'] = df['company_location'].map(country_map)
    df['employment_type'] = df['employment_type'].map(job_types)
    # --- Asegurarse de que el año de trabajo es un tipo numérico para el filtrado ---
    df['work_year'] = pd.to_numeric(df['work_year'])
    return df

df = load_data()


# --- ESTILOS CSS ---
st.markdown("""
<style>
    /* --- FONDO Y ESTILO GENERAL --- */
    body {
        background-color: #0e1117;
    }
    .main > div {
        background: none;
    }

    /* --- ESTILO PARA LOS CONTENEDORES (WRAPPERS) --- */
    .card-wrapper {
        position: relative;
        width: 100%;
        z-index: 1;
        margin-bottom: 25px;
    }

    /* Pseudo-elemento para crear el borde y la sombra tornasol */
    .card-wrapper::before {
        content: "";
        position: absolute;
        z-index: -1;
        inset: -3px;
        border-radius: 20px;
        background: conic-gradient(
            from 180deg at 50% 50%,
            #00aaff, #00ffcc, #a300ff, #ff2a2a, #fcee09,
            #00ff66, #00c4ff, #a300ff, #00aaff
        );
        filter: blur(15px);
    }

    /* --- ESTILO PARA EL CONTENIDO INTERNO DE LAS TARJETAS --- */
    .kpi-card, .chart-container {
        padding: 1.5rem;
        border-radius: 18px;
        color: #ffffff;
        text-align: center;
        background: rgba(14, 18, 27, 0.75);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .kpi-card h3 { color: #00aaff; margin-top: 0; }
    .kpi-card h2 { margin-top: 10px; }
    .chart-container h3 { color: #00aaff; margin-top: 0; text-align: center; }

    /* --- TÍTULOS PRINCIPALES --- */
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        background: -webkit-linear-gradient(45deg, #00aaff, #a300ff, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        text-align: center; color: #a0a0a0; font-size: 1.2rem; margin-bottom: 2rem;
    }
    .section-header {
        color: #fafafa; margin-top: 2rem; margin-bottom: 1rem;
        border-bottom: 2px solid #a300ff; padding-bottom: 5px;
        text-align: center;
    }
    
    /* --- TÍTULOS DE GRÁFICAS --- */
    .chart-title { text-align: center; color: #fff; }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR DE FILTROS ---
with st.sidebar:
    st.header('🔍 Filtros')

    # --- Filtro por año ---
    year_options = ['Todos'] + sorted(df['work_year'].unique().tolist(), reverse=True)
    selected_year = st.selectbox('Año de trabajo', year_options)

    exp_options = ['Todos'] + sorted(df['exp_level_name'].unique().tolist())
    selected_exp = st.selectbox('Nivel de experiencia', exp_options)

    emp_options = ['Todos'] + sorted(df['employment_type'].unique().tolist())
    selected_emp = st.selectbox('Tipo de empleo', emp_options)

    size_options = ['Todos'] + sorted(df['company_size'].unique().tolist())
    selected_size = st.selectbox('Tamaño de empresa', size_options)

    country_options = ['Todos'] + sorted(df['country'].dropna().unique().tolist())
    selected_country = st.selectbox('País de la empresa', country_options)

    min_salary, max_salary = int(df['salary_in_usd'].min()), int(df['salary_in_usd'].max())
    salary_range = st.slider(
        'Rango salarial (USD)',
        min_value=min_salary, 
        max_value=max_salary, 
        value=(min_salary, max_salary)
    )

    # ---  Lógica de filtrado simplificada usando el método query() de Pandas ---
    query_parts = []
    if selected_year != 'Todos':
        query_parts.append(f"work_year == {selected_year}")
    if selected_exp != 'Todos':
        query_parts.append(f"exp_level_name == '{selected_exp}'")
    if selected_emp != 'Todos':
        query_parts.append(f"employment_type == '{selected_emp}'")
    if selected_size != 'Todos':
        query_parts.append(f"company_size == '{selected_size}'")
    if selected_country != 'Todos':
        query_parts.append(f"country == '{selected_country}'")
    
    # Añade el filtro de rango salarial
    min_sal, max_sal = salary_range
    query_parts.append(f"salary_in_usd >= {min_sal} and salary_in_usd <= {max_sal}")
    
    # Une todas las condiciones con 'and' y filtra el DataFrame
    filtered_df = df.query(" and ".join(query_parts)) if query_parts else df.copy()

    st.markdown("---")
    st.info("Este dashboard analiza salarios en la industria tecnológica basado en datos globales.")


# --- CUERPO PRINCIPAL DEL DASHBOARD ---

# Título
st.markdown("""
<h1 class="main-title">🚀 Análisis de Salarios en la Industria Tecnológica</h1>
<p class="sub-title">2020-2025</p>
""", unsafe_allow_html=True)

# --- KPIs Principales ---
st.markdown('<h2 class="section-header">📊 KPIs Principales</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4) 

with col1:
    # --- KPI de Salario Promedio ---
    avg_salario = filtered_df['salary_in_usd'].mean() if not filtered_df.empty else 0
    card_wrapper(f'<h2>${avg_salario:,.2f}</h2>', 'Salario Promedio (USD)')

with col2:
    # --- KPI de Salario Mediano --- 
    median_salary = filtered_df['salary_in_usd'].median() if not filtered_df.empty else 0
    card_wrapper(f'<h2>${median_salary:,.2f}</h2>', 'Salario Mediano (USD)')

with col3:
    # --- KPI de Desviación Estándar para ver la dispersión ---
    std_salary = filtered_df['salary_in_usd'].std() if not filtered_df.empty else 0
    card_wrapper(f'<h2>${std_salary:,.2f}</h2>', 'Dispersión Salarial (Std)')

with col4:
    # --- KPI de Total de Registros Filtrados ---
    total_records = len(filtered_df)
    card_wrapper(f'<h2>{total_records}</h2>', 'Total de Registros')


# --- Gráfico de Evolución Temporal ---
st.markdown('<h2 class="section-header">📈 Evolución Anual de Salarios</h2>', unsafe_allow_html=True)
trend_df = df.groupby('work_year')['salary_in_usd'].median().reset_index()


fig_trend = px.line(
    trend_df, 
    x='work_year', 
    y='salary_in_usd', 
    markers=True,
    text='salary_in_usd',
    labels={'work_year': 'Año', 'salary_in_usd': 'Salario Mediano (USD)'},
    
)
fig_trend.update_traces(
    mode='lines+markers',
    line=dict(color='#00ffcc', width=5),
    text=trend_df['salary_in_usd'],  # ← coma faltante añadida aquí
    textposition='top center',
    textfont=dict(
        family="Arial",
        size=14,
        color="white"
    ),
    hoverlabel=dict(
        bgcolor='rgba(10,25,20)',
        bordercolor='#00ffcc',
        font=dict(color='#00ffcc', size=14)
    )
)

fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='white',
        xaxis_title='Año',
        yaxis_title='Salario Mediano (USD)',
)
# Usamos una estructura similar a la tarjeta para mantener el estilo
st.markdown('<div class="card-wrapper"><div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)


st.markdown('<h2 class="section-header">Visualizaciones Detalladas</h2>', unsafe_allow_html=True)

# --- GRÁFICOS ---
# --- MODIFICADO: Se utiliza la función card_wrapper para simplificar ---
col_graf_1, col_graf_2 = st.columns(2)

with col_graf_1:
    with st.container():
        card_wrapper(
            '<div id="hist-chart"></div>',
            'Distribución de Salarios', 
            card_class='chart-container'
        )
        fig = px.histogram(filtered_df, x='salary_in_usd', nbins=30, color_discrete_sequence=['#00aaff'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_title='Frecuencia', xaxis_title='Salario en USD', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        card_wrapper(
            '<div id="top-jobs-chart"></div>',
            'Top 10 Trabajos Mejor Pagados',
            card_class='chart-container'
        )
        top_jobs = filtered_df.groupby('job_title')['salary_in_usd'].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top_jobs, y='job_title', x='salary_in_usd', color='salary_in_usd', color_continuous_scale='Plasma', orientation='h')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_title=None, xaxis_title='Salario Promedio (USD)', font_color='white', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

with col_graf_2:
    with st.container():
        card_wrapper(
            '<div id="box-plot-chart"></div>',
            'Salarios por Nivel de Experiencia',
            card_class='chart-container'
        )
        fig = px.box(filtered_df, x='exp_level_name', y='salary_in_usd', color='exp_level_name',
                     color_discrete_sequence=['#00aaff', '#00ffcc', '#a300ff', '#ff2a2a'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_title='Nivel de Experiencia', yaxis_title='Salario en USD', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        card_wrapper(
            '<div id="country-chart"></div>',
            'Top 10 Países por Salario Promedio',
            card_class='chart-container'
        )
        country_avg = filtered_df.groupby('country')['salary_in_usd'].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(country_avg, x='country', y='salary_in_usd', color='salary_in_usd', color_continuous_scale='Viridis')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title='País', yaxis_title='Salario Promedio (USD)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

# --- GRÁFICO DE IMPACTO DEL TRABAJO REMOTO ---
with st.container():
    card_wrapper(
        '<div id="remote-chart"></div>',
        'Impacto del Trabajo Remoto en Salarios',
        card_class='chart-container'
    )
    remote_analysis = filtered_df.groupby('remote_type')['salary_in_usd'].mean().reset_index()
    fig = px.bar(remote_analysis, x='remote_type', y='salary_in_usd', color='salary_in_usd', color_continuous_scale='Magma')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title='Tipo de Trabajo Remoto', yaxis_title='Salario Promedio (USD)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

# --- NUEVO: Tabla de datos interactiva al final ---
st.markdown('<h2 class="section-header">🔬 Explorar Datos Filtrados</h2>', unsafe_allow_html=True)
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# --- NUEVO: Pie de página con enlace al repositorio ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #a0a0a0;">
        <p>Código fuente disponible en <a href="https://github.com/beyondAnalysIs/dashboard_salaries/blob/main/app.py" target="_blank" style="color: #00aaff;">GitHub</a>.</p>
    </div>
    """,
    unsafe_allow_html=True
)