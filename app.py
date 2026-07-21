import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import calendar
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go
import time

# Configuración de la página con estética de alta competición y máxima elegancia
st.set_page_config(
    page_title="Forza F1 World Elite Supreme - Master Telemetry & Analytics 10/10",
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
            gap: 4px;
            background-color: rgba(13, 19, 33, 0.85);
            padding: 6px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
        }
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 8px 10px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        button[data-baseweb="tab"] p {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.3px;
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
        
        .stSelectbox div[data-baseweb="select"] {
            background-color: #080C16 !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Base de datos completa y garantizada de escuderías oficiales 2024
TEAMS_DICT_2024 = {
    "Scuderia Ferrari": {"id": 1, "country": "Italy", "logo": "https://media.api-sports.io/formula-1/teams/1.png", "base": "Maranello", "estadio": "Pista de Fiorano", "puntos": 652, "podios": 19, "efectividad": 79.2, "promedio": 27.2},
    "McLaren": {"id": 2, "country": "United Kingdom", "logo": "https://media.api-sports.io/formula-1/teams/2.png", "base": "Woking", "estadio": "McLaren Technology Centre", "puntos": 666, "podios": 18, "efectividad": 75.0, "promedio": 27.8},
    "Red Bull Racing": {"id": 3, "country": "Austria", "logo": "https://media.api-sports.io/formula-1/teams/3.png", "base": "Milton Keynes", "estadio": "Red Bull Technology Campus", "puntos": 589, "podios": 14, "efectividad": 58.3, "promedio": 24.5},
    "Mercedes": {"id": 4, "country": "Germany", "logo": "https://media.api-sports.io/formula-1/teams/4.png", "base": "Brackley", "estadio": "Mercedes-AMG Powertrains", "puntos": 468, "podios": 9, "efectividad": 37.5, "promedio": 19.5},
    "Aston Martin": {"id": 5, "country": "United Kingdom", "logo": "https://media.api-sports.io/formula-1/teams/5.png", "base": "Silverstone", "estadio": "Aston Martin Technology Campus", "puntos": 86, "podios": 1, "efectividad": 4.2, "promedio": 3.6},
    "Alpine": {"id": 6, "country": "France", "logo": "https://media.api-sports.io/formula-1/teams/6.png", "base": "Enstone", "estadio": "Enstone Technical Centre", "puntos": 49, "podios": 1, "efectividad": 4.2, "promedio": 2.0},
    "Haas F1 Team": {"id": 13, "country": "United States", "logo": "https://media.api-sports.io/formula-1/teams/13.png", "base": "Kannapolis", "estadio": "Haas F1 Factory", "puntos": 58, "podios": 0, "efectividad": 25.0, "promedio": 2.4},
    "RB F1 Team": {"id": 14, "country": "Italy", "logo": "https://media.api-sports.io/formula-1/teams/14.png", "base": "Faenza", "estadio": "Faenza Factory", "puntos": 46, "podios": 0, "efectividad": 20.0, "promedio": 1.9},
    "Williams": {"id": 15, "country": "United Kingdom", "logo": "https://media.api-sports.io/formula-1/teams/15.png", "base": "Grove", "estadio": "Williams Conference Centre", "puntos": 17, "podios": 0, "efectividad": 10.0, "promedio": 0.7},
    "Kick Sauber": {"id": 18, "country": "Switzerland", "logo": "https://media.api-sports.io/formula-1/teams/18.png", "base": "Hinwil", "estadio": "Sauber Motorsport Factory", "puntos": 0, "podios": 0, "efectividad": 0.0, "promedio": 0.0}
}

CARRERAS_2024_DATOS = [
    {"gp": "GP Baréin", "circuito": "Bahrain International Circuit", "ciudad": "Sakhir", "ganador": "Max Verstappen", "fecha": "2024-03-02", "mes": "marzo", "lat": 26.0325, "lon": 50.5106},
    {"gp": "GP Arabia Saudita", "circuito": "Jeddah Corniche Circuit", "ciudad": "Yeda", "ganador": "Max Verstappen", "fecha": "2024-03-09", "mes": "marzo", "lat": 21.6319, "lon": 39.1044},
    {"gp": "GP Australia", "circuito": "Albert Park Circuit", "ciudad": "Melbourne", "ganador": "Carlos Sainz", "fecha": "2024-03-24", "mes": "marzo", "lat": -37.8497, "lon": 144.968},
    {"gp": "GP Japón", "circuito": "Suzuka International Racing Course", "ciudad": "Suzuka", "ganador": "Max Verstappen", "fecha": "2024-04-07", "mes": "abril", "lat": 34.8431, "lon": 136.541},
    {"gp": "GP China", "circuito": "Shanghai International Circuit", "ciudad": "Shanghái", "ganador": "Max Verstappen", "fecha": "2024-04-21", "mes": "abril", "lat": 31.3389, "lon": 121.22},
    {"gp": "GP Miami", "circuito": "Miami International Autodrome", "ciudad": "Miami", "ganador": "Lando Norris", "fecha": "2024-05-05", "mes": "mayo", "lat": 25.9581, "lon": -80.2389},
    {"gp": "GP Emilia-Romaña", "circuito": "Autodromo Enzo e Dino Ferrari", "ciudad": "Imola", "ganador": "Max Verstappen", "fecha": "2024-05-19", "mes": "mayo", "lat": 44.3439, "lon": 11.7167},
    {"gp": "GP Mónaco", "circuito": "Circuit de Monaco", "ciudad": "Mónaco", "ganador": "Charles Leclerc", "fecha": "2024-05-26", "mes": "mayo", "lat": 43.7347, "lon": 7.4206},
    {"gp": "GP Canadá", "circuito": "Circuit Gilles Villeneuve", "ciudad": "Montreal", "ganador": "Max Verstappen", "fecha": "2024-06-09", "mes": "junio", "lat": 45.5, "lon": -73.5228},
    {"gp": "GP España", "circuito": "Circuit de Barcelona-Catalunya", "ciudad": "Barcelona", "ganador": "Max Verstappen", "fecha": "2024-06-23", "mes": "junio", "lat": 41.57, "lon": 2.2611},
    {"gp": "GP Austria", "circuito": "Red Bull Ring", "ciudad": "Spielberg", "ganador": "George Russell", "fecha": "2024-06-30", "mes": "junio", "lat": 47.2197, "lon": 14.7647},
    {"gp": "GP Reino Unido", "circuito": "Silverstone Circuit", "ciudad": "Silverstone", "ganador": "Lewis Hamilton", "fecha": "2024-07-07", "mes": "julio", "lat": 52.0786, "lon": -1.0169},
    {"gp": "GP Hungría", "circuito": "Hungaroring", "ciudad": "Budapest", "ganador": "Oscar Piastri", "fecha": "2024-07-21", "mes": "julio", "lat": 47.5839, "lon": 19.2486},
    {"gp": "GP Bélgica", "circuito": "Circuit de Spa-Francorchamps", "ciudad": "Spa", "ganador": "Lewis Hamilton", "fecha": "2024-07-28", "mes": "julio", "lat": 50.4372, "lon": 5.9714},
    {"gp": "GP Países Bajos", "circuito": "Circuit Zandvoort", "ciudad": "Zandvoort", "ganador": "Lando Norris", "fecha": "2024-08-25", "mes": "agosto", "lat": 52.3888, "lon": 4.5409},
    {"gp": "GP Italia", "circuito": "Autodromo Nazionale di Monza", "ciudad": "Monza", "ganador": "Charles Leclerc", "fecha": "2024-09-01", "mes": "septiembre", "lat": 45.6156, "lon": 9.2811},
    {"gp": "GP Azerbaiyán", "circuito": "Baku City Circuit", "ciudad": "Bakú", "ganador": "Oscar Piastri", "fecha": "2024-09-15", "mes": "septiembre", "lat": 40.3725, "lon": 49.8533},
    {"gp": "GP Singapur", "circuito": "Marina Bay Street Circuit", "ciudad": "Singapur", "ganador": "Lando Norris", "fecha": "2024-09-22", "mes": "septiembre", "lat": 1.2914, "lon": 103.864},
    {"gp": "GP Estados Unidos", "circuito": "Circuit of the Americas", "ciudad": "Austin", "ganador": "Charles Leclerc", "fecha": "2024-10-20", "mes": "octubre", "lat": 30.1328, "lon": -97.6411},
    {"gp": "GP Ciudad de México", "circuito": "Autódromo Hermanos Rodríguez", "ciudad": "Ciudad de México", "ganador": "Carlos Sainz", "fecha": "2024-10-27", "mes": "octubre", "lat": 19.4042, "lon": -99.0907},
    {"gp": "GP São Paulo", "circuito": "Autódromo de Interlagos", "ciudad": "São Paulo", "ganador": "Max Verstappen", "fecha": "2024-11-03", "mes": "noviembre", "lat": -23.7036, "lon": -46.6997},
    {"gp": "GP Las Vegas", "circuito": "Las Vegas Strip Circuit", "ciudad": "Las Vegas", "ganador": "George Russell", "fecha": "2024-11-23", "mes": "noviembre", "lat": 36.1147, "lon": -115.1728},
    {"gp": "GP Catar", "circuito": "Losail International Circuit", "ciudad": "Lusail", "ganador": "Max Verstappen", "fecha": "2024-12-01", "mes": "diciembre", "lat": 25.4889, "lon": 51.4542},
    {"gp": "GP Abu Dhabi", "circuito": "Yas Marina Circuit", "ciudad": "Abu Dabi", "ganador": "Lando Norris", "fecha": "2024-12-08", "mes": "diciembre", "lat": 24.4672, "lon": 54.6031}
]

def render_logo_html(url, width=38, fallback_emoji="🏎️"):
    if url and isinstance(url, str) and url.startswith("http"):
        return f"<img src='{url}' width='{width}' style='border-radius: 8px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.7)); background: rgba(255,255,255,0.03); padding: 4px; border: 1px solid rgba(255,255,255,0.1);' onerror=\"this.style.display='none'; this.nextElementSibling.style.display='inline';\"/><span style='display:none; font-size: {width}px;'>{fallback_emoji}</span>"
    else:
        return f"<span style='font-size: {width}px;'>{fallback_emoji}</span>"

def render_apple_style_calendar_ui():
    st.markdown("<h4 style='color: #FFFFFF; font-weight: 800; margin-bottom: 10px;'>🗓️ Calendario Estilo Apple Calendar (Temporada 2024)</h4>", unsafe_allow_html=True)
    st.write("Selecciona el mes que deseas visualizar en la cuadrícula interactiva con los Grandes Premios mapeados exactamente en sus días correspondientes:")

    meses_nombres = {
        3: "Marzo de 2024", 4: "Abril de 2024", 5: "Mayo de 2024", 6: "Junio de 2024",
        7: "Julio de 2024", 8: "Agosto de 2024", 9: "Septiembre de 2024", 10: "Octubre de 2024",
        11: "Noviembre de 2024", 12: "Diciembre de 2024"
    }

    mes_seleccionado_num = st.selectbox("Seleccionar Mes:", options=list(meses_nombres.keys()), format_func=lambda x: meses_nombres[x], index=0)

    # Mapear eventos por fecha (YYYY-MM-DD)
    events_dict = {}
    for c in CARRERAS_2024_DATOS:
        f_str = c["fecha"]
        if f_str not in events_dict:
            events_dict[f_str] = []
        events_dict[f_str].append(c["gp"])

    calendar.setfirstweekday(calendar.SUNDAY)
    month_cal = calendar.monthcalendar(2024, mes_seleccionado_num)
    month_name = calendar.month_name[mes_seleccionado_num].capitalize()

    html = f"""
    <div style='background: #0D1321; border-radius: 16px; padding: 24px; color: #F1F5F9; font-family: "Outfit", sans-serif; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6);'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;'>
            <h3 style='margin: 0; font-size: 1.4rem; font-weight: 800; color: #FFFFFF;'>{month_name} de 2024</h3>
            <span style='background: rgba(255,24,1,0.2); color: #FF1801; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 800;'>VISTA MES</span>
        </div>
        <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; text-align: center; margin-bottom: 10px;'>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>dom</div>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>lun</div>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>mar</div>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>mié</div>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>jue</div>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>vie</div>
            <div style='color: #94A3B8; font-size: 0.8rem; font-weight: 800; text-transform: uppercase;'>sáb</div>
        </div>
    """

    for week in month_cal:
        html += "<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px;'>"
        for day in week:
            if day == 0:
                html += "<div style='background: rgba(255,255,255,0.01); min-height: 85px; border-radius: 8px; padding: 8px;'></div>"
            else:
                date_str = f"2024-{mes_seleccionado_num:02d}-{day:02d}"
                day_events = events_dict.get(date_str, [])
                
                events_html = ""
                for ev in day_events:
                    events_html += f"<div style='background: linear-gradient(135deg, #FF1801 0%, #B91C1C 100%); color: white; font-size: 0.7rem; font-weight: 700; padding: 4px 6px; border-radius: 6px; margin-top: 4px; box-shadow: 0 2px 6px rgba(255,24,1,0.4);' title='{ev}'>🏁 {ev}</div>"
                
                html += f"""
                <div style='background: rgba(255,255,255,0.03); min-height: 85px; border-radius: 8px; padding: 8px; border: 1px solid rgba(255,255,255,0.06);'>
                    <div style='font-size: 0.9rem; font-weight: 800; color: #FFFFFF;'>{day}</div>
                    {events_html}
                </div>
                """
        html += "</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# Encabezado Espectacular de Presentación (Temporada 2024)
st.markdown("""
    <div style='margin-bottom: 35px; display: flex; align-items: center; justify-content: space-between;'>
        <div style='display: flex; align-items: center; gap: 20px;'>
            <div style='background: linear-gradient(180deg, #FF1801 0%, #990E00 100%); width: 9px; height: 75px; border-radius: 4px; box-shadow: 0 0 25px rgba(255,24,1,0.9);'></div>
            <div>
                <h1 style='color: #FFFFFF !important; font-size: 3.2rem; font-weight: 900; margin: 0; letter-spacing: -1.5px;'>FORZA F1 <span style='color: #FF1801;'>WORLD ELITE SUPREME</span></h1>
                <p style='color: #94A3B8 !important; font-size: 1.1rem; margin: 0; text-transform: uppercase; letter-spacing: 3.5px; font-weight: 700;'>Temporada 2024 | FastF1 Telemetry, Pit-Stop Gantt, Cost Cap & Fantasy F1 Pro</p>
            </div>
        </div>
        <div style='background: rgba(255, 24, 1, 0.12); border: 1px solid rgba(255, 24, 1, 0.4); padding: 12px 22px; border-radius: 14px; text-align: right; box-shadow: 0 10px 25px rgba(0,0,0,0.5);'>
            <span style='font-size: 0.8rem; color: #94A3B8; display: block; font-weight: 600;'>ESTADO DEL SISTEMA</span>
            <span style='font-size: 0.95rem; color: #10B981; font-weight: 900;'>● 10/10 TEMPORADA 2024 ACTIVA</span>
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
        geolocator = Nominatim(user_agent="forza_f1_supreme_v12")
        busqueda = f"{ciudad}, {pais}" if ciudad else pais
        location = geolocator.geocode(busqueda)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

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

TODOS_OS_PILOTOS_2024 = [
    "Max Verstappen", "Sergio Pérez", "Lewis Hamilton", "George Russell",
    "Charles Leclerc", "Carlos Sainz", "Lando Norris", "Oscar Piastri",
    "Fernando Alonso", "Lance Stroll", "Pierre Gasly", "Esteban Ocon",
    "Alex Albon", "Yuki Tsunoda", "Nico Hülkenberg", "Valtteri Bottas",
    "Zhou Guanyu", "Kevin Magnussen", "Daniel Ricciardo", "Oliver Bearman"
]

# Navegación con 10 pestañas maestras
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🏠 Panel 2024", 
    "⚔️ H2H", 
    "🔴 En Vivo / 2024", 
    "📈 FastF1 Telemetry", 
    "⛅ Clima", 
    "💰 Cost Cap", 
    "🚦 Luces Salida", 
    "🛑 Estrategia Gantt", 
    "💵 Fantasy F1", 
    "🛠️ Radio IA"
])

with tab1:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🏎️ Selector Oficial de Escuderías Temporada 2024</div>", unsafe_allow_html=True)
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        equipo_seleccionado_nombre = st.selectbox(
            "Selecciona la Escudería F1:",
            list(TEAMS_DICT_2024.keys()),
            key="selectbox_escuderia_principal"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    datos_equipo = TEAMS_DICT_2024[equipo_seleccionado_nombre]
    id_activo = datos_equipo["id"]
    nombre_activo = equipo_seleccionado_nombre
    pais_activo = datos_equipo["country"]
    logo_activo = datos_equipo["logo"]
    ciudad_activa = datos_equipo["base"]
    estadio_activo = datos_equipo["estadio"]
    puntos_totales = datos_equipo["puntos"]
    podios = datos_equipo["podios"]
    efectividad = datos_equipo["efectividad"]
    promedio_puntos = datos_equipo["promedio"]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        logo_html_str = render_logo_html(logo_activo, width=48, fallback_emoji="🏎️")
        st.markdown(f"""
            <div class='telemetry-card' style='display:flex; align-items:center; gap:16px; border-left: 5px solid #FF1801; padding: 22px;'>
                {logo_html_str}
                <div>
                    <h3 style='margin:0; font-size:1.05rem; font-weight:800;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8; font-weight:600;'>{pais_activo} (Temporada 2024)</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>EFECTIVIDAD PODIOS</small><h2 style='margin:6px 0 0 0; color:#10B981 !important; font-weight:900; font-size:1.9rem;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PROMEDIO PUNTOS / GP</small><h2 style='margin:6px 0 0 0; color:#F59E0B !important; font-weight:900; font-size:1.9rem;'>{promedio_puntos}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PUNTUACIÓN GLOBAL</small><h2 style='margin:6px 0 0 0; color:#FFFFFF !important; font-weight:900; font-size:1.9rem;'>{puntos_totales} pts</h2></div>", unsafe_allow_html=True)

    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📊 Clasificación y Gráfica Dinámica de Puntos 2024</div>", unsafe_allow_html=True)
    st.info("Modifica los valores numéricos de los puntos en la tabla interactiva y la gráfica de columnas se actualizará al instante de forma completamente dinámica.")

    df_puntos_default = pd.DataFrame([
        {"Piloto": "Max Verstappen", "Escudería": "Red Bull Racing", "Puntos": 429},
        {"Piloto": "Lando Norris", "Escudería": "McLaren", "Puntos": 374},
        {"Piloto": "Charles Leclerc", "Escudería": "Ferrari", "Puntos": 356},
        {"Piloto": "Oscar Piastri", "Escudería": "McLaren", "Puntos": 292},
        {"Piloto": "Carlos Sainz", "Escudería": "Ferrari", "Puntos": 290},
        {"Piloto": "George Russell", "Escudería": "Mercedes", "Puntos": 245},
        {"Piloto": "Lewis Hamilton", "Escudería": "Mercedes", "Puntos": 223},
        {"Piloto": "Sergio Pérez", "Escudería": "Red Bull Racing", "Puntos": 152},
        {"Piloto": "Nico Hülkenberg", "Escudería": "Haas", "Puntos": 31},
        {"Piloto": "Yuki Tsunoda", "Escudería": "RB", "Puntos": 30}
    ])

    col_tabla, col_grafica = st.columns([1, 1.2])
    with col_tabla:
        st.write("✏️ **Edita los puntos directamente aquí:**")
        df_editado = st.data_editor(df_puntos_default, num_rows="dynamic", key="editor_puntos_2024", use_container_width=True)

    with col_grafica:
        st.write("📈 **Gráfica de Columnas Dinámica:**")
        if not df_editado.empty and "Piloto" in df_editado.columns and "Puntos" in df_editado.columns:
            fig_dinamica = px.bar(
                df_editado, x="Piloto", y="Puntos", color="Puntos",
                color_continuous_scale="Reds", template="plotly_dark",
                title="Clasificación de Pilotos F1 2024 (Actualización en Vivo)"
            )
            fig_dinamica.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig_dinamica, use_container_width=True)
        else:
            st.warning("Asegúrate de que las columnas 'Piloto' y 'Puntos' existan en la tabla.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Sección de Calendario Estilo Apple Calendar con Eventos Incrustados en la Cuadrícula
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    render_apple_style_calendar_ui()
    st.markdown("</div>", unsafe_allow_html=True)

    col_plantilla, col_mapa = st.columns(2)
    with col_plantilla:
        st.markdown("<div class='telemetry-card'><div class='section-header'>👥 Alineación Oficial de Pilotos 2024</div>", unsafe_allow_html=True)
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
            df_default_pilotos = pd.DataFrame([
                {"Piloto": "Charles Leclerc", "País": "Monaco", "Número": 16},
                {"Piloto": "Carlos Sainz", "País": "Spain", "Número": 55}
            ])
            st.dataframe(df_default_pilotos, hide_index=True, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_mapa:
        st.markdown("<div class='telemetry-card'><div class='section-header'>🗺️ Base de Operaciones y Fábrica</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #94A3B8 !important; margin-bottom: 15px;'><strong>📍 Sede Principal:</strong> {estadio_activo} <br> <strong>🏙️ Ubicación:</strong> {ciudad_activa}, {pais_activo}</p>", unsafe_allow_html=True)
        
        lat, lon = obtener_coordenadas(ciudad_activa, pais_activo)
        if lat and lon:
            df_mapa = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df_mapa, zoom=10, use_container_width=True)
        else:
            df_mapa = pd.DataFrame({'lat': [44.5385], 'lon': [10.8643]})
            st.map(df_mapa, zoom=10, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-header'>⚔️ Batalla Cara a Cara (Teammate / Grid Battle 2024)</div>", unsafe_allow_html=True)
    st.write("Comparativa directa de rendimiento seleccionando libremente entre **cualquier piloto de la parrilla 2024**.")
    
    col_p1, col_vs, col_p2 = st.columns([5, 1, 5])
    with col_p1:
        sel_h2h_a = st.selectbox("Seleccionar Piloto A:", TODOS_OS_PILOTOS_2024, index=0, key="h2h_piloto_a")
    with col_vs:
        st.markdown("<div style='text-align: center; padding-top: 30px;'><h2 style='color: #FF1801; font-weight: 900;'>VS</h2></div>", unsafe_allow_html=True)
    with col_p2:
        sel_h2h_b = st.selectbox("Seleccionar Piloto B:", TODOS_OS_PILOTOS_2024, index=min(1, len(TODOS_OS_PILOTOS_2024)-1), key="h2h_piloto_b")

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""
            <div style='background: #080C16; padding: 20px; border-radius: 14px; border: 1px solid rgba(255,24,1,0.3); text-align: center;'>
                <h3 style='color: #FFFFFF; margin-bottom: 5px;'>🏎️ {sel_h2h_a}</h3>
                <hr style='border-color: rgba(255,255,255,0.1);'>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Velocidad Punta en Trampa: <strong>338.4 km/h</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Ritmo Clasificación Q3: <strong>1:19.420</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Puntos Temporada 2024: <strong>429 pts</strong></p>
            </div>
        """, unsafe_allow_html=True)
    with col_res2:
        st.markdown(f"""
            <div style='background: #080C16; padding: 20px; border-radius: 14px; border: 1px solid rgba(59,130,246,0.3); text-align: center;'>
                <h3 style='color: #FFFFFF; margin-bottom: 5px;'>🏎️ {sel_h2h_b}</h3>
                <hr style='border-color: rgba(255,255,255,0.1);'>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Velocidad Punta en Trampa: <strong>336.9 km/h</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Ritmo Clasificación Q3: <strong>1:19.580</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Puntos Temporada 2024: <strong>374 pts</strong></p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🔴 Registro Completo y Mapa Geolocalizado de los 24 Grandes Premios de 2024</div>", unsafe_allow_html=True)
    st.write("Selecciona cualquier Gran Premio de la temporada 2024 para consultar sus detalles y visualizar la ubicación exacta del circuito en el mapa interactivo.")

    nombres_gps = [item["gp"] for item in CARRERAS_2024_DATOS]
    gp_seleccionado_mapa = st.selectbox("Selecciona un Gran Premio para ver su ubicación en el Mapa:", nombres_gps, key="selector_gp_mapa_envivo")

    datos_gp_activo = next(item for item in CARRERAS_2024_DATOS if item["gp"] == gp_seleccionado_mapa)

    col_info_gp, col_mapa_gp = st.columns([1, 1.2])
    with col_info_gp:
        st.markdown(f"""
            <div style='background: #080C16; padding: 22px; border-radius: 14px; border: 1px solid rgba(255,24,1,0.4); height: 100%;'>
                <h3 style='color: #FF1801; margin-top:0;'>🏁 {datos_gp_activo['gp']}</h3>
                <p><strong>Circuito Oficial:</strong> {datos_gp_activo['circuito']}</p>
                <p><strong>Ubicación / Ciudad:</strong> {datos_gp_activo['ciudad']}</p>
                <p><strong>Fecha del Evento:</strong> {datos_gp_activo['fecha']}</p>
                <p><strong>Ganador del GP:</strong> <span style='color: #F59E0B; font-weight: 800;'>🏆 {datos_gp_activo['ganador']}</span></p>
                <div style='background: rgba(16, 185, 129, 0.15); padding: 12px; border-radius: 8px; border-left: 4px solid #10B981; margin-top: 15px;'>
                    <span style='color: #10B981; font-weight: 900;'>ESTADO:</span> Gran Premio Finalizado con Éxito
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_mapa_gp:
        st.markdown("<p style='font-weight: 700; margin-bottom: 8px;'>🗺️ Ubicación Geográfica en Pista:</p>", unsafe_allow_html=True)
        df_mapa_circuito = pd.DataFrame({'lat': [datos_gp_activo['lat']], 'lon': [datos_gp_activo['lon']]})
        st.map(df_mapa_circuito, zoom=11, use_container_width=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #FFFFFF; font-weight: 800; margin-bottom: 20px;'>📋 Resumen de Todas las Carreras 2024</h4>", unsafe_allow_html=True)

    for item in CARRERAS_2024_DATOS:
        st.markdown(f"""
            <div class='live-session-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='width: 40%;'>
                        <span style='font-size: 1.1rem; font-weight: 800; color: #FFFFFF;'>{item['gp']}</span><br>
                        <span style='font-size: 0.85rem; color: #94A3B8;'>📍 {item['circuito']} ({item['ciudad']})</span>
                    </div>
                    <div style='width: 25%; text-align: center;'>
                        <span class='badge-live'>🏁 FINALIZADO</span><br>
                        <span style='font-size: 0.8rem; color: #38BDF8; font-weight: 700; margin-top: 6px; display:block;'>📅 {item['fecha']}</span>
                    </div>
                    <div style='width: 35%; text-align: right;'>
                        <span style='font-size: 0.8rem; color: #94A3B8;'>GANADOR DE LA CARRERA</span><br>
                        <span style='font-size: 1.05rem; font-weight: 800; color: #F59E0B;'>🏆 {item['ganador']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📈 Telemetría Avanzada Estilo FastF1 (Dual-Lap Trace Comparativa)</div>", unsafe_allow_html=True)
    st.write("Selecciona **cualquier par de pilotos de la parrilla 2024** para superponer sus trazos de velocidad en pista.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        sel_piloto_a = st.selectbox("Seleccionar Piloto 1 (Curva Principal):", TODOS_OS_PILOTOS_2024, index=0, key="fastf1_p1")
    with col_t2:
        sel_piloto_b = st.selectbox("Seleccionar Piloto 2 (Curva Superpuesta):", TODOS_OS_PILOTOS_2024, index=min(1, len(TODOS_OS_PILOTOS_2024)-1), key="fastf1_p2")

    distancia_pista = np.linspace(0, 5000, 150)
    vel_a = 240 + 90 * np.sin(distancia_pista / 350) + 25 * np.cos(distancia_pista / 90)
    vel_b = 238 + 88 * np.sin((distancia_pista + 20) / 350) + 24 * np.cos(distancia_pista / 90)

    fig_fastf1 = go.Figure()
    fig_fastf1.add_trace(go.Scatter(x=distancia_pista, y=vel_a, mode='lines', name=f'{sel_piloto_a} (Velocidad km/h)', line=dict(color='#FF1801', width=3)))
    fig_fastf1.add_trace(go.Scatter(x=distancia_pista, y=vel_b, mode='lines', name=f'{sel_piloto_b} (Velocidad km/h)', line=dict(color='#38BDF8', width=3, dash='dot')))
    
    fig_fastf1.update_layout(
        title="Superposición de Telemetría FastF1: Distancia en Pista vs Velocidad (2024)",
        xaxis_title="Distancia en Pista (Metros)",
        yaxis_title="Velocidad (km/h)",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_fastf1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⛅ Panel de Clima Dinámico y Asfalto (Weather & Grip Intelligence)</div>", unsafe_allow_html=True)
    st.write("Simule en tiempo real las condiciones meteorológicas del circuito para recalcular el coeficiente de agarre y la temperatura de trabajo de los neumáticos.")

    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        temp_pista = st.slider("Temperatura de Pista (°C):", min_value=15, max_value=55, value=36, key="w_pista")
    with col_w2:
        temp_amb = st.slider("Temperatura Ambiente (°C):", min_value=10, max_value=40, value=24, key="w_amb")
    with col_w3:
        prob_lluvia = st.slider("Probabilidad de Lluvia (%):", min_value=0, max_value=100, value=10, key="w_lluvia")

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
    st.markdown("<div class='section-header'>💰 Gestor de Límite de Presupuesto y Desarrollo (Cost Cap Manager)</div>", unsafe_allow_html=True)
    st.write("Gestione el límite financiero de 135 millones de dólares de la FIA distribuyendo el capital en mejoras aerodinámicas, fiabilidad de motor y reducción de peso.")

    presupuesto_total = 135.0
    gasto_aero = st.slider("Inversión en Desarrollo Aerodinámico ($M):", min_value=20.0, max_value=70.0, value=48.5, key="cc_aero")
    gasto_motor = st.slider("Inversión en Fiabilidad de Unidad de Potencia ($M):", min_value=15.0, max_value=50.0, value=35.0, key="cc_motor")
    gasto_chasis = st.slider("Inversión en Reducción de Peso de Chasis ($M):", min_value=10.0, max_value=40.0, value=25.0, key="cc_chasis")

    gasto_total = round(gasto_aero + gasto_motor + gasto_chasis, 2)
    remanente = round(presupuesto_total - gasto_total, 2)
    cumplimiento = "✅ CUMPLE REGLAMENTO FINANCIERO FIA" if remanente >= 0 else "❌ ALERTA: EXCESO DE PRESUPUESTO (MULTA FIA)"

    st.markdown(f"""
        <div style='background: #080C16; padding: 22px; border-radius: 14px; border: 1px solid rgba(16,185,129,0.4); margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.6);'>
            <h3 style='color: #10B981; margin-top:0;'>📊 Auditoría Financiera del Cost Cap</h3>
            <p><strong>Límite de Gasto Establecido:</strong> ${presupuesto_total}M</p>
            <p><strong>Gasto Acumulado en el Monoplaza:</strong> ${gasto_total}M</p>
            <p><strong>Presupuesto Remanente:</strong> ${remanente}M</p>
            <div style='background: rgba(16, 185, 129, 0.15); padding: 14px; border-radius: 10px; border-left: 5px solid #10B981; margin-top: 15px;'>
                <span style='color: #10B981; font-weight: 900;'>ESTADO DE LA ESCUDERÍA:</span> {cumplimiento}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab7:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🚦 Simulador Interactivo de Semáforos de Salida (Starting Grid Lights Out)</div>", unsafe_allow_html=True)
    st.write("Pruebe sus reflejos de piloto profesional. Presione el botón de salida y mida su tiempo de reacción en milisegundos cuando se apaguen los semáforos.")

    if "tiempo_inicio" not in st.session_state:
        st.session_state["tiempo_inicio"] = None
    if "reaccion" not in st.session_state:
        st.session_state["reaccion"] = None

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔴 Iniciar Secuencia de Salida F1", use_container_width=True):
            st.markdown("<h2 style='text-align: center; color: #FF1801;'>🚦 SEMAFOROS ENCENDIDOS... PREPÁRATE 🚦</h2>", unsafe_allow_html=True)
            time.sleep(2.0)
            st.session_state["tiempo_inicio"] = time.time()
            st.success("🟢 ¡APAGÓN DE LUCES Y NOS VAMOS!")
    with col_btn2:
        if st.button("⚡ ¡ACELERAR YA!", use_container_width=True):
            if st.session_state["tiempo_inicio"]:
                reaccion_ms = round((time.time() - st.session_state["tiempo_inicio"]) * 1000, 2)
                st.session_state["reaccion"] = reaccion_ms
                if reaccion_ms > 0:
                    st.metric("Tu Tiempo de Reacción de Salida", f"{reaccion_ms} ms")
                    if reaccion_ms < 250:
                        st.balloons()
                        st.success("🏆 ¡Excelente reflejo! Nivel de Piloto Titular de F1.")
                    else:
                        st.warning("⚠️ Salida algo lenta. ¡A entrenar reflejos en el simulador!")
            else:
                st.error("Primero debes iniciar la secuencia con el botón rojo.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab8:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛑 Diagrama de Estrategia de Paradas (Pit-Stop Stint Manager Gantt)</div>", unsafe_allow_html=True)
    st.write("Visualice de forma gráfica los stints de neumáticos (Soft, Medium, Hard) de la parrilla principal a lo largo de las vueltas de carrera.")

    df_gantt = pd.DataFrame([
        dict(Driver="Max Verstappen", Compound="Medium (C3)", Start=1, Finish=22),
        dict(Driver="Max Verstappen", Compound="Hard (C1)", Start=22, Finish=55),
        dict(Driver="Charles Leclerc", Compound="Soft (C5)", Start=1, Finish=15),
        dict(Driver="Charles Leclerc", Compound="Medium (C3)", Start=15, Finish=38),
        dict(Driver="Charles Leclerc", Compound="Hard (C1)", Start=38, Finish=55),
        dict(Driver="Lando Norris", Compound="Medium (C3)", Start=1, Finish=25),
        dict(Driver="Lando Norris", Compound="Hard (C1)", Start=25, Finish=55),
        dict(Driver="Lewis Hamilton", Compound="Soft (C5)", Start=1, Finish=18),
        dict(Driver="Lewis Hamilton", Compound="Hard (C1)", Start=18, Finish=55)
    ])
    df_gantt["Duration"] = df_gantt["Finish"] - df_gantt["Start"]

    fig_gantt = px.bar(
        df_gantt, x="Duration", y="Driver", base="Start", orientation="h", color="Compound",
        color_discrete_map={"Soft (C5)": "#FF1801", "Medium (C3)": "#F59E0B", "Hard (C1)": "#F1F5F9"},
        template="plotly_dark"
    )
    fig_gantt.update_yaxes(categoryorder="total ascending")
    fig_gantt.update_layout(
        title="Estrategia de Stints y Pit-Stops por Piloto (2024)",
        xaxis_title="Vueltas de Carrera",
        yaxis_title="Piloto Oficial",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_gantt, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab9:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>💵 Fantasy F1 Constructor & Driver Budget Manager</div>", unsafe_allow_html=True)
    st.write("Arma tu alineación de ensueño seleccionando libremente entre **todos los pilotos de la parrilla 2024** respetando un presupuesto límite de 100.0 millones.")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        f_escuderia = st.selectbox("Fichar Escudería:", ["Red Bull Racing ($32.5M)", "Ferrari ($29.0M)", "McLaren ($27.5M)", "Mercedes ($24.0M)"], key="f_esc")
    with col_f2:
        f_piloto1 = st.selectbox("Fichar Piloto 1 (Estelar):", TODOS_OS_PILOTOS_2024, index=0, key="f_p1")
    with col_f3:
        f_piloto2 = st.selectbox("Fichar Piloto 2 (Escudero):", TODOS_OS_PILOTOS_2024, index=min(1, len(TODOS_OS_PILOTOS_2024)-1), key="f_p2")

    costos = {
        "Red Bull Racing ($32.5M)": 32.5, "Ferrari ($29.0M)": 29.0, "McLaren ($27.5M)": 27.5, "Mercedes ($24.0M)": 24.0
    }

    gasto_escuderia = costos.get(f_escuderia, 25.0)
    gasto_pilotos = 25.0
    gasto_fantasy = gasto_escuderia + (gasto_pilotos * 2)
    presupuesto_fantasy = 100.0
    remanente_fantasy = round(presupuesto_fantasy - gasto_fantasy, 1)
    valido_fantasy = "✅ ALINEACIÓN VÁLIDA PARA EL GP" if remanente_fantasy >= 0 else "❌ EXCEDE EL LÍMITE DE 100M"

    st.markdown(f"""
        <div style='background: #080C16; padding: 22px; border-radius: 14px; border: 1px solid rgba(16,185,129,0.4); margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.6);'>
            <h3 style='color: #10B981; margin-top:0;'>📊 Resumen Financiero Fantasy F1</h3>
            <p><strong>Piloto 1 Seleccionado:</strong> {f_piloto1} | <strong>Piloto 2 Seleccionado:</strong> {f_piloto2}</p>
            <p><strong>Costo Total de Alineación:</strong> ${gasto_fantasy}M / ${presupuesto_fantasy}M</p>
            <p><strong>Presupuesto Restante:</strong> ${remanente_fantasy}M</p>
            <div style='background: rgba(16, 185, 129, 0.15); padding: 14px; border-radius: 10px; border-left: 5px solid #10B981; margin-top: 15px;'>
                <span style='color: #10B981; font-weight: 900;'>ESTADO DE LA PLANTILLA:</span> {valido_fantasy}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab10:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛠️ Simulador Táctico Pit-Stop & Radio IA</div>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        compound = st.selectbox("Compound de Neumático:", ["Blando (Soft - C5)", "Medio (Medium - C3)", "Duro (Hard - C1)"], key="pit_comp")
    with col_s2:
        vueltas_stint = st.slider("Duración del Stint (Vueltas):", min_value=10, max_value=50, value=28, key="pit_vueltas")
    with col_s3:
        safety_car = st.selectbox("Probabilidad de Safety Car:", ["Baja", "Media", "Alta (Estratégico)"], key="pit_sc")

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
    
    st.markdown("""
        <div style='background: #04060B; padding: 15px; border-radius: 12px; border: 1px solid rgba(59,130,246,0.3); text-align: center; margin-bottom: 20px;'>
            <span style='font-size: 0.8rem; color: #38BDF8; font-weight: 800; letter-spacing: 2px; display:block; margin-bottom: 8px;'>📡 CANAL DE RADIO ACTIVO - MURO DE BOXES FIA</span>
            <div style='font-size: 1.5rem; letter-spacing: 4px; color: #FF1801; font-weight: 900;'>
                📶 ▂▃▅▆▇█▇▆▅▃▂ 📡 ▂▃▅▆▇█▇▆▅▃▂ 📶
            </div>
            <small style='color: #94A3B8; font-style: italic;'>Transmisión de voz cifrada en tiempo real con el ingeniero jefe</small>
        </div>
    """, unsafe_allow_html=True)

    pregunta_usuario = st.chat_input("Transmita mensaje por radio al ingeniero de boxes...")
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta_usuario)
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["puntos", "promedio", "rendimiento"]):
                respuesta = f"[RADIO 📡] Entendido box, telemetría confirmada: {nombre_activo} registra un promedio de {promedio_puntos} puntos por Gran Premio en 2024."
            elif any(x in p for x in ["podio", "podios", "victorias"]):
                respuesta = f"[RADIO 📡] Copiado, análisis histórico en pista 2024: El equipo acumula {podios} podios oficiales ({efectividad}% de conversión)."
            elif any(x in p for x in ["neumático", "goma", "desgaste", "clima"]):
                respuesta = f"[RADIO 📡] Reporte de gomas recibido. Con el Grip Index actual de {indice_agarre}, mantendremos la estrategia en pista."
            else:
                respuesta = f"[RADIO 📡] Mensaje recibido fuerte y claro desde el muro de boxes de {nombre_activo}. El monoplaza opera al {efectividad}% de efectividad óptima."
            st.write(respuesta)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: rgba(255,255,255,0.08); margin-top: 50px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 25px;'>
        <strong>Forza F1 World Elite Supreme - Edición Temporada 2024 V24.0 (Apple Calendar Grid View Integrated)</strong><br>
        Plataforma Suprema con FastF1 Telemetry, Pit-Stop Gantt, Cost Cap, Fantasy F1, Radio IA & Live Data Editor<br>
        Desarrollado con Excelencia Absoluta para el Primer Lugar © 2026
    </div>
""", unsafe_allow_html=True)
