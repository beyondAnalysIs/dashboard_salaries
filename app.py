import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# carga de datos
df = pd.read_csv('salaries.csv')
print(f'Informacion general: {df.info()}\n')
print(f'Primeras columnas: {df.head()}\n')
print(f'Informacion estadística: {df.describe()}\n')
print(f'Últimas columnas: {df.tail()}\n')
print(f'Tamaño del Dataframe: {df.shape}\n')



# Mostrst información del DataFrame
#st.title('Data Analysis')
#st.write(df.head())
#st.write(df.describe())

# Verificar si hay valores nulos
print(f'Valores nulos: {df.isnull().sum()}\n')

# anaálisis de columnas categóricas
categorical_columns = ['experience_level', 'employment_type', 'job_title',
                        'salary_currency', 'employee_residence', 
                        'company_location','company_size']

for column in categorical_columns:
    print(f'conteo: {df[column].value_counts()}\n')
    print(f'Valores únicos en {column}: {df[column].unique()}\n')

# analisis de salarios
print(f'''\nEstadísticas de salarios en USD:
      \n{df["salary_in_usd"].describe()}\n''')

# top 10 trabajos mejor pagados
top_10_jobs = df.groupby('job_title')['salary_in_usd'].mean().sort_values(ascending=False).head(10)
print(f'Top 10 trabajos mejor pagados:\n{top_10_jobs}\n')

# visualización
# Distribucion de salarios
plt.figure(figsize=(12, 6))
sns.histplot(df['salary_in_usd'], bins=30, kde=True) 
plt.title('Distribución de Salarios en USD')
plt.xlabel('Salario en USD')
plt.ylabel('Frecuencia')
#st.pyplot(plt)

# Salarios por nivel de experiencia
plt.figure(figsize=(12, 6))
sns.boxplot(x='experience_level', y='salary_in_usd', data=df)
plt.title('Salarios por Nivel de Experiencia')
plt.xlabel('Nivel de Experiencia')
plt.ylabel('Salario en USD')
#st.pyplot(plt)

# Salarios por tipo de empresa
plt.figure(figsize=(12, 6))
sns.boxplot(x='company_size', y='salary_in_usd', data=df)
plt.title('Salarios por Tamaño de Empresa')
plt.xlabel('Tamaño de Empresa')
plt.ylabel('Salario en USD')
#st.pyplot(plt)

# configuracion de la página
st.set_page_config(
    page_title='Análisis de Salarios',
    page_icon='📊',
    layout='wide'
)

# Título
st.markdown(f'''\n
    <style>
        .main-title {{
            text-align: center;
            color: #4CAF50;
            font-size: 2.5rem;
            margin-botton: .5rem
        }}
        .sub-title {{
            text-align: center;
            color: #555;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }} 
    </style> 
    <h1 class="main-title">
        🚀 Análisis de Salarios en la Industria Tecnológica
    </h1>
    <p class="sub-title">
        Exploración de datos y visualización de salarios en la industria tecnológica a partir de un conjunto de datos global.
    </p>
''', unsafe_allow_html=True)
    
# kpis Principales
st.header('📊 KPIs Principales')
col1, col2, col3 = st.columns(3)

with col1:
    avg_salario = df['salary_in_usd'].mean()
    st.metric(label='Salario Promedio (USD)', value=f'${avg_salario:,.2f}')

with col2:
    median_salary = df['salary_in_usd'].median()
    st.metric(label='Salario Mediano (USD)', value=f'${median_salary:,.2f}')

with col3:
    total_records = len(df)
    st.metric(label='Total de Registros', value=total_records)
    