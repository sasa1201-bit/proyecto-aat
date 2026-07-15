import streamlit as st
import pandas as pd
import requests

# Configuración de la página estilo Deportivo Premium
st.set_page_config(page_title="Forza Fútbol Live & Tracker", page_icon="⚽", layout="wide")

st.title("⚽ Forza Fútbol: Marcadores & Seguimiento Personalizado")
st.caption("Consumiendo datos de API-Football con procesamiento y analítica avanzada en Pandas")

# =========================================================================
# CONFIGURACIÓN DE LA API (Tu API Key ya integrada de forma fija)
# =========================================================================
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {
    'x-apisports-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Botón para forzar actualización de los datos en la barra lateral
st.sidebar.header("🔄 Control de Datos")
btn_refresh = st.sidebar.button("Actualizar Todo Ahora")

if btn_refresh:
    st.cache_data.clear()  # Limpia la caché para obligar a traer datos frescos de la API

# Mapas de IDs internos de la API para traer datos de los equipos favoritos de forma exacta
MAPA_EQUIPOS_IDS = {
    "Real Madrid": 541,
    "Barcelona": 529,
    "Manchester City": 50,
    "PSG": 85,
    "Chelsea": 49,
    "Arsenal": 42,
    "Liverpool": 40,
    "Juventus": 496,
    "Bayern Munich": 157,
    "Boca Juniors": 451,
    "River Plate": 435,
    "América": 2281,
    "Chivas": 2288
}

# =========================================================================
# LLAMADAS EN VIVO E HISTÓRICAS A LA API
# =========================================================================
@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo(key_api):
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        st.error(f"Error de conexión en vivo: {e}")
    return None

@st.cache_data(ttl=300, show_spinner=False) # Guardamos 5 minutos el calendario histórico para no agotar la API
def obtener_calendario_equipo(id_equipo):
    # Trae los 20 partidos más recientes y próximos del equipo seleccionado
    url = f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&last=20"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        st.error(f"Error de conexión al historial: {e}")
    return []

# =========================================================================
# FLUJO DE DATOS PRINCIPAL
# =========================================================================
live_fixtures = obtener_partidos_en_vivo(API_KEY)

# Convertir partidos en vivo a DataFrame de Pandas
records_live = []
if live_fixtures:
    for match in live_fixtures:
        records_live.append({
            "Liga": match['league']['name'],
            "País": match['league']['country'],
            "Local": match['teams']['home']['name'],
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

# Pestañas de Navegación
tab1, tab2, tab3 = st.tabs(["🔴 En Vivo Ahora", "⭐ Mis Equipos (Seguimiento Completo)", "📊 Análisis Estadístico (Pandas)"])

# -------------------------------------------------------------------------
# PESTAÑA 1: PARTIDOS EN VIVO
# -------------------------------------------------------------------------
with tab1:
    st.header("⚽ Marcadores en Tiempo Real")
    
    if df_live.empty:
        st.info("ℹ️ No hay partidos jugándose en vivo en este momento. Revisa la pestaña de 'Mis Equipos' para ver calendarios e historial.")
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
            
        # Renderizado de los marcadores en vivo
        for index, row in df_live_filtered.iterrows():
            col_match, col_meta = st.columns([3, 1])
            with col_match:
                st.markdown(f"### {row['Local']} **{row['Goles L']}** - **{row['Goles V']}** {row['Visita']}")
                st.caption(f"🏆 {row['Liga']} ({row['País']})")
            with col_meta:
                st.metric(label="Minuto", value=f"{row['Minuto']}'", delta="En Directo", delta_color="inverse")
            st.markdown("---")

# -------------------------------------------------------------------------
# PESTAÑA 2: SEGUIMIENTO COMPLETO DE FAVORITOS (Historial y Próximos)
# -------------------------------------------------------------------------
with tab2:
    st.header("⭐ Zona de Seguimiento Avanzado")
    st.write("Selecciona un equipo de tus favoritos para auditar todos sus partidos recientes y próximos compromisos:")
    
    # Selector único para enfocar el análisis en un equipo
    equipo_favorito = st.selectbox(
        "Selecciona el equipo a inspeccionar de manera profunda:",
        options=list(MAPA_EQUIPOS_IDS.keys())
    )
    
    id_fav = MAPA_EQUIPOS_IDS[equipo_favorito]
    historial_raw = obtener_calendario_equipo(id_fav)
    
    if historial_raw:
        # Convertimos el historial a un DataFrame estructurado usando Pandas
        records_historial = []
        for f in historial_raw:
            records_historial.append({
                "Fecha": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                "Competencia": f['league']['name'],
                "Local": f['teams']['home']['name'],
                "Goles Local": f['goals']['home'],
                "Goles Visita": f['goals']['away'],
                "Visita": f['teams']['away']['name'],
                "Estado": f['fixture']['status']['long']
            })
        
        df_historial = pd.DataFrame(records_historial)
        
        # 1. ¿Está jugando en vivo ahorita? (Buscar en df_live usando Pandas)
        if not df_live.empty:
            partido_en_vivo = df_live[(df_live['Local'] == equipo_favorito) | (df_live['Visita'] == equipo_favorito)]
            if not partido_en_vivo.empty:
                st.warning(f"🚨 ¡{equipo_favorito} ESTÁ JUGANDO EN VIVO AHORA MISMO!")
                st.dataframe(partido_en_vivo, use_container_width=True)
                st.markdown("---")
        
        # Separar partidos usando lógica condicional de Pandas
        df_finalizados = df_historial[df_historial['Estado'] == 'Match Finished'].head(5)
        df_proximos = df_historial[df_historial['Estado'] != 'Match Finished'].head(5)
        
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.subheader("⏮️ Últimos 5 Resultados")
            if not df_finalizados.empty:
                for idx, row in df_finalizados.iterrows():
                    # Definimos un formato visual amigable
                    st.markdown(f"**{row['Local']} {int(row['Goles Local'])} - {int(row['Goles Visita'])} {row['Visita']}**")
                    st.caption(f"📅 {row['Fecha']} | 🏆 {row['Competencia']}")
                    st.markdown("---")
            else:
                st.info("No hay registros recientes finalizados.")
                
        with col_der:
            st.subheader("⏭️ Próximos Encuentros")
            if not df_proximos.empty:
                for idx, row in df_proximos.iterrows():
                    st.markdown(f"**{row['Local']} vs {row['Visita']}**")
                    st.caption(f"📅 {row['Fecha']} | 🏆 {row['Competencia']} ({row['Estado']})")
                    st.markdown("---")
            else:
                st.info("No hay partidos programados en el calendario próximo.")
    else:
        st.warning("No se pudieron cargar datos para este equipo desde la API.")

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
        
        st.markdown("**Ligas con más partidos disputándose ahora mismo:**")
        liga_activity = df_live['Liga'].value_counts()
        st.bar_chart(liga_activity, color="#ff4b4b")
    else:
        st.info("Cuando haya partidos jugándose en vivo, aquí verás estadísticas de actividad en tiempo real.")
