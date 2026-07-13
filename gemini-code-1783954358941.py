import streamlit as st
import pandas as pd

# 1. SIMULACIÓN DE DATOS (Tu "Base de Datos" manual con la columna 'tipo')
if 'tasks_data' not in st.session_state:
    st.session_state.tasks_data = [
        {"task_id": 1, "task_name": "Configurar repositorio GitHub", "tipo": "Desarrollo", "priority": "Alta", "status": "Completada", "days_to_complete": 1.0},
        {"task_id": 2, "task_name": "Diseñar base de datos", "tipo": "Diseño", "priority": "Alta", "status": "Completada", "days_to_complete": 3.0},
        {"task_id": 3, "task_name": "Maquetar vista principal", "tipo": "Diseño", "priority": "Media", "status": "Pendiente", "days_to_complete": None},
        {"task_id": 4, "task_name": "Integrar API de pagos", "tipo": "Desarrollo", "priority": "Alta", "status": "Pendiente", "days_to_complete": None},
        {"task_id": 5, "task_name": "Escribir pruebas unitarias", "tipo": "Pruebas", "priority": "Baja", "status": "Completada", "days_to_complete": 2.0},
        {"task_id": 6, "task_name": "Optimizar carga de imágenes", "tipo": "Desarrollo", "priority": "Media", "status": "Completada", "days_to_complete": 1.0},
        {"task_id": 7, "task_name": "Configurar despliegue web", "tipo": "Desarrollo", "priority": "Alta", "status": "Pendiente", "days_to_complete": None},
    ]

# Convertimos los datos originales a DataFrame de Pandas
df_base = pd.DataFrame(st.session_state.tasks_data)

# INTERFAZ
st.set_page_config(page_title="Gestor de Proyectos + Analytics", layout="wide")
st.title("🚀 Panel de Control de Proyectos & Productividad")
st.subheader("Mejora del sistema: Integración de KPIs con Pandas")

# BARRA LATERAL DE FILTROS (Manejo Dinámico con Pandas)
st.sidebar.header("🎯 Filtros de Datos (Pandas)")
filtro_tipo = st.sidebar.multiselect(
    "Filtrar por Tipo de Tarea:",
    options=df_base["tipo"].unique(),
    default=df_base["tipo"].unique()
)

filtro_prioridad = st.sidebar.multiselect(
    "Filtrar por Prioridad:",
    options=df_base["priority"].unique(),
    default=df_base["priority"].unique()
)

# Aplicamos todos los filtros con la lógica de Pandas
df = df_base[df_base["tipo"].isin(filtro_tipo) & df_base["priority"].isin(filtro_prioridad)]

# 2. CÁLCULO DE KPIs CON PANDAS
total_tasks = len(df)
completed_tasks = len(df[df['status'] == 'Completada'])
completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
avg_time_resolution = df['days_to_complete'].mean() if total_tasks > 0 else 0
high_priority_blockers = len(df[(df['priority'] == 'Alta') & (df['status'] == 'Pendiente')])

# 3. MOSTRAR KPIs
st.markdown("### 📊 Panel de Insights & KPIs (Métricas en Tiempo Real)")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Tareas Visibles", value=total_tasks)
with col2: st.metric(label="Tasa de Finalización", value=f"{completion_rate:.1f}%")
with col3: 
    val_promedio = f"{avg_time_resolution:.1f} días" if not pd.isna(avg_time_resolution) else "N/A"
    st.metric(label="Tiempo Promedio de Cierre", value=val_promedio)
with col4: st.metric(label="Bloqueadores Críticos (Alta)", value=high_priority_blockers)

st.markdown("---")

# 4. GRÁFICAS DE ÁREA INTERACTIVAS CON PANDAS
st.markdown("### 📈 Visualización Dinámica (Gráficas de Área)")
if total_tasks > 0:
    grafica_col1, grafica_col2 = st.columns(2)
    with grafica_col1:
        st.markdown("**Volumen por Tipo de Tarea**")
        tipo_counts = df['tipo'].value_counts()
        st.area_chart(tipo_counts, color="#29b5e8")
    with grafica_col2:
        st.markdown("**Volumen por Estado de los Entregables**")
        status_counts = df['status'].value_counts()
        st.area_chart(status_counts, color="#ff4b4b")
else:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")

st.markdown("---")

# 5. VISTA DE DATOS EDITABLE Y FORMULARIO
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("### 📝 Listado Actual de Tareas (¡Doble clic en cualquier celda para renombrar o cambiar!)")
    
    # Hemos configurado la tabla para que los nombres de las tareas ('task_name') se puedan editar libremente
    edited_df = st.data_editor(
        df, 
        use_container_width=True,
        disabled=["task_id"], # El ID es lo único bloqueado para no romper la base de datos
        column_config={
            "task_name": st.column_config.TextColumn("Nombre de la Tarea", required=True), # TEXTO TOTALMENTE EDITABLE
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["Desarrollo", "Diseño", "Documentación", "Pruebas"]),
            "priority": st.column_config.SelectboxColumn("Priority", options=["Alta", "Media", "Baja"]),
            "status": st.column_config.SelectboxColumn("Status", options=["Pendiente", "Completada"])
        }
    )
    
    # Guardar cambios editados en la tabla (incluyendo los nuevos nombres)
    if not edited_df.equals(df):
        for index, row in edited_df.iterrows():
            idx_original = next((i for i, item in enumerate(st.session_state.tasks_data) if item["task_id"] == row["task_id"]), None)
            if idx_original is not None:
                st.session_state.tasks_data[idx_original] = row.to_dict()
        st.rerun()

with col_right:
    st.markdown("### ➕ Añadir Nueva Tarea")
    with st.form("new_task_form", clear_on_submit=True):
        new_name = st.text_input("Nombre de la tarea:")
        new_tipo = st.selectbox("Tipo de Tarea:", ["Desarrollo", "Diseño", "Documentación", "Pruebas"])
        new_priority = st.selectbox("Prioridad:", ["Alta", "Media", "Baja"])
        submitted = st.form_submit_button("Registrar Tarea")
        if submitted and new_name:
            st.session_state.tasks_data.append({
                "task_id": len(st.session_state.tasks_data) + 1,
                "task_name": new_name,
                "tipo": new_tipo,
                "priority": new_priority,
                "status": "Pendiente",
                "days_to_complete": None
            })
            st.rerun()
