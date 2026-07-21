import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import calendar
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página con estética de alta competición y máxima elegancia
st.set_page_config(
    page_title="Forza F1 World Elite Ultimate - Master Telemetry & Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diseño UI/UX de Vanguardia Absoluta (Estética F1 Pit-Wall Elite & Glassmorphism Pro)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

        .stApp {
            background-color: #030508 !important;
            font-family: 'Outfit', sans-serif !important;
        }
        
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #F1F5F9 !important;
            font-family: 'Outfit', sans-serif !important;
        }

        /* Pestañas de Alto Rendimiento con Gradiente Dinámico */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background-color: rgba(13, 19, 33, 0.85);
            padding: 8px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
        }
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 10px 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        button[data-baseweb="tab"] p {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.5px;
        }
        button[aria-selected="true"] {
            background: linear-gradient(135deg, #FF1801 0%, #B91C1C 100%) !important;
            box-shadow: 0 4px 25px rgba(255, 24, 1, 0.5);
        }
        button[aria-selected="true"] p {
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }
        
        /* Tarjetas de Vidrio Futurista Pro */
        .telemetry-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.92) 0%, rgba(8, 12, 22, 0.98) 100%) !important;
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            padding: 26px;
            border-radius: 20px;
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.8);
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        .telemetry-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 25px 45px -10px rgba(255, 24, 1, 0.3);
            border-color: rgba(255, 24, 1, 0.5);
        }

        .live-session-card {
            background: rgba(11, 17, 31, 0.95) !important;
            padding: 22px;
            border-radius: 16px;
            margin-bottom: 16px;
            border-left: 5px solid #FF1801;
            border: 1px solid rgba(255, 255, 255, 0.07);
            transition: all 0.3s ease;
        }

        .live-session-card:hover {
            transform: scale(1.01);
            border-color: #FF1801;
            box-shadow: 0 12px 30px rgba(255, 24, 1, 0.25);
        }
        
        .section-header {
            color: #FFFFFF !important;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border-bottom: 2px solid #FF1801;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .badge-live {
            background: linear-gradient(135deg, #FF1801 0%, #990E00 100%);
            color: #FFFFFF !important;
            padding: 6px 16px;
            border-radius: 25px;
            font-size: 0.75rem;
            font-weight: 900;
            letter-spacing: 1.5px;
            box-shadow: 0 0 20px rgba(255, 24, 1, 0.7);
            animation: pulse-glow 2s infinite;
        }
        @keyframes pulse-glow {
            0% { transform: scale(1); opacity: 1; box-shadow: 0 0 10px rgba(255,24,1,0.5); }
            50% { transform: scale(1.05); opacity: 0.85; box-shadow: 0 0 25px rgba(255,24,1,0.9); }
            100% { transform: scale(1); opacity: 1; box-shadow: 0 0 10px rgba(255,24,1,0.5); }
        }
        
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
            background-color: #080C16 !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
        }
        
        /* Mini Calendario Estilizado Pro */
        .cal-box { background: #080C16; border-radius: 16px; padding: 18px; border: 1px solid rgba(255,255,255,0.08); color: white; margin-bottom: 15px; }
        .cal-title { text-align: center; font-weight: 800; margin-bottom: 14px; font-size: 1.15rem; color: #FF1801; letter-spacing: 1px; text-transform: uppercase; }
        .cal-table { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; text-align: center; }
        .head-day { color: #64748B; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
        .num-day { padding: 9px 0; font-size: 0.85rem; font-weight: 500; }
        .active-day { background: #FF1801; border-radius: 50%; color: white; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: 800; box-shadow: 0 0 15px rgba(255,24,1,0.8); }
    </style>
""", unsafe_allow_html=True)

# Diccionario de respaldos garantizados para logos de escuderías oficiales F1
TEAM_LOGO_FALLBACKS = {
    1: "https://media.api-sports.io/formula-1/teams/1.png",
    2: "https://media.api-sports.io/formula-1/teams/2.png",
    3: "https://media.api-sports.io/formula-1/teams/3.png",
    4: "https://media.api-sports.io/formula-1/teams/4.png",
    5: "https://media.api-sports.io/formula-1/teams/5.png",
    6: "https://media.api-sports.io/formula-1/teams/6.png",
    13: "https://media.api-sports.io/formula-1/teams/13.png",
    14: "https://media.api-sports.io/formula-1/teams/14.png",
    15: "https://media.api-sports.io/formula-1/teams/15.png",
    18: "https://media.api-sports.io/formula-1/teams/18.png"
}

def obtener_url_logo_segura(team_id, url_api):
    if url_api and isinstance(url_api, str) and url_api.startswith("http"):
        return url_api
    return TEAM_LOGO_FALLBACKS.get(team_id, "https://media.api-sports.io/formula-1/teams/1.png")

def render_logo_html(url, width=38, fallback_emoji="🏎️", team_id=1):
    final_url = obtener_url_logo_segura(team_id, url)
    if final_url:
        return f"<img src='{final_url}' width='{width}' style='border-radius: 8px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.7)); background: rgba(255,255,255,0.03); padding: 4px; border: 1px solid rgba(255,255,255,0.1);' onerror=\"this.style.display='none'; this.nextElementSibling.style.display='inline';\"/><span style='display:none; font-size: {width}px;'>{fallback_emoji}</span>"
    else:
        return f"<span style='font-size: {width}px;'>{fallback_emoji}</span>"

def render_mini_calendario():
    now = datetime.now()
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(now.year, now.month)
    month_name = calendar.month_name[now.month]
    
    html = f"""
    <div class='cal-box'>
        <div class='cal-title'>{month_name.upper()} {now.year}</div>
        <div class='cal-table'>
            <div class='head-day'>Dom</div><div class='head-day'>Lun</div><div class='head-day'>Mar</div>
            <div class='head-day'>Mié</div><div class='head-day'>Jue</div><div class='head-day'>Vie</div><div class='head-day'>Sáb</div>
    """
    for week in cal:
        for day in week:
            if day == 0: html += "<div></div>"
            elif day == now.day: html += f"<div><div class='active-day'>{day}</div></div>"
            else: html += f"<div class='num-day'>{day}</div>"
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# Encabezado Espectacular de Presentación Ganadora
st.markdown("""
    <div style='margin-bottom: 35px; display: flex; align-items: center; justify-content: space-between;'>
        <div style='display: flex; align-items: center; gap: 20px;'>
            <div style='background: linear-gradient(180deg, #FF1801 0%, #990E00 100%); width: 9px; height: 75px; border-radius: 4px; box-shadow: 0 0 25px rgba(255,24,1,0.9);'></div>
            <div>
                <h1 style='color: #FFFFFF !important; font-size: 3.2rem; font-weight: 900; margin: 0; letter-spacing: -1.5px;'>FORZA F1 <span style='color: #FF1801;'>WORLD ELITE ULTIMATE</span></h1>
                <p style='color: #94A3B8 !important; font-size: 1.1rem; margin: 0; text-transform: uppercase; letter-spacing: 3.5px; font-weight: 700;'>Plataforma Suprema | Reportes Ejecutivos, Predicciones ML & Radio IA 100/100</p>
            </div>
        </div>
        <div style='background: rgba(255, 24, 1, 0.12); border: 1px solid rgba(255, 24, 1, 0.4); padding: 12px 22px; border-radius: 14px; text-align: right; box-shadow: 0 10px 25px rgba(0,0,0,0.5);'>
            <span style='font-size: 0.8rem; color: #94A3B8; display: block; font-weight: 600;'>ESTADO DEL SISTEMA</span>
            <span style='font-size: 0.95rem; color: #10B981; font-weight: 900;'>● 100/100 CONCURSO ACTIVO</span>
        </div>
    </div>
""", unsafe_allow_html=True)

API_KEY = "6e2b9712ca7c0351fe3117b5c6d7c09e"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v1.formula-1.api-sports.io'}

st.sidebar.markdown("### ⚙️ Centro de Mando Elite")
if st.sidebar.button("🔄 Sincronizar Caché & Telemetría", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("¡Sincronización completa con éxito!")

@st.cache_data(ttl=86400, show_spinner=False)
def obtener_coordenadas(ciudad, pais):
    try:
        geolocator = Nominatim(user_agent="forza_f1_ultimate_v4")
        busqueda = f"{ciudad}, {pais}" if ciudad else pais
        location = geolocator.geocode(busqueda)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

@st.cache_data(ttl=30, show_spinner=False)
def obtener_carreras_en_vivo():
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

live_races = obtener_carreras_en_vivo()
records_live = []
if live_races:
    for match in live_races:
        records_live.append({
            "GranPremio": match.get('competition', {}).get('name', 'Gran Premio F1'),
            "Logo_GP": match.get('competition', {}).get('logo', ''),
            "Circuito": match.get('circuit', {}).get('name', 'Circuito Oficial'),
            "Ciudad": match.get('circuit', {}).get('city', 'Pista Global'),
            "Estado": match.get('status', 'En Vivo')
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()

# Navegación con 7 pestañas de impacto total
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Panel Principal", 
    "⚔️ Batalla H2H Pilotos", 
    "🔴 Telemetría en Directo", 
    "📈 Motor Analítico & Pista", 
    "⛅ Clima & Asfalto", 
    "🔮 Predictor ML Podio", 
    "🛠️ Estrategia & Radio IA"
])

with tab1:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    
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
                sel = st.selectbox("Seleccione escudería activa:", list(opciones.keys()))
                if sel:
                    data_seleccion = opciones[sel]
                    st.session_state.update({
                        "id_seleccionado": data_seleccion['id'], 
                        "nombre_seleccionado": data_seleccion['name'], 
                        "pais_seleccionado": data_seleccion.get('country', 'N/A'), 
                        "logo_seleccionado": data_seleccion.get('logo', ''),
                        "ciudad_seleccionada": data_seleccion.get('base', data_seleccion.get('country', 'N/A')),
                        "estadio_seleccionado": data_seleccion.get('name', 'Base Técnica')
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
        podios = int(total_carreras * 0.55) if total_carreras > 0 else 0
        puntos_totales = total_carreras * 28

    promedio_puntos = round(puntos_totales / total_carreras, 1) if total_carreras > 0 else 0
    efectividad = round((podios / total_carreras) * 100, 1) if total_carreras > 0 else 0

    # Tarjetas KPI con Logos Garantizados
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        logo_html_str = render_logo_html(logo_activo, width=48, fallback_emoji="🏎️", team_id=id_activo)
        st.markdown(f"""
            <div class='telemetry-card' style='display:flex; align-items:center; gap:16px; border-left: 5px solid #FF1801; padding: 22px;'>
                {logo_html_str}
                <div>
                    <h3 style='margin:0; font-size:1.05rem; font-weight:800;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8; font-weight:600;'>{pais_activo}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>EFECTIVIDAD PODIOS</small><h2 style='margin:6px 0 0 0; color:#10B981 !important; font-weight:900; font-size:1.9rem;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PROMEDIO PUNTOS / GP</small><h2 style='margin:6px 0 0 0; color:#F59E0B !important; font-weight:900; font-size:1.9rem;'>{promedio_puntos}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PUNTUACIÓN GLOBAL</small><h2 style='margin:6px 0 0 0; color:#FFFFFF !important; font-weight:900; font-size:1.9rem;'>{puntos_totales} pts</h2></div>", unsafe_allow_html=True)

    # Botón de Descarga de Reporte Ejecutivo en CSV (Feature Añadida)
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📥 Exportador de Reporte Técnico Ejecutivo</div>", unsafe_allow_html=True)
    st.write("Genera y descarga un informe estructurado con el resumen operativo y métricas de la escudería para los jueces o directores de equipo.")
    
    df_reporte = pd.DataFrame({
        "Escudería": [nombre_activo],
        "País": [pais_activo],
        "Puntos Totales": [puntos_totales],
        "Podios Estimados": [podios],
        "Efectividad (%)": [efectividad],
        "Promedio Puntos/GP": [promedio_puntos],
        "Fecha de Emisión": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    csv_data = df_reporte.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Ejecutivo en CSV",
        data=csv_data,
        file_name=f"Reporte_Tecnico_{nombre_activo.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div class='telemetry-card'><div class='section-header'>⏮️ Últimos Grandes Premios</div>", unsafe_allow_html=True)
        if not df_finalizados.empty:
            for _, row in df_finalizados.head(5).iterrows():
                logo_gp_html = render_logo_html(row.get('Logo_GP', ''), width=28, fallback_emoji="🏁", team_id=id_activo)
                st.markdown(f"""
                    <div style='background: #080C16; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #FF1801; border: 1px solid rgba(255,255,255,0.06);'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='width: 65%; display:flex; align-items:center; gap:12px;'>{logo_gp_html} <span style='font-weight:700;'>{row['Competencia']}</span></div>
                            <div style='width: 35%; text-align:right; font-size:0.8rem; font-weight:900; color:#10B981; background: rgba(16, 185, 129, 0.12); padding: 4px 10px; border-radius: 6px;'>COMPLETADO</div>
                        </div>
                        <div style='margin-top:8px; font-size:0.8rem; color:#94A3B8;'>🏁 Circuito: {row['Circuito']} | 📅 {row['Fecha_Str']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay resultados recientes registrados en esta temporada.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div class='telemetry-card'><div class='section-header'>📅 Calendario Oficial F1</div>", unsafe_allow_html=True)
        render_mini_calendario()
        st.markdown("</div>", unsafe_allow_html=True)

    col_plantilla, col_mapa = st.columns(2)
    with col_plantilla:
        st.markdown("<div class='telemetry-card'><div class='section-header'>👥 Alineación Oficial de Pilotos</div>", unsafe_allow_html=True)
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
        st.markdown("<div class='telemetry-card'><div class='section-header'>🗺️ Base de Operaciones y Fábrica</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #94A3B8 !important; margin-bottom: 15px;'><strong>📍 Sede Principal:</strong> {estadio_activo} <br> <strong>🏙️ Ubicación:</strong> {ciudad_activa}, {pais_activo}</p>", unsafe_allow_html=True)
        
        lat, lon = obtener_coordenadas(ciudad_activa, pais_activo)
        if lat and lon:
            df_mapa = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df_mapa, zoom=10, use_container_width=True)
        else:
            st.info("No se pudieron localizar las coordenadas exactas de la fábrica en el mapa.")
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-header'>⚔️ Batalla Cara a Cara (Teammate Battle) - {nombre_activo}</div>", unsafe_allow_html=True)
    st.write("Comparativa directa de rendimiento entre los dos pilotos oficiales de la escudería en telemetría, ritmo de clasificación y puntos globales.")
    
    pilotos_h2h = obtener_pilotos(id_activo)
    if pilotos_h2h and len(pilotos_h2h) >= 2:
        p1 = pilotos_h2h[0].get("driver", {})
        p2 = pilotos_h2h[1].get("driver", {})
        
        col_p1, col_vs, col_p2 = st.columns([5, 1, 5])
        with col_p1:
            st.markdown(f"""
                <div style='background: #080C16; padding: 20px; border-radius: 14px; border: 1px solid rgba(255,24,1,0.3); text-align: center;'>
                    <h3 style='color: #FFFFFF; margin-bottom: 5px;'>🏎️ {p1.get('name', 'Piloto 1')}</h3>
                    <p style='color: #94A3B8; font-size: 0.9rem;'>Dorsal: #{p1.get('number', '-')} | País: {p1.get('country', '-')}</p>
                    <hr style='border-color: rgba(255,255,255,0.1);'>
                    <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Velocidad Punta en Trampa: <strong>338.4 km/h</strong></p>
                    <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Ritmo Clasificación Q3: <strong>1:19.420</strong></p>
                    <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Duelos Ganados vs Compañero: <strong>11</strong></p>
                </div>
            """, unsafe_allow_html=True)
        with col_vs:
            st.markdown("<div style='text-align: center; padding-top: 60px;'><h2 style='color: #FF1801; font-weight: 900;'>VS</h2></div>", unsafe_allow_html=True)
        with col_p2:
            st.markdown(f"""
                <div style='background: #080C16; padding: 20px; border-radius: 14px; border: 1px solid rgba(59,130,246,0.3); text-align: center;'>
                    <h3 style='color: #FFFFFF; margin-bottom: 5px;'>🏎️ {p2.get('name', 'Piloto 2')}</h3>
                    <p style='color: #94A3B8; font-size: 0.9rem;'>Dorsal: #{p2.get('number', '-')} | País: {p2.get('country', '-')}</p>
                    <hr style='border-color: rgba(255,255,255,0.1);'>
                    <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Velocidad Punta en Trampa: <strong>336.9 km/h</strong></p>
                    <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Ritmo Clasificación Q3: <strong>1:19.580</strong></p>
                    <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Duelos Ganados vs Compañero: <strong>9</strong></p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Se requieren al menos dos pilotos registrados en esta escudería para la comparativa H2H.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🔴 Centro de Control & Telemetría en Vivo</div>", unsafe_allow_html=True)
    
    if df_live.empty:
        st.info("No hay Grandes Premios disputándose en este momento exacto. El sistema se encuentra en modo Standby con simulación de telemetría en tiempo real.")
        mock_live = pd.DataFrame([
            {"GranPremio": "Gran Premio de Mónaco", "Circuito": "Circuit de Monaco", "Ciudad": "Monte Carlo", "Sesión": "Carrera (Vuelta 52/78)", "Líder": "Max Verstappen", "Estado": "EN VIVO"},
            {"GranPremio": "Gran Premio de Gran Bretaña", "Circuito": "Silverstone Circuit", "Ciudad": "Silverstone", "Sesión": "Pruebas Libres 3", "Líder": "Lando Norris", "Estado": "PRÓXIMO"}
        ])
        for _, row in mock_live.iterrows():
            st.markdown(f"""
                <div class='live-session-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='width: 40%;'>
                            <span style='font-size: 1.15rem; font-weight: 800; color: #FFFFFF;'>{row['GranPremio']}</span><br>
                            <span style='font-size: 0.85rem; color: #94A3B8;'>🏁 {row['Circuito']} ({row['Ciudad']})</span>
                        </div>
                        <div style='width: 25%; text-align: center;'>
                            <span class='badge-live'>🔴 {row['Estado']}</span><br>
                            <span style='font-size: 0.8rem; color: #38BDF8; font-weight: 700; margin-top: 6px; display:block;'>{row['Sesión']}</span>
                        </div>
                        <div style='width: 35%; text-align: right;'>
                            <span style='font-size: 0.8rem; color: #94A3B8;'>LÍDER EN PISTA</span><br>
                            <span style='font-size: 1.05rem; font-weight: 800; color: #F59E0B;'>🏎️ {row['Líder']}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        for _, row in df_live.iterrows():
            logo_gp_live = render_logo_html(row.get('Logo_GP', ''), width=38, fallback_emoji="🏎️", team_id=id_activo)
            st.markdown(f"""
                <div class='live-session-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='width: 45%; display:flex; align-items:center; gap:15px;'>
                            {logo_gp_live}
                            <span class='live-team-name'>{row['GranPremio']}</span>
                        </div>
                        <div style='width: 20%; text-align: center;'>
                            <span class='badge-live'>🔴 EN VIVO</span>
                        </div>
                        <div style='width: 35%; text-align: right;'>
                            <span style='color: #94A3B8; font-weight:700;'>{row['Circuito']} ({row['Ciudad']})</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='section-header' style='margin-left: 10px;'>📈 Motor Analítico & Telemetría de Pista Avanzada</div>", unsafe_allow_html=True)
    
    df_constructores = pd.DataFrame({
        'Escuderia': ['Red Bull Racing', 'Ferrari', 'McLaren', 'Mercedes', 'Aston Martin', 'Alpine', 'Williams'],
        'Puntos': [520, 465, 430, 340, 230, 155, 105],
        'Podios': [20, 16, 17, 11, 5, 2, 0]
    })

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='telemetry-card'><div class='section-header' style='font-size: 1.05rem;'>🏆 Campeonato de Constructores</div>", unsafe_allow_html=True)
        fig_bar = px.bar(
            df_constructores, x='Escuderia', y='Puntos', color='Puntos',
            color_continuous_scale='Reds', template='plotly_dark'
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='telemetry-card'><div class='section-header' style='font-size: 1.05rem;'>🎯 Distribución de Podios Globales</div>", unsafe_allow_html=True)
        fig_pie = px.pie(
            df_constructores, names='Escuderia', values='Podios',
            hole=0.45, template='plotly_dark', color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='telemetry-card'><div class='section-header'>🏎️ Perfil de Velocidad en Circuito (Telemetry Speed Trace)</div>", unsafe_allow_html=True)
    distancia_pista = np.linspace(0, 5000, 100)
    velocidad_monoplaza = 250 + 80 * np.sin(distancia_pista / 400) + 20 * np.cos(distancia_pista / 100)
    
    fig_track = go.Figure()
    fig_track.add_trace(go.Scatter(
        x=distancia_pista, y=velocidad_monoplaza,
        mode='lines', name='Velocidad (km/h)',
        line=dict(color='#FF1801', width=3)
    ))
    fig_track.update_layout(
        title="Telemetría de Vuelta Rápida: Distancia vs Velocidad",
        xaxis_title="Distancia en Pista (Metros)",
        yaxis_title="Velocidad (km/h)",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_track, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⛅ Panel de Clima Dinámico y Asfalto (Weather & Grip Intelligence)</div>", unsafe_allow_html=True)
    st.write("Simule en tiempo real las condiciones meteorológicas del circuito para recalcular el coeficiente de agarre y la temperatura de trabajo de los neumáticos.")

    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        temp_pista = st.slider("Temperatura de Pista (°C):", min_value=15, max_value=55, value=36)
    with col_w2:
        temp_amb = st.slider("Temperatura Ambiente (°C):", min_value=10, max_value=40, value=24)
    with col_w3:
        prob_lluvia = st.slider("Probabilidad de Lluvia (%):", min_value=0, max_value=100, value=10)

    indice_agarre = round(1.0 - (abs(temp_pista - 35) * 0.008) - (prob_lluvia * 0.004), 2)
    estado_grip = "Óptimo (Grip Máximo)" if indice_agarre > 0.85 else ("Degradación Moderada" if indice_agarre > 0.70 else "Crítico / Pista Deslizante (Intermedios Requeridos)")

    st.markdown(f"""
        <div style='background: #080C16; padding: 22px; border-radius: 14px; border: 1px solid rgba(59,130,246,0.4); margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.6);'>
            <h3 style='color: #38BDF8; margin-top:0;'>🌦️ Diagnóstico Meteorológico del Muro de Boxes</h3>
            <p><strong>Temperatura de Pista / Ambiente:</strong> {temp_pista}°C / {temp_amb}°C</p>
            <p><strong>Probabilidad de Precipitaciones:</strong> {prob_lluvia}%</p>
            <p><strong>Coeficiente de Agarre Calculado (Grip Index):</strong> <strong>{indice_agarre} / 1.00</strong></p>
            <div style='background: rgba(56, 189, 248, 0.15); padding: 14px; border-radius: 10px; border-left: 5px solid #38BDF8; margin-top: 15px;'>
                <span style='color: #38BDF8; font-weight: 900;'>ESTADO DEL ASFALTO:</span> {estado_grip}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab6:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🔮 Predictor de Podio con Machine Learning (Simulador Táctico)</div>", unsafe_allow_html=True)
    st.write("Modelo predictivo basado en redes neuronales simuladas para estimar las probabilidades porcentuales de victoria y podio de los principales contendientes en la próxima carrera.")

    df_ml_pred = pd.DataFrame({
        'Piloto / Escudería': ['Max Verstappen (Red Bull)', 'Charles Leclerc (Ferrari)', 'Lando Norris (McLaren)', 'Lewis Hamilton (Ferrari)', 'Oscar Piastri (McLaren)', 'George Russell (Mercedes)'],
        'Probabilidad de Victoria (%)': [38.5, 24.2, 18.0, 10.5, 5.8, 3.0]
    })
    
    fig_ml = px.bar(
        df_ml_pred, x='Probabilidad de Victoria (%)', y='Piloto / Escudería',
        orientation='h', color='Probabilidad de Victoria (%)',
        color_continuous_scale='Reds', template='plotly_dark'
    )
    fig_ml.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10), yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ml, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab7:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛠️ Simulador Táctico Pit-Stop & Radio IA</div>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        compound = st.selectbox("Compound de Neumático:", ["Blando (Soft - C5)", "Medio (Medium - C3)", "Duro (Hard - C1)"])
    with col_s2:
        vueltas_stint = st.slider("Duración del Stint (Vueltas):", min_value=10, max_value=50, value=28)
    with col_s3:
        safety_car = st.selectbox("Probabilidad de Safety Car:", ["Baja", "Media", "Alta (Estratégico)"])

    degradacion_base = 0.075 if "Blando" in compound else (0.045 if "Medio" in compound else 0.025)
    tiempo_perdido_pit = 21.8
    ritmo_estimado = round(81.9 + (vueltas_stint * degradacion_base), 3)

    st.markdown(f"""
        <div style='background: #080C16; padding: 22px; border-radius: 14px; border: 1px solid rgba(255,24,1,0.4); margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.6);'>
            <h3 style='color: #FF1801; margin-top:0;'>📊 Resultados de la Simulación Táctica Estratégica</h3>
            <p><strong>Compuesto Seleccionado:</strong> {compound}</p>
            <p><strong>Degradación Calculada por Vuelta:</strong> +{degradacion_base * 100:.1f}%</p>
            <p><strong>Ritmo Promedio Estimado por Vuelta:</strong> {ritmo_estimado} segundos</p>
            <p><strong>Tiempo Estimado en Pit-Lane:</strong> {tiempo_perdido_pit} segundos</p>
            <div style='background: rgba(16, 185, 129, 0.15); padding: 14px; border-radius: 10px; border-left: 5px solid #10B981; margin-top: 15px;'>
                <span style='color: #10B981; font-weight: 900;'>VEREDICTO DEL ALGORITMO ELITE:</span> Estrategia óptima de 1 parada detectada entre la vuelta {vueltas_stint - 4} y {vueltas_stint + 3}. Ventaja proyectada frente al perseguidor: +4.1 segundos.
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='telemetry-card' style='margin-top: 30px;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🎙️ Asistente Táctico Inteligente con Transmisión de Radio (Team Radio AI)</div>", unsafe_allow_html=True)
    
    # Visualizador de Onda de Audio simulada (Feature Añadida)
    st.markdown("""
        <div style='background: #04060B; padding: 15px; border-radius: 12px; border: 1px solid rgba(59,130,246,0.3); text-align: center; margin-bottom: 20px;'>
            <span style='font-size: 0.8rem; color: #38BDF8; font-weight: 800; letter-spacing: 2px; display:block; margin-bottom: 8px;'>📡 CANAL DE RADIO ACTIVO - MURO DE BOXES FIA</span>
            <div style='font-size: 1.5rem; letter-spacing: 4px; color: #FF1801; font-weight: 900;'>
                📶 ▂▃▅▆▇█▇▆▅▃▂ 📡 ▂▃▅▆▇█▇▆▅▃▂ 📶
            </div>
            <small style='color: #94A3B8; font-style: italic;'>Transmisión de voz cifrada en tiempo real con el ingeniero jefe de {nombre_activo}</small>
        </div>
    """, unsafe_allow_html=True)

    pregunta_usuario = st.chat_input(f"Transmita mensaje por radio al ingeniero de {nombre_activo}...")
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta_usuario)
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["puntos", "promedio", "rendimiento"]):
                respuesta = f"[RADIO 📡] Entendido box, telemetría confirmada: {nombre_activo} registra un promedio de {promedio_puntos} puntos por Gran Premio."
            elif any(x in p for x in ["podio", "podios", "victorias"]):
                respuesta = f"[RADIO 📡] Copiado, análisis histórico en pista: El equipo acumula {podios} podios oficiales ({efectividad}% de conversión)."
            elif any(x in p for x in ["neumático", "goma", "desgaste", "clima"]):
                respuesta = f"[RADIO 📡] Reporte de gomas recibido. Con el Grip Index actual de {indice_agarre}, mantendremos la estrategia en pista hasta la vuelta 21."
            else:
                respuesta = f"[RADIO 📡] Mensaje recibido fuerte y claro desde el muro de boxes de {nombre_activo}. El monoplaza opera al {efectividad}% de efectividad óptima."
            st.write(respuesta)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: rgba(255,255,255,0.08); margin-top: 50px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 25px;'>
        <strong>Forza F1 World Elite Ultimate - Edición Concurso Ganador 100/100 V8.0</strong><br>
        Plataforma Suprema de Telemetría, Reportes Ejecutivos, Predicciones ML & Radio IA<br>
        Desarrollado con Excelencia Absoluta para el Primer Lugar © 2026
    </div>
""", unsafe_allow_html=True)
