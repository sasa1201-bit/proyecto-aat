import streamlit as st
import pandas as pd
import requests

# Configuración de la página
st.set_page_config(page_title="Forza Football Analytics", page_icon="⚽", layout="wide")

# Título y encabezado
st.title("⚽ Forza Football Analytics")
st.caption("Resultados en tiempo real, seguimiento de favoritos y análisis de rendimiento con Pandas")

# =========================================================================
# CONFIGURACIÓN DE LA API (football-data.org)
# =========================================================================
# El usuario o el profe puede pegar su API Key en la barra lateral
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Ingresa tu API Key de Football-Data:", type="password")

# =========================================================================
# FUNCIONES PARA OBTENER DATOS (Con simulación de respaldo si no hay API Key)
# =========================================================================
@st.cache_data(ttl=60) # Guarda en caché por 1 minuto para no saturar la API gratuita
def obtener_tabla_posiciones(liga_code="PD"): # PD = Primera División de España
    if not api_key:
        # SIMULACIÓN si no hay API Key activa para que el profe vea cómo funciona de inmediato
        datos_simulados = {
            "Real Madrid": [38, 29, 8, 1, 87, 26, 95],
            "FC Barcelona": [38, 26, 7, 5, 79, 44, 85],
            "Girona FC": [38, 25, 6, 7, 85, 46, 81],
            "Atlético de Madrid": [38, 24, 4, 10, 70, 43, 76],
            "Athletic Club": [38, 19, 11, 8, 61, 37, 68],
            "Real Sociedad": [38, 16, 12, 10, 51, 39, 60]
        }
        df = pd.DataFrame.from_dict(datos_simulados, orient='index', 
                                    columns=['Jugados', 'Ganados', 'Empatados', 'Perdidos', 'Goles Favor', 'Goles Contra', 'Puntos'])
        df.index.name = "Equipo"
        return df.reset_index()
    
    # Llamada real a la API
    headers = {'X-Auth-Token': api_key}
    url = f"https://api.football-data.org/v4/competitions/{liga_code}/standings"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            standing_list = data['standings'][0]['table']
            records = []
            for item in standing_list:
                records.append({
                    "Equipo": item['team']['name'],
                    "Jugados": item['playedGames'],
                    "Ganados": item['won'],
                    "Empatados": item['draw'],
                    "Perdidos": item['lost'],
                    "Goles Favor": item['goalsFor'],
                    "Goles Contra": item['goalsAgainst'],
                    "Puntos": item['points']
                })
            return pd.DataFrame(records)
        else:
            st.sidebar.error(f"Error de API: {response.status_code}. Cargando simulación...")
            return obtener_tabla_posiciones("") # Cae en simulación
    except Exception as e:
        return obtener_tabla_posiciones("")

# =========================================================================
# VISTA PRINCIPAL (Pestañas)
# =========================================================================
tab1, tab2, tab3 = st.tabs(["📅 Partidos y Resultados", "⭐ Mis Equipos Favoritos", "📈 Analítica Avanzada (Pandas)"])

# -------------------------------------------------------------------------
# PESTAÑA 1: Partidos y Resultados
# -------------------------------------------------------------------------
with tab1:
    st.header("Matchday - Partidos Recientes y En Vivo")
    
    # Buscador de equipos rápido
    filtro_equipo = st.text_input("🔍 Buscar partido de un equipo específico:", placeholder="Ej. Real Madrid")
    
    # Simulación de partidos de la jornada
    partidos = [
        {"Local": "Real Madrid", "Goles L": 2, "Visita": "FC Barcelona", "Goles V": 1, "Estado": "Finalizado"},
        {"Local": "Girona FC", "Goles L": 3, "Visita": "Athletic Club", "Goles V": 3, "Estado": "En Vivo - Min 78'"},
        {"Local": "Atlético de Madrid", "Goles L": 0, "Visita": "Real Sociedad", "Goles V": 0, "Estado": "Por Jugar (13:00)"},
        {"Local": "Sevilla FC", "Goles L": 1, "Visita": "Real Betis", "Goles V": 2, "Estado": "Finalizado"}
    ]
    
    # Filtrar si el usuario busca algo
    if filtro_equipo:
        partidos = [p for p in partidos if filtro_equipo.lower() in p["Local"].lower() or filtro_equipo.lower() in p["Visita"].lower()]

    # Mostrar tarjetas visuales de los partidos
    for p in partidos:
        col_local, col_vs, col_visita, col_estado = st.columns([3, 2, 3, 2])
        with col_local:
            st.markdown(f"### **{p['Local']}**")
        with col_vs:
            if p['Estado'] != "Por Jugar (13:00)":
                st.markdown(f"<h2 style='text-align: center; color: #ff4b4b;'>{p['Goles L']} - {p['Goles V']}</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='text-align: center; color: gray;'>VS</h2>", unsafe_allow_html=True)
        with col_visita:
            st.markdown(f"### **{p['Visita']}**")
        with col_estado:
            st.info(f"**{p['Estado']}**")
        st.markdown("---")

# -------------------------------------------------------------------------
# PESTAÑA 2: Mis Equipos Favoritos
# -------------------------------------------------------------------------
with tab2:
    st.header("⭐ Tu Zona Personalizada")
    st.write("Selecciona tus clubes para hacerles un seguimiento prioritario:")
    
    # Inicializar favoritos en el estado de la app
    if 'favoritos' not in st.session_state:
        st.session_state.favoritos = ["Real Madrid", "FC Barcelona"]
        
    df_posiciones = obtener_tabla_posiciones()
    
    # Multiselector de favoritos conectado con Pandas
    equipos_disponibles = df_posiciones["Equipo"].tolist()
    seleccionados = st.multiselect("Elige tus equipos favoritos:", options=equipos_disponibles, default=st.session_state.favoritos)
    st.session_state.favoritos = seleccionados
    
    if seleccionados:
        # Filtro dinámico con Pandas (.isin)
        df_favoritos = df_posiciones[df_posiciones["Equipo"].isin(seleccionados)]
        st.write("📊 **Tabla de posiciones de tus favoritos:**")
        st.dataframe(df_favoritos.set_index("Equipo"), use_container_width=True)
    else:
        st.warning("Selecciona al menos un equipo en la lista de arriba para hacerle seguimiento.")

# -------------------------------------------------------------------------
# PESTAÑA 3: Analítica Avanzada (Pandas)
# -------------------------------------------------------------------------
with tab3:
    st.header("📈 Rendimiento de la Liga (Visualizaciones con Pandas)")
    
    df_analisis = obtener_tabla_posiciones()
    
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        # Equipo más goleador usando Pandas (.max())
        goleador_idx = df_analisis["Goles Favor"].idxmax()
        equipo_goleador = df_analisis.loc[goleador_idx, "Equipo"]
        goles_max = df_analisis.loc[goleador_idx, "Goles Favor"]
        st.metric(label="🔥 Más Goleador de la Liga", value=equipo_goleador, delta=f"{goles_max} goles")
        
    with col_metric2:
        # Mejor defensa usando Pandas (.min())
        defensa_idx = df_analisis["Goles Contra"].idxmin()
        equipo_defensa = df_analisis.loc[defensa_idx, "Equipo"]
        goles_contra_min = df_analisis.loc[defensa_idx, "Goles Contra"]
        st.metric(label="🛡️ Mejor Defensa (Menos goles encajados)", value=equipo_defensa, delta=f"{goles_contra_min} goles", delta_color="inverse")
        
    with col_metric3:
        # Promedio de goles en la liga
        promedio_goles = df_analisis["Goles Favor"].mean()
        st.metric(label="⚽ Promedio de Goles por Equipo", value=f"{promedio_goles:.1f} goles")

    st.markdown("---")
    
    col_grafica1, col_grafica2 = st.columns(2)
    with col_grafica1:
        st.markdown("**Comparativa de Puntos de los Equipos**")
        # Gráfica interactiva de puntos usando los datos limpios de Pandas
        df_puntos = df_analisis.set_index("Equipo")["Puntos"]
        st.bar_chart(df_puntos, color="#10b981")
        
    with col_visita:
        st.markdown("**Relación Goles a Favor vs Goles en Contra**")
        # Mostramos una tabla con el diferencial de goles calculado mediante Pandas
        df_analisis["Diferencial"] = df_analisis["Goles Favor"] - df_analisis["Goles Contra"]
        st.dataframe(df_analisis[["Equipo", "Goles Favor", "Goles Contra", "Diferencial"]].set_index("Equipo"), use_container_width=True)
