import streamlit as st
import pandas as pd
import requests

# Configuración de la página estilo Deportivo Premium
st.set_page_config(page_title="Forza Fútbol Live", page_icon="⚽", layout="wide")

st.title("⚽ Forza Fútbol: Marcadores en Vivo")
st.caption("Consumiendo datos reales al instante con API-Football y análisis estadístico con Pandas")

# =========================================================================
# CONFIGURACIÓN DE LA API (Barra lateral)
# =========================================================================
st.sidebar.header("⚙️ Configuración de API")
api_key = st.sidebar.text_input(
    "Ingresa tu API Key de API-Football:", 
    type="password", 
    placeholder="Pega tu x-apisports-key aquí"
)

# Botón para forzar actualización de los datos
st.sidebar.markdown("---")
btn_refresh = st.sidebar.button("🔄 Actualizar Marcadores Ahora")

# =========================================================================
# LLAMADAS EN VIVO A LA API
# =========================================================================
@st.cache_data(ttl=15, show_spinner=False) # Guardamos en caché solo por 15 segundos para no quemar tus consultas
def obtener_partidos_en_vivo(key_api):
    if not key_api:
        return None
    
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
live_fixtures = obtener_partidos_en_vivo(api_key)

# Pestañas de Navegación
tab1, tab2, tab3 = st.tabs(["🔴 En Vivo Ahora", "⭐ Mis Equipos", "📊 Análisis Estadístico (Pandas)"])

# -------------------------------------------------------------------------
# PESTAÑA 1: PARTIDOS EN VIVO (Mundo Real)
# -------------------------------------------------------------------------
with tab1:
    st.header("⚽ Marcadores en Tiempo Real")
    
    if not api_key:
        st.warning("⚠️ Ingresa tu API Key en la barra lateral para ver los partidos que se están jugando EN VIVO en este instante.")
        st.markdown("""
        **¿Cómo conseguir una clave gratis?**
        1. Regístrate gratis en [api-football.com](https://www.api-football.com/)
        2. Copia tu clave de la sección API-Keys.
        3. Pégala a la izquierda para conectar tu app al satélite de datos en vivo.
        """)
    elif live_fixtures is None or len(live_fixtures) == 0:
        st.info("ℹ️ No hay partidos jugándose en vivo en este momento, o has alcanzado el límite de tu API Key.")
    else:
        st.success(f"¡Conectado! Mostrando {len(live_fixtures)} partidos jugándose en vivo ahora mismo:")
        
        # Procesamos los datos con Pandas para poder buscar/filtrar rápido
        records = []
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
        
        df_live = pd.DataFrame(records)
        
        # Buscador de partidos de Pandas
        search_team = st.text_input("🔍 Filtrar marcadores en vivo por equipo o liga:", "")
        if search_team:
            df_live = df_live[
                df_live['Local'].str.contains(search_team, case=False) | 
                df_live['Visita'].str.contains(search_team, case=False) |
                df_live['Liga'].str.contains(search_team, case=False)
            ]
            
        # Renderizado estético de marcadores
        for index, row in df_live.iterrows():
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
    st.write("Registra tus clubes favoritos para aislar sus datos de manera inteligente:")
    
    if 'mis_favoritos' not in st.session_state:
        st.session_state.mis_favoritos = ["Real Madrid", "Barcelona", "Manchester City", "PSG"]
        
    nuevos_favs = st.multiselect(
        "Edita tu lista de equipos favoritos:",
        options=["Real Madrid", "Barcelona", "Manchester City", "PSG", "Liverpool", "Juventus", "Bayern Munich", "Boca Juniors", "River Plate", "América", "Chivas"],
        default=st.session_state.mis_favoritos
    )
    st.session_state.mis_favoritos = nuevos_favs
    
    if api_key and live_fixtures:
        # Filtramos los partidos en vivo usando la lista de favoritos de forma dinámica con Pandas
        df_fav_matches = df_live[df_live['Local'].isin(nuevos_favs) | df_live['Visita'].isin(nuevos_favs)]
        
        if not df_fav_matches.empty:
            st.subheader("🚨 ¡Tus equipos están jugando ahora mismo!")
            st.dataframe(df_fav_matches, use_container_width=True)
        else:
            st.info("Ninguno de tus equipos favoritos está en la cancha ahora mismo.")
    else:
        st.info("Conecta tu API Key para rastrear a tus favoritos en directo.")

# -------------------------------------------------------------------------
# PESTAÑA 3: ANALÍTICA CON PANDAS (Para el maestro)
# -------------------------------------------------------------------------
with tab3:
    st.header("📊 Analítica del Tablero (Mapeo Estadístico de Pandas)")
    
    if api_key and live_fixtures and len(live_fixtures) > 0:
        # Convertimos toda la data en vivo en un DataFrame para análisis pesado
        df_stats = pd.DataFrame(records)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            total_goles = df_stats['Goles L'].sum() + df_stats['Goles V'].sum()
            st.metric(label="Total de Goles Marcados en Vivo", value=int(total_goles))
        with col_m2:
            promedio_min = df_stats['Minuto'].mean()
            st.metric(label="Minuto Promedio de los partidos", value=f"{promedio_min:.1f}'")
            
        st.markdown("---")
        
        # Gráfica interactiva de Pandas con las ligas más activas en vivo
        st.markdown("**Ligas con más partidos disputándose ahora mismo:**")
        liga_activity = df_stats['Liga'].value_counts()
        st.bar_chart(liga_activity, color="#ff4b4b")
    else:
        st.info("Esta sección analizará y generará gráficos de barras automáticos de goles y actividad de ligas en cuanto conectes tu API Key.")
