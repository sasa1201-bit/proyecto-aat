import streamlit as st
import pandas as pd
import requests

# Configuración de la página estilo Deportivo Premium
st.set_page_config(page_title="Forza Fútbol Live", page_icon="⚽", layout="wide")

st.title("⚽ Forza Fútbol: Marcadores en Vivo")
st.caption("Consumiendo datos reales al instante con API-Football y análisis estadístico con Pandas")

# =========================================================================
# CONFIGURACIÓN DE LA API (Tu API Key ya integrada de forma fija)
# =========================================================================
API_KEY = "acb867b68f5987d9c226e48c12c090e3"

# Botón para forzar actualización de los datos en la barra lateral
st.sidebar.header("🔄 Control de Datos")
st.sidebar.write("La base de datos se actualiza automáticamente, pero puedes forzar una recarga aquí:")
btn_refresh = st.sidebar.button("Actualizar Marcadores Ahora")

if btn_refresh:
    st.cache_data.clear()  # Limpia la caché para obligar a traer datos frescos de la API

# =========================================================================
# LLAMADAS EN VIVO A LA API
# =========================================================================
@st.cache_data(ttl=15, show_spinner=False) # Guardamos en caché por 15 segundos para proteger tu cuota diaria
def obtener_partidos_en_vivo(key_api):
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        'x-apisports-key': key_api,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    return None

# =========================================================================
# FLUJO DE DATOS PRINCIPAL
# =========================================================================
live_fixtures = obtener_partidos_en_vivo(API_KEY)

# Pestañas de Navegación
tab1, tab2, tab3 = st.tabs(["🔴 En Vivo Ahora", "⭐ Mis Equipos", "📊 Análisis Estadístico (Pandas)"])

# Procesamos los datos con Pandas si hay partidos en vivo
records = []
if live_fixtures:
    for match in live_fixtures:
        records.append({
            "Liga": match['league']['name'],
            "País": match['league']['country'],
            "Local": match['teams']['home']['name'],
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })

df_live = pd.DataFrame(records) if records else pd.DataFrame()

# -------------------------------------------------------------------------
# PESTAÑA 1: PARTIDOS EN VIVO
# -------------------------------------------------------------------------
with tab1:
    st.header("⚽ Marcadores en Tiempo Real")
    
    if df_live.empty:
        st.info("ℹ️ No hay partidos jugándose en vivo en este momento en ninguna parte del mundo (o la API está refrescando sus credenciales).")
    else:
        st.success(f"¡Conexión Exitosa! Mostrando {len(df_live)} partidos en juego en este instante:")
        
        # Buscador interactivo con Pandas
        search_team = st.text_input("🔍 Filtrar marcadores en vivo por equipo o liga:", "")
        if search_team:
            df_live_filtered = df_live[
                df_live['Local'].str.contains(search_team, case=False) | 
                df_live['Visita'].str.contains(search_team, case=False) |
                df_live['Liga'].str.contains(search_team, case=False)
            ]
        else:
            df_live_filtered = df_live
            
        # Renderizado de los marcadores en vivo filtrados
        for index, row in df_live_filtered.iterrows():
            col_match, col_meta = st.columns([3, 1])
            with col_match:
                st.markdown(
                    f"### {row['Local']} **{row['Goles L']}** - **{row['Goles V']}** {row['Visita']}"
                )
                st.caption(f"🏆 {row['Liga']} ({row['País']})")
            with col_meta:
                st.metric(label="Minuto", value=f"{row['Minuto']}'", delta="En Directo", delta_color="inverse")
            st.markdown("---")

# -------------------------------------------------------------------------
# PESTAÑA 2: SEGUIMIENTO DE FAVORITOS
# -------------------------------------------------------------------------
with tab2:
    st.header("⭐ Seguimiento de tus Equipos")
    st.write("Registra tus clubes favoritos para aislar sus partidos de manera inteligente usando Pandas:")
    
    if 'mis_favoritos' not in st.session_state:
        st.session_state.mis_favoritos = ["Real Madrid", "Barcelona", "Manchester City", "PSG", "Chelsea", "Arsenal"]
        
    nuevos_favs = st.multiselect(
        "Edita tu lista de equipos favoritos:",
        options=["Real Madrid", "Barcelona", "Manchester City", "PSG", "Chelsea", "Arsenal", "Liverpool", "Juventus", "Bayern Munich", "Boca Juniors", "River Plate", "América", "Chivas"],
        default=st.session_state.mis_favoritos
    )
    st.session_state.mis_favoritos = nuevos_favs
    
    if not df_live.empty:
        # Filtramos los partidos en vivo usando la lista de favoritos de forma dinámica con Pandas (.isin)
        df_fav_matches = df_live[df_live['Local'].isin(nuevos_favs) | df_live['Visita'].isin(nuevos_favs)]
        
        if not df_fav_matches.empty:
            st.subheader("🚨 ¡Tus equipos están jugando ahora mismo!")
            st.dataframe(df_fav_matches, use_container_width=True)
        else:
            st.info("Ninguno de tus equipos favoritos está en la cancha jugando en vivo en este minuto.")
    else:
        st.info("No hay partidos en curso actualmente para contrastar con tus favoritos.")

# -------------------------------------------------------------------------
# PESTAÑA 3: ANALÍTICA CON PANDAS
# -------------------------------------------------------------------------
with tab3:
    st.header("📊 Analítica del Tablero (Mapeo Estadístico de Pandas)")
    
    if not df_live.empty:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            total_goles = df_live['Goles L'].sum() + df_live['Goles V'].sum()
            st.metric(label="Total de Goles Marcados en Vivo", value=int(total_goles))
        with col_m2:
            promedio_min = df_live['Minuto'].mean()
            st.metric(label="Minuto Promedio de los partidos", value=f"{promedio_min:.1f}'")
            
        st.markdown("---")
        
        # Gráfica interactiva con Pandas que cuenta cuántos partidos en vivo hay por liga
        st.markdown("**Ligas con más partidos disputándose ahora mismo:**")
        liga_activity = df_live['Liga'].value_counts()
        st.bar_chart(liga_activity, color="#ff4b4b")
    else:
        st.info("Cuando haya partidos jugándose en vivo, aquí verás gráficos de barras automáticos de goles y actividad por liga calculados con Pandas.")
