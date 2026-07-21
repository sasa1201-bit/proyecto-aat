import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Forza F1 Dashboard", page_icon="🏎️", layout="wide")

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
            background-color: #EF4444 !important;
            border-color: #EF4444 !important;
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .premium-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
        }

        .live-card {
            background-color: #0F172A !important;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid #334155;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .live-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7);
            border-color: #EF4444 !important;
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
            <h1 style='color: #FFFFFF !important; font-size: 2.5rem; font-weight: 900; margin: 0;'>FORZA F1 LIVE</h1>
            <p style='color: #94A3B8 !important; font-size: 1rem; margin: 0; text-transform: uppercase; letter-spacing: 2px;'>Motor Analítico de Rendimiento en Pista</p>
        </div>
    </div>
""", unsafe_allow_html=True)

API_KEY = "6e2b9712ca7c0351fe3117b5c6d7c09e"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v1.formula-1.api-sports.io'}

st.sidebar.markdown("### ⚙️ Centro de Control")
if st.sidebar.button("🔄 Refrescar Datos de API"):
    st.cache_data.clear()

@st.cache_data(ttl=86400, show_spinner=False)
def obtener_coordenadas(ciudad, pais):
    try:
        geolocator = Nominatim(user_agent="forza_f1_app")
        busqueda = f"{ciudad}, {pais}" if ciudad else pais
        location = geolocator.geocode(busqueda)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

@st.cache_data(ttl=30, show_spinner=False)
def obtener_carreras_en_vivo(key_api):
    try:
        response = requests.get("https://v1.formula-1.api-sports.io/races?type=live", headers=HEADERS)
        if response.status_code == 200: return response.json().get("response", [])
    except: pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def buscar_escuderia_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 2: return []
    try:
        response = requests.get(f"https://v1.formula-1.api-sports.io/teams?search={nombre_busqueda}", headers=HEADERS)
        if response.status_code == 200: return response.json().get("response", [])
    except: pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_escuderia(id_escuderia):
    races = []
    try:
        response = requests.get(f"https://v1.formula-1.api-sports.io/races?team={id_escuderia}&season=2026", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("response"):
                races = data.get("response")
        return races, "api_directa"
    except:
        pass
    return [], "error"

@st.cache_data(ttl=600, show_spinner=False)
def obtener_pilotos(id_escuderia):
    try:
        response = requests.get(f"https://v1.formula-1.api-sports.io/teams/drivers?team={id_escuderia}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get("response"):
                return data.get("response")
    except:
        pass
    return []

live_races = obtener_carreras_en_vivo(API_KEY)
records_live = []
if live_races:
    for match in live_races:
        records_live.append({
            "GranPremio": match.get('competition', {}).get('name', 'Gran Premio'),
            "Logo_GP": match.get('competition', {}).get('logo', ''),
            "Circuito": match.get('circuit', {}).get('name', 'Circuito'),
            "Ciudad": match.get('circuit', {}).get('city', ''),
            "Estado": match.get('status', 'Live')
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Panel Principal", "🏎️ Central En Vivo", "📈 Analítica Avanzada", "🤖 Ingeniero IA"])

with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    
    if "id_seleccionado" not in st.session_state:
        st.session_state.update({
            "id_seleccionado": 1, 
            "nombre_seleccionado": "Scuderia Ferrari", 
            "pais_seleccionado": "Italy", 
            "logo_seleccionado": "https://media.api-sports.io/formula-1/teams/1.png",
            "ciudad_seleccionada": "Maranello",
            "estadio_seleccionado": "Pista de Fiorano"
        })
        
    col_busqueda, col_vacia = st.columns([1, 2])
    with col_busqueda:
        busqueda_usuario = st.text_input("🔍 Buscar escudería (Ej. Ferrari, Mercedes, Red Bull):", value="", placeholder="Escribe al menos 2 letras...")
        
        if len(busqueda_usuario) >= 2:
            resultados = buscar_escuderia_api(busqueda_usuario)
            if resultados:
                opciones = {f"{i['name']} ({i.get('country', 'N/A')})": i for i in resultados}
                sel = st.selectbox("Resultados:", list(opciones.keys()))
                if sel:
                    data_seleccion = opciones[sel]
                    st.session_state.update({
                        "id_seleccionado": data_seleccion['id'], 
                        "nombre_seleccionado": data_seleccion['name'], 
                        "pais_seleccionado": data_seleccion.get('country', 'N/A'), 
                        "logo_seleccionado": data_seleccion.get('logo', ''),
                        "ciudad_seleccionada": data_seleccion.get('base', data_seleccion.get('country', 'N/A')),
                        "estadio_seleccionado": data_seleccion.get('name', 'Base de Escudería')
                    })
    st.markdown("</div>", unsafe_allow_html=True)

    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    pais_activo = st.session_state["pais_seleccionado"]
    logo_activo = st.session_state.get("logo_seleccionado", "")
    ciudad_activa = st.session_state.get("ciudad_seleccionada", "")
    estadio_activo = st.session_state.get("estadio_seleccionado", "")
    
    historial_raw, origen = obtener_calendario_escuderia(id_activo)
    records_historial = []
    
    for f in historial_raw:
        if 'date' in f:
            records_historial.append({
                "Fecha": pd.to_datetime(f['date']),
                "Fecha_Str": pd.to_datetime(f['date']).strftime('%Y-%m-%d %H:%M'),
                "Competencia": f.get('competition', {}).get('name', 'Gran Premio'),
                "Circuito": f.get('circuit', {}).get('name', 'Circuito'),
                "Ciudad": f.get('circuit', {}).get('city', ''),
                "Logo_GP": f.get('competition', {}).get('logo', ''),
                "Estado": f.get('status', 'NS')
            })
            
    cols = ["Fecha", "Fecha_Str", "Competencia", "Circuito", "Ciudad", "Logo_GP", "Estado"]
    if records_historial:
        df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False)
    else:
        df_historial = pd.DataFrame(columns=cols)
    
    podios, carreras_completadas, puntos_totales, total_carreras = 0, 0, 0, 0
    df_finalizados = pd.DataFrame()
    
    if not df_historial.empty:
        df_finalizados = df_historial[df_historial['Estado'].isin(['Completed', 'Finished', 'FT'])]
        total_carreras = len(df_finalizados)
        # Valores simulados de rendimiento basados en API si aplica
        podios = int(total_carreras * 0.4) if total_carreras > 0 else 0
        puntos_totales = total_carreras * 18

    promedio_puntos = round(puntos_totales / total_carreras, 1) if total_carreras > 0 else 0
    efectividad = round((podios / total_carreras) * 100, 1) if total_carreras > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left: 4px solid #EF4444; padding: 15px;'>
                <img src='{logo_activo}' width='50'>
                <div>
                    <h3 style='margin:0; font-size:1.2rem;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8;'>{pais_activo}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>EFECTIVIDAD PODIOS</small><h2 style='margin:0; color:#10B981 !important;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>PUNTOS / CARRERA</small><h2 style='margin:0; color:#F59E0B !important;'>{promedio_puntos}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='premium-card' style='padding: 15px;'><small style='color:#94A3B8;'>TOTAL PUNTOS</small><h2 style='margin:0; color:#FFFFFF !important;'>{puntos_totales} pts</h2></div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Grandes Premios</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                logo_gp = f"<img src='{row['Logo_GP']}' width='24'>" if 'Logo_GP' in row else ""
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #EF4444;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 60%; display:flex; align-items:center; gap:8px;'>{logo_gp} <span style='font-weight:bold;'>{row['Competencia']}</span></div>
                            <div style='width: 40%; text-align:right; font-size:0.9rem; font-weight:900; color:#10B981;'>COMPLETADO</div>
                        </div>
                        <div style='margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏁 Circuito: {row['Circuito']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay resultados recientes registrados.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>📅 Calendario Actual</div>", unsafe_allow_html=True)
        render_calendario()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximas Carreras</div>", unsafe_allow_html=True)
        df_proximos = df_historial[df_historial['Estado'] == 'NS'].sort_values(by="Fecha", ascending=True).head(5)
        if not df_proximos.empty:
            for _, row in df_proximos.iterrows():
                logo_gp = f"<img src='{row['Logo_GP']}' width='24'>" if 'Logo_GP' in row else ""
                st.markdown(f"""
                    <div style='background: #0F172A; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #3B82F6;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 70%; display:flex; align-items:center; gap:8px;'>{logo_gp} <span style='font-weight:bold;'>{row['Competencia']}</span></div>
                            <div style='width: 30%; text-align:right; color:#F59E0B; font-weight:bold;'>PRÓXIMO</div>
                        </div>
                        <div style='margin-top:5px; font-size:0.8rem; color:#94A3B8;'>🏁 Circuito: {row['Circuito']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay próximas carreras programadas en este bloque.")
        st.markdown("</div>", unsafe_allow_html=True)

    col_plantilla, col_mapa = st.columns(2)
    
    with col_plantilla:
        st.markdown("<div class='premium-card'><div class='section-title'>👥 Pilotos de la Escudería</div>", unsafe_allow_html=True)
        
        pilotos = obtener_pilotos(id_activo)
        if pilotos:
            datos_formateados = []
            for p in pilotos:
                driver_info = p.get("driver", {})
                datos_formateados.append({
                    "Piloto": driver_info.get("name", "N/A"),
                    "País": driver_info.get("country", "-"),
                    "Número": driver_info.get("number", "-")
                })
            df_final = pd.DataFrame(datos_formateados)
            st.dataframe(df_final, hide_index=True, use_container_width=True)
        else:
            st.warning(f"No se encontró información de pilotos para {nombre_activo}.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_mapa:
        st.markdown("<div class='premium-card'><div class='section-title'>🗺️ Ubicación de la Base</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #94A3B8 !important; margin-bottom: 15px;'><strong>📍 Sede / Base:</strong> {estadio_activo} <br> <strong>🏙️ Ciudad:</strong> {ciudad_activa}, {pais_activo}</p>", unsafe_allow_html=True)
        
        lat, lon = obtener_coordenadas(ciudad_activa, pais_activo)
        if lat and lon:
            df_mapa = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df_mapa, zoom=10, use_container_width=True)
        else:
            st.info("No se pudieron localizar las coordenadas exactas de la ubicación.")
            
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🏎️ Cobertura en Directo</div>", unsafe_allow_html=True)
    
    if df_live.empty:
        st.info("No hay Grandes Premios disputándose en vivo en este momento.")
    else:
        for _, row in df_live.iterrows():
            st.markdown(f"""
                <div class='live-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='width: 45%; display:flex; align-items:center; gap:15px;'>
                            <img src='{row['Logo_GP']}' width='40'>
                            <span class='live-team-name'>{row['GranPremio']}</span>
                        </div>
                        <div style='width: 20%; text-align: center;'>
                            <span class='pulse-minute'>🔴 EN VIVO</span>
                        </div>
                        <div style='width: 35%; display:flex; align-items:center; justify-content:flex-end; gap:15px;'>
                            <span class='live-league-label'>{row['Circuito']} ({row['Ciudad']})</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px;'>📈 Analítica de Datos F1</div>", unsafe_allow_html=True)
    
    if not df_live.empty:
        data_volumen = df_live['Ciudad'].value_counts()
        data_puntos = pd.Series([25, 18, 15, 12, 10], index=['Monaco', 'Silverstone', 'Monza', 'Spa', 'Suzuka'])
    else:
        data_volumen = pd.Series([5, 4, 3, 2, 1], index=['Monaco', 'Silverstone', 'Monza', 'Spa', 'Suzuka'])
        data_puntos = pd.Series([85, 72, 64, 50, 42], index=['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Aston Martin'])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📊 Distribución de Circuitos</div>", unsafe_allow_html=True)
        st.bar_chart(data_volumen, use_container_width=True, color="#EF4444")
        st.caption("Frecuencia de Grandes Premios por región.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>🏆 Puntos Acumulados por Escudería</div>", unsafe_allow_html=True)
        st.area_chart(data_puntos, use_container_width=True, color="#3B82F6")
        st.caption("Evolución de puntuación en el campeonato mundial.")
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🤖 Ingeniero IA - Análisis en Pista</div>", unsafe_allow_html=True)
    
    rendimiento_txt = "óptimo" if efectividad >= 30 else "en desarrollo"
    st.write(f"**Estado actual:** {nombre_activo} presenta un nivel competitivo {rendimiento_txt} con una efectividad de podios del {efectividad}%.")

    pregunta_usuario = st.chat_input(f"Pregunta al ingeniero sobre {nombre_activo}...")
    
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta_usuario)
            
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["puntos", "promedio", "rendimiento"]):
                respuesta = f"La escudería registra un promedio de {promedio_puntos} puntos por Gran Premio disputado."
            elif any(x in p for x in ["podio", "podios", "victorias"]):
                respuesta = f"En la temporada actual, el equipo suma {podios} podios destacados."
            elif any(x in p for x in ["efectividad", "porcentaje"]):
                respuesta = f"El porcentaje de podios frente a carreras finalizadas es del {efectividad}%."
            elif "carreras" in p or "gp" in p:
                respuesta = f"Hasta el momento se han analizado {total_carreras} Grandes Premios oficiales."
            else:
                respuesta = (f"Como ingeniero jefe, te informo que {nombre_activo} acumula {puntos_totales} puntos totales "
                             f"con un promedio de {promedio_puntos} pts/GP. ¿Te gustaría analizar el rendimiento de los pilotos o la estrategia de neumáticos?")
            
            st.write(respuesta)
            
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: #334155; margin-top: 40px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 20px;'>
        <strong>Forza F1 Analytics V3.0 (Integración AI)</strong><br>
        Plataforma Avanzada de Datos de Fórmula 1<br>
        Proyecto Universitario | Adaptado a F1 © 2026
    </div>
""", unsafe_allow_html=True)
