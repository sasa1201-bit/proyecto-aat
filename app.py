import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
import plotly.graph_objects as go

st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

# 1. Inicialización segura de variables globales de estado al inicio absoluto
if "id_seleccionado" not in st.session_state:
    st.session_state.id_seleccionado = 541
    st.session_state.nombre_seleccionado = "Real Madrid"
    st.session_state.pais_seleccionado = "Spain"
    st.session_state.logo_seleccionado = "https://media.api-sports.io/football/teams/541.png"

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

st.markdown("""
    <style>
        .stApp { background-color: #0F172A !important; }
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #F8FAFC !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
        button[data-baseweb="tab"] { background-color: #1E293B !important; border-radius: 8px 8px 0 0; border: 1px solid #334155; border-bottom: none; }
        button[data-baseweb="tab"] p { color: #94A3B8 !important; font-weight: 600 !important; font-size: 1.05rem !important; }
        button[aria-selected="true"] { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        button[aria-selected="true"] p { color: #FFFFFF !important; font-weight: 800 !important; }
        .premium-card { background-color: #1E293B !important; padding: 24px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 20px; border: 1px solid #334155; }
        .live-card { background-color: #0F172A !important; padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #334155; }
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

API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

st.sidebar.markdown("### ⚙️ Centro de Control")
if st.sidebar.button("🔄 Refrescar Datos de API"):
    st.cache_data.clear()

@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo_y_jornada():
    """Trae partidos en vivo reales; si no hay nada en juego, trae la jornada completa de hoy para evitar pantallas vacías."""
    try:
        response = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
        if response.status_code == 200 and len(response.json().get("response", [])) > 0:
            return response.json().get("response", []), "🔴 EN VIVO"
        
        # Fallback dinámico a los partidos del día real de hoy
        hoy = datetime.now().strftime('%Y-%m-%d')
        response_hoy = requests.get(f"https://v3.football.api-sports.io/fixtures?date={hoy}", headers=HEADERS)
        if response_hoy.status_code == 200:
            return response_hoy.json().get("response", []), "📅 JORNADA DE HOY"
    except:
        pass
    return [], "SIN PARTIDOS RECIENTES"

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3: return []
    try:
        response = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}", headers=HEADERS)
        if response.status_code == 200: 
            return response.json().get("response", [])
    except: 
        pass
    return []

@st.cache_data(ttl=120, show_spinner=False)
def obtener_calendario_dinamico_equipo(id_equipo):
    """Consulta los encuentros pasados y futuros dinámicamente sin amarrarse a un año estático."""
    fixtures_totales = []
    try:
        # 1. Obtener los últimos 15 partidos jugados para métricas y resultados históricos
        res_pasados = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"team": id_equipo, "last": 15})
        if res_pasados.status_code == 200:
            fixtures_totales.extend(res_pasados.json().get("response", []))
            
        # 2. Obtener los siguientes 15 partidos programados para la pestaña de próximos
        res_futuros = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"team": id_equipo, "next": 15})
        if res_futuros.status_code == 200:
            fixtures_totales.extend(res_futuros.json().get("response", []))
    except:
        pass
    return fixtures_totales

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

# Carga de Datos en Vivo / Jornada Actual Real
live_fixtures, tipo_cobertura = obtener_partidos_en_vivo_y_jornada()
records_live = []
if live_fixtures:
    for match in live_fixtures:
        status_short = match['fixture']['status']['short']
        minuto_mostrado = f"{match['fixture']['status']['elapsed']}'" if status_short in ['1H', '2H', 'HT', 'ET'] else status_short
        records_live.append({
            "Liga": match['league']['name'],
            "Logo_Liga": match['league'].get('logo', ''),
            "Local": match['teams']['home']['name'],
            "Logo_L": match['teams']['home'].get('logo', ''),
            "Goles L": match['goals']['home'] if match['goals']['home'] is not None else 0,
            "Visita": match['teams']['away']['name'],
            "Logo_V": match['teams']['away'].get('logo', ''),
            "Goles V": match['goals']['away'] if match['goals']['away'] is not None else 0,
            "Minuto": minuto_mostrado
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Panel Principal", "🔴 Central En Vivo", "📈 Analítica Avanzada", "🤖 Scout IA"])

with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    col_busqueda, col_vacia = st.columns([1, 2])
    with col_busqueda:
        busqueda_usuario = st.text_input("🔍 Buscar club (Ej. Arsenal, Barcelona, Milan):", value="")

        if len(busqueda_usuario) >= 3:
            resultados = buscar_equipo_api(busqueda_usuario)
            if resultados:
                opciones = {f"{i['team']['name']} ({i['team']['country']})": i['team'] for i in resultados}
                seleccion_actual = st.selectbox("Clubes encontrados:", list(opciones.keys()))
                
                if seleccion_actual:
                    equipo_datos = opciones[seleccion_actual]
                    if st.session_state.id_seleccionado != equipo_datos['id']:
                        st.session_state.id_seleccionado = equipo_datos['id']
                        st.session_state.nombre_seleccionado = equipo_datos['name']
                        st.session_state.pais_seleccionado = equipo_datos['country']
                        st.session_state.logo_seleccionado = equipo_datos['logo']
                        st.rerun()
            else:
                st.info("No se encontraron equipos con ese nombre.")
    st.markdown("</div>", unsafe_allow_html=True)

    id_activo = st.session_state.id_seleccionado
    nombre_activo = st.session_state.nombre_seleccionado
    pais_activo = st.session_state.pais_seleccionado
    logo_activo = st.session_state.logo_seleccionado
    
    # Procesar Calendarios y Resultados de forma Relativa/Dinámica
    historial_raw = obtener_calendario_dinamico_equipo(id_activo)
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
    df_historial = pd.DataFrame(records_historial) if records_historial else pd.DataFrame(columns=cols)
    
    victorias, empates, derrotas, goles_favor, partidos_jugados = 0, 0, 0, 0, 0
    df_finalizados = pd.DataFrame()
    
    if not df_historial.empty:
        df_finalizados = df_historial[df_historial['Estado'].isin(['FT', 'AET', 'PEN'])].sort_values(by="Fecha", ascending=False)
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
            <div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left: 4px solid #3B82F6; padding: 15px;'>
                <img src='{logo_activo}' width='50'>
                <div>
                    <h3 style='margin:0; font-size:1.2rem;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8;'>{pais_activo}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>EFECTIVIDAD REAL</small><h2 style='margin:0; color:#10B981 !important;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>GOLES / ENCUENTRO</small><h2 style='margin:0; color:#F59E0B !important;'>{promedio_goles}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>RÉCORD (V-E-D)</small><h2 style='margin:0; color:#FFFFFF !important;'>{victorias} - {empates} - {derrotas}</h2></div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Resultados Reales</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                color_borde = "#10B981" if (row['Local'] == nombre_activo and row['Goles Local'] > row['Goles Visita']) or (row['Visita'] == nombre_activo and row['Goles Visita'] > row['Goles Local']) else ("#64748B" if row['Goles Local'] == row['Goles Visita'] else "#EF4444")
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {color_borde};'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'><img src='{row['Logo_L']}' width='24'> <span style='font-weight:bold;'>{row['Local']}</span></div>
                            <div style='width: 20%; text-align:center; font-size:1.2rem; font-weight:900;'>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'><span style='font-weight:bold;'>{row['Visita']}</span> <img src='{row['Logo_V']}' width='24'></div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Buscando el historial de encuentros del club en la API...")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>📅 Calendario Actual</div>", unsafe_allow_html=True)
        render_calendario()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximos Encuentros Programados</div>", unsafe_allow_html=True)
        df_proximos = df_historial[df_historial['Estado'] == 'NS'].sort_values(by="Fecha", ascending=True).head(5)
        if not df_proximos.empty:
            for _, row in df_proximos.iterrows():
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #3B82F6;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'><img src='{row['Logo_L']}' width='24'> {row['Local']}</div>
                            <div style='width: 20%; text-align:center; color:#F59E0B; font-weight:bold;'>VS</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'>{row['Visita']} <img src='{row['Logo_V']}' width='24'></div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay partidos inmediatos programados en esta ventana de la API.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='premium-card'><div class='section-title'>👥 Plantilla del Equipo</div>", unsafe_allow_html=True)
    plantilla = obtener_plantilla(id_activo)
    if plantilla:
        datos_formateados = [{"Número": p.get("number") if p.get("number") is not None else "-", "Nombre": p.get("name", "N/A"), "Edad": p.get("age", "-"), "Posición": p.get("position", "-")} for p in plantilla]
        st.dataframe(pd.DataFrame(datos_formateados), hide_index=True, use_container_width=True)
    else:
        st.warning("Información de plantilla no disponible de forma temporal en la API.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>📡 Cobertura Real: {tipo_cobertura}</div>", unsafe_allow_html=True)
    
    if df_live.empty:
        st.info("No hay partidos programados ni disputándose hoy en la API.")
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
                            <div style='margin-top:10px;'><span class='pulse-minute'>⏱️ {row['Minuto']}</span></div>
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
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px;'>📈 Analítica de Datos</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📊 Volumen por Competencia</div>", unsafe_allow_html=True)
        if not df_live.empty:
            st.bar_chart(df_live['Liga'].value_counts(), use_container_width=True, color="#3B82F6")
        else:
            st.info("Esperando volumen de partidos de la jornada.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>⚽ Distribución de Goles de la Jornada</div>", unsafe_allow_html=True)
        if not df_live.empty:
            st.area_chart(df_live.groupby('Liga')['Goles L'].sum(), use_container_width=True, color="#EF4444")
        else:
            st.info("Esperando goles en los encuentros de la jornada.")
        st.markdown("</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>🕸️ Perfil Táctico Radar</div>", unsafe_allow_html=True)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[efectividad, min(100, int(promedio_goles * 35)), 75, 70, 80], 
            theta=['Efectividad', 'Poder Goleador', 'Solidez Defensiva', 'Consistencia', 'Volumen'], 
            fill='toself', 
            fillcolor=hex_to_rgba("#3B82F6", 0.25), 
            line=dict(color="#3B82F6", width=3)
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
    st.write(f"**Análisis:** {nombre_activo} cuenta con una efectividad calculada del {efectividad}% en sus encuentros recientes analizados.")
    
    pregunta_usuario = st.chat_input(f"Preguntar métricas de {nombre_activo}...")
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"): st.write(pregunta_usuario)
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["goles", "promedio"]): respuesta = f"El promedio histórico registrado es de {promedio_goles} goles por partido."
            elif any(x in p for x in ["victoria", "ganados"]): respuesta = f"El club acumula {victorias} victorias en sus encuentros analizados."
            elif "efectividad" in p: respuesta = f"La efectividad de rendimiento actual corresponde al {efectividad}%."
            else: respuesta = f"Métricas de {nombre_activo}: Récord de {victorias}V-{empates}E-{derrotas}D. ¿Te gustaría analizar otra variable?"
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
