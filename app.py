import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-color: #0F172A !important;
        }
        
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #F8FAFC !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        button[data-baseweb="tab"] {
            background-color: #1E293B !important;
            border-radius: 8px 8px 0 0;
            border: 1px solid #334155;
            border-bottom: none;
        }
        button[data-baseweb="tab"] p {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
        }
        button[aria-selected="true"] {
            background-color: #3B82F6 !important;
            border-color: #3B82F6 !important;
        }
        button[aria-selected="true"] p {
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }
        
        .premium-card {
            background-color: #1E293B !important;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
            border: 1px solid #334155;
        }
        
        .section-title {
            color: #FFFFFF !important;
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #334155;
            padding-bottom: 8px;
        }
        
        .live-team-name {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 1.15rem !important;
        }
        
        .live-score {
            color: #EF4444 !important;
            font-weight: 900 !important;
            font-size: 1.5rem !important;
            margin: 0 15px !important;
            background: #000000;
            padding: 4px 12px;
            border-radius: 6px;
        }
        
        .live-league-label {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }

        .pulse-minute {
            background-color: #EF4444;
            color: #FFFFFF !important;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 800;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
        
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border: 1px solid #334155 !important;
        }
    </style>
""", unsafe_allow_html=True)

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
        # Consulta corregida para el plan gratuito usando la temporada 2026
        response = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season=2026", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("errors"):
                st.warning(f"Nota de API: {data.get('errors')}")
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
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    
    if "id_seleccionado" not in st.session_state:
        st.session_state.update({"id_seleccionado": 541, "nombre_seleccionado": "Real Madrid", "pais_seleccionado": "Spain", "logo_seleccionado": "https://media.api-sports.io/football/teams/541.png"})
        
    col_busqueda, col_vacia = st.columns([1, 2])
    with col_busqueda:
        busqueda_usuario = st.text_input("🔍 Buscar club (Ej. Arsenal, Milan):", value="", placeholder="Escribe al menos 3 letras...")
        
        if len(busqueda_usuario) >= 3:
            resultados = buscar_equipo_api(busqueda_usuario)
            if resultados:
                opciones = {f"{i['team']['name']} ({i['team']['country']})": i['team'] for i in resultados}
                sel = st.selectbox("Resultados:", list(opciones.keys()))
                if sel:
                    t = opciones[sel]
                    st.session_state.update({"id_seleccionado": t['id'], "nombre_seleccionado": t['name'], "pais_seleccionado": t['country'], "logo_seleccionado": t['logo']})
    st.markdown("</div>", unsafe_allow_html=True)

    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    pais_activo = st.session_state["pais_seleccionado"]
    logo_activo = st.session_state.get("logo_seleccionado", "")
    
    historial_raw, origen = obtener_calendario_equipo(id_activo)
    records_historial = []
    
    for f in historial_raw:
        if 'fixture' in f:
            records_historial.append({
                "Fecha": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                "Competencia": f['league']['name'],
                "Local": f['teams']['home']['name'],
                "Logo_L": f['teams']['home']['logo'],
                "Goles Local": f['goals']['home'],
                "Goles Visita": f['goals']['away'],
                "Visita": f['teams']['away']['name'],
                "Logo_V": f['teams']['away']['logo'],
                "Estado": f['fixture']['status']['short']
            })
            
    df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False) if records_historial else pd.DataFrame()
    
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
            <div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left: 4px solid #3B82F6; padding: 15px;'>
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
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay resultados recientes.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Calendario</div>", unsafe_allow_html=True)
        if not df_historial.empty:
            df_proximos = df_historial[~df_historial['Estado'].isin(['FT', 'AET', 'PEN'])].tail(5)
            for _, row in df_proximos.iloc[::-1].iterrows():
                logo_l = f"<img src='{row['Logo_L']}' width='24'>" if 'Logo_L' in row else ""
                logo_v = f"<img src='{row['Logo_V']}' width='24'>" if 'Logo_V' in row else ""
                
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #3B82F6;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 40%; display:flex; align-items:center; gap:8px;'>{logo_l} {row['Local']}</div>
                            <div style='width: 20%; text-align:center; color:#F59E0B; font-weight:bold;'>VS</div>
                            <div style='width: 40%; display:flex; align-items:center; justify-content:flex-end; gap:8px;'>{row['Visita']} {logo_v}</div>
                        </div>
                        <div style='text-align:center; margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏆 {row['Competencia']} | 📅 {row['Fecha']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay próximos partidos.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='premium-card'><div class='section-title'>👥 Plantilla del Equipo</div>", unsafe_allow_html=True)
    plantilla = obtener_plantilla(id_activo)
    if plantilla:
        df_plantilla = pd.DataFrame(plantilla)
        if not df_plantilla.empty:
            df_plantilla['Edad'] = df_plantilla['age']
            df_plantilla['Posición'] = df_plantilla['position']
            df_plantilla['Número'] = df_plantilla['number'].fillna("-")
            st.dataframe(
                df_plantilla[['Número', 'name', 'Edad', 'Posición']],
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("No se encontró información de la plantilla para este equipo.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔴 Cobertura en Directo</div>", unsafe_allow_html=True)
    
    if df_live.empty:
        st.info("No hay partidos disputándose en vivo en este momento.")
    else:
        for _, row in df_live.iterrows():
            st.markdown(f"""
                <div style='background-color: #0F172A; padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #334155;'>
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
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px;'>📈 Analítica de Datos</div>", unsafe_allow_html=True)
    
    if not df_live.empty:
        data_volumen = df_live['Liga'].value_counts()
        goles_local = pd.to_numeric(df_live['Goles L'], errors='coerce').fillna(0)
        goles_visita = pd.to_numeric(df_live['Goles V'], errors='coerce').fillna(0)
        df_live['Goles Totales'] = goles_local + goles_visita
        data_goles = df_live.groupby('Liga')['Goles Totales'].sum()
    else:
        data_volumen = pd.Series([12, 8, 5, 4, 3], index=['LaLiga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1'])
        data_goles = pd.Series([34, 22, 15, 12, 9], index=['LaLiga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1'])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📊 Volumen de Partidos</div>", unsafe_allow_html=True)
        st.bar_chart(data_volumen, use_container_width=True, color="#3B82F6")
        st.caption("Cantidad de encuentros activos por competencia.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>⚽ Goles Totales por Liga</div>", unsafe_allow_html=True)
        st.area_chart(data_goles, use_container_width=True, color="#EF4444")
        st.caption("Suma de goles registrados en la jornada actual.")
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🤖 Scout IA - Análisis Táctico</div>", unsafe_allow_html=True)
    
    rendimiento_txt = "óptimo" if efectividad >= 50 else "en desarrollo"
    st.write(f"**Estado actual:** {nombre_activo} presenta un rendimiento {rendimiento_txt} con una efectividad del {efectividad}%.")

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
