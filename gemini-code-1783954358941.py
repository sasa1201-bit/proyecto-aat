import streamlit as st
import pandas as pd

# 1. SIMULACIÓN DE DATOS
if 'tasks_data' not in st.session_state:
    st.session_state.tasks_data = [
        {"task_id": 1, "task_name": "Configurar repositorio GitHub", "priority": "Alta", "status": "Completada", "days_to_complete": 1.0},
        {"task_id": 2, "task_name": "Diseñar base de datos", "priority": "Alta", "status": "Completada", "days_to_complete": 3.0},
        {"task_id": 3, "task_name": "Maquetar vista principal", "priority": "Media", "status": "Pendiente", "days_to_complete": None},
        {"task_id": 4, "task_name": "Integrar API de pagos", "priority": "Alta", "status": "Pendiente", "days_to_complete": None},
        {"task_id": 5, "task_name": "Escribir pruebas unitarias", "priority": "Baja", "status": "Completada", "days_to_complete": 2.0},
        {"task_id": 6, "task_name": "Optimizar carga de imágenes", "priority": "Media", "status": "Completada", "days_to_complete": 1.0},
        {"task_id": 7, "task_name": "Configurar despliegue web", "priority": "Alta", "status": "Pendiente", "days_to_complete": None},
    ]

# Convertimos los datos originales a DataFrame de Pandas
df_base = pd.DataFrame(st.session_state.tasks_data)

# INTERFAZ PREMIUM
st.set_page_config(page_title="Enterprise Project Dashboard", layout="wide")
st.title("💼 Enterprise Analytics & Project Dashboard")
st.caption("Módulo de Inteligencia de Datos y Control de Entregables desarrollado con Streamlit & Pandas")

# BARRA LATERAL DE FILTROS (Manejo Dinámico con Pandas)
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

# Aplicamos los filtros base con la lógica de Pandas
df = df_base[df_base["priority"].isin(filtro_prioridad) & df_base["status"].isin(filtro_estado)]

# 2. CÁLCULO DE KPIs CON PANDAS
total_tasks = len(df)
completed_tasks = len(df[df['status'] == 'Completada'])
completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
avg_time_resolution = df['days_to_complete'].mean() if total_tasks > 0 else 0
high_priority_blockers = len(df[(df['priority'] == 'Alta') & (df['status'] == 'Pendiente')])

# 3. MOSTRAR KPIs (Con diseño de contenedores profesionales)
st.markdown("### 📊 Indicadores Clave de Rendimiento (Métricas de Operación)")
col1, col2, col3, col4 = st.columns(4)
with col1: 
    st.metric(label="Volumen Total Visible", value=total_tasks)
with col2: 
    st.metric(label="Tasa de Cierre Eficiente", value=f"{completion_rate:.1f}%")
with col3: 
    val_promedio = f"{avg_time_resolution:.1f} días" if not pd.isna(avg_time_resolution) else "N/A"
    st.metric(label="Tiempo Medio de Resolución", value=val_promedio)
with col4: 
    # Alerta visual en color si hay bloqueadores críticos
    if high_priority_blockers > 0:
        st.metric(label="⚠️ Riesgos Críticos (Alta)", value=high_priority_blockers, delta="Acción Requerida", delta_color="inverse")
    else:
        st.metric(label="Riesgos Críticos (Alta)", value=high_priority_blockers, delta="Estable")

st.markdown("---")

# 4. GRÁFICAS DE ÁREA INTERACTIVAS CON PANDAS
st.markdown("### 📈 Tendencias y Distribución del Flujo de Trabajo")
if total_tasks > 0:
    grafica_col1, grafica_col2 = st.columns(2)
    with grafica_col1:
        st.markdown("**Carga Operativa por Nivel de Prioridad**")
        priority_counts = df['priority'].value_counts()
        st.area_chart(priority_counts, color="#29b5e8")
    with grafica_col2:
        st.markdown("**Balance de Entregables Completados vs Pendientes**")
        status_counts = df['status'].value_counts()
        st.area_chart(status_counts, color="#10b981") # Color verde corporativo
else:
    st.warning("⚠️ No se encontraron registros que coincidan con la segmentación actual.")

st.markdown("---")

# 5. VISTA DE DATOS PREMIUM Y SECCIÓN DE OPERACIONES
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📝 Repositorio Central de Datos (Editable)")
    
    # Buscador integrado de texto estructurado
    search_query = st.text_input("🔍 Filtrado inteligente por palabras clave:", "")
    if search_query:
        df = df[df['task_name'].str.contains(search_query, case=False, na=False)]
    
    # CONFIGURACIÓN PROFESIONAL DE COLUMNAS (Formato tipo SaaS)
    edited_df = st.data_editor(
        df, 
        use_container_width=True,
        disabled=["task_id"], 
        column_config={
            "task_id": st.column_config.NumberColumn("ID", format="%d"),
            "task_name": st.column_config.TextColumn("Descripción de la Actividad", required=True), 
            "priority": st.column_config.SelectboxColumn("Prioridad Organizacional", options=["Alta", "Media", "Baja"]),
            "status": st.column_config.SelectboxColumn("Estado de Entrega", options=["Pendiente", "Completada"]),
            "days_to_complete": st.column_config.NumberColumn("Tiempo Empleado (Días)", format="%.1f")
        }
    )
    
    # Descarga directa formateada
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Dataframe a CSV Lineal",
        data=csv_data,
        file_name="data_audit_report.csv",
        mime="text/csv"
    )
    
    # Sincronizar cambios en la tabla
    if not edited_df.equals(df):
        for index, row in edited_df.iterrows():
            idx_original = next((i for i, item in enumerate(st.session_state.tasks_data) if item["task_id"] == row["task_id"]), None)
            if idx_original is not None:
                st.session_state.tasks_data[idx_original] = row.to_dict()
        st.rerun()

with col_right:
    st.markdown("### ⚙️ Consola de Control")
    
    # Organización en pestañas limpias
    tab1, tab2 = st.tabs(["➕ Registrar Tarea", "ℹ️ Acerca del Sistema"])
    
    with tab1:
        with st.form("new_task_form", clear_on_submit=True):
            new_name = st.text_input("Definición de nueva actividad:")
            new_priority = st.selectbox("Asignar Prioridad:", ["Alta", "Media", "Baja"])
            submitted = st.form_submit_button("Inyectar Datos al Dataframe")
            if submitted and new_name:
                st.session_state.tasks_data.append({
                    "task_id": len(st.session_state.tasks_data) + 1,
                    "task_name": new_name,
                    "priority": new_priority,
                    "status": "Pendiente",
                    "days_to_complete": None
                })
                st.rerun()
                
    with tab2:
        st.markdown("""
        **Tecnologías Utilizadas:**
        *   **Pandas core Engine:** Filtrado matricial de datos a través de máscaras booleanas `.isin()`.
        *   **Stateful Memory:** Persistencia de datos local reactiva con `st.session_state`.
        *   **Dynamic UI Layout:** Columnas asíncronas y layouts autoajustables.
        """)
