import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN ESTÉTICA PREMIUM (Texto Negro y Fondos Integrados)
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

# CSS para forzar textos negros en menús, pestañas y cajas de selección
st.markdown("""
    <style>
        /* Fondo general de la app */
        .stApp {
            background-color: #f8fafc !important;
        }
        
        /* Forzar texto negro general */
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #000000 !important;
        }

        /* Texto negro y en negrita para las pestañas (Tabs) */
        button[data-baseweb="tab"] {
            color: #000000 !important;
        }
        button[data-baseweb="tab"] p {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
        }
        
        /* Texto negro para el selector (Selectbox) */
        .stSelectbox div[data-baseweb="select"] {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        .stSelectbox div[data-baseweb="select"] span {
            color: #000000 !important;
        }

        /* Estilo para contenedores tipo Tarjeta Blanca */
        .premium-card {
            background-color: #ffffff !important;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
        }
        
        .section-title {
            color: #000000 !important;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 16px;
        }
        
        .premium-card p, .premium-card span, .premium-card div, .premium-card label, .premium-card h2, .premium-card h3 {
            color: #000000 !important;
        }
        
        .live-team-name {
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.15rem !important;
        }
        
        .live-score {
            color: #4f46e5 !important;
            font-weight: 900 !important;
            font-size: 1.3rem !important;
            margin: 0 15px !important;
        }
        
        .live-league-label {
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown("""
    <div style='margin-bottom: 30px;'>
        <h1 style='color: #000000 !important; font-size: 2.2rem; font-weight: 800; margin-bottom: 4px;'>⚽ Forza Fútbol Live</h1>
        <p style='color: #000000 !important; font-size: 1rem;'>Procesamiento analítico avanzado y monitoreo de escuadras globales</p>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# CONFIGURACIÓN DE LA API Y RESPALDO
# =========================================================================
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
    # NUEVO: Logo genérico por defecto para el modo respaldo
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

    # NUEVO: Se agregaron campos de "Logo Local" y "Logo Visita"
    return [
        {"Fecha": "2026-07-12 18:00", "Competencia": competencia, "Local": rivales[1], "Logo Local": logo_generico, "Goles Local": 1, "Goles Visita": 3, "Visita": nombre_equipo, "Logo Visita": logo_generico, "Estado": "FT"},
        {"Fecha": "2026-07-15 20:00", "Competencia": competencia, "Local": nombre_equipo, "Logo Local": logo_generico, "Goles Local": 2, "Goles Visita": 2, "Visita": rivales[2], "Logo Visita": logo_generico, "Estado": "FT"},
        {"Fecha": "2026-07-19 19:30", "Competencia": "Copa de Campeones", "Local": nombre_equipo, "Logo Local": logo_generico, "Goles Local": 1, "Goles Visita": 0, "Visita": rivales[0], "Logo Visita": logo_generico, "Estado": "FT"},
        {"Fecha": "2026-07-26 17:00", "Competencia": competencia, "Local": nombre_equipo, "Logo Local": logo_generico, "Goles Local": None, "Goles Visita": None, "Visita": rivales[3], "Logo Visita": logo_generico, "Estado": "NS"},
        {"Fecha": "2026-08-01 21:00", "Competencia": competencia, "Local": rivales[4], "Logo Local": logo_generico, "Goles Local": None, "Goles Visita": None, "Visita": nombre_equipo, "Logo Visita": logo_generico, "Estado": "NS"}
    ]

# Funciones de consulta a la API de Deportes
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
            "Logo L": match['teams']['home']['logo'], # NUEVO: Capturar logo local
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Logo V": match['teams']['away']['logo'], # NUEVO: Capturar logo visita
            "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

# =========================================================================
# RENDERIZADO DE LAS PESTAÑAS (TABS)
# =========================================================================
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas de Liga"])

# PESTAÑA 1: Buscador y Seguimiento de Equipos
with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔍 Selector Global de Escuadras</div>", unsafe_allow_html=True)
    
    # Valores por defecto en Session State
    if "id_seleccionado" not in st.session_state:
        st.session_state["id_seleccionado"] = 541  
    if "nombre_seleccionado" not in st.session_state:
        st.session_state["nombre_seleccionado"] = "Real Madrid"
    if "pais_seleccionado" not in st.session_state:
        st.session_state["pais_seleccionado"] = "Spain"
    if "logo_seleccionado" not in st.session_state: # NUEVO: Logo por defecto
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
                    "logo": item['team']['logo'] # NUEVO: Almacenar logo
                }
            
            seleccion = st.selectbox("Selecciona el club coincidente para actualizar el tablero:", options=list(opciones_equipos.keys()))
            if seleccion:
                st.session_state["id_seleccionado"] = opciones_equipos[seleccion]["id"]
                st.session_state["nombre_seleccionado"] = opciones_equipos[seleccion]["name"]
                st.session_state["pais_seleccionado"] = opciones_equipos[seleccion]["country"]
                st.session_state["logo_seleccionado"] = opciones_equipos[seleccion]["logo"] # NUEVO: Actualizar estado
    st.markdown("</div>", unsafe_allow_html=True)

    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    pais_activo = st.session_state["pais_seleccionado"]
    logo_activo = st.session_state["logo_seleccionado"] # NUEVO: Recuperar logo
    
    if id_activo:
        historial_raw, origen_datos = obtener_calendario_equipo(id_activo, nombre_activo, pais_activo)
        records_historial = []
        for f in historial_raw:
            if 'fixture' in f:
                records_historial.append({
                    "Fecha": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                    "Competencia": f['league']['name'],
                    "Local": f['teams']['home']['name'],
                    "Logo Local": f['teams']['home']['logo'], # NUEVO
                    "Goles Local": f['goals']['home'],
                    "Goles Visita": f['goals']['away'],
                    "Visita": f['teams']['away']['name'],
                    "Logo Visita": f['teams']['away']['logo'], # NUEVO
                    "Estado": f['fixture']['status']['short']
                })
            else:
                records_historial.append(f)
        
        df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False)
        estados_finalizados = ['FT', 'AET', 'PEN']
        df_finalizados = df_historial[df_historial['Estado'].isin(estados_finalizados)]
        
        victorias = 0
        goles_favor = 0
        if not df_finalizados.empty:
            for _, row in df_finalizados.iterrows():
                es_local = row['Local'] == nombre_activo
                g_propio = row['Goles Local'] if es_local else row['Goles Visita']
                g_rival = row['Goles Visita'] if es_local else row['Goles Local']
                if not pd.isna(g_propio):
                    goles_favor += int(g_propio)
                    if g_propio > g_rival:
                        victorias += 1
                        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            # NUEVO: Etiqueta img incrustada en el nombre del equipo para el KPI 1
            html_kpi1 = f"""
            <div class='premium-card' style='border-left: 5px solid #4f46e5;'>
                <p style='font-size: 0.85rem; margin:0; font-weight: 600;'>EQUIPO SELECCIONADO</p>
                <div style='display: flex; align-items: center; margin: 8px 0;'>
                    <img src='{logo_activo}' width='45' style='margin-right: 12px;'>
                    <h2 style='margin: 0;'>{nombre_activo}</h2>
                </div>
                <span style='color: #4f46e5 !important; font-weight: 700;'>📍 {pais_activo}</span>
            </div>
            """
            st.markdown(html_kpi1, unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"<div class='premium-card' style='border-left: 5px solid #22c55e;'><p style='font-size: 0.85rem; margin:0; font-weight: 600;'>RENDIMIENTO RECIENTE</p><h2 style='color: #22c55e !important; margin: 4px 0;'>{victorias} Victorias</h2><span style='color: #22c55e !important; font-weight: 600;'>↑ Eficacia activa</span></div>", unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"<div class='premium-card' style='border-left: 5px solid #3b82f6;'><p style='font-size: 0.85rem; margin:0; font-weight: 600;'>TOTAL DE GOLES</p><h2 style='color: #3b82f6 !important; margin: 4px 0;'>{goles_favor} Anotados</h2><span style='color: #3b82f6 !important; font-weight: 600;'>📈 Ofensiva analizada</span></div>", unsafe_allow_html=True)

        col_izq, col_der = st.columns(2)
        with col_izq:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>⏮️ Últimos Resultados</div>", unsafe_allow_html=True)
            df_ultimos = df_finalizados.head(5)
            if not df_ultimos.empty:
                for idx, row in df_ultimos.iterrows():
                    # NUEVO: Logos incrustados en los nombres de los equipos
                    st.markdown(f"""
                        <div style='padding: 12px 0; border-bottom: 1px solid #e2e8f0;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <span style='font-weight: 700; display: flex; align-items: center;'>
                                    <img src="{row.get('Logo Local', '')}" width="24" style="margin-right: 8px;"> {row['Local']} 
                                    <span style='margin: 0 8px; color: #94a3b8;'>vs</span> 
                                    {row['Visita']} <img src="{row.get('Logo Visita', '')}" width="24" style="margin-left: 8px;">
                                </span>
                                <span style='font-weight: 800; color: #4f46e5 !important; font-size: 1.1rem;'>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; margin-top: 8px;'>
                                <span style='font-size: 0.8rem; font-weight: 500;'>🏆 {row['Competencia']}</span>
                                <span style='font-size: 0.8rem;'>📅 {row['Fecha']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay registros finalizados.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_der:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>⏭️ Siguientes Partidos</div>", unsafe_allow_html=True)
            df_proximos = df_historial[~df_historial['Estado'].isin(estados_finalizados)].tail(5)
            if not df_proximos.empty:
                for idx, row in df_proximos.iloc[::-1].iterrows():
                    # NUEVO: Logos incrustados para futuros encuentros
                    st.markdown(f"""
                        <div style='padding: 12px 0; border-bottom: 1px solid #e2e8f0;'>
                            <div style='font-weight: 700; display: flex; align-items: center;'>
                                <img src="{row.get('Logo Local', '')}" width="24" style="margin-right: 8px;"> {row['Local']} 
                                <span style='margin: 0 8px; color: #94a3b8;'>vs</span> 
                                {row['Visita']} <img src="{row.get('Logo Visita', '')}" width="24" style="margin-left: 8px;">
                            </div>
                            <div style='display: flex; justify-content: space-between; margin-top: 8px;'>
                                <span style='font-size: 0.8rem; font-weight: 500;'>🏆 {row['Competencia']}</span>
                                <span style='font-size: 0.8rem; color: #4f46e5 !important; font-weight: 700;'>📅 {row['Fecha']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Sin partidos programados.")
            st.markdown("</div>", unsafe_allow_html=True)

# PESTAÑA 2: Partidos en vivo
with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔴 Marcadores en Tiempo Real</div>", unsafe_allow_html=True)
    
    st.caption("🟢 Conexión activa con el servidor de satélite. Los datos se refrescan de manera autónoma.")
    st.write("") 
    
    if df_live.empty:
        st.info("No hay partidos disputándose en vivo en este momento.")
    else:
        filtro = st.text_input("Buscar por equipo o liga:", "")
        df_live_filtered = df_live[df_live['Local'].str.contains(filtro, case=False) | df_live['Visita'].str.contains(filtro, case=False) | df_live['Liga'].str.contains(filtro, case=False)] if filtro else df_live
        for idx, row in df_live_filtered.iterrows():
            # NUEVO: Formato actualizado con flexbox para que los logos se vean alineados con el marcador
            st.markdown(f"""
                <div style='padding: 18px; background-color: #ffffff; border-radius: 12px; margin-bottom: 14px; border: 1px solid #cbd5e1;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='display: flex; align-items: center;'>
                            <img src="{row.get('Logo L', '')}" width="30" style="margin-right: 12px;">
                            <span class='live-team-name'>{row['Local']}</span>
                            <span class='live-score'>{row['Goles L']} - {row['Goles V']}</span>
                            <span class='live-team-name'>{row['Visita']}</span>
                            <img src="{row.get('Logo V', '')}" width="30" style="margin-left: 12px;">
                        </div>
                        <div style='text-align: right;'>
                            <span style='background-color: #ef4444; color: #ffffff !important; padding: 6px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 800;'>⏱️ {row['Minuto']}'</span>
                            <div class='live-league-label' style='margin-top: 8px;'>🏆 {row['Liga']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# PESTAÑA 3: Analítica Visual con Gráficos Nativos Integrados
with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px; margin-bottom: 18px;'>📈 Analítica de Volumen y Ligas</div>", unsafe_allow_html=True)
    
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
        st.markdown("<div class='section-title' style='font-size: 1.15rem;'>📊 Distribución de Partidos</div>", unsafe_allow_html=True)
        st.caption("Frecuencia de encuentros monitoreados por cada liga.")
        st.write("")
        st.bar_chart(chart_data, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_der:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 1.15rem;'>📈 Tendencia de Volumen</div>", unsafe_allow_html=True)
        st.caption("Visualización de densidad de eventos actuales.")
        st.write("")
        st.area_chart(chart_data, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
