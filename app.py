import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Football Analytics Pro", page_icon="⚽", layout="wide")

# ==========================================
# CONFIGURACIÓN DE LA API
# ==========================================
API_KEY = "acb867b68f5987d9c226e48c12c090e3" # <-- ¡IMPORTANTE! Pon tu API Key aquí
HEADERS = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_KEY
}

# ==========================================
# ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #00FF7F; }
    .metric-label { font-size: 1rem; color: #AAAAAA; }
    .match-card {
        background-color: #262730;
        border-left: 5px solid #00FF7F;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .match-date { font-size: 0.8rem; color: #888888; margin-bottom: 5px; }
    .match-teams { font-size: 1.1rem; font-weight: bold; }
    .match-score { font-size: 1.2rem; color: #00FF7F; font-weight: bold; float: right; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES DE LA API (CON CACHE)
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def buscar_equipos(query):
    if len(query) < 3:
        return []
    try:
        res = requests.get(f"https://v3.football.api-sports.io/teams?search={query}", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            return res.json().get("response", [])
    except:
        pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_info_equipo(id_equipo):
    try:
        res = requests.get(f"https://v3.football.api-sports.io/teams?id={id_equipo}", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json().get("response")
            if data:
                return data[0]
    except:
        pass
    return None

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo):
    """
    Obtiene 100% datos reales: Los últimos 10 partidos jugados y los próximos 5 programados.
    """
    fixtures = []
    try:
        # 1. Últimos 10 partidos (Historial real)
        res_last = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&last=10", headers=HEADERS, timeout=5)
        if res_last.status_code == 200:
            data_last = res_last.json().get("response")
            if data_last:
                fixtures.extend(data_last)
                
        # 2. Próximos 5 partidos (Calendario real futuro)
        res_next = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&next=5", headers=HEADERS, timeout=5)
        if res_next.status_code == 200:
            data_next = res_next.json().get("response")
            if data_next:
                fixtures.extend(data_next)
                
        return fixtures
    except Exception as e:
        print(f"Error en API Calendario: {e}")
        return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_plantilla(id_equipo):
    try:
        res = requests.get(f"https://v3.football.api-sports.io/players/squad?team={id_equipo}", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json().get("response")
            if data:
                return data[0].get("players", [])
    except:
        pass
    return []

# ==========================================
# INTERFAZ DE USUARIO (BARRA LATERAL)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1865/1865806.png", width=80)
    st.title("Buscador de Equipos")
    
    if st.button("🔄 Refrescar Datos de API"):
        st.cache_data.clear()
        st.success("Caché limpiada. Se descargarán datos nuevos.")

    busqueda = st.text_input("🔍 Buscar equipo (ej. Arsenal, Madrid, America):", "")
    
    equipo_seleccionado = None
    if busqueda:
        with st.spinner('Buscando en la base de datos...'):
            resultados = buscar_equipos(busqueda)
            if resultados:
                opciones = {f"{r['team']['name']} ({r['team']['country']})": r['team']['id'] for r in resultados}
                seleccion = st.selectbox("Selecciona un equipo:", list(opciones.keys()))
                id_activo = opciones[seleccion]
                equipo_seleccionado = obtener_info_equipo(id_activo)
            else:
                st.warning("No se encontraron equipos reales con ese nombre.")

# ==========================================
# PANTALLA PRINCIPAL
# ==========================================
if equipo_seleccionado:
    team_info = equipo_seleccionado['team']
    venue_info = equipo_seleccionado['venue']
    
    # Encabezado del equipo
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        st.image(team_info['logo'], width=120)
    with col_titulo:
        st.title(team_info['name'])
        st.caption(f"📍 {team_info['country']} | 🏟️ Estadio: {venue_info['name']} ({venue_info['capacity']} espectadores)")

    # Pestañas de navegación
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "👥 Plantilla de Jugadores"])

    # ----------------------------------------------------
    # PESTAÑA 1: DASHBOARD (CALENDARIO Y PARTIDOS REALES)
    # ----------------------------------------------------
    with tab1:
        st.subheader("Rendimiento Reciente y Próximos Encuentros")
        
        # Llamada a la API SIN datos ficticios
        historial_raw = obtener_calendario_equipo(team_info['id'])
        
        if not historial_raw:
            st.error("⚠️ No se encontraron partidos registrados en la API para este equipo en este momento.")
        else:
            # Separar partidos terminados de los próximos (Status FT = Full Time, PEN, AET son terminados)
            terminados = [f for f in historial_raw if f['fixture']['status']['short'] in ['FT', 'AET', 'PEN']]
            proximos = [f for f in historial_raw if f['fixture']['status']['short'] not in ['FT', 'AET', 'PEN']]
            
            # Calcular métricas básicas con los últimos partidos reales
            victorias = empates = derrotas = goles_favor = 0
            for p in terminados:
                es_local = (p['teams']['home']['id'] == team_info['id'])
                goles_local = p['goals']['home'] if p['goals']['home'] is not None else 0
                goles_visitante = p['goals']['away'] if p['goals']['away'] is not None else 0
                
                if es_local:
                    goles_favor += goles_local
                    if goles_local > goles_visitante: victorias += 1
                    elif goles_local == goles_visitante: empates += 1
                    else: derrotas += 1
                else:
                    goles_favor += goles_visitante
                    if goles_visitante > goles_local: victorias += 1
                    elif goles_visitante == goles_local: empates += 1
                    else: derrotas += 1

            total_jugados = victorias + empates + derrotas
            
            # Mostrar Tarjetas de Métricas
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_jugados}</div><div class='metric-label'>Últimos Partidos</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{victorias}</div><div class='metric-label'>Victorias</div></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{empates}</div><div class='metric-label'>Empates</div></div>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{goles_favor}</div><div class='metric-label'>Goles a Favor</div></div>", unsafe_allow_html=True)

            # Mostrar Partidos en dos columnas
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                st.markdown("### 🔙 Últimos Resultados")
                if not terminados:
                    st.info("No hay resultados recientes registrados.")
                else:
                    for p in reversed(terminados[-5:]): # Mostrar solo los últimos 5 para no saturar
                        fecha = datetime.strptime(p['fixture']['date'][:10], '%Y-%m-%d').strftime('%d %b, %Y')
                        local = p['teams']['home']['name']
                        visitante = p['teams']['away']['name']
                        goles_L = p['goals']['home']
                        goles_V = p['goals']['away']
                        liga = p['league']['name']
                        
                        st.markdown(f"""
                        <div class='match-card'>
                            <div class='match-date'>{fecha} - {liga}</div>
                            <span class='match-teams'>{local} vs {visitante}</span>
                            <span class='match-score'>{goles_L} - {goles_V}</span>
                        </div>
                        """, unsafe_allow_html=True)

            with col_der:
                st.markdown("### 🔜 Próximos Encuentros")
                if not proximos:
                    st.info("No hay partidos próximos programados por el momento.")
                else:
                    for p in proximos[:5]:
                        fecha = datetime.strptime(p['fixture']['date'][:10], '%Y-%m-%d').strftime('%d %b, %Y')
                        hora = p['fixture']['date'][11:16]
                        local = p['teams']['home']['name']
                        visitante = p['teams']['away']['name']
                        liga = p['league']['name']
                        
                        st.markdown(f"""
                        <div class='match-card' style='border-left-color: #FFA500;'>
                            <div class='match-date'>{fecha} | {hora} Hrs - {liga}</div>
                            <span class='match-teams'>{local} vs {visitante}</span>
                            <span class='match-score'>⏳</span>
                        </div>
                        """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # PESTAÑA 2: PLANTILLA
    # ----------------------------------------------------
    with tab2:
        st.subheader("Plantilla Actual")
        jugadores = obtener_plantilla(team_info['id'])
        
        if jugadores:
            df_jugadores = pd.DataFrame(jugadores)
            if not df_jugadores.empty:
                # Limpiar y organizar los datos
                df_jugadores['Edad'] = df_jugadores['age']
                df_jugadores['Posición'] = df_jugadores['position']
                df_jugadores['Número'] = df_jugadores['number'].fillna("-")
                
                # Mostrar en formato de tabla limpia
                st.dataframe(
                    df_jugadores[['Número', 'name', 'Edad', 'Posición']],
                    column_config={
                        "name": "Nombre del Jugador",
                    },
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No se encontró información de la plantilla actual.")

else:
    # Pantalla de inicio cuando no hay equipo seleccionado
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>⚽ Bienvenido a Football Analytics Pro</h1>
            <p style='font-size: 1.2rem; color: #888;'>Utiliza el buscador de la izquierda para seleccionar un equipo y ver sus datos reales en tiempo real.</p>
        </div>
    """, unsafe_allow_html=True)
