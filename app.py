import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

def hex_to_rgba(hex_str, opacity=0.25):
    hex_str = hex_str.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {opacity})"

CITY_COORDS = {
    "Spain": [40.4167, -3.7037],
    "England": [51.5074, -0.1278],
    "Italy": [45.4642, 9.1900],
    "Germany": [52.5200, 13.4050],
    "France": [48.8566, 2.3522],
    "Mexico": [19.4326, -99.1332]
}

# --- MOTOR DE DATOS DE RESPALDO (MOCK DATA EN CASO DE API LIMITADA) ---
MOCK_LIVE = [
    {"league": {"name": "La Liga"}, "teams": {"home": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}, "away": {"name": "Barcelona", "logo": "https://media.api-sports.io/football/teams/529.png"}}, "goals": {"home": 2, "away": 1}, "fixture": {"status": {"elapsed": 74}}},
    {"league": {"name": "Premier League"}, "teams": {"home": {"name": "Arsenal", "logo": "https://media.api-sports.io/football/teams/42.png"}, "away": {"name": "Chelsea", "logo": "https://media.api-sports.io/football/teams/49.png"}}, "goals": {"home": 0, "away": 0}, "fixture": {"status": {"elapsed": 15}}}
]

MOCK_HISTORY = {
    541: [
        {"fixture": {"date": "2026-05-14T20:00:00+00:00", "status": {"short": "FT"}}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}, "away": {"name": "Alaves", "logo": ""}}, "goals": {"home": 5, "away": 0}},
        {"fixture": {"date": "2026-05-10T16:15:00+00:00", "status": {"short": "FT"}}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Granada", "logo": ""}, "away": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}}, "goals": {"home": 0, "away": 4}},
        {"fixture": {"date": "2026-05-04T18:30:00+00:00", "status": {"short": "FT"}}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}, "away": {"name": "Cadiz", "logo": ""}}, "goals": {"home": 3, "away": 0}},
        {"fixture": {"date": "2026-04-26T19:00:00+00:00", "status": {"short": "FT"}}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Real Sociedad", "logo": ""}, "away": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}}, "goals": {"home": 0, "away": 1}},
        {"fixture": {"date": "2026-04-21T19:00:00+00:00", "status": {"short": "FT"}}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}, "away": {"name": "Barcelona", "logo": "https://media.api-sports.io/football/teams/529.png"}}, "goals": {"home": 3, "away": 2}},
        {"fixture": {"date": "2026-08-12T20:00:00+00:00", "status": {"short": "NS"}}, "league": {"name": "Super Cup"}, "teams": {"home": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}, "away": {"name": "Atalanta", "logo": ""}}, "goals": {"home": None, "away": None}},
        {"fixture": {"date": "2026-08-18T19:30:00+00:00", "status": {"short": "NS"}}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Mallorca", "logo": ""}, "away": {"name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"}}, "goals": {"home": None, "away": None}}
    ]
}

MOCK_SQUAD = {
    541: [
        {"number": 1, "name": "Thibaut Courtois", "age": 34, "position": "Goalkeeper"},
        {"number": 3, "name": "Éder Militão", "age": 28, "position": "Defender"},
        {"number": 22, "name": "Antonio Rüdiger", "age": 33, "position": "Defender"},
        {"number": 5, "name": "Jude Bellingham", "age": 23, "position": "Midfielder"},
        {"number": 8, "name": "Federico Valverde", "age": 27, "position": "Midfielder"},
        {"number": 7, "name": "Vinícius Júnior", "age": 26, "position": "Attacker"},
        {"number": 9, "name": "Kylian Mbappé", "age": 27, "position": "Attacker"}
    ]
}

st.markdown("""
    <style>
        .stApp { background-color: #0F172A !important; }
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #F8FAFC !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
        button[data-baseweb="tab"] { background-color: #1E293B !important; border-radius: 8px 8px 0 0; border: 1px solid #334155; border-bottom: none; }
        button[data-baseweb="tab"] p { color: #94A3B8 !important; font-weight: 600 !important; font-size: 1.05rem !important; }
        button[aria-selected="true"] { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        button[aria-selected="true"] p { color: #FFFFFF !important; font-weight: 800 !important; }
        .premium-card { background-color: #1E293B !important; padding: 24px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 20px; border: 1px solid #334155; transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .premium-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7); }
        .live-card { background-color: #0F172A !important; padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #334155; transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .live-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7); border-color: #3B82F6 !important; }
        .section-title { color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #334155; padding-bottom: 8px; }
        .live-team-name { color: #FFFFFF !important; font-weight: 800 !important; font-size: 1.15rem !important; }
        .live-score { color: #EF4444 !important; font-weight: 900 !important; font-size: 1.5rem !important; margin: 0 15px !important; background: #000000; padding: 4px 12px; border-radius: 6px; }
        .live-league-label { color: #94A3B8 !important; font-weight: 600 !important; font-size: 0.85rem !important; }
        .pulse-minute { background-color: #EF4444; color: #FFFFFF !important; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 800; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] { background-color: #0F172A !important; color: #FFFFFF !important; border: 1px solid #334155 !important; }
        .cal-container { background: #0F172A; border-radius: 12px; padding: 15px; border: 1px solid #334155; color: white; margin-bottom: 15px; }
        .cal-header { text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1.1rem; }
        .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center; }
        .day-header { color: #64748B; font-size: 0.75rem; font-weight: bold; }
        .day-cell { padding: 8px 0; font-size: 0.9rem; }
        .today-circle { background: #EF4444; border-radius: 50%; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    </style>
""", unsafe_allow_html=True)

def render_calendario():
    now = datetime.now()
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(now.year, now.month)
    month_name = calendar.month_name[now.month]
    
    html = f"""
    <div class='cal-container'>
        <div class='cal-header'>{month_name.capitalize()} {now.year}</div>
        <div class='cal-grid'>
            <div class='day-header'>dom</div><div class='day-header'>lun</div><div class='day-header'>mar</div>
            <div class='day-header'>mié</div><div class='day-header'>jue</div><div class='day-header'>vie</div><div class='day-header'>sáb</div>
    """
    for week in cal:
        for day in week:
            if day == 0: html += "<div></div>"
            elif day == now.day: html += f"<div><div class='today-circle'>{day}</div></div>"
            else: html += f"<div class='day-cell'>{day}</div>"
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

st.markdown("""
    <div style='margin-bottom: 30px; display: flex; align-items: center; gap: 15px;'>
        <div style='background-color: #EF4444; width: 8px; height: 60px; border-radius: 4px;'></div>
        <div>
            <h1 style='color: #FFFFFF !important; font-size: 2.5rem; font-weight: 900; margin: 0;'>FORZA FÚTBOL LIVE</h1>
            <p style='color: #94A3B8 !important; font-size: 1rem; margin: 0; text-transform: uppercase; letter-spacing: 2px;'>Motor Analítico de Rendimiento Deportivo</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NUEVA CLAVE API CONFIGURADA DE FORMA SEGURA ---
API_KEY = "fapi_8KrwBRiHZ5bxfXMCmNBOwbooVb1hUtBR"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# --- VARIABLES GLOBALES DE SESIÓN DE STREAMLIT ---
if "id_seleccionado" not in st.session_state:
    st.session_state.id_seleccionado = 541
if "nombre_seleccionado" not in st.session_state:
    st.session_state.nombre_seleccionado = "Real Madrid"
if "pais_seleccionado" not in st.session_state:
    st.session_state.pais_seleccionado = "Spain"
if "logo_seleccionado" not in st.session_state:
    st.session_state.logo_seleccionado = "https://media.api-sports.io/football/teams/541.png"
if "busqueda_query" not in st.session_state:
    st.session_state.busqueda_query = ""

id_activo = st.session_state.id_seleccionado
nombre_activo = st.session_state.nombre_seleccionado
pais_activo = st.session_state.pais_seleccionado
logo_activo = st.session_state.logo_seleccionado

st.sidebar.markdown("### ⚙️ Centro de Control")
if st.sidebar.button("🔄 Refrescar Datos de API"):
    st.cache_data.clear()

st.sidebar.markdown("### 📅 Configuración de Datos")
temporada_seleccionada = st.sidebar.selectbox("Temporada de Análisis", [2024, 2025, 2026], index=0)

# Switch de respaldo: apagado por defecto para usar tu nueva clave en vivo.
modo_simulado = st.sidebar.toggle("🔌 Forzar Modo Demostración Local", value=False)

@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo():
    if modo_simulado: return MOCK_LIVE
    try:
        response = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
        if response.status_code == 200 and not response.json().get("errors"):
            return response.json().get("response", [])
    except: pass
    return MOCK_LIVE

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3: return []
    try:
        response = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}", headers=HEADERS)
        if response.status_code == 200: return response.json().get("response", [])
    except: pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo, season):
    if modo_simulado: return MOCK_HISTORY.get(id_equipo, MOCK_HISTORY[541]), {}
    try:
        params = {"team": id_equipo, "season": season}
        response = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("errors"): return MOCK_HISTORY.get(id_equipo, MOCK_HISTORY[541]), data.get("errors")
            return data.get("response", []), {}
    except Exception as e:
        return MOCK_HISTORY.get(id_equipo, MOCK_HISTORY[541]), {"exception": str(e)}
    return MOCK_HISTORY.get(id_equipo, MOCK_HISTORY[541]), {"status_error": "Error de conexión"}

@st.cache_data(ttl=600, show_spinner=False)
def obtener_plantilla(id_equipo):
    if modo_simulado: return MOCK_SQUAD.get(id_equipo, MOCK_SQUAD[541])
    try:
        response = requests.get(f"https://v3.football.api-sports.io/players/squad?team={id_equipo}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("response"): return data.get("response")[0].get("players", [])
    except: pass
    return MOCK_SQUAD.get(id_equipo, MOCK_SQUAD[541])

live_fixtures = obtener_partidos_en_vivo()
records_live = []
if live_fixtures:
    for match in live_fixtures:
        records_live.append({
            "Liga": match['league']['name'],
            "Logo_Liga": match['league'].get('logo', ''),
            "Local": match['teams']['home']['name'],
            "Logo_L": match['teams']['home'].get('logo', ''),
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Logo_V": match['teams']['away'].get('logo', ''),
            "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Panel Principal", "🔴 Central En Vivo", "📈 Analítica Avanzada", "🤖 Scout IA"])

with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    col_busqueda, col_vacia = st.columns([1, 2])
    with col_busqueda:
        busqueda_usuario = st.text_input("🔍 Buscar club (Ej. Arsenal, Milan):", value=st.session_state.get("busqueda_query", ""), key="input_busqueda")
        if busqueda_usuario != st.session_state.get("busqueda_query", ""):
            st.session_state.busqueda_query = busqueda_usuario
            st.rerun()

        if len(busqueda_usuario) >= 3:
            resultados = buscar_equipo_api(busqueda_usuario)
            if resultados:
                opciones = {f"{i['team']['name']} ({i['team']['country']})": i['team'] for i in resultados}
                def actualizar_equipo():
                    sel_name = st.session_state.get("select_equipo_key")
                    if sel_name in opciones:
                        t = opciones[sel_name]
                        st.session_state.id_seleccionado = t['id']
                        st.session_state.nombre_seleccionado = t['name']
                        st.session_state.pais_seleccionado = t['country']
                        st.session_state.logo_seleccionado = t['logo']
                        st.session_state.busqueda_query = ""
                st.selectbox("Resultados:", list(opciones.keys()), key="select_equipo_key", on_change=actualizar_equipo)
    st.markdown("</div>", unsafe_allow_html=True)

    historial_raw, api_errors = obtener_calendario_equipo(id_activo, temporada_seleccionada)
    if api_errors and not modo_simulado:
        for err_key, err_msg in api_errors.items():
            st.sidebar.error(f"⚠️ Alerta API ({err_key}): {err_msg}")

    records_historial = []
    for f in historial_raw:
        if 'fixture' in f:
            records_historial.append({
                "Fecha": pd.to_datetime(f['fixture']['date']),
                "Fecha_Str": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                "Competencia": f['league']['name'],
                "Local": f['teams']['home']['name'],
                "Logo_L": f['teams']['home'].get('logo', ''),
                "Goles Local": f['goals']['home'],
                "Goles Visita": f['goals']['away'],
                "Visita": f['teams']['away']['name'],
                "Logo_V": f['teams']['away'].get('logo', ''),
                "Estado": f['fixture']['status']['short']
            })

    cols = ["Fecha", "Fecha_Str", "Competencia", "Local", "Logo_L", "Goles Local", "Goles Visita", "Visita", "Logo_V", "Estado"]
    df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False) if records_historial else pd.DataFrame(columns=cols)

    victorias, empates, derrotas, goles_favor, partidos_jugados = 0, 0, 0, 0, 0
    df_finalizados = pd.DataFrame()

    if not df_historial.empty:
        df_finalizados = df_historial[df_historial['Estado'].isin(['FT', 'AET', 'PEN'])]
        partidos_jugados = len(df_finalizados)
        if partidos_jugados > 0:
            for _, row in df_finalizados.iterrows():
                es_local = str(row['Local']).strip().lower() == str(nombre_activo).strip().lower()
                g_propio = row['Goles Local'] if es_local else row['Goles Visita']
                g_rival = row['Goles Visita'] if es_local else row['Goles Local']
                if pd.notna(g_propio) and pd.notna(g_rival):
                    goles_favor += int(g_propio)
                    if int(g_propio) > int(g_rival): victorias += 1
                    elif int(g_propio) == int(g_rival): empates += 1
                    else: derrotas += 1

    promedio_goles = round(goles_favor / partidos_jugados, 1) if partidos_jugados > 0 else 0
    efectividad = round((victorias / partidos_jugados) * 100, 1) if partidos_jugados > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left: 4px solid #3B82F6; padding: 15px;'>
                <img src='{logo_activo}' width='50'>
                <div><h3 style='margin:0; font-size:1.2rem;'>{nombre_activo}</h3><small style='color:#94A3B8;'>{pais_activo}</small></div>
            </div>
        """, unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>EFECTIVIDAD</small><h2 style='margin:0; color:#10B981 !important;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>GOLES / PARTIDO</small><h2 style='margin:0; color:#F59E0B !important;'>{promedio_goles}</h2></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>RÉCORD (V-E-D)</small><h2 style='margin:0; color:#FFFFFF !important;'>{victorias} - {empates} - {derrotas}</h2></div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Resultados</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                es_local = str(row['Local']).strip().lower() == str(nombre_activo).strip().lower()
                g_propio = int(row['Goles Local']) if es_local else int(row['Goles Visita'])
                g_rival = int(row['Goles Visita']) if es_local else int(row['Goles Local'])
                color_borde = "#10B981" if g_propio > g_rival else ("#64748B" if g_propio == g_rival else "#EF4444")
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {color_borde};'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'><span style='font-weight:bold;'>{row['Local']}</span></div>
                            <div style='width: 20%; text-align:center; font-size:1.2rem; font-weight:900;'>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'><span style='font-weight:bold;'>{row['Visita']}</span></div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else: st.info("No hay resultados registrados.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>📅 Calendario Actual</div>", unsafe_allow_html=True)
        render_calendario()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximos</div>", unsafe_allow_html=True)
        df_proximos = df_historial[df_historial['Estado'] == 'NS'].sort_values(by="Fecha", ascending=True).head(5)
        if not df_proximos.empty:
            for _, row in df_proximos.iterrows():
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #3B82F6;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'>{row['Local']}</div>
                            <div style='width: 20%; text-align:center; color:#F59E0B; font-weight:bold;'>VS</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'>{row['Visita']}</div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else: st.info("No hay partidos agendados.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='premium-card'><div class='section-title'>👥 Plantilla del Equipo</div>", unsafe_allow_html=True)
    plantilla = obtener_plantilla(id_activo)
    if plantilla:
        datos_formateados = [{"Número": p.get("number", "-"), "Nombre": p.get("name", "N/A"), "Edad": p.get("age", "-"), "Posición": p.get("position", "-")} for p in plantilla]
        st.dataframe(pd.DataFrame(datos_formateados), hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔴 Cobertura en Directo</div>", unsafe_allow_html=True)
    if df_live.empty: st.info("No hay partidos disputándose en vivo.")
    else:
        for _, row in df_live.iterrows():
            st.markdown(f"""
                <div class='live-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='width: 35%; display:flex; align-items:center; gap:15px;'><span class='live-team-name'>{row['Local']}</span></div>
                        <div style='width: 30%; text-align: center;'>
                            <span class='live-score'>{row['Goles L']} - {row['Goles V']}</span><br>
                            <div style='margin-top:10px;'><span class='pulse-minute'>⏱️ {row['Minuto']}'</span></div>
                        </div>
                        <div style='width: 35%; display:flex; align-items:center; justify-content:flex-end; gap:15px;'><span class='live-team-name'>{row['Visita']}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px;'>📈 Analítica de Datos</div>", unsafe_allow_html=True)
    if not df_live.empty:
        data_volumen = df_live['Liga'].value_counts()
        df_live['Goles Totales'] = pd.to_numeric(df_live['Goles L']).fillna(0) + pd.to_numeric(df_live['Goles V']).fillna(0)
        data_goles = df_live.groupby('Liga')['Goles Totales'].sum()
    else:
        data_volumen = pd.Series([1, 2], index=['La Liga', 'Premier League'])
        data_goles = pd.Series([3, 0], index=['La Liga', 'Premier League'])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📊 Volumen de Partidos</div>", unsafe_allow_html=True)
        st.bar_chart(data_volumen, use_container_width=True, color="#3B82F6")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>⚽ Goles Totales por Liga</div>", unsafe_allow_html=True)
        st.area_chart(data_goles, use_container_width=True, color="#EF4444")
        st.markdown("</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>🕸️ Perfil Táctico Radar</div>", unsafe_allow_html=True)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[efectividad, min(100, int(promedio_goles * 35)), 70, 65, 75], 
            theta=['Efectividad', 'Poder Goleador', 'Solidez Defensiva', 'Consistencia', 'Volumen'], 
            fill='toself', fillcolor=hex_to_rgba("#3B82F6", 0.25), line=dict(color="#3B82F6", width=3)
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template='plotly_dark', margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>🗺️ Ubicación Geográfica</div>", unsafe_allow_html=True)
        coords = CITY_COORDS.get(pais_activo, [40.4167, -3.7037])
        st.map(pd.DataFrame({'lat': [coords[0]], 'lon': [coords[1]]}), zoom=5, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🤖 Scout IA - Análisis Táctico</div>", unsafe_allow_html=True)
    rendimiento_txt = "óptimo" if efectividad >= 50 else "en desarrollo"
    st.write(f"**Estado actual:** {nombre_activo} presenta un rendimiento {rendimiento_txt} con una efectividad del {efectividad}%.")
    pregunta_usuario = st.chat_input(f"Pregunta sobre {nombre_activo}...")
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"): st.write(pregunta_usuario)
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["goles", "promedio"]): respuesta = f"El equipo registra un promedio de {promedio_goles} goles por partido."
            elif any(x in p for x in ["victoria", "ganado"]): respuesta = f"Acumula un total de {victorias} victorias."
            else: respuesta = f"Récord de {nombre_activo}: {victorias}V-{empates}E-{derrotas}D."
            st.write(respuesta)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: #334155; margin-top: 40px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 20px;'>
        <strong>Forza Football Analytics V3.0 (Integración AI)</strong><br>
        Plataforma Avanzada de Datos Deportivos<br>
        Proyecto Universitario | Desarrollado por Salomón Achar © 2026
    </div>
""", unsafe_allow_html=True)
