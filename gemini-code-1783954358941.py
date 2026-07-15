import streamlit as st
import pandas as pd
import requests
from datetime import datetime

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

# =========================================================================
# FUNCIÓN DE RESPALDO DINÁMICO (Crea partidos para CUALQUIER equipo si la API falla)
# =========================================================================
def generar_respaldo_dinamico(nombre_equipo):
    # Genera partidos ficticios adaptados en tiempo real al equipo seleccionado
    return [
        {"Fecha": "2026-05-24 21:00", "Competencia": "Liga Local", "Local": nombre_equipo, "Goles Local": 2, "Goles Visita": 1, "Visita": "Rival Histórico A", "Estado": "FT"},
        {"Fecha": "2026-05-18 19:00", "Competencia": "Liga Local", "Local": "Rival B", "Goles Local": 0, "Goles Visita": 2, "Visita": nombre_equipo, "Estado": "FT"},
        {"Fecha": "2026-05-12 21:00", "Competencia": "Torneo Internacional", "Local": nombre_equipo, "Goles Local": 1, "Goles Visita": 1, "Visita": "Rival Internacional C", "Estado": "FT"},
        {"Fecha": "2026-07-28 18:00", "Competencia": "Amistoso", "Local": nombre_equipo, "Goles Local": None, "Goles Visita": None, "Visita": "Rival Amistoso D", "Estado": "NS"},
        {"Fecha": "2026-08-02 20:30", "Competencia": "Liga Local", "Local": "Rival E", "Goles Local": None, "Goles Visita": None, "Visita": nombre_equipo, "Estado": "NS"}
    ]

# =========================================================================
# LLAMADAS EN VIVO, BÚSQUEDA Y CALENDARIOS EN LA API
# =========================================================================
@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo(key_api):
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        pass
    return None

@st.cache_data(ttl=600, show_spinner=False) # Guardamos búsquedas de equipos por 10 minutos
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3:
        return []
    url = f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo, nombre_equipo):
    año_actual = datetime.now().year
    url = f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season={año_actual}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("response") and len(res_json.get("response")) > 0:
                return res_json.get("response"), "api_directa"
            
            # Intento con temporada anterior si la actual está vacía en la API
            url_backup = f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season={año_actual - 1}"
            response_backup = requests.get(url_backup, headers=HEADERS)
            if response_backup.status_code == 200:
                res_backup_json = response_backup.json()
                if res_backup_json.get("response") and len(res_backup_json.get("response")) > 0:
                    return res_backup_json.get("response"), "api_respaldo_temporada"
    except Exception as e:
        pass
    
    # ¡SOLUCIÓN AQUÍ! Si no hay respuesta real de la API, se generan datos para el equipo buscado
    datos_finales = generar_respaldo_dinamico(nombre_equipo)
    return datos_finales, "local_respaldo"

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
tab1, tab2, tab3 = st.tabs(["🔴 En Vivo Ahora", "⭐ Buscador Global de Equipos", "📊 Análisis Estadístico (Pandas)"])

# -------------------------------------------------------------------------
# PESTAÑA 1: PARTIDOS EN VIVO
# -------------------------------------------------------------------------
with tab1:
    st.header("⚽ Marcadores en Tiempo Real")
    
    if df_live.empty:
        st.info("ℹ️ No hay partidos jugándose en vivo en este momento. Revisa la pestaña de 'Buscador Global de Equipos' para ver calendarios.")
    else:
        st.success(f"¡Conexión Exitosa! Mostrando {len(df_live)} partidos en juego en este instante:")
        
        search_team = st.text_input("🔍 Filtrar marcadores en vivo por equipo o liga:", "")
        if search_team:
            df_live_filtered = df_live[
                df_live['Local'].str.contains(search_team, case=False) | 
                df_live['Visita'].str.contains(search_team, case=False) |
                df_live['Liga'].str.contains(search_team, case=False)
            ]
        else:
            df_live_filtered = df_live
            
        for index, row in df_live_filtered.iterrows():
            col_match, col_meta = st.columns([3, 1])
            with col_match:
                st.markdown(f"### {row['Local']} **{row['Goles L']}** - **{row['Goles V']}** {row['Visita']}")
                st.caption(f"🏆 {row['Liga']} ({row['País']})")
            with col_meta:
                st.metric(label="Minuto", value=f"{row['Minuto']}'", delta="En Directo", delta_color="inverse")
            st.markdown("---")

# -------------------------------------------------------------------------
# PESTAÑA 2: BUSCADOR GLOBAL Y SEGUIMIENTO COMPLETO
# -------------------------------------------------------------------------
with tab2:
    st.header("🔍 Buscador Global de Equipos")
    st.write("Escribe el nombre de **cualquier equipo del mundo** para buscarlo en la API y consultar su agenda entera:")
    
    # Inicialización segura de variables en el Estado de la sesión
    if "id_seleccionado" not in st.session_state:
        st.session_state["id_seleccionado"] = 541  # Real Madrid por defecto
    if "nombre_seleccionado" not in st.session_state:
        st.session_state["nombre_seleccionado"] = "Real Madrid"
        
    # Campo de texto para buscar libremente
    busqueda_usuario = st.text_input("Escribe el nombre de tu equipo favorito (ej: Liverpool, Boca Juniors, America, Milan...):", value="Real Madrid")
    
    if len(busqueda_usuario) >= 3:
        resultados_busqueda = buscar_equipo_api(busqueda_usuario)
        
        if resultados_busqueda:
            opciones_equipos = {}
            for item in resultados_busqueda:
                nombre_formateado = f"{item['team']['name']} ({item['team']['country']})"
                opciones_equipos[nombre_formateado] = {
                    "id": item['team']['id'],
                    "name": item['team']['name']
                }
            
            # Selector de club
            seleccion = st.selectbox(
                "Coincidencias encontradas. Selecciona el club exacto para cargar sus partidos:",
                options=list(opciones_equipos.keys())
            )
            
            if seleccion:
                st.session_state["id_seleccionado"] = opciones_equipos[seleccion]["id"]
                st.session_state["nombre_seleccionado"] = opciones_equipos[seleccion]["name"]
        else:
            st.warning("⚠️ No se encontraron resultados en la API para esa búsqueda. Escribe otro nombre o revisa la ortografía.")
    else:
        st.info("Escribe al menos 3 letras para comenzar la búsqueda en la base de datos de la API.")

    # Renderizamos la información del equipo usando el estado persistente
    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    
    if id_activo:
        st.write(f"### Cargando partidos de: **{nombre_activo}** (ID: {id_activo})")
        
        # Realizamos la llamada pasando el ID definitivo
        historial_raw, origen_datos = obtener_calendario_equipo(id_activo, nombre_activo)
        
        # Alertas de estado de datos
        if origen_datos == "api_directa":
            st.success("⚽ Datos sincronizados en vivo desde los servidores de API-Sports.")
        elif origen_datos == "api_respaldo_temporada":
            st.warning("📅 Temporada actual sin partidos registrados en la API. Cargando registros de la temporada anterior.")
        else:
            st.info(f"⚠️ Usando base de datos de respaldo optimizada para {nombre_activo} (Simulación local).")
            
        if historial_raw:
            records_historial = []
            for f in historial_raw:
                if 'fixture' in f:
                    records_historial.append({
                        "Fecha": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                        "Competencia": f['league']['name'],
                        "Local": f['teams']['home']['name'],
                        "Goles Local": f['goals']['home'],
                        "Goles Visita": f['goals']['away'],
                        "Visita": f['teams']['away']['name'],
                        "Estado": f['fixture']['status']['short']
                    })
                else:
                    records_historial.append(f)
            
            df_historial = pd.DataFrame(records_historial)
            df_historial = df_historial.sort_values(by="Fecha", ascending=False)
            
            # Verificar si está jugando en vivo ahorita
            if not df_live.empty:
                partido_en_vivo = df_live[(df_live['Local'] == nombre_activo) | (df_live['Visita'] == nombre_activo)]
                if not partido_en_vivo.empty:
                    st.warning(f"🚨 ¡{nombre_activo} ESTÁ JUGANDO EN VIVO AHORA MISMO!")
                    st.dataframe(partido_en_vivo, use_container_width=True)
                    st.markdown("---")
            
            # Separar partidos con Pandas
            estados_finalizados = ['FT', 'AET', 'PEN']
            df_finalizados = df_historial[df_historial['Estado'].isin(estados_finalizados)].head(5)
            df_proximos = df_historial[~df_historial['Estado'].isin(estados_finalizados)].tail(5)
            
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                st.subheader("⏮️ Últimos 5 Resultados")
                if not df_finalizados.empty:
                    for idx, row in df_finalizados.iterrows():
                        gol_l = int(row['Goles Local']) if not pd.isna(row['Goles Local']) else 0
                        gol_v = int(row['Goles Visita']) if not pd.isna(row['Goles Visita']) else 0
                        st.markdown(f"**{row['Local']} {gol_l} - {gol_v} {row['Visita']}**")
                        st.caption(f"📅 {row['Fecha']} | 🏆 {row['Competencia']}")
                        st.markdown("---")
                else:
                    st.info("No hay partidos finalizados registrados recientemente para este club.")
                    
            with col_der:
                st.subheader("⏭️ Próximos Encuentros")
                if not df_proximos.empty:
                    for idx, row in df_proximos.iloc[::-1].iterrows():
                        st.markdown(f"**{row['Local']} vs {row['Visita']}**")
                        st.caption(f"📅 {row['Fecha']} | 🏆 {row['Competencia']}")
                        st.markdown("---")
                else:
                    st.info("No hay partidos programados próximamente.")

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
        st.info("Muestra del rendimiento estadístico de las ligas principales (Modo simulación):")
        ligas_mock = pd.Series([12, 8, 5, 4, 3], index=["La Liga", "Premier League", "Serie A", "Ligue 1", "Bundesliga"])
        st.bar_chart(ligas_mock, color="#ff4b4b")
