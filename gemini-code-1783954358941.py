import streamlit as st
import pandas as pd

# 1. SIMULACIÓN DE DATOS (Tu "Base de Datos" manual en Pandas)
if 'tasks_data' not in st.session_state:
    st.session_state.tasks_data = [
        {"task_id": 1, "task_name": "Configurar repositorio GitHub", "priority": "Alta", "status": "Completada", "days_to_complete": 1},
        {"task_id": 2, "task_name": "Diseñar base de datos", "priority": "Alta", "status": "Completada", "days_to_complete": 3},
        {"task_id": 3, "task_name": "Maquetar vista principal", "priority": "Media", "status": "Pendiente", "days_to_complete": None},
        {"task_id": 4, "task_name": "Integrar API de pagos", "priority": "Alta", "status": "Pendiente", "days_to_complete": None},
        {"task_id": 5, "task_name": "Escribir pruebas unitarias", "priority": "Baja", "status": "Completada", "days_to_complete": 2},
        {"task_id": 6, "task_name": "Optimizar carga de imágenes", "priority": "Media", "status": "Completada", "days_to_complete": 1},
        {"task_id": 7, "task_name": "Configurar despliegue web", "priority": "Alta", "status": "Pendiente", "days_to_complete": None},
    ]

# Convertimos los datos originales a DataFrame de Pandas
df_base = pd.DataFrame(st.session_state.tasks_data)

# INTERFAZ
st.set_page_config(page_title="Gestor de Proyectos + Analytics", layout="wide")
st.title("🚀 Panel de Control de Proyectos & Productividad")
st.subheader("Mejora del sistema: Integración de KPIs con Pandas")

# =========================================================================
# NUEVA SECCIÓN: BARRA LATERAL DE FILTROS (Manejo Dinámico con Pandas)
# =========================================================================
st.sidebar.header("🎯 Filtros de Datos (Pandas)")
filtro_prioridad = st.sidebar.multiselect(
    "Filtrar por Prioridad:",
    options=df_base["priority"].unique(),
    default=df_base["priority"].unique()
)

filtro_estado = st.sidebar.multiselect(
    "Filtrar por Estado:",
    options=df_base["status"].unique(),
    default=df_base["status"].unique()
)

# Aplicamos los filtros al DataFrame usando la lógica de Pandas
df = df_base[df_base["priority"].isin(filtro_prioridad) & df_base["status"].isin(filtro_estado)]
# =========================================================================

# 2. CÁLCULO DE KPIs CON PANDAS (Ahora sobre el DataFrame filtrado)
total_tasks = len(df)
completed_tasks = len(df[df['status'] == 'Completada'])
completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
avg_time_resolution = df['days_to_complete'].mean() if total_tasks > 0 else 0
high_priority_blockers = len(df[(df['priority'] == 'Alta') & (df['status'] == 'Pendiente')])

# 3. MOSTRAR KPIs (PANEL DE INSIGHTS)
st.markdown("### 📊 Panel de Insights & KPIs (Métricas en Tiempo Real)")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Tareas Visibles", value=total_tasks)
with col2: st.metric(label="Tasa de Finalización", value=f"{completion_rate:.1f}%")
with col3: 
    # Validar si el promedio es nulo
    val_promedio = f"{avg_time_resolution:.1f} días" if not pd.isna(avg_time_resolution) else "N/A"
    st.metric(label="Tiempo Promedio de Cierre", value=val_promedio)
with col4: st.metric(label="Bloqueadores Críticos (Alta)", value=high_priority_blockers)

st.markdown("---")

# 4. GRÁFICAS DE ANALÍTICA CON PANDAS
st.markdown("### 📈 Visualización y Distribución de Datos")
if total_tasks > 0:
    grafica_col1, grafica_col2 = st.columns(2)
    with grafica_col1:
        st.markdown("**Cantidad de Tareas por Prioridad**")
        priority_counts = df['priority'].value_counts()
        st.bar_chart(priority_counts, color="#29b5e8")
    with grafica_col2:
        st.markdown("**Estado Actual de los Entregables**")
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts, color="#ff4b4b")
else:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados en la barra lateral.")

st.markdown("---")

# 5. VISTA DE DATOS AND FORMULARIO
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("### 📝 Listado Actual de Tareas (DataFrame Filtrado)")
    st.dataframe(df, use_container_width=True)
with col_right:
    st.markdown("### ➕ Añadir Nueva Tarea")
    with st.form("new_task_form", clear_on_submit=True):
        new_name = st.text_input("Nombre de la tarea:")
        new_priority = st.selectbox("Prioridad:", ["Alta", "Media", "Baja"])
        submitted = st.form_submit_button("Registrar Tarea")
        if submitted and new_name:
            st.session_state.tasks_data.append({
                "task_id": len(st.session_state.tasks_data) + 1,
                "task_name": new_name,
                "priority": new_priority,
                "status": "Pendiente",
                "days_to_complete": None
            })
            st.rerun()
