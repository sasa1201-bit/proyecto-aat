import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

# Función auxiliar segura para convertir HEX a RGBA nativo de Plotly sin romper validaciones
def hex_to_rgba(hex_str, opacity=0.25):
    hex_str = hex_str.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {opacity})"

CITY_COORDS = {
    "Madrid": [40.4167, -3.7037],
    "London": [51.5074, -0.1278],
    "Manchester": [53.4808, -2.2426],
    "Milan": [45.4642, 9.1900],
    "Munich": [48.1351, 11.5820],
    "Paris": [48.8566, 2.3522],
    "Liverpool": [53.4084, -2.9916],
    "Turin": [45.0703, 7.6869],
    "Rome": [41.9028, 12.4964],
    "Buenos Aires": [-34.6037, -58.3816],
    "Rio de Janeiro": [-22.9068, -43.1729],
    "Mexico City": [19.4326, -99.1332]
}

TEAM_THEMES = {
    541: "#FEBE10",  
    42: "#EF0107",   
    33: "#DA291C",   
    50: "#034694",   
    40: "#6CABDD",   
    496: "#C4122E",  
    505: "#0066B2",  
    157: "#DC052D"   
}

if "id_seleccionado" not in st.session_state:
    st.session_state.update({
        "id_seleccionado": 541, 
        "nombre_seleccionado": "Real Madrid", 
        "pais_seleccionado": "Spain", 
        "logo_seleccionado": "https://media.api-sports.io/football/teams/541.png",
        "estadio_seleccionado": "Estadio Santiago Bernabéu",
        "ciudad_seleccionada": "Madrid"
    })

# CONTROLES SIDEBAR
st.sidebar.markdown("### ⚙️ Centro de Control")
modo_demo = st.sidebar.checkbox("🚨 Activar Modo Demostración (Sin API)", value=False, help="Actívalo si la API se queda sin créditos o no carga datos.")

if st.sidebar.button("🔄 Refrescar Caché"):
    st.cache_data.clear()

id_activo = st.session_state["id_seleccionado"]
accent_color = TEAM_THEMES.get(id_activo, "#3B82F6")

st.markdown(f"""
    <style>
        .stApp {{ background-color: #0F172A !important; }}
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{ color: #F8FAFC !important; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 10px; background-color: transparent; }}
        button[data-baseweb="tab"] {{ background-color: #1E293B !important; border-radius: 8px 8px 0 0; border: 1px solid #334155; border-bottom: none; }}
        button[data-baseweb="tab"] p {{ color: #94A3B8 !important; font-weight: 600 !important; font-size: 1.05rem !important; }}
        button[aria-selected="true"] {{ background-color: {accent_color} !important; border-color: {accent_color} !important; }}
        button[aria-selected="true"] p {{ color: #FFFFFF !important; font-weight: 800 !important; }}
        .premium-card {{ background-color: #1E293B !important; padding: 24px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 20px; border: 1px solid #334155; transition: transform 0.3s ease; }}
        .premium-card:hover {{ transform: translateY(-5px); }}
        .live-card {{ background-color: #0F172A !important; padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #334155; }}
        .section-title {{ color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px; text-transform: uppercase; border-bottom: 2px solid #334155; padding-bottom: 8px; }}
        .live-team-name {{ font-weight: 800 !important; font-size: 1.15rem !important; }}
        .live-score {{ color: #EF4444 !important; font-weight: 900 !important; font-size: 1.5rem !important; margin: 0 15px !important; background: #000000; padding: 4px 12px; border-radius: 6px; }}
        .pulse-minute {{ background-color: {accent_color}; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 800; }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{ background-color: #0F172A !important; color: #FFFFFF !important; border: 1px solid #334155 !important; }}
        .cal-container {{ background: #0F172A; border-radius: 12px; padding: 15px; border: 1px solid #334155; text-align: center; }}
        .cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; }}
        .today-circle {{ background: #EF4444; border-radius: 50%; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .match-day-circle {{ background: {accent_color}; border-radius: 50%; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
    </style>
""", unsafe_allow_html=True)

def render_calendario(dias_partido):
    now = datetime.now()
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(now.year, now.month)
    html = f"<div class='cal-container'><div style='font-weight:bold; margin-bottom:10px;'>{calendar.month_name[now.month].capitalize()} {now.year}</div><div class='cal-grid'>"
    for d in ['D','L','M','M','J','V','S']: html += f"<div style='color:#64748B; font-size:0.75rem;'>{d}</div>"
    for week in cal:
        for day in week:
            if day == 0: html += "<div></div>"
            elif day == now.day: html += f"<div><div class='today-circle'>{day}</div></div>"
            elif day in dias_partido: html += f"<div><div class='match-day-circle'>{day}</div></div>"
            else: html += f"<div style='padding:8px 0;'>{day}</div>"
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

st.markdown(f"""
    <div style='margin-bottom: 30px; display: flex; align-items: center; gap: 15px;'>
        <div style='background-color: {accent_color}; width: 8px; height: 60px; border-radius: 4px;'></div>
        <div>
            <h1 style='color: #FFFFFF !important; font-size: 2.5rem; font-weight: 900; margin: 0;'>FORZA FÚTBOL LIVE</h1>
            <p style='color: #94A3B8 !important; font-size: 1rem; margin: 0; text-transform: uppercase; letter-spacing: 2px;'>Motor Analítico de Rendimiento Deportivo</p>
        </div>
    </div>
""", unsafe_allow_html=True)

API_KEY = "2540a6ade056a06d82e67727b70a5f00"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# PROCESAMIENTO DE CONEXIÓN E INFRAESTRUCTURA DE RESPALDO
@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo():
    if modo_demo:
        return [{"league": {"name": "LaLiga", "logo": ""}, "teams": {"home": {"name": "Real Madrid", "logo": ""}, "away": {"name": "Atlético de Madrid", "logo": ""}}, "goals": {"home": 2, "away": 1}, "fixture": {"status": {"elapsed": 75}}}]
    try:
        response = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("errors"): st.sidebar.warning("⚠️ Límite de API alcanzado o error.")
            return res_json.get("response", [])
    except: pass
    return []

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if modo_demo:
        return [{"team": {"id": 541, "name": "Real Madrid", "country": "Spain", "logo": "https://media.api-sports.io/football/teams/541.png"}, "venue": {"name": "Santiago Bernabéu", "city": "Madrid"}}]
    if not nombre_busqueda or len(nombre_busqueda) < 3: return []
    try:
        response = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}", headers=HEADERS)
        if response.status_code == 200: return response.json().get("response", [])
    except: pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo):
    if modo_demo:
        return [{"fixture": {"date": "2026-05-10T20:00:00+00:00", "status": {"short": "FT"}}, "league": {"name": "LaLiga"}, "teams": {"home": {"name": "Real Madrid", "logo": ""}, "away": {"name": "Valencia", "logo": ""}}, "goals": {"home": 3, "away": 1}}], "demo"
    try:
        response = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season=2025", headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", []), "api"
    except: pass
    return [], "error"

@st.cache_data(ttl=600, show_spinner=False)
def obtener_plantilla(id_equipo):
    if modo_demo:
        return [
            {"name": "Thibaut Courtois", "number": 1, "age": 34, "position": "Goalkeeper"},
            {"name": "Dani Carvajal", "number": 2, "age": 34, "position": "Defender"},
            {"name": "Éder Militão", "number": 3, "age": 28, "position": "Defender"},
            {"name": "Jude Bellingham", "number": 5, "age": 23, "position": "Midfielder"},
            {"name": "Kylian Mbappé", "number": 9, "age": 27, "position": "Attacker"},
            {"name": "Vinícius Júnior", "number": 7, "age": 25, "position": "Attacker"},
            {"name": "Federico Valverde", "number": 8, "age": 27, "position": "Midfielder"}
        ]
    try:
        response = requests.get(f"https://v3.football.api-sports.io/players/squad?team={id_equipo}", headers=HEADERS)
        if response.status_code == 200:
            res_data = response.json().get("response", [])
            if res_data: return res_data[0].get("players", [])
    except: pass
    return []

live_fixtures = obtener_partidos_en_vivo()
records_live = []
if live_fixtures:
    for match in live_fixtures:
        records_live.append({
            "Liga": match['league']['name'], "Logo_Liga": match['league'].get('logo', ''),
            "Local": match['teams']['home']['name'], "Logo_L": match['teams']['home'].get('logo', ''), "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'], "Logo_V": match['teams']['away'].get('logo', ''), "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Panel Principal", "🔴 Central En Vivo", "📈 Analítica Avanzada", "🤖 Scout IA"])

with tab1:
    col_busqueda, col_vacia = st.columns([1, 2])
    with col_busqueda:
        busqueda_usuario = st.text_input("🔍 Buscar club (Ej. Arsenal, Milan):", value="", placeholder="Escribe al menos 3 letras...")
        
        if len(busqueda_usuario) >= 3:
            resultados = buscar_equipo_api(busqueda_usuario)
            if resultados:
                opciones = {f"{i['team']['name']} ({i['team']['country']})": i for i in resultados}
                sel = st.selectbox("Resultados encontrados:", list(opciones.keys()), index=None, placeholder="Selecciona el club de la lista...")
                if sel:
                    item_sel = opciones[sel]
                    t = item_sel['team']
                    v = item_sel.get('venue', {})
                    st.session_state.update({
                        "id_seleccionado": t['id'], "nombre_seleccionado": t['name'], 
                        "pais_seleccionado": t['country'], "logo_seleccionado": t['logo'],
                        "estadio_seleccionado": v.get('name', 'Estadio Desconocido'), "ciudad_seleccionada": v.get('city', 'Ciudad Desconocida')
                    })
                    st.rerun()
            else:
                st.warning("No se obtuvieron resultados de la API. Activa el 'Modo Demostración' en el sidebar para continuar exponiendo.")

    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    pais_activo = st.session_state["pais_seleccionado"]
    logo_activo = st.session_state.get("logo_seleccionado", "")
    
    historial_raw, origen = obtener_calendario_equipo(id_activo)
    records_historial = []
    
    for f in historial_raw:
        if 'fixture' in f:
            records_historial.append({
                "Fecha": pd.to_datetime(f['fixture']['date']),
                "Fecha_Str": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                "Competencia": f['league']['name'],
                "Local": f['teams']['home']['name'], "Logo_L": f['teams']['home'].get('logo', ''),
                "Goles Local": f['goals']['home'], "Goles Visita": f['goals']['away'],
                "Visita": f['teams']['away']['name'], "Logo_V": f['teams']['away'].get('logo', ''),
                "Estado": f['fixture']['status']['short']
            })
            
    if records_historial:
        df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False)
    else:
        df_historial = pd.DataFrame(columns=["Fecha", "Fecha_Str", "Competencia", "Local", "Logo_L", "Goles Local", "Goles Visita", "Visita", "Logo_V", "Estado"])
    
    victorias, empates, derrotas, goles_favor, partidos_jugados = 0, 0, 0, 0, 0
    df_finalizados = pd.DataFrame()
    
    if not df_historial.empty:
        df_finalizados = df_historial[df_historial['Estado'].isin(['FT', 'AET', 'PEN'])]
        partidos_jugados = len(df_finalizados)
        for _, row in df_finalizados.iterrows():
            es_local = row['Local'] == nombre_activo
            g_propio = row['Goles Local'] if es_local else row['Goles Visita']
            g_rival = row['Goles Visita'] if es_local else row['Goles Local']
            if pd.notna(g_propio) and pd.notna(g_rival):
                goles_favor += int(g_propio)
                if g_propio > g_rival: victorias += 1
                elif g_propio == g_rival: empates += 1
                else: derrotas += 1

    promedio_goles = round(goles_favor / partidos_jugados, 1) if partidos_jugados > 0 else 0
    efectividad = round((victorias / partidos_jugados) * 100, 1) if partidos_jugados > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left:4px solid {accent_color}; padding:15px;'><img src='{logo_activo}' width='50'><div><h3 style='margin:0;'>{nombre_activo}</h3><small style='color:#94A3B8;'>{pais_activo}</small></div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='premium-card' style='padding:15px;'><small style='color:#94A3B8;'>EFECTIVIDAD</small><h2 style='margin:0; color:#10B981 !important;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='premium-card' style='padding:15px;'><small style='color:#94A3B8;'>GOLES / PARTIDO</small><h2 style='margin:0; color:#F59E0B !important;'>{promedio_goles}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='premium-card' style='padding:15px;'><small style='color:#94A3B8;'>RÉCORD (V-E-D)</small><h2 style='margin:0;'>{victorias} - {empates} - {derrotas}</h2></div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Resultados</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                es_local = row['Local'] == nombre_activo
                g_propio = int(row['Goles Local']) if es_local else int(row['Goles Visita'])
                g_rival = int(row['Goles Visita']) if es_local else int(row['Goles Local'])
                color_borde = "#10B981" if g_propio > g_rival else ("#64748B" if g_propio == g_rival else "#EF4444")
                st.markdown(f"<div style='background:#0F172A; padding:12px; border-radius:8px; margin-bottom:8px; border-left:4px solid {color_borde}; display:flex; justify-content:space-between; align-items:center;'><div><b>{row['Local']}</b></div><div>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</div><div style='text-align:right;'><b>{row['Visita']}</b></div></div>", unsafe_allow_html=True)
        else:
            st.info("No se registran partidos finalizados en la temporada actual.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>📅 Calendario Actual</div>", unsafe_allow_html=True)
        df_proximos = df_historial[df_historial['Estado'] == 'NS'].sort_values(by="Fecha", ascending=True)
        render_calendario(df_proximos['Fecha'].dt.day.tolist() if not df_proximos.empty else [])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='premium-card'><div class='section-title'>👥 Plantilla del Equipo</div>", unsafe_allow_html=True)
    plantilla = obtener_plantilla(id_activo)
    if plantilla:
        df_final = pd.DataFrame([{"Número": p.get("number", "-"), "Nombre": p.get("name", "N/A"), "Edad": p.get("age", "-"), "Posición": p.get("position", "-")} for p in plantilla])
        st.dataframe(df_final, hide_index=True, use_container_width=True)
    else:
        st.warning("Información de plantilla no disponible de forma síncrona.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-title'>🔴 Cobertura en Directo</div>", unsafe_allow_html=True)
    if df_live.empty:
        st.info("No hay partidos disputándose en vivo en este momento.")
    else:
        for _, row in df_live.iterrows():
            st.markdown(f"<div class='live-card'><div style='display:flex; justify-content:space-between; align-items:center;'><span>{row['Local']}</span><span class='live-score'>{row['Goles L']} - {row['Goles V']}</span><span>{row['Visita']}</span></div><center><span class='pulse-minute'>⏱️ {row['Minuto']}'</span></center></div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title'>📈 Analítica de Datos Avanzada</div>", unsafe_allow_html=True)
    data_volumen = pd.DataFrame({'Liga': ['LaLiga', 'Premier League', 'Serie A'], 'Partidos': [12, 8, 5]})
    data_goles = pd.DataFrame({'Liga': ['LaLiga', 'Premier League', 'Serie A'], 'Goles Totales': [34, 22, 15]})
    
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(data_volumen, x='Liga', y='Partidos', template='plotly_dark', color_discrete_sequence=[accent_color])
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.area(data_goles, x='Liga', y='Goles Totales', template='plotly_dark', color_discrete_sequence=['#EF4444'])
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[efectividad, min(100, int(promedio_goles * 35)), 70, 65, 75], theta=['Efectividad', 'Poder Goleador', 'Solidez Defensiva', 'Consistencia', 'Volumen'], fill='toself', fillcolor=hex_to_rgba(accent_color, 0.25), line=dict(color=accent_color, width=3)))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template='plotly_dark')
        st.plotly_chart(fig_radar, use_container_width=True)
    with c4:
        ciudad = st.session_state.get("ciudad_seleccionada", "Madrid")
        coords = CITY_COORDS.get(ciudad, [40.4167, -3.7037])
        st.map(pd.DataFrame({'lat': [coords[0]], 'lon': [coords[1]]}), zoom=12, use_container_width=True)

with tab4:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🤖 Scout IA - Análisis Táctico</div>", unsafe_allow_html=True)
    estilo_rival = st.selectbox("Arquetipo Táctico del Rival:", ["🛡️ Bloque Bajo", "⚔️ Presión Alta"])
    st.write(f"**Estado del Motor IA:** {nombre_activo} presenta un rendimiento adaptativo basado en métricas históricas de la temporada.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: #334155; margin-top: 40px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 20px;'>
        <strong>Forza Football Analytics V3.0 (Integración AI)</strong><br>
        Plataforma Avanzada de Datos Deportivos | Proyecto Universitario | Desarrollado por Salomón Achar © 2026
    </div>
""", unsafe_allow_html=True)
