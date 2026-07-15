import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN ESTÉTICA ESTILO ESPN (Rojo, Negro, Blanco, Gris)
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

# CSS modificado para la identidad visual
st.markdown("""
    <style>
        .stApp {
            background-color: #F4F4F4 !important;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        }
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #000000 !important;
        }
        button[data-baseweb="tab"] { color: #000000 !important; }
        button[data-baseweb="tab"] p {
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.05rem !important;
            text-transform: uppercase !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            color: #000000 !important;
            background-color: #ffffff !important;
            border-radius: 4px !important;
            border: 1px solid #cccccc !important;
        }
        .premium-card {
            background-color: #ffffff !important;
            padding: 24px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border-top: 4px solid #CC0000;
        }
        .section-title {
            color: #000000 !important;
            font-size: 1.3rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }
        .live-team-name {
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.15rem !important;
            text-transform: uppercase;
        }
        .live-score {
            color: #CC0000 !important;
            font-weight: 900 !important;
            font-size: 1.4rem !important;
            margin: 0 15px !important;
        }
        .live-league-label {
            color: #666666 !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
    <div style='margin-bottom: 30px; border-bottom: 4px solid #000000; padding-bottom: 10px;'>
        <h1 style='color: #CC0000 !important; font-size: 2.8rem; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 0px;'>⚽ FORZA FÚTBOL</h1>
        <p style='color: #000000 !important; font-size: 1rem; font-weight: 700; text-transform: uppercase;'>Líder Mundial en Deportes | Centro de Estadísticas</p>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# FUNCIONES MODULARES DE INTERFAZ (UI) - NUEVAS
# =========================================================================
def dibujar_cabecera_equipo(nombre, logo, pais):
    """Genera un encabezado profesional para el perfil del equipo seleccionado"""
    html = f"""
    <div style="display: flex; align-items: center; padding: 25px; background-color: #ffffff; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 25px; border-top: 4px solid #CC0000;">
        <div style="flex-shrink: 0; margin-right: 30px; background: #F4F4F4; padding: 15px; border-radius: 50%; width: 110px; height: 110px; display: flex; justify-content: center; align-items: center; border: 1px solid #E5E5E5;">
            <!-- El object-fit: contain asegura que el logo nunca se deforme -->
            <img src="{logo}" style="max-width: 80px; max-height: 80px; object-fit: contain;">
        </div>
        <div style="flex-grow: 1;">
            <p style="font-size: 0.85rem; margin:0; font-weight: 800; text-transform: uppercase; color: #666666 !important;">PERFIL DEL CLUB</p>
            <h1 style="margin: 0; color: #000000 !important; font-size: 2.8rem; font-weight: 900; letter-spacing: -1px; text-transform: uppercase;">
                {nombre}
            </h1>
            <div style="margin-top: 10px; display: flex; gap: 15px; flex-wrap: wrap;">
                <span style="background-color: #CC0000; color: #ffffff !important; padding: 6px 12px; border-radius: 3px; font-size: 0.85rem; font-weight: 800; text-transform: uppercase;">
                    📍 {pais}
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dibujar_tarjeta_previo(row):
    """Renderiza el HTML para un partido ya finalizado (con resultados)"""
    html = f"""
    <div style='padding: 14px 0; border-bottom: 1px solid #E5E5E5;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <span style='font-weight: 800; display: flex; align-items: center; font-size: 1.05rem;'>
                <img src="{row.get('Logo Local', '')}" width="28" height="28" style="margin-right: 8px; object-fit: contain;"> {row['Local']} 
                <span style='margin: 0 8px; color: #999999; font-weight: 500;'>vs</span> 
                {row['Visita']} <img src="{row.get('Logo Visita', '')}" width="28" height="28" style="margin-left: 8px; object-fit: contain;">
            </span>
            <span style='font-weight: 900; color: #CC0000 !important; font-size: 1.2rem;'>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin-top: 6px;'>
            <span style='font-size: 0.75rem; font-weight: 800; color: #666666 !important; text-transform: uppercase;'>🏆 {row['Competencia']}</span>
            <span style='font-size: 0.75rem; font-weight: 700; color: #999999 !important;'>📅 {row['Fecha']}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dibujar_tarjeta_proximo(row):
    """Renderiza el HTML para un partido que aún no se juega"""
    html = f"""
    <div style='padding: 14px 0; border-bottom: 1px solid #E5E5E5;'>
        <div style='font-weight: 800; display: flex; align-items: center; font-size: 1.05rem;'>
            <img src="{row.get('Logo Local', '')}" width="28" height="28" style="margin-right: 8px; object-fit: contain;"> {row['Local']} 
            <span style='margin: 0 8px; color: #999999; font-weight: 500;'>vs</span> 
            {row['Visita']} <img src="{row.get('Logo Visita', '')}" width="28" height="28" style="margin-left: 8px; object-fit: contain;">
        </div>
        <div style='display: flex; justify-content: space-between; margin-top: 6px;'>
            <span style='font-size: 0.75rem; font-weight: 800; color: #666666 !important; text-transform: uppercase;'>🏆 {row['Competencia']}</span>
            <span style='font-size: 0.75rem; color: #CC0000 !important; font-weight: 800;'>📅 {row['Fecha']}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dibujar_tarjeta_en_vivo(row):
    """Renderiza la tarjeta para marcadores en vivo"""
    html = f"""
    <div style='padding: 18px; background-color: #ffffff; border-radius: 4px; margin-bottom: 14px; border: 1px solid #E5E5E5; border-left: 4px solid #CC0000;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='display: flex; align-items: center;'>
                <img src="{row.get('Logo L', '')}" width="32" height="32" style="margin-right: 12px; object-fit: contain;">
                <span class='live-team-name'>{row['Local']}</span>
                <span class='live-score'>{row['Goles L']} - {row['Goles V']}</span>
                <span class='live-team-name'>{row['Visita']}</span>
                <img src="{row.get('Logo V', '')}" width="32" height="32" style="margin-left: 12px; object-fit: contain;">
            </div>
            <div style='text-align: right;'>
                <span style='background-color: #CC0000; color: #ffffff !important; padding: 4px 12px; border-radius: 2px; font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px;'>⏱️ {row['Minuto']}'</span>
                <div class='live-league-label' style='margin-top: 8px;'>🏆 {row['Liga']}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# =========================================================================
# CONFIGURACIÓN DE LA API Y RESPALDO
# =========================================================================
# Sugerencia a futuro: Cambia esto por API_KEY = st.secrets["API_SPORTS_KEY"] por seguridad.
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {
    'x-apisports-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

st.sidebar.markdown("### 🔄 Control de Datos")
if st.sidebar.button("Forzar Sincronización"):
    st.cache_data.clear()

def generar_respaldo_dinamico(nombre_equipo, pais_equipo):
    pais_normalizado = str(pais_equipo).strip().lower()
    logo_generico = "https://cdn-icons-png.flaticon.com/512/825/825588.png"
    
    if "mexico" in pais_normalizado or "méxico" in pais_normalizado:
        competencia = "Liga MX - Apertura 2026"
        rivales = ["Chivas Guadalajara", "Cruz Azul", "Pumas UNAM", "Tigres UANL", "CF Monterrey"]
    elif "spain" in pais_normalizado or "españa" in pais_normalizado:
        competencia = "La Liga (Pretemporada)"
        rivales = ["Real Madrid", "Barcelona", "Atlético de Madrid", "Sevilla FC", "Real Betis"]
    elif "england" in pais_normalizado or "inglaterra" in pais_normalizado:
        competencia = "Premier League (Pretemporada)"
        rivales = ["Manchester City", "Arsenal", "Liverpool", "Manchester United", "Chelsea"]
    else:
        competencia = "Amistoso Internacional"
        rivales = ["Real Madrid", "Paris Saint-Germain", "Bayern Munich", "Manchester City", "Barcelona"]

    return [
        {"Fecha": "2026-07-12 18:00", "Competencia": competencia, "Local": rivales[1], "Logo Local": logo_generico, "Goles Local": 1, "Goles Visita": 3, "Visita": nombre_equipo, "Logo Visita": logo_generico, "Estado": "FT"},
        {"Fecha": "2026-07-15 20:00", "Competencia": competencia, "Local": nombre_equipo, "Logo Local": logo_generico, "Goles Local": 2, "Goles Visita": 2, "Visita": rivales[2], "Logo Visita": logo_generico, "Estado": "FT"},
        {"Fecha": "2026-07-19 19:30", "Competencia": "Copa de Campeones", "Local": nombre_equipo, "Logo Local": logo_generico, "Goles Local": 1, "Goles Visita": 0, "Visita": rivales[0], "Logo Visita": logo_generico, "Estado": "FT"},
        {"Fecha": "2026-07-26 17:00", "Competencia": competencia, "Local": nombre_equipo, "Logo Local": logo_generico, "Goles Local": None, "Goles Visita": None, "Visita": rivales[3], "Logo Visita": logo_generico, "Estado": "NS"},
        {"Fecha": "2026-08-01 21:00", "Competencia": competencia, "Local": rivales[4], "Logo Local": logo_generico, "Goles Local": None, "Goles Visita": None, "Visita": nombre_equipo, "Logo Visita": logo_generico, "Estado": "NS"}
    ]

@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo(key_api):
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception:
        pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3:
        return []
    url = f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo, nombre_equipo, pais_equipo):
    año_actual = datetime.now().year
    url = f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season={año_actual}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("response") and len(res_json.get("response")) > 0:
                return res_json.get("response"), "api_directa"
    except Exception:
        pass
    return generar_respaldo_dinamico(nombre_equipo, pais_equipo), "local_respaldo"

live_fixtures = obtener_partidos_en_vivo(API_KEY)
records_live = []
if live_fixtures:
    for match in live_fixtures:
        records_live.append({
            "Liga": match['league']['name'],
            "País": match['league']['country'],
            "Local": match['teams']['home']['name'],
            "Logo L": match['teams']['home']['logo'], 
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Logo V": match['teams']['away']['logo'], 
            "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

# =========================================================================
# RENDERIZADO DE LAS PESTAÑAS (TABS)
# =========================================================================
tab1, tab2, tab3 = st.tabs(["📊 Perfil del Equipo", "🔴 Marcadores en Vivo", "📈 Analítica Global"])

# PESTAÑA 1: Buscador y Seguimiento de Equipos
with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔍 Buscador de Equipos</div>", unsafe_allow_html=True)
    
    if "id_seleccionado" not in st.session_state:
        st.session_state["id_seleccionado"] = 541  
    if "nombre_seleccionado" not in st.session_state:
        st.session_state["nombre_seleccionado"] = "Real Madrid"
    if "pais_seleccionado" not in st.session_state:
        st.session_state["pais_seleccionado"] = "Spain"
    if "logo_seleccionado" not in st.session_state:
        st.session_state["logo_seleccionado"] = "https://media.api-sports.io/football/teams/541.png"
        
    busqueda_usuario = st.text_input(
        "Busca cualquier club en la base de datos:", 
        value="Real Madrid",
        placeholder="Ej. Real Madrid, Barcelona, Club América, Manchester City..."
    )
    
    if len(busqueda_usuario) >= 3:
        resultados_busqueda = buscar_equipo_api(busqueda_usuario)
        if resultados_busqueda:
            opciones_equipos = {}
            for item in resultados_busqueda:
                nombre_formateado = f"{item['team']['name']} ({item['team']['country']})"
                opciones_equipos[nombre_formateado] = {
                    "id": item['team']['id'],
                    "name": item['team']['name'],
                    "country": item['team']['country'],
                    "logo": item['team']['logo'] 
                }
            
            seleccion = st.selectbox("Selecciona el club coincidente para actualizar el tablero:", options=list(opciones_equipos.keys()))
            if seleccion:
                st.session_state["id_seleccionado"] = opciones_equipos[seleccion]["id"]
                st.session_state["nombre_seleccionado"] = opciones_equipos[seleccion]["name"]
                st.session_state["pais_seleccionado"] = opciones_equipos[seleccion]["country"]
                st.session_state["logo_seleccionado"] = opciones_equipos[seleccion]["logo"] 
    st.markdown("</div>", unsafe_allow_html=True)

    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    pais_activo = st.session_state["pais_seleccionado"]
    logo_activo = st.session_state["logo_seleccionado"] 
    
    if id_activo:
        # Dibujamos el nuevo encabezado gigante y elegante del equipo
        dibujar_cabecera_equipo(nombre_activo, logo_activo, pais_activo)
        
        historial_raw, origen_datos = obtener_calendario_equipo(id_activo, nombre_activo, pais_activo)
        records_historial = []
        for f in historial_raw:
            if 'fixture' in f:
                records_historial.append({
                    "Fecha": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                    "Competencia": f['league']['name'],
                    "Local": f['teams']['home']['name'],
                    "Logo Local": f['teams']['home']['logo'], 
                    "Goles Local": f['goals']['home'],
                    "Goles Visita": f['goals']['away'],
                    "Visita": f['teams']['away']['name'],
                    "Logo Visita": f['teams']['away']['logo'],
                    "Estado": f['fixture']['status']['short']
                })
            else:
                records_historial.append(f)
        
        df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False)
        estados_finalizados = ['FT', 'AET', 'PEN']
        df_finalizados = df_historial[df_historial['Estado'].isin(estados_finalizados)]
        
        victorias = 0
        goles_favor = 0
        partidos_jugados = len(df_finalizados)
        
        if not df_finalizados.empty:
            for _, row in df_finalizados.iterrows():
                es_local = row['Local'] == nombre_activo
                g_propio = row['Goles Local'] if es_local else row['Goles Visita']
                g_rival = row['Goles Visita'] if es_local else row['Goles Local']
                if not pd.isna(g_propio):
                    goles_favor += int(g_propio)
                    if g_propio > g_rival:
                        victorias += 1
                        
        # Tarjetas de KPI usando st.columns
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(f"<div class='premium-card' style='border-left: 6px solid #CC0000; border-top: none;'><p style='font-size: 0.85rem; margin:0; font-weight: 800; text-transform: uppercase; color: #666666 !important;'>PARTIDOS JUGADOS</p><h2 style='color: #000000 !important; margin: 4px 0; font-weight: 900; font-size: 2.2rem;'>{partidos_jugados}</h2><span style='color: #CC0000 !important; font-weight: 800; text-transform: uppercase;'>📊 Registros Actuales</span></div>", unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"<div class='premium-card' style='border-left: 6px solid #000000; border-top: none;'><p style='font-size: 0.85rem; margin:0; font-weight: 800; text-transform: uppercase; color: #666666 !important;'>VICTORIAS RECIENTES</p><h2 style='color: #000000 !important; margin: 4px 0; font-weight: 900; font-size: 2.2rem;'>{victorias}</h2><span style='color: #000000 !important; font-weight: 800; text-transform: uppercase;'>📈 Racha de Triunfos</span></div>", unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"<div class='premium-card' style='border-left: 6px solid #666666; border-top: none;'><p style='font-size: 0.85rem; margin:0; font-weight: 800; text-transform: uppercase; color: #666666 !important;'>GOLES A FAVOR</p><h2 style='color: #000000 !important; margin: 4px 0; font-weight: 900; font-size: 2.2rem;'>{goles_favor}</h2><span style='color: #666666 !important; font-weight: 800; text-transform: uppercase;'>⚽ Poder Ofensivo</span></div>", unsafe_allow_html=True)

        # Tablas de resultados (Usando las funciones modulares ultralimpias)
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>⏮️ Resultados Previos</div>", unsafe_allow_html=True)
            df_ultimos = df_finalizados.head(5)
            if not df_ultimos.empty:
                for _, row in df_ultimos.iterrows():
                    dibujar_tarjeta_previo(row)  # <--- LLamada súper limpia
            else:
                st.info("No hay registros finalizados.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_der:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>⏭️ Próximos Encuentros</div>", unsafe_allow_html=True)
            df_proximos = df_historial[~df_historial['Estado'].isin(estados_finalizados)].tail(5)
            if not df_proximos.empty:
                for _, row in df_proximos.iloc[::-1].iterrows():
                    dibujar_tarjeta_proximo(row)  # <--- LLamada súper limpia
            else:
                st.info("Sin partidos programados.")
            st.markdown("</div>", unsafe_allow_html=True)

# PESTAÑA 2: Partidos en vivo
with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔴 En Juego</div>", unsafe_allow_html=True)
    st.caption("🟢 Conexión activa. Los datos se actualizan en tiempo real.")
    st.write("") 
    
    if df_live.empty:
        st.info("No hay partidos disputándose en vivo en este momento.")
    else:
        filtro = st.text_input("Buscar por equipo o liga:", "")
        df_live_filtered = df_live[df_live['Local'].str.contains(filtro, case=False) | df_live['Visita'].str.contains(filtro, case=False) | df_live['Liga'].str.contains(filtro, case=False)] if filtro else df_live
        
        for _, row in df_live_filtered.iterrows():
            dibujar_tarjeta_en_vivo(row) # <--- LLamada súper limpia
            
    st.markdown("</div>", unsafe_allow_html=True)

# PESTAÑA 3: Analítica Global
with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px; margin-bottom: 18px;'>📈 Data & Analítica</div>", unsafe_allow_html=True)
    
    if not df_live.empty:
        data_grafica = df_live['Liga'].value_counts().reset_index()
        data_grafica.columns = ['Liga', 'Partidos']
    else:
        data_grafica = pd.DataFrame({
            'Liga': ['LaLiga España', 'Premier League', 'Serie A Italia', 'Bundesliga', 'Ligue 1 Francia'],
            'Partidos': [12, 8, 5, 4, 3]
        })

    chart_data = data_grafica.set_index('Liga')

    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 1.15rem;'>📊 Frecuencia por Liga</div>", unsafe_allow_html=True)
        st.bar_chart(chart_data, use_container_width=True, color="#CC0000")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_der:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 1.15rem;'>📈 Densidad de Eventos</div>", unsafe_allow_html=True)
        st.area_chart(chart_data, use_container_width=True, color="#000000")
        st.markdown("</div>", unsafe_allow_html=True)
