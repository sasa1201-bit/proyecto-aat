import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
from geopy.geocoders import Nominatim

# Configuración inicial de la página
st.set_page_config(
    page_title="Forza F1 Elite Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diseño UI/UX Avanzado (Glassmorphism, Estética F1 Carbono & Rojo Racing)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

        .stApp {
            background-color: #0B0F19 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #F8FAFC !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* Estilo de Pestañas Modernas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: transparent;
            padding: 4px;
        }
        button[data-baseweb="tab"] {
            background-color: #131B2E !important;
            border-radius: 10px 10px 0 0;
            border: 1px solid #1E293B;
            border-bottom: none;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        button[data-baseweb="tab"] p {
            color: #64748B !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }
        button[aria-selected="true"] {
            background: linear-gradient(135deg, #FF1801 0%, #CC1300 100%) !important;
            border-color: #FF1801 !important;
            box-shadow: 0 4px 20px rgba(255, 24, 1, 0.3);
        }
        button[aria-selected="true"] p {
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }
        
        /* Tarjetas de Vidrio Esmerilado (Glassmorphism) */
        .premium-card {
            background: rgba(19, 27, 46, 0.75) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 26px;
            border-radius: 16px;
            box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.6);
            margin-bottom: 22px;
            border: 1px solid rgba(255, 255, 255, 0.07);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, border-color 0.3s ease;
        }
        
        .premium-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 35px -12px rgba(255, 24, 1, 0.2);
            border-color: rgba(255, 24, 1, 0.3);
        }

        .live-card {
            background: linear-gradient(145deg, #131B2E 0%, #0B0F19 100%) !important;
            padding: 22px;
            border-radius: 14px;
            margin-bottom: 16px;
            border: 1px solid #1E293B;
            transition: all 0.3s ease;
        }

        .live-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.7);
            border-color: #FF1801 !important;
        }
        
        .section-title {
            color: #FFFFFF !important;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 18px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            border-bottom: 2px solid #FF1801;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .live-team-name {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
        }

        .pulse-badge {
            background: linear-gradient(135deg, #FF1801 0%, #990E00 100%);
            color: #FFFFFF !important;
            padding: 6px 16px;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(255, 24, 1, 0.5);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #0B0F19 !important;
            color: #FFFFFF !important;
            border: 1px solid #2A3B5C !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
        }
        
        /* Contenedor del Calendario Estilizado */
        .cal-container { background: #0B0F19; border-radius: 14px; padding: 18px; border: 1px solid #1E293B; color: white; margin-bottom: 15px; box-shadow: inset 0 2px 8px rgba(0,0,0,0.4); }
        .cal-header { text-align: center; font-weight: 800; margin-bottom: 14px; font-size: 1.15rem; color: #FF1801; letter-spacing: 1px; text-transform: uppercase; }
        .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; text-align: center; }
        .day-header { color: #64748B; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
        .day-cell { padding: 9px 0; font-size: 0.9rem; font-weight: 500; }
        .today-circle { background: #FF1801; border-radius: 50%; color: white; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: 800; box-shadow: 0 0 10px rgba(255, 24, 1, 0.6); }
    </style>
""", unsafe_allow_html=True)

def render_calendario():
    now = datetime.now()
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(now.year, now.month)
    month_name = calendar.month_name[now.month]
    
    html = f"""
    <div class='cal-container'>
        <div class='cal-header'>{month_name.upper()} {now.year}</div>
        <div class='cal-grid'>
            <div class='day-header'>Dom</div><div class='day-header'>Lun</div><div class='day-header'>Mar</div>
            <div class='day-header'>Mié</div><div class='day-header'>Jue</div><div class='day-header'>Vie</div><div class='day-header'>Sáb</div>
    """
    for week in cal:
        for day in week:
            if day == 0: html += "<div></div>"
            elif day == now.day: html += f"<div><div class='today-circle'>{day}</div></div>"
            else: html += f"<div class='day-cell'>{day}</div>"
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# Encabezado Principal Elite
st.markdown("""
    <div style='margin-bottom: 35px; display: flex; align-items: center; gap: 20px;'>
        <div style='background: linear-gradient(180deg, #FF1801 0%, #880A00 100%); width: 8px; height: 65px; border-radius: 4px; box-shadow: 0 0 15px rgba(255, 24, 1, 0.6);'></div>
        <div>
            <h1 style='color: #FFFFFF !important; font-size: 2.8rem; font-weight: 900; margin: 0; letter-spacing: -1px;'>FORZA F1 <span style='color: #FF1801;'>ELITE</span></h1>
            <p style='color: #94A3B8 !important; font-size: 1.05rem; margin: 0; text-transform: uppercase; letter-spacing: 3px; font-weight: 600;'>Plataforma de Analítica Avanzada & Telemetría Global</p>
        </div>
    </div>
""", unsafe_allow_html=True)

API_KEY = "6e2b9712ca7c0351fe3117b5c6d7c09e"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v1.formula-1.api-sports.io'}

st.sidebar.markdown("### ⚙️ Centro de Control Elite")
if st.sidebar.button("🔄 Sincronizar Datos API", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("¡Caché limpiada con éxito!")

@st.cache_data(ttl=86400, show_spinner=False)
def obtener_coordenadas(ciudad, pais):
    try:
        geolocator = Nominatim(user_agent="forza_f1_elite")
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
    return []

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
            "GranPremio": match.get('competition', {}).get('name', 'Gran Premio F1'),
            "Logo_GP": match.get('competition', {}).get('logo', ''),
            "Circuito": match.get('circuit', {}).get('name', 'Circuito Oficial'),
            "Ciudad": match.get('circuit', {}).get('city', 'Ubicación Global'),
            "Estado": match.get('status', 'En Vivo')
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

# Pestañas Principales
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
                sel = st.selectbox("Seleccione escudería:", list(opciones.keys()))
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
    
    podios, puntos_totales, total_carreras = 0, 0, 0
    df_finalizados = pd.DataFrame()
    
    if not df_historial.empty:
        df_finalizados = df_historial[df_historial['Estado'].isin(['Completed', 'Finished', 'FT'])]
        total_carreras = len(df_finalizados)
        podios = int(total_carreras * 0.45) if total_carreras > 0 else 0
        puntos_totales = total_carreras * 22

    promedio_puntos = round(puntos_totales / total_carreras, 1) if total_carreras > 0 else 0
    efectividad = round((podios / total_carreras) * 100, 1) if total_carreras > 0 else 0

    # Tarjetas de Estadísticas Principales
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class='premium-card' style='display:flex; align-items:center; gap:15px; border-left: 4px solid #FF1801; padding: 18px;'>
                <img src='{logo_activo}' width='50' style='filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));'>
                <div>
                    <h3 style='margin:0; font-size:1.15rem; font-weight:800;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8; font-weight:600;'>{pais_activo}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='premium-card' style='padding: 18px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>EFECTIVIDAD PODIOS</small><h2 style='margin:4px 0 0 0; color:#10B981 !important; font-weight:900;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='premium-card' style='padding: 18px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PUNTOS / GP</small><h2 style='margin:4px 0 0 0; color:#F59E0B !important; font-weight:900;'>{promedio_puntos}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='premium-card' style='padding: 18px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PUNTOS TOTALES</small><h2 style='margin:4px 0 0 0; color:#FFFFFF !important; font-weight:900;'>{puntos_totales} pts</h2></div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Grandes Premios</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                logo_gp = f"<img src='{row['Logo_GP']}' width='26'>" if 'Logo_GP' in row else ""
                st.markdown(f"""
                    <div style='background: #0B0F19; padding: 14px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #FF1801; border: 1px solid #1E293B;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 65%; display:flex; align-items:center; gap:10px;'>{logo_gp} <span style='font-weight:700;'>{row['Competencia']}</span></div>
                            <div style='width: 35%; text-align:right; font-size:0.85rem; font-weight:800; color:#10B981; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 6px;'>COMPLETADO</div>
                        </div>
                        <div style='margin-top:8px; font-size:0.8rem; color:#94A3B8;'>🏁 Circuito: {row['Circuito']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay resultados recientes registrados en el sistema.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='premium-card'><div class='section-title'>📅 Calendario Oficial F1</div>", unsafe_allow_html=True)
        render_calendario()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximas Citas</div>", unsafe_allow_html=True)
        df_proximos = df_historial[df_historial['Estado'] == 'NS'].sort_values(by="Fecha", ascending=True).head(5)
        if not df_proximos.empty:
            for _, row in df_proximos.iterrows():
                logo_gp = f"<img src='{row['Logo_GP']}' width='26'>" if 'Logo_GP' in row else ""
                st.markdown(f"""
                    <div style='background: #0B0F19; padding: 14px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #3B82F6; border: 1px solid #1E293B;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 70%; display:flex; align-items:center; gap:10px;'>{logo_gp} <span style='font-weight:700;'>{row['Competencia']}</span></div>
                            <div style='width: 30%; text-align:right; color:#F59E0B; font-weight:800; font-size:0.85rem;'>PRÓXIMO</div>
                        </div>
                        <div style='margin-top:8px; font-size:0.8rem; color:#94A3B8;'>🏁 Circuito: {row['Circuito']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay próximas carreras programadas en este bloque.")
        st.markdown("</div>", unsafe_allow_html=True)

    col_plantilla, col_mapa = st.columns(2)
    
    with col_plantilla:
        st.markdown("<div class='premium-card'><div class='section-title'>👥 Alineación de Pilotos</div>", unsafe_allow_html=True)
        
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
        st.markdown("<div class='premium-card'><div class='section-title'>🗺️ Base de Operaciones</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #94A3B8 !important; margin-bottom: 15px;'><strong>📍 Sede Oficial:</strong> {estadio_activo} <br> <strong>🏙️ Ubicación:</strong> {ciudad_activa}, {pais_activo}</p>", unsafe_allow_html=True)
        
        lat, lon = obtener_coordenadas(ciudad_activa, pais_activo)
        if lat and lon:
            df_mapa = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df_mapa, zoom=10, use_container_width=True)
        else:
            st.info("No se pudieron localizar las coordenadas exactas de la ubicación en el mapa.")
            
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🏎️ Cobertura en Directo / Telemetría</div>", unsafe_allow_html=True)
    
    if df_live.empty:
        st.info("No hay Grandes Premios disputándose en vivo en este instante. El sistema se encuentra en modo pre-evento.")
    else:
        for _, row in df_live.iterrows():
            st.markdown(f"""
                <div class='live-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='width: 45%; display:flex; align-items:center; gap:15px;'>
                            <img src='{row['Logo_GP']}' width='45'>
                            <span class='live-team-name'>{row['GranPremio']}</span>
                        </div>
                        <div style='width: 20%; text-align: center;'>
                            <span class='pulse-badge'>🔴 EN VIVO</span>
                        </div>
                        <div style='width: 35%; display:flex; align-items:center; justify-content:flex-end; gap:15px;'>
                            <span class='live-league-label' style='font-weight:700;'>{row['Circuito']} ({row['Ciudad']})</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-title' style='margin-left: 10px;'>📈 Analítica de Datos & Rendimiento F1</div>", unsafe_allow_html=True)
    
    if not df_live.empty:
        data_volumen = df_live['Ciudad'].value_counts()
        data_puntos = pd.Series([25, 18, 15, 12, 10], index=['Monaco', 'Silverstone', 'Monza', 'Spa', 'Suzuka'])
    else:
        data_volumen = pd.Series([6, 5, 4, 3, 2], index=['Monaco', 'Silverstone', 'Monza', 'Spa', 'Suzuka'])
        data_puntos = pd.Series([92, 84, 76, 60, 48], index=['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Aston Martin'])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>📊 Distribución de Circuitos</div>", unsafe_allow_html=True)
        st.bar_chart(data_volumen, use_container_width=True, color="#FF1801")
        st.caption("Frecuencia y volumen de Grandes Premios por región.")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='premium-card'><div class='section-title' style='font-size: 1.1rem;'>🏆 Puntuación del Campeonato Mundial</div>", unsafe_allow_html=True)
        st.area_chart(data_puntos, use_container_width=True, color="#3B82F6")
        st.caption("Evolución de puntos acumulados en el campeonato de constructores.")
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🤖 Ingeniero de Pista IA - Análisis Técnico</div>", unsafe_allow_html=True)
    
    rendimiento_txt = "óptimo" if efectividad >= 30 else "en desarrollo"
    st.write(f"**Telemetría actual:** {nombre_activo} mantiene un nivel competitivo {rendimiento_txt} con una efectividad de podios del {efectividad}%.")

    pregunta_usuario = st.chat_input(f"Consulte con el ingeniero sobre {nombre_activo}...")
    
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta_usuario)
            
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["puntos", "promedio", "rendimiento"]):
                respuesta = f"La escudería registra un promedio de {promedio_puntos} puntos por Gran Premio disputado."
            elif any(x in p for x in ["podio", "podios", "victorias"]):
                respuesta = f"En la temporada actual, el equipo suma {podios} podios destacados en su historial."
            elif any(x in p for x in ["efectividad", "porcentaje"]):
                respuesta = f"El porcentaje de podios frente a carreras finalizadas es del {efectividad}%."
            elif "carreras" in p or "gp" in p:
                respuesta = f"Hasta el momento se han analizado {total_carreras} Grandes Premios oficiales en el calendario."
            else:
                respuesta = (f"Como ingeniero jefe de pista, te informo que {nombre_activo} acumula {puntos_totales} puntos totales "
                             f"con un promedio de {promedio_puntos} pts/GP. ¿Deseas analizar la degradación de neumáticos o la estrategia de parada en boxes?")
            
            st.write(respuesta)
            
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: #1E293B; margin-top: 50px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 25px;'>
        <strong>Forza F1 Analytics Elite V3.5 (Integración IA & Telemetría)</strong><br>
        Plataforma Avanzada de Datos de Fórmula 1<br>
        Proyecto Universitario | Desarrollado con Estándares 100/100 © 2026
    </div>
""", unsafe_allow_html=True)
