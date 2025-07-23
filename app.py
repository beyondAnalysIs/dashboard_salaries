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
    df['exp_level_name'] = df['experience_level'].map(exp_levels)
    df['remote_type'] = df['remote_ratio'].map(remote_types)
    df['country'] = df['company_location'].map(country_map)
    return df

df = load_data()


# --- ESTILOS CSS CON EL EFECTO NEON/TORNASOL (ESTÁTICO) ---
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
        /* Se ha eliminado la línea de animación para que el borde sea estático */
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
    .chart-container h3 { color: #a300ff; margin-top: 0; text-align: center; }

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
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR DE FILTROS ---
with st.sidebar:
    st.header('🔍 Filtros')
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
        min_value=min_salary, max_value=max_salary, value=(min_salary, max_salary)
    )

    # Aplicar filtros
    filtered_df = df.copy()
    if selected_exp != 'Todos':
        filtered_df = filtered_df[filtered_df['exp_level_name'] == selected_exp]
    if selected_emp != 'Todos':
        filtered_df = filtered_df[filtered_df['employment_type'] == selected_emp]
    if selected_size != 'Todos':
        filtered_df = filtered_df[filtered_df['company_size'] == selected_size]
    if selected_country != 'Todos':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    filtered_df = filtered_df[
        (filtered_df['salary_in_usd'] >= salary_range[0]) &
        (filtered_df['salary_in_usd'] <= salary_range[1])
    ]

    st.markdown("---")
    st.info("Este dashboard analiza salarios en la industria tecnológica basado en datos globales.")


# --- CUERPO PRINCIPAL DEL DASHBOARD ---

# Título
st.markdown("""
<h1 class="main-title">🚀 Análisis de Salarios en la Industria Tecnológica</h1>
<p class="sub-title">Exploración de datos con un toque de neón.</p>
""", unsafe_allow_html=True)

# KPIs Principales
st.markdown('<h2 class="section-header">📊 KPIs Principales</h2>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    avg_salario = filtered_df['salary_in_usd'].mean() if not filtered_df.empty else 0
    st.markdown(f"""
    <div class="card-wrapper">
        <div class="kpi-card">
            <h3>Salario Promedio (USD)</h3>
            <h2>${avg_salario:,.2f}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    median_salary = filtered_df['salary_in_usd'].median() if not filtered_df.empty else 0
    st.markdown(f"""
    <div class="card-wrapper">
        <div class="kpi-card">
            <h3 class="char-container">Salario Mediano (USD)</h3>
            <h2>${median_salary:,.2f}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_records = len(filtered_df)
    st.markdown(f"""
    <div class="card-wrapper">
        <div class="kpi-card">
            <h3>Total de Registros</h3>
            <h2>{total_records}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<h2 class="section-header">📈 Visualizaciones Detalladas</h2>', unsafe_allow_html=True)

# --- GRÁFICOS ---
col_graf_1, col_graf_2 = st.columns(2)

with col_graf_1:
    with st.container():
        st.markdown('<div class="card-wrapper"><div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-container">Distribución de Salarios</h3>', unsafe_allow_html=True)
        fig = px.histogram(filtered_df, x='salary_in_usd', nbins=30, color_discrete_sequence=['#00aaff'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_title='Frecuencia', xaxis_title='Salario en USD', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card-wrapper"><div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-container">Top 10 Trabajos Mejor Pagados</h3>', unsafe_allow_html=True)
        top_jobs = filtered_df.groupby('job_title')['salary_in_usd'].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top_jobs, y='job_title', x='salary_in_usd', color='salary_in_usd', color_continuous_scale='Plasma', orientation='h')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_title=None, xaxis_title='Salario Promedio (USD)', font_color='white', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

with col_graf_2:
    with st.container():
        st.markdown('<div class="card-wrapper"><div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-container">Salarios por Nivel de Experiencia</h3>', unsafe_allow_html=True)
        fig = px.box(filtered_df, x='exp_level_name', y='salary_in_usd', color='exp_level_name',
                     color_discrete_sequence=['#00aaff', '#00ffcc', '#a300ff', '#ff2a2a'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_title='Nivel de Experiencia', yaxis_title='Salario en USD', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # GRÁFICO DE COMPARACIÓN GEOGRÁFICA
    with st.container():
        st.markdown('<div class="card-wrapper"><div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-container">Comparación Geográfica de Salarios</h3>', unsafe_allow_html=True)
        country_avg = filtered_df.groupby('country')['salary_in_usd'].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(country_avg, x='country', y='salary_in_usd', color='salary_in_usd', color_continuous_scale='Viridis')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title='País', yaxis_title='Salario Promedio (USD)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

# GRÁFICO DE IMPACTO DEL TRABAJO REMOTO
with st.container():
    st.markdown('<div class="card-wrapper"><div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-container">Impacto del Trabajo Remoto en los Salarios</h3>', unsafe_allow_html=True)
    remote_analysis = filtered_df.groupby('remote_type')['salary_in_usd'].mean().reset_index()
    fig = px.bar(remote_analysis, x='remote_type', y='salary_in_usd', color='salary_in_usd', color_continuous_scale='Magma')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title='Tipo de Trabajo Remoto', yaxis_title='Salario Promedio (USD)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)