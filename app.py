import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

CITY_COORDS = {
    "Madrid": [40.4167, -3.7037],
    "Barcelona": [41.3851, 2.1734],
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
    529: "#A81E3D",  
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

id_activo = st.session_state["id_seleccionado"]
accent_color = TEAM_THEMES.get(id_activo, "#3B82F6")

st.markdown(f"""
    <style>
        .stApp {{
            background-color: #0F172A !important;
        }}
        
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
            color: #F8FAFC !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: transparent;
        }}
        button[data-baseweb="tab"] {{
            background-color: #1E293B !important;
            border-radius: 8px 8px 0 0;
            border: 1px solid #334155;
            border-bottom: none;
        }}
        button[data-baseweb="tab"] p {{
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
        }}
        button[aria-selected="true"] {{
            background-color: {accent_color} !important;
            border-color: {accent_color} !important;
        }}
        button[aria-selected="true"] p {{
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }}
        
        .premium-card {{
            background-color: #1E293B !important;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
            border: 1px solid #334155;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .premium-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
        }}

        .live-card {{
            background-color: #0F172A !important;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid #334155;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .live-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
            border-color: {accent_color} !important;
        }}
        
        .section-title {{
            color: #FFFFFF !important;
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #334155;
            padding-bottom: 8px;
        }}
        
        .live-team-name {{
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 1.15rem !important;
        }}
        
        .live-score {{
            color: #EF4444 !important;
            font-weight: 900 !important;
            font-size: 1.5rem !important;
            margin: 0 15px !important;
            background: #000000;
            padding: 4px 12px;
            border-radius: 6px;
        }}
        
        .live-league-label {{
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }}

        .pulse-minute {{
            background-color: {accent_color};
            color: #FFFFFF !important;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 800;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
            100% {{ opacity: 1; }}
        }}
        
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border: 1px solid #334155 !important;
        }

        .cal-container {{ background: #0F172A; border-radius: 12px; padding: 15px; border: 1px solid #334155; color: white; margin-bottom: 15px; }}
        .cal-header {{ text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 1.1rem; }}
        .cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center; }}
        .day-header {{ color: #64748B; font-size: 0.75rem; font-weight: bold; }}
        .day-cell {{ padding: 8px 0; font-size: 0.9rem; }}
        .today-circle {{ background: #EF4444; border-radius: 50%; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
        .match-day-circle {{ background: {accent_color}; border-radius: 50%; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }}
    </style>
""", unsafe_allow_html=True)

def render_calendario(dias_partido):
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
            elif day in dias_partido: html += f"<div><div class='match-day-circle'>{day}</div></div>"
            else: html += f"<div class='day-cell'>{day}</div>"
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

API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

st.sidebar.markdown("### ⚙️ Centro de Control")
if st.sidebar.button("🔄 Refrescar Datos de API"):
    st.cache_data.clear()

@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo(key_api):
    try:
        response = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
        if response.status_code == 200: return response.json().get("response", [])
    except: pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3: return []
    try:
        response = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}", headers=HEADERS)
        if response.status_code == 200: return response.json().get("response", [])
    except: pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo):
    fixtures = []
    try:
        response = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season=2024", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("response"):
                fixtures = data.get("response")
        return fixtures, "api_directa"
    except:
        pass
    return [], "error"

@st.cache_data(ttl=600, show_spinner=False)
def obtener_plantilla(id_equipo):
    try:
        response = requests.get(f"https://v3.football.api-sports.io/players/squad?team={id_equipo}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("response"):
                return data.get("response")[0].get("players", [])
    except:
        pass
    return []

live_fixtures = obtener_partidos_en_vivo(API_KEY)
records_live = []
if live_fixtures:
    for match in live_fixtures:
        records_live.append({
            "Liga": match['league']['name'],
            "Logo_Liga": match['league']['logo'],
            "Local": match['teams']['home']['name'],
            "Logo_L": match['teams']['home']['logo'],
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Logo_V": match['teams']['away']['logo'],
            "Goles V": match['goals']['away'],
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
                sel = st.selectbox("Resultados:", list(opciones.keys()))
                if sel:
                    item_sel = opciones[sel]
                    t = item_sel['team']
                    v = item_sel.get('venue', {})
                    st.session_state.update({
                        "id_seleccionado": t['id'], 
                        "nombre_seleccionado": t['name'], 
                        "pais_seleccionado": t['country'], 
                        "logo_seleccionado": t['logo'],
                        "estadio_seleccionado": v.get('name', 'Estadio Desconocido'),
                        "ciudad_seleccionada": v.get('city', 'Ciudad Desconocida')
                    })
                    st.rerun()

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
                "Local": f['teams']['home']['name'],
                "Logo_L": f['teams']['home']['logo'],
                "Goles Local": f['goals']['home'],
                "Goles Visita": f['goals']['away'],
                "Visita": f['teams']['away']['name'],
                "Logo_V": f['teams']['away']['logo'],
                "Estado": f['fixture']['status']['short']
            })
            
    cols = ["Fecha", "Fecha_Str", "Competencia", "Local", "Logo_L", "Goles Local", "Goles Visita", "Visita", "Logo_V", "Estado"]
    if records_historial:
        df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False)
    else:
        df_historial = pd.DataFrame(columns=cols)
    
    victorias, empates, derrotas, goles_favor, partidos_jugados = 0, 0, 0, 0, 0
    df_finalizados = pd.DataFrame()
    
    if not df_historial.empty:
        df_finalizados = df_historial[df_historial['Estado'].isin(['FT', 'AET', 'PEN'])]
        partidos_jugados = len(df_finalizados)
        
        if partidos_jugados > 0:
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
        st.markdown(f"""
            <div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left: 4px solid {accent_color}; padding: 15px;'>
                <img src='{logo_activo}' width='50'>
                <div>
                    <h3 style='margin:0; font-size:1.2rem;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8;'>{pais_activo}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>EFECTIVIDAD</small><h2 style='margin:0; color:#10B981 !important;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>GOLES / PARTIDO</small><h2 style='margin:0; color:#F59E0B !important;'>{promedio_goles}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>RÉCORD (V-E-D)</small><h2 style='margin:0; color:#FFFFFF !important;'>{victorias} - {empates} - {derrotas}</h2></div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Resultados</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                es_local = row['Local'] == nombre_activo
                g_propio = int(row['Goles Local']) if es_local else int(row['Goles Visita'])
                g_rival = int(row['Goles Visita']) if es_local else int(row['Goles Local'])
                
                color_borde = "#10B981" if g_propio > g_rival else ("#64748B" if g_propio == g_rival else "#EF4444")
                
                logo_l = f"<img src='{row['Logo_L']}' width='24'>" if 'Logo_L' in row else ""
                logo_v = f"<img src='{row['Logo_V']}' width='24'>" if 'Logo_V' in row else ""

                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {color_borde};'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'>{logo_l} <span style='font-weight:bold;'>{row['Local']}</span></div>
                            <div style='width: 20%; text-align:center; font-size:1.2rem; font-weight:900;'>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'><span style='font-weight:bold;'>{row['Visita']}</span> {logo_v}</div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay resultados recientes.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>📅 Calendario Actual</div>", unsafe_allow_html=True)
        df_proximos = df_historial[df_historial['Estado'] == 'NS'].sort_values(by="Fecha", ascending=True)
        dias_con_partidos = df_proximos['Fecha'].dt.day.tolist() if not df_proximos.empty else []
        render_calendario(dias_con_partidos)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximos</div>", unsafe_allow_html=True)
        df_proximos_limit = df_proximos.head(5)
        if not df_proximos_limit.empty:
            for _, row in df_proximos_limit.iterrows():
                logo_l = f"<img src='{row['Logo_L']}' width='24'>" if 'Logo_L' in row else ""
                logo_v = f"<img src='{row['Logo_V']}' width='24'>" if 'Logo_V' in row else ""
                
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {accent_color};'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'>{logo_l} {row['Local']}</div>
                            <div style='width: 20%; text-align:center; color:#F59E0B; font-weight:bold;'>VS</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'>{row['Visita']} {logo_v}</div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay próximos partidos.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='premium-card'><div class='section-title'>👥 Plantilla del Equipo</div>", unsafe_allow_html=True)
    st.subheader(f"Jugadores de: {nombre_activo}")
    plantilla = obtener_plantilla(id_activo)
    
    if plantilla:
        datos_formateados = []
        for p in plantilla:
            datos_formateados.append({
                "Número": p.get("number") if p.get("number") is not None else "-",
                "Nombre": p.get("name", "N/A"),
                "Edad": p.get("age", "-"),
                "Posición": p.get("position", "-")
            })
        df_final = pd.DataFrame(datos_formateados)
        st.dataframe(df_final, hide_index=True, use_container_width=True)
    else:
        st.warning(f"No se encontró información de la plantilla para {nombre_activo}.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-title'>🔴 Cobertura en Directo</div>", unsafe_allow_html=True)
    
    if df_live.empty:
        st.info("No hay partidos disputándose en vivo en este momento.")
    else:
        for _, row in df_live.iterrows():
            st.markdown(f"""
                <div class='live-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='width: 35%; display:flex; align-items:center; gap:15px;'>
                            <img src='{row['Logo_L']}' width='40'>
                            <span class='live-team-name'>{row['Local']}</span>
                        </div>
                        <div style='width: 30%; text-align: center;'>
                            <span class='live-score'>{row['Goles L']} - {row['Goles V']}</span><br>
                            <div style='margin-top:10px;'><span class='pulse-minute'>⏱️ {row['Minuto']}'</span></div>
                        </div>
                        <div style='width: 35%; display:flex; align-items:center; justify-content:flex-end; gap:15px;'>
                            <span class='live-team-name'>{row['Visita']}</span>
                            <img src='{row['Logo_V']}' width='40'>
                        </div>
                    </div>
                    <div style='text-align:center; margin-top: 15px; border-top: 1px solid #1E293B; padding-top: 10px;'>
                        <img src='{row['Logo_Liga']}' width='20' style='vertical-align:middle;'> 
                        <span class='live-league-label'> {row['Liga']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px;'>📈 Analítica de Datos Avanzada</div>", unsafe_allow_html=True)
    
    if not df_live.empty:
        data_volumen = df_live['Liga'].value_counts().reset_index()
        data_volumen.columns = ['Liga', 'Partidos']
        goles_local = pd.to_numeric(df_live['Goles L'], errors='coerce').fillna(0)
        goles_visita = pd.to_numeric(df_live['Goles V'], errors='coerce').fillna(0)
        df_live['Goles Totales'] = goles_local + goles_visita
        data_goles = df_live.groupby('Liga')['Goles Totales'].sum().reset_index()
    else:
        data_volumen = pd.DataFrame({'Liga': ['LaLiga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1'], 'Partidos': [12, 8, 5, 4, 3]})
        data_goles = pd.DataFrame({'Liga': ['LaLiga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1'], 'Goles Totales': [34, 22, 15, 12, 9]})

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📊 Volumen de Partidos Interactivos</div>", unsafe_allow_html=True)
        fig1 = px.bar(data_volumen, x='Liga', y='Partidos', color='Liga', template='plotly_dark', color_discrete_sequence=[accent_color, '#64748B'])
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>⚽ Distribución Híbrida de Goles</div>", unsafe_allow_html=True)
        fig2 = px.area(data_goles, x='Liga', y='Goles Totales', template='plotly_dark', color_discrete_sequence=['#EF4444'])
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>🕸️ Matriz Táctica de Rendimiento (Radar)</div>", unsafe_allow_html=True)
        
        val_goles = min(100, int(promedio_goles * 35))
        val_derrotas_inv = max(0, int((1 - (derrotas/partidos_jugados)) * 100)) if partidos_jugados > 0 else 50
        
        radar_metrics = ['Efectividad', 'Poder Goleador', 'Solidez Defensiva', 'Consistencia', 'Volumen Juego']
        radar_values = [efectividad, val_goles, val_derrotas_inv, max(20, efectividad - 5), 75]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_metrics,
            fill='toself',
            fillcolor=f"{accent_color}40",
            line=dict(color=accent_color, width=3),
            name=nombre_activo
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"),
                angularaxis=dict(color="#F8FAFC")
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c4:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📍 Geo-Localización de Sedes Oficiales</div>", unsafe_allow_html=True)
        ciudad = st.session_state.get("ciudad_seleccionada", "Madrid")
        estadio = st.session_state.get("estadio_seleccionado", "Estadio Santiago Bernabéu")
        coords = CITY_COORDS.get(ciudad, [40.4167, -3.7037])
        
        df_geo = pd.DataFrame({'lat': [coords[0]], 'lon': [coords[1]], 'Sede': [estadio]})
        st.markdown(f"<p style='margin-bottom:10px;'>🏠 <b>Sede:</b> {estadio} | 📍 <b>Ciudad:</b> {ciudad}</p>", unsafe_allow_html=True)
        st.map(df_geo, zoom=12, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🤖 Scout IA - Análisis Táctico Predictivo</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🎲 Simulador Táctico de Probabilidades")
    st.write("Configura el arquetipo del próximo rival para calcular la proyección matemática de resultados.")
    
    estilo_rival = st.selectbox("Arquetipo Táctico del Rival:", ["🛡️ Bloque Bajo / Defensivo", "⚔️ Presión Alta / Ofensivo", "⚖️ Equilibrado / Contragolpe"])
    
    base_win = efectividad if efectividad > 0 else 45
    if "Defensivo" in estilo_rival:
        win_p = max(15, base_win - 8)
        draw_p = min(55, 100 - win_p - 10)
    elif "Ofensivo" in estilo_rival:
        win_p = min(88, base_win + 12)
        draw_p = max(8, 100 - win_p - 15)
    else:
        win_p = base_win
        draw_p = (empates / partidos_jugados * 100) if partidos_jugados > 0 else 25
        
    loss_p = max(0, 100 - win_p - draw_p)
    
    df_prob = pd.DataFrame({
        'Resultado': ['Victoria', 'Empate', 'Derrota'],
        'Probabilidad (%)': [round(win_p, 1), round(draw_p, 1), round(loss_p, 1)]
    })
    
    fig_prob = px.bar(
        df_prob, x='Probabilidad (%)', y='Resultado', orientation='h', 
        color='Resultado', color_discrete_map={'Victoria': '#10B981', 'Empate': '#64748B', 'Derrota': '#EF4444'},
        template="plotly_dark"
    )
    fig_prob.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_prob, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    rendimiento_txt = "óptimo" if efectividad >= 50 else "en desarrollo"
    st.write(f"**Estado del Motor IA:** {nombre_activo} presenta un rendimiento {rendimiento_txt} con una efectividad del {efectividad}%.")

    pregunta_usuario = st.chat_input(f"Pregunta sobre {nombre_activo}...")
    
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta_usuario)
            
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["goles", "promedio", "anotaciones"]):
                respuesta = f"El equipo registra un promedio de {promedio_goles} goles por partido actualmente."
            elif any(x in p for x in ["victoria", "ganado", "triunfos"]):
                respuesta = f"En la temporada actual, el equipo ha logrado {victorias} victorias."
            elif any(x in p for x in ["derrota", "perdido"]):
                respuesta = f"El equipo suma {derrotas} derrotas en el registro actual."
            elif any(x in p for x in ["efectividad", "porcentaje", "desempeño"]):
                respuesta = f"El nivel de efectividad actual es del {efectividad}%, basado en {partidos_jugados} partidos."
            elif "partidos" in p or "jugados" in p:
                respuesta = f"Hasta el momento, se han analizado {partidos_jugados} partidos oficiales."
            else:
                respuesta = (f"Como analista, puedo decirte que {nombre_activo} tiene un récord de {victorias}V-{empates}E-{derrotas}D. "
                            f"¿Te gustaría profundizar en su promedio goleador ({promedio_goles}) o en su efectividad ({efectividad}%)?")
            
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
