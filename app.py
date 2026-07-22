import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import calendar
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Configuración de la página con estética de alta competición y máxima elegancia
st.set_page_config(
    page_title="Forza F1 World Elite Supreme - Master Telemetry & Analytics 10/10",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MÚSICA F1 (COVER ÉPICO EN BUCLE INFINITO) ---
st.sidebar.markdown("### 🎵 Tema Oficial F1")
st.sidebar.markdown("""
    <iframe width="100%" height="180" src="https://www.youtube.com/embed/MSrHoJHCa3I?loop=1&playlist=MSrHoJHCa3I" 
    title="F1 Theme Cover" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" style="border-radius: 8px;">
    </iframe>
""", unsafe_allow_html=True)

# Diseño UI/UX de Vanguardia Absoluta (Estética F1 Pit-Wall Elite & Glassmorphism Pro)
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

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
    {"gp": "Gran Premio de Baréin 2024", "circuito": "Bahrain International Circuit", "ciudad": "Sakhir", "ganador": "Max Verstappen", "fecha": "2024-03-02", "lat": 26.0325, "lon": 50.5106},
    {"gp": "Gran Premio de Arabia Saudita 2024", "circuito": "Jeddah Corniche Circuit", "ciudad": "Yeda", "ganador": "Max Verstappen", "fecha": "2024-03-09", "lat": 21.6319, "lon": 39.1044},
    {"gp": "Gran Premio de Australia 2024", "circuito": "Albert Park Circuit", "ciudad": "Melbourne", "ganador": "Carlos Sainz", "fecha": "2024-03-24", "lat": -37.8497, "lon": 144.968},
    {"gp": "Gran Premio de Japón 2024", "circuito": "Suzuka International Racing Course", "ciudad": "Suzuka", "ganador": "Max Verstappen", "fecha": "2024-04-07", "lat": 34.8431, "lon": 136.541},
    {"gp": "Gran Premio de China 2024", "circuito": "Shanghai International Circuit", "ciudad": "Shanghái", "ganador": "Max Verstappen", "fecha": "2024-04-21", "lat": 31.3389, "lon": 121.22},
    {"gp": "Gran Premio de Miami 2024", "circuito": "Miami International Autodrome", "ciudad": "Miami", "ganador": "Lando Norris", "fecha": "2024-05-05", "lat": 25.9581, "lon": -80.2389},
    {"gp": "Gran Premio de Emilia-Romaña 2024", "circuito": "Autodromo Internazionale Enzo e Dino Ferrari", "ciudad": "Imola", "ganador": "Max Verstappen", "fecha": "2024-05-19", "lat": 44.3439, "lon": 11.7167},
    {"gp": "Gran Premio de Mónaco 2024", "circuito": "Circuit de Monaco", "ciudad": "Mónaco", "ganador": "Charles Leclerc", "fecha": "2024-05-26", "lat": 43.7347, "lon": 7.4206},
    {"gp": "Gran Premio de Canadá 2024", "circuito": "Circuit Gilles Villeneuve", "ciudad": "Montreal", "ganador": "Max Verstappen", "fecha": "2024-06-09", "lat": 45.5, "lon": -73.5228},
    {"gp": "Gran Premio de España 2024", "circuito": "Circuit de Barcelona-Catalunya", "ciudad": "Barcelona", "ganador": "Max Verstappen", "fecha": "2024-06-23", "lat": 41.57, "lon": 2.2611},
    {"gp": "Gran Premio de Austria 2024", "circuito": "Red Bull Ring", "ciudad": "Spielberg", "ganador": "George Russell", "fecha": "2024-06-30", "lat": 47.2197, "lon": 14.7647},
    {"gp": "Gran Premio del Reino Unido 2024", "circuito": "Silverstone Circuit", "ciudad": "Silverstone", "ganador": "Lewis Hamilton", "fecha": "2024-07-07", "lat": 52.0786, "lon": -1.0169},
    {"gp": "Gran Premio de Hungría 2024", "circuito": "Hungaroring", "ciudad": "Budapest", "ganador": "Oscar Piastri", "fecha": "2024-07-21", "lat": 47.5839, "lon": 19.2486},
    {"gp": "Gran Premio de Bélgica 2024", "circuito": "Circuit de Spa-Francorchamps", "ciudad": "Spa", "ganador": "Lewis Hamilton", "fecha": "2024-07-28", "lat": 50.4372, "lon": 5.9714},
    {"gp": "Gran Premio de los Países Bajos 2024", "circuito": "Circuit Zandvoort", "ciudad": "Zandvoort", "ganador": "Lando Norris", "fecha": "2024-08-25", "lat": 52.3888, "lon": 4.5409},
    {"gp": "Gran Premio de Italia 2024", "circuito": "Autodromo Nazionale di Monza", "ciudad": "Monza", "ganador": "Charles Leclerc", "fecha": "2024-09-01", "lat": 45.6156, "lon": 9.2811},
    {"gp": "Gran Premio de Azerbaiyán 2024", "circuito": "Baku City Circuit", "ciudad": "Bakú", "ganador": "Oscar Piastri", "fecha": "2024-09-15", "lat": 40.3725, "lon": 49.8533},
    {"gp": "Gran Premio de Singapur 2024", "circuito": "Marina Bay Street Circuit", "ciudad": "Singapur", "ganador": "Lando Norris", "fecha": "2024-09-22", "lat": 1.2914, "lon": 103.864},
    {"gp": "Gran Premio de Estados Unidos 2024", "circuito": "Circuit of the Americas", "ciudad": "Austin", "ganador": "Charles Leclerc", "fecha": "2024-10-20", "lat": 30.1328, "lon": -97.6411},
    {"gp": "Gran Premio de Ciudad de México 2024", "circuito": "Autódromo Hermanos Rodríguez", "ciudad": "Ciudad de México", "ganador": "Carlos Sainz", "fecha": "2024-10-27", "lat": 19.4042, "lon": -99.0907},
    {"gp": "Gran Premio de São Paulo 2024", "circuito": "Autódromo de Interlagos", "ciudad": "São Paulo", "ganador": "Max Verstappen", "fecha": "2024-11-03", "lat": -23.7036, "lon": -46.6997},
    {"gp": "Gran Premio de Las Vegas 2024", "circuito": "Las Vegas Strip Circuit", "ciudad": "Las Vegas", "ganador": "George Russell", "fecha": "2024-11-23", "lat": 36.1147, "lon": -115.1728},
    {"gp": "Gran Premio de Catar 2024", "circuito": "Losail International Circuit", "ciudad": "Lusail", "ganador": "Max Verstappen", "fecha": "2024-12-01", "lat": 25.4889, "lon": 51.4542},
    {"gp": "Gran Premio de Abu Dhabi 2024", "circuito": "Yas Marina Circuit", "ciudad": "Abu Dabi", "ganador": "Lando Norris", "fecha": "2024-12-08", "lat": 24.4672, "lon": 54.6031}
]

def render_logo_html(url, width=38, fallback_emoji="🏎️"):
    if url and isinstance(url, str) and url.startswith("http"):
        err_script = "this.style.display='none'; this.nextElementSibling.style.display='inline';"
        return f'<img src="{url}" width="{width}" style="border-radius: 8px; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.7)); background: rgba(255,255,255,0.03); padding: 4px; border: 1px solid rgba(255,255,255,0.1);" onerror="{err_script}"/><span style="display:none; font-size: {width}px;">{fallback_emoji}</span>'
    else:
        return f'<span style="font-size: {width}px;">{fallback_emoji}</span>'

def render_calendario_anual_2024():
    race_dates_set = {datetime.strptime(c["fecha"], "%Y-%m-%d").date() for c in CARRERAS_2024_DATOS}
    months_spanish = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio", 
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    calendar.setfirstweekday(calendar.SUNDAY)
    html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 18px; margin-top: 10px;'>"
    for month_idx in range(1, 13):
        month_name = months_spanish[month_idx - 1]
        cal = calendar.monthcalendar(2024, month_idx)
        html += f"""
        <div style='background: #080C16; border-radius: 14px; padding: 14px; border: 1px solid rgba(255,255,255,0.08);'>
            <div style='color: #FF1801; font-weight: 800; font-size: 1.05rem; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;'>{month_name}</div>
            <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center; margin-bottom: 8px;'>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>d</div>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>l</div>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>m</div>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>m</div>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>j</div>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>v</div>
                <div style='color: #64748B; font-size: 0.65rem; font-weight: 800;'>s</div>
            </div>
            <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center;'>
        """
        for week in cal:
            for day in week:
                if day == 0:
                    html += "<div></div>"
                else:
                    d_obj = datetime(2024, month_idx, day).date()
                    if d_obj in race_dates_set:
                        html += f"<div><div style='background: #38BDF8; color: #030508; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: 900; font-size: 0.75rem; box-shadow: 0 0 10px rgba(56,189,248,0.8);' title='Gran Premio de F1'>{day}</div></div>"
                    else:
                        html += f"<div style='padding: 3px 0; font-size: 0.8rem; color: #F1F5F9; font-weight: 500;'>{day}</div>"
        html += "</div></div>"
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
        response = requests.get(f"https://v1.formula-1.api-sports.io/teams/drivers?team={id_escuderia}", headers=HEADERS, timeout=10)
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

FANTASY_DB = {
    "Max Verstappen": {"costo": 30.5, "puntos": 437},
    "Lando Norris": {"costo": 26.0, "puntos": 374},
    "Charles Leclerc": {"costo": 25.0, "puntos": 356},
    "Oscar Piastri": {"costo": 22.0, "puntos": 292},
    "Carlos Sainz": {"costo": 21.5, "puntos": 290},
    "George Russell": {"costo": 20.0, "puntos": 245},
    "Lewis Hamilton": {"costo": 19.0, "puntos": 223},
    "Sergio Pérez": {"costo": 16.5, "puntos": 152},
    "Fernando Alonso": {"costo": 13.5, "puntos": 62},
    "Pierre Gasly": {"costo": 8.5, "puntos": 26},
    "Nico Hülkenberg": {"costo": 9.5, "puntos": 31},
    "Yuki Tsunoda": {"costo": 9.0, "puntos": 30},
    "Lance Stroll": {"costo": 8.5, "puntos": 24},
    "Esteban Ocon": {"costo": 8.5, "puntos": 23},
    "Kevin Magnussen": {"costo": 7.5, "puntos": 16},
    "Alex Albon": {"costo": 7.5, "puntos": 12},
    "Daniel Ricciardo": {"costo": 7.5, "puntos": 12},
    "Oliver Bearman": {"costo": 7.0, "puntos": 7},
    "Valtteri Bottas": {"costo": 6.0, "puntos": 0},
    "Zhou Guanyu": {"costo": 6.0, "puntos": 0}
}

if "df_puntos_state" not in st.session_state:
    st.session_state["df_puntos_state"] = pd.DataFrame([
        {"Piloto": "Max Verstappen", "Escudería": "Red Bull Racing", "Puntos": 437},
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

if "tiempo_inicio" not in st.session_state:
    st.session_state["tiempo_inicio"] = None

if "reaccion" not in st.session_state:
    st.session_state["reaccion"] = None

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
    "💵 Fantasy Optimizer", 
    "🛠️ Ing. Radio IA"
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

    # Panel de métricas clave (KPIs estilizados con altura uniforme)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        logo_html_str = render_logo_html(logo_activo, width=48, fallback_emoji="🏎️")
        st.markdown(f"""
            <div class='telemetry-card' style='display:flex; align-items:center; gap:16px; border-left: 5px solid #FF1801; padding: 22px; height: 100%;'>
                {logo_html_str}
                <div>
                    <h3 style='margin:0; font-size:1.05rem; font-weight:800; color: #FFFFFF;'>{nombre_activo}</h3>
                    <small style='color:#94A3B8; font-weight:600;'>{pais_activo} (Temporada 2024)</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px; height: 100%;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>EFECTIVIDAD PODIOS</small><h2 style='margin:6px 0 0 0; color:#10B981 !important; font-weight:900; font-size:1.8rem;'>{efectividad}%</h2></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px; height: 100%;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PROMEDIO PUNTOS / GP</small><h2 style='margin:6px 0 0 0; color:#F59E0B !important; font-weight:900; font-size:1.8rem;'>{promedio_puntos}</h2></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='telemetry-card' style='padding: 22px; height: 100%;'><small style='color:#94A3B8; font-weight:700; letter-spacing:1px;'>PUNTUACIÓN GLOBAL</small><h2 style='margin:6px 0 0 0; color:#FFFFFF !important; font-weight:900; font-size:1.8rem;'>{puntos_totales} pts</h2></div>", unsafe_allow_html=True)

    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📊 Clasificación y Gráfica Dinámica de Puntos 2024</div>", unsafe_allow_html=True)
    st.info("Modifica los valores numéricos de los puntos en la tabla interactiva y la gráfica se actualizará al instante en tiempo real.")

    # Inicialización de respaldo para el estado del editor de puntos general
    if "df_puntos_state" not in st.session_state:
        st.session_state["df_puntos_state"] = pd.DataFrame([
            {"Piloto": "Max Verstappen", "Puntos": 429},
            {"Piloto": "Lando Norris", "Puntos": 349},
            {"Piloto": "Charles Leclerc", "Puntos": 341},
            {"Piloto": "Oscar Piastri", "Puntos": 292},
            {"Piloto": "Carlos Sainz", "Puntos": 290}
        ])

    col_tabla, col_grafica = st.columns([1, 1.2])
    with col_tabla:
        st.write("✏️ **Edita los puntos directamente aquí:**")
        st.session_state["df_puntos_state"] = st.data_editor(
            st.session_state["df_puntos_state"], 
            num_rows="dynamic", 
            key="editor_puntos_2024", 
            use_container_width=True
        )

    with col_grafica:
        st.write("📈 **Gráfica de Columnas Dinámica:**")
        df_actual = st.session_state["df_puntos_state"]
        if not df_actual.empty and "Piloto" in df_actual.columns and "Puntos" in df_actual.columns:
            fig_dinamica = px.bar(
                df_actual, x="Piloto", y="Puntos", color="Puntos",
                color_continuous_scale="Reds", template="plotly_dark",
                title="Clasificación de Pilotos F1 2024 (Actualización en Vivo)"
            )
            fig_dinamica.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=10, l=10, r=10),
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig_dinamica, use_container_width=True, key="chart_puntos_dinamico")
        else:
            st.warning("Asegúrate de que las columnas 'Piloto' y 'Puntos' existan en la tabla.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📅 Calendario Oficial Completo F1 2024 (Carreras en Azul)</div>", unsafe_allow_html=True)
    st.write("Vista completa de los 12 meses de la temporada 2024 con los días de Gran Premio destacados en color azul.")
    render_calendario_anual_2024()
    st.markdown("</div>", unsafe_allow_html=True)

    # Diccionario con los pilotos oficiales de cada escudería para 2024
    PILOTOS_EQUIPOS_2024 = {
        "Red Bull Racing": [
            {"Piloto": "Max Verstappen", "País": "Netherlands", "Número": 1},
            {"Piloto": "Sergio Pérez", "País": "Mexico", "Número": 11}
        ],
        "Ferrari": [
            {"Piloto": "Charles Leclerc", "País": "Monaco", "Número": 16},
            {"Piloto": "Carlos Sainz", "País": "Spain", "Número": 55}
        ],
        "McLaren": [
            {"Piloto": "Lando Norris", "País": "United Kingdom", "Número": 4},
            {"Piloto": "Oscar Piastri", "País": "Australia", "Número": 81}
        ],
        "Mercedes": [
            {"Piloto": "Lewis Hamilton", "País": "United Kingdom", "Número": 44},
            {"Piloto": "George Russell", "País": "United Kingdom", "Número": 63}
        ],
        "Aston Martin": [
            {"Piloto": "Fernando Alonso", "País": "Spain", "Número": 14},
            {"Piloto": "Lance Stroll", "País": "Canada", "Número": 18}
        ],
        "RB": [
            {"Piloto": "Yuki Tsunoda", "País": "Japan", "Número": 22},
            {"Piloto": "Daniel Ricciardo", "País": "Australia", "Número": 3}
        ],
        "Haas": [
            {"Piloto": "Nico Hulkenberg", "País": "Germany", "Número": 27},
            {"Piloto": "Kevin Magnussen", "País": "Denmark", "Número": 20}
        ],
        "Alpine": [
            {"Piloto": "Pierre Gasly", "País": "France", "Número": 10},
            {"Piloto": "Esteban Ocon", "País": "France", "Número": 31}
        ],
        "Williams": [
            {"Piloto": "Alexander Albon", "País": "Thailand", "Número": 23},
            {"Piloto": "Logan Sargeant", "País": "United States", "Número": 2}
        ],
        "Kick Sauber": [
            {"Piloto": "Valtteri Bottas", "País": "Finland", "Número": 77},
            {"Piloto": "Zhou Guanyu", "País": "China", "Número": 24}
        ]
    }

    col_plantilla, col_mapa = st.columns(2)
    with col_plantilla:
        st.markdown(f"<div class='telemetry-card'><div class='section-header'>👥 Alineación Oficial de Pilotos - {equipo_seleccionado_nombre}</div>", unsafe_allow_html=True)
        
        pilotos_equipo_info = PILOTOS_EQUIPOS_2024.get(equipo_seleccionado_nombre, [])
        if pilotos_equipo_info:
            df_final = pd.DataFrame(pilotos_equipo_info)
            st.dataframe(df_final, hide_index=True, use_container_width=True)
        else:
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
            st.map(df_mapa, zoom=10)
        else:
            df_mapa = pd.DataFrame({'lat': [44.5385], 'lon': [10.8643]})
            st.map(df_mapa, zoom=10)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⚔️ Batalla Cara a Cara (Teammate / Grid Battle 2024)</div>", unsafe_allow_html=True)
    st.write("Comparativa dinámica de rendimiento y telemetría cruzada seleccionando libremente entre **cualquier piloto de la parrilla 2024**.")
    
    col_p1, col_vs, col_p2 = st.columns([5, 1, 5])
    with col_p1:
        sel_h2h_a = st.selectbox("Seleccionar Piloto A (Referencia):", TODOS_OS_PILOTOS_2024, index=0, key="h2h_piloto_a")
    with col_vs:
        st.markdown("<div style='text-align: center; padding-top: 30px;'><h2 style='color: #FF1801; font-weight: 900;'>VS</h2></div>", unsafe_allow_html=True)
    with col_p2:
        sel_h2h_b = st.selectbox("Seleccionar Piloto B (Rival):", TODOS_OS_PILOTOS_2024, index=min(1, len(TODOS_OS_PILOTOS_2024)-1), key="h2h_piloto_b")

    if sel_h2h_a == sel_h2h_b:
        st.warning("⚠️ Has seleccionado al mismo piloto en ambos lados. Selecciona pilotos diferentes para una comparativa H2H real.")

    seed_a = sum(ord(c) for c in sel_h2h_a)
    seed_b = sum(ord(c) for c in sel_h2h_b)
    
    vel_a_val = round(330 + (seed_a % 15) + np.sin(seed_a)*3, 1)
    vel_b_val = round(330 + (seed_b % 15) + np.sin(seed_b)*3, 1)
    
    pts_a_val = FANTASY_DB.get(sel_h2h_a, {"puntos": 50})["puntos"]
    pts_b_val = FANTASY_DB.get(sel_h2h_b, {"puntos": 50})["puntos"]

    q3_a = (seed_a % 40) + 60
    q3_b = (seed_b % 40) + 60

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""
            <div style='background: rgba(255,24,1,0.03); padding: 22px; border-radius: 14px; border: 1px solid rgba(255,24,1,0.3);'>
                <h3 style='color: #FFFFFF; margin-bottom: 5px; text-align: center;'>🏎️ {sel_h2h_a}</h3>
                <hr style='border-color: rgba(255,255,255,0.1); margin: 12px 0;'>
                <p style='font-size: 0.9rem; margin: 8px 0;'>⚡ Velocidad Punta: <b style='color: #38BDF8;'>{vel_a_val} km/h</b></p>
                <p style='font-size: 0.9rem; margin: 8px 0;'>⏱️ Ritmo Q3: <b style='color: #F59E0B;'>1:19.{seed_a % 90}</b></p>
                <p style='font-size: 0.9rem; margin: 8px 0;'>🏆 Puntos Temporada: <b style='color: #10B981;'>{pts_a_val} pts</b></p>
            </div>
        """, unsafe_allow_html=True)
    with col_res2:
        st.markdown(f"""
            <div style='background: rgba(59,130,246,0.03); padding: 22px; border-radius: 14px; border: 1px solid rgba(59,130,246,0.3);'>
                <h3 style='color: #FFFFFF; margin-bottom: 5px; text-align: center;'>🏎️ {sel_h2h_b}</h3>
                <hr style='border-color: rgba(255,255,255,0.1); margin: 12px 0;'>
                <p style='font-size: 0.9rem; margin: 8px 0;'>⚡ Velocidad Punta: <b style='color: #38BDF8;'>{vel_b_val} km/h</b></p>
                <p style='font-size: 0.9rem; margin: 8px 0;'>⏱️ Ritmo Q3: <b style='color: #F59E0B;'>1:19.{seed_b % 90}</b></p>
                <p style='font-size: 0.9rem; margin: 8px 0;'>🏆 Puntos Temporada: <b style='color: #10B981;'>{pts_b_val} pts</b></p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfica comparativa visual Plotly con formato ordenado (tidy dataframe)
    df_h2h = pd.DataFrame({
        "Métrica": ["Puntos 2024", "Velocidad Punta (km/h)", "Índice Q3"],
        sel_h2h_a: [pts_a_val, vel_a_val, q3_a],
        sel_h2h_b: [pts_b_val, vel_b_val, q3_b]
    })
    
    df_melted = df_h2h.melt(id_vars=["Métrica"], var_name="Piloto", value_name="Valor")

    fig_h2h = px.bar(
        df_melted, x="Métrica", y="Valor", color="Piloto", barmode="group",
        template="plotly_dark", title="Comparativa Gráfica Directa H2H",
        color_discrete_map={sel_h2h_a: "#FF1801", sel_h2h_b: "#38BDF8"}
    )
    fig_h2h.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20), height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_h2h, use_container_width=True, key=f"chart_h2h_{sel_h2h_a}_{sel_h2h_b}")

    # Veredicto dinámico basado en puntos
    if pts_a_val > pts_b_val:
        ganador_pts = sel_h2h_a
    elif pts_b_val > pts_a_val:
        ganador_pts = sel_h2h_b
    else:
        ganador_pts = "Empate técnico"

    st.markdown(f"""
        <div style='background: rgba(255,255,255,0.02); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); text-align: center; margin-top: 15px;'>
            <span style='color: #94A3B8; font-size: 0.85rem;'>🏁 <b>Veredicto H2H 2024:</b> En la acumulada de puntos de la temporada, el piloto con ventaja es <b style='color: #10B981;'>{ganador_pts}</b>.</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
with tab3:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🗺️ Calendario y Geolocalización de los Grandes Premios (2024)</div>", unsafe_allow_html=True)
    st.write("Selecciona cualquier Gran Premio de la temporada para consultar los detalles clave del circuito y su ubicación exacta en el mapa.")

    # Selector limpio y directo
    nombres_gps = [item["gp"] for item in CARRERAS_2024_DATOS]
    gp_seleccionado = st.selectbox("Selecciona un Gran Premio:", nombres_gps, key="selector_gp_simple_v3")

    # Extraer datos del GP activo
    gp_info = next(item for item in CARRERAS_2024_DATOS if item["gp"] == gp_seleccionado)

    # Formatear fecha de forma elegante
    fecha_dt = datetime.strptime(gp_info['fecha'], "%Y-%m-%d")
    fecha_formateada = fecha_dt.strftime("%d de %B, %Y")

    # Distribución en dos columnas claras con altura equilibrada
    col_det, col_map = st.columns([1, 1])

    with col_det:
        st.markdown(f"""
            <div style='background: rgba(8, 12, 22, 0.7); padding: 22px; border-radius: 12px; border: 1px solid rgba(255,24,1,0.3); height: 280px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div>
                    <h3 style='color: #FF1801; margin-top: 0; font-size: 1.2rem;'>🏁 {gp_info['gp']}</h3>
                    <p style='margin: 6px 0;'><b>Circuito:</b> {gp_info['circuito']}</p>
                    <p style='margin: 6px 0;'><b>Ubicación:</b> {gp_info['ciudad']}</p>
                    <p style='margin: 6px 0;'><b>Fecha:</b> {fecha_formateada}</p>
                </div>
                <div>
                    <p style='margin: 0; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08);'><b>Ganador:</b> <span style='color: #F59E0B; font-weight: bold;'>🏆 {gp_info['ganador']}</span></p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_map:
        st.markdown("<p style='font-weight: 600; margin-bottom: 6px;'>📍 Ubicación en el Mapa:</p>", unsafe_allow_html=True)
        df_mapa = pd.DataFrame({'lat': [gp_info['lat']], 'lon': [gp_info['lon']]})
        st.map(df_mapa, zoom=10, height=245)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 25px 0;'>", unsafe_allow_html=True)
    
    # Encabezado del resumen con diseño amigable para el filtro de pilotos
    st.markdown("<h4 style='color: #FFFFFF; font-weight: 700; margin-bottom: 15px;'>📋 Resumen Interactivo de Carreras 2024</h4>", unsafe_allow_html=True)
    
    # Obtener lista única de ganadores de forma ordenada
    ganadores_disponibles = ["Todos los Pilotos"] + sorted(list(set(item['ganador'] for item in CARRERAS_2024_DATOS)))
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        piloto_filtro = st.selectbox("Selecciona un corredor:", ganadores_disponibles, key="select_filtro_piloto_victorias")

    # Crear DataFrame base
    df_carreras = pd.DataFrame(CARRERAS_2024_DATOS)[["gp", "circuito", "fecha", "ganador"]]
    df_carreras.columns = ["Gran Premio", "Circuito Oficial", "Fecha", "Ganador del GP"]
    
    # Filtrar dinámicamente si se selecciona un piloto específico
    if piloto_filtro != "Todos los Pilotos":
        df_carreras = df_carreras[df_carreras["Ganador del GP"] == piloto_filtro]
        total_victorias = len(df_carreras)
        with col_f2:
            st.markdown(f"""
                <div style='background: rgba(255, 24, 1, 0.15); border: 1px solid rgba(255, 24, 1, 0.4); padding: 8px 15px; border-radius: 8px; text-align: center; margin-top: 24px;'>
                    <span style='font-size: 0.75rem; color: #94A3B8; display: block;'>VICTORIAS FILTRADAS</span>
                    <strong style='color: #FF1801; font-size: 1.1rem;'>{total_victorias} Gp's</strong>
                </div>
            """, unsafe_allow_html=True)

    # Tabla interactiva moderna
    st.dataframe(
        df_carreras, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Gran Premio": st.column_config.TextColumn("Gran Premio", width="medium"),
            "Circuito Oficial": st.column_config.TextColumn("Circuito Oficial", width="large"),
            "Fecha": st.column_config.TextColumn("Fecha", width="small"),
            "Ganador del GP": st.column_config.TextColumn("Ganador del GP", width="medium")
        }
    )

    st.markdown("</div>", unsafe_allow_html=True)
    
with tab4:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📈 Análisis de Telemetría Avanzada (Sector a Sector)</div>", unsafe_allow_html=True)
    st.write(
        "Análisis cruzado de los inputs del piloto: Acelerador, Freno, Velocidad y Diferencial Directo "
        "mediante la integración simulada de FastF1."
    )
    
    # --- DICCIONARIO DE COLORES OFICIALES DE ESCUDERÍAS ---
    DRIVER_COLORS = {
        "Max Verstappen": "#0600EF", "Sergio Pérez": "#1E41FF",
        "Lewis Hamilton": "#00D2BE", "George Russell": "#00D2BE",
        "Charles Leclerc": "#DC0000", "Carlos Sainz": "#DC0000",
        "Lando Norris": "#FF8000", "Oscar Piastri": "#FF8000",
        "Fernando Alonso": "#006F62", "Lance Stroll": "#006F62",
        "Pierre Gasly": "#0090FF", "Esteban Ocon": "#0090FF",
        "Alex Albon": "#005AFF", "Yuki Tsunoda": "#2B4562",
        "Nico Hülkenberg": "#B6BABD", "Kevin Magnussen": "#B6BABD",
        "Valtteri Bottas": "#52E252", "Zhou Guanyu": "#52E252",
        "Daniel Ricciardo": "#2B4562", "Oliver Bearman": "#DC0000"
    }

    # --- INICIALIZAR ESTADOS DE SESIÓN PARA LOS SELECTORES ---
    if "tel_driver_1" not in st.session_state:
        st.session_state["tel_driver_1"] = "Max Verstappen"
    if "tel_driver_2" not in st.session_state:
        st.session_state["tel_driver_2"] = "Lando Norris"
    if "tel_session" not in st.session_state:
        st.session_state["tel_session"] = "Q3 - Clasificación"

    # --- DUELOS / PRESETS RÁPIDOS ---
    st.markdown("<b style='color: #38BDF8; font-size: 0.9rem;'>⚡ Duelos Destacados en Pista (Presets):</b>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        if st.button("🔥 Verstappen vs Norris (Batalla por el Título)", use_container_width=True, key="btn_duel_1"):
            st.session_state["tel_driver_1"] = "Max Verstappen"
            st.session_state["tel_driver_2"] = "Lando Norris"
            st.rerun()
    with col_p2:
        if st.button("🔴 Hamilton vs Leclerc (Legado Ferrari/Merc)", use_container_width=True, key="btn_duel_2"):
            st.session_state["tel_driver_1"] = "Lewis Hamilton"
            st.session_state["tel_driver_2"] = "Charles Leclerc"
            st.rerun()
    with col_p3:
        if st.button("⚡ Piastri vs Russell (Nueva Generación)", use_container_width=True, key="btn_duel_3"):
            st.session_state["tel_driver_1"] = "Oscar Piastri"
            st.session_state["tel_driver_2"] = "George Russell"
            st.rerun()

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    # --- SELECTORES DE PILOTOS Y SESIÓN ---
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        driver1 = st.selectbox("Piloto 1 (Referencia):", TODOS_OS_PILOTOS_2024, key="tel_driver_1", help="Piloto base de comparación.")
        color1 = DRIVER_COLORS.get(driver1, "#FF1801")
    with col_t2:
        driver2 = st.selectbox("Piloto 2 (Comparativa):", TODOS_OS_PILOTOS_2024, key="tel_driver_2", help="Piloto evaluado contra la referencia.")
        color2 = DRIVER_COLORS.get(driver2, "#38BDF8")
    with col_t3:
        session = st.selectbox("Sesión F1:", ["Q3 - Clasificación", "Carrera", "FP2"], key="tel_session")

    # --- GENERACIÓN DE DATOS DINÁMICOS ---
    x = np.linspace(0, 100, 600)
    
    seed1 = sum(ord(c) for c in driver1)
    seed2 = sum(ord(c) for c in driver2)
    
    fase1 = (seed1 % 12) * 0.08
    fase2 = (seed2 % 12) * 0.08
    
    speed1 = 305 + (seed1 % 18) - 150 * np.exp(-x/16) + 35 * np.sin(x/3.5 + fase1) + np.random.normal(0, 1.2, 600)
    throttle1 = np.where(np.sin(x/3.5 + fase1) > -0.15, 100, 0) + np.random.normal(0, 2, 600)
    brake1 = np.where(np.sin(x/3.5 + fase1) < -0.65, 100, 0)
    
    speed2 = 305 + (seed2 % 18) - 150 * np.exp(-x/16) + 35 * np.sin(x/3.5 + fase2) + np.random.normal(0, 1.2, 600)
    throttle2 = np.where(np.sin(x/3.5 + fase2) > -0.15, 100, 0) + np.random.normal(0, 2, 600)
    brake2 = np.where(np.sin(x/3.5 + fase2) < -0.65, 100, 0)

    # Diferencial de velocidad instantáneo (Piloto 2 menos Piloto 1)
    speed_diff = speed2 - speed1

    max_speed_1 = round(max(speed1), 1)
    max_speed_2 = round(max(speed2), 1)
    delta_max_speed = round(max_speed_1 - max_speed_2, 1)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- KPIS / MÉTRICAS RÁPIDAS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label=f"Vmax {driver1.split()[-1]}", value=f"{max_speed_1} km/h")
    with m2:
        st.metric(label=f"Vmax {driver2.split()[-1]}", value=f"{max_speed_2} km/h")
    with m3:
        st.metric(label="Delta Vmax Pura", value=f"{delta_max_speed:+g} km/h", delta_color="normal" if delta_max_speed >= 0 else "inverse")
    with m4:
        st.metric(label="Ganancia Máxima", value=f"{round(max(speed_diff), 1)} km/h", delta="Punto álgido P2")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICA MULTI-SUBPLOT DE TELEMETRÍA (4 PANELES) ---
    fig_tel = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05,
        subplot_titles=("Velocidad (km/h)", "Acelerador (%)", "Freno (%)", f"Diferencial de Velocidad ({driver2.split()[-1]} vs {driver1.split()[-1]}) (km/h)")
    )
    
    # Panel 1: Velocidad
    fig_tel.add_trace(go.Scatter(x=x, y=speed1, name=driver1, line=dict(color=color1, width=2.5)), row=1, col=1)
    fig_tel.add_trace(go.Scatter(x=x, y=speed2, name=driver2, line=dict(color=color2, width=2.5)), row=1, col=1)
    
    # Panel 2: Acelerador
    fig_tel.add_trace(go.Scatter(x=x, y=np.clip(throttle1, 0, 100), showlegend=False, line=dict(color=color1, width=2)), row=2, col=1)
    fig_tel.add_trace(go.Scatter(x=x, y=np.clip(throttle2, 0, 100), showlegend=False, line=dict(color=color2, width=2)), row=2, col=1)
    
    # Panel 3: Freno
    fig_tel.add_trace(go.Scatter(x=x, y=brake1, showlegend=False, line=dict(color=color1, width=2)), row=3, col=1)
    fig_tel.add_trace(go.Scatter(x=x, y=brake2, showlegend=False, line=dict(color=color2, width=2)), row=3, col=1)

    # Panel 4: Diferencial de Velocidad Instantáneo (Verde = P2 más rápido / Rojo = P2 más lento)
    diff_verde = np.where(speed_diff >= 0, speed_diff, 0)
    diff_rojo = np.where(speed_diff < 0, speed_diff, 0)

    fig_tel.add_trace(go.Scatter(
        x=x, y=diff_verde, name=f"{driver2.split()[-1]} más rápido",
        line=dict(color='#10B981', width=2), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)'
    ), row=4, col=1)
    
    fig_tel.add_trace(go.Scatter(
        x=x, y=diff_rojo, name=f"{driver2.split()[-1]} más lento",
        line=dict(color='#EF4444', width=2), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)'
    ), row=4, col=1)

    fig_tel.update_layout(
        height=820, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=20, l=10, r=10), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1)
    )
    fig_tel.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)', zeroline=True, zerolinecolor='rgba(255,255,255,0.4)')
    fig_tel.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)', title_text="<b>Distancia del Circuito (m)</b>", row=4, col=1)

    st.plotly_chart(fig_tel, use_container_width=True, key="chart_telemetry_pro_4panels_speeddiff")
    st.markdown("</div>", unsafe_allow_html=True)
    
with tab5:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⛅ AWS Insights: Advanced Weather Radar & Track Evolution</div>", unsafe_allow_html=True)
    st.write(
        "Simulador atmosférico predictivo y análisis de desgaste de neumáticos por circuito. "
        "Utiliza los escenarios meteorológicos rápidos o personaliza las variables para evaluar la ventana táctica Pirelli."
    )
    
    # --- INICIALIZAR ESTADOS DE SESIÓN PARA EL CLIMA ---
    if "nw_temp" not in st.session_state:
        st.session_state["nw_temp"] = 25
    if "nw_rain" not in st.session_state:
        st.session_state["nw_rain"] = 15
    if "nw_hum" not in st.session_state:
        st.session_state["nw_hum"] = 45
    if "nw_wind" not in st.session_state:
        st.session_state["nw_wind"] = 12

    # --- ESCENARIOS METEOROLÓGICOS RÁPIDOS (PRESETS) ---
    st.markdown("<b style='color: #38BDF8; font-size: 0.9rem;'>⚡ Escenarios Atmosféricos Rápidos:</b>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        if st.button("☀️ Calor Extremo / Verano", use_container_width=True, key="btn_weather_hot"):
            st.session_state["nw_temp"] = 36
            st.session_state["nw_rain"] = 5
            st.session_state["nw_hum"] = 30
            st.session_state["nw_wind"] = 8
            st.rerun()
    with col_p2:
        if st.button("🌧️ Tormenta Inminente", use_container_width=True, key="btn_weather_rain"):
            st.session_state["nw_temp"] = 21
            st.session_state["nw_rain"] = 85
            st.session_state["nw_hum"] = 90
            st.session_state["nw_wind"] = 28
            st.rerun()
    with col_p3:
        if st.button("🌙 Nocturna / Pista Fría", use_container_width=True, key="btn_weather_cold"):
            st.session_state["nw_temp"] = 16
            st.session_state["nw_rain"] = 10
            st.session_state["nw_hum"] = 65
            st.session_state["nw_wind"] = 10
            st.rerun()

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    circuitos_f1 = {
        "Bahrain International Circuit (Sakhir)": {"factor_abrasion": 1.4, "tipo": "Alta Abrasión"},
        "Jeddah Corniche Circuit (Arabia Saudita)": {"factor_abrasion": 0.9, "tipo": "Urbano Rápido / Media"},
        "Albert Park Circuit (Australia)": {"factor_abrasion": 1.0, "tipo": "Urbano / Semi-permanente"},
        "Suzuka Circuit (Japón)": {"factor_abrasion": 1.2, "tipo": "Alta Exigencia / Lateral"},
        "Shanghai International Circuit (China)": {"factor_abrasion": 1.25, "tipo": "Exigente Frontal"},
        "Miami International Autodrome (Miami)": {"factor_abrasion": 1.1, "tipo": "Superficie Nueva / Térmica"},
        "Autodromo Internazionale Enzo e Dino Ferrari - Imola (Emilia-Romaña)": {"factor_abrasion": 1.05, "tipo": "Clásico / Técnico"},
        "Circuit de Monaco (Mónaco)": {"factor_abrasion": 0.7, "tipo": "Baja Abrasión / Urbano"},
        "Circuit Gilles Villeneuve (Canadá)": {"factor_abrasion": 0.85, "tipo": "Frenadas Severas / Baja Abrasión"},
        "Circuit de Barcelona-Catalunya (España)": {"factor_abrasion": 1.3, "tipo": "Técnico / Severo"},
        "Red Bull Ring (Austria)": {"factor_abrasion": 1.0, "tipo": "Equilibrado / Tracción"},
        "Silverstone Circuit (Gran Bretaña)": {"factor_abrasion": 1.35, "tipo": "Alta Carga Lateral"},
        "Hungaroring (Hungría)": {"factor_abrasion": 1.1, "tipo": "Alta Tracción / Curvas Lentas"},
        "Circuit de Spa-Francorchamps (Bélgica)": {"factor_abrasion": 1.15, "tipo": "Alta Carga / Mixto"},
        "Circuit Zandvoort (Países Bajos)": {"factor_abrasion": 1.25, "tipo": "Peraltes / Carga Severa"},
        "Autodromo Nazionale Monza (Italia)": {"factor_abrasion": 0.8, "tipo": "Baja Carga / Velocidad Pura"},
        "Baku City Circuit (Azerbaiyán)": {"factor_abrasion": 0.85, "tipo": "Urbano / Frenadas Fuertes"},
        "Marina Bay Street Circuit (Singapur)": {"factor_abrasion": 1.0, "tipo": "Urbano Nocturno / Térmico"},
        "Circuit of the Americas (Estados Unidos)": {"factor_abrasion": 1.2, "tipo": "Exigente / Mixto"},
        "Autódromo Hermanos Rodríguez (México)": {"factor_abrasion": 0.9, "tipo": "Gran Altitud / Refrigeración"},
        "Autódromo José Carlos Pace - Interlagos (São Paulo)": {"factor_abrasion": 1.15, "tipo": "Desnivel / Desgaste Medio"},
        "Las Vegas Strip Circuit (Las Vegas)": {"factor_abrasion": 0.75, "tipo": "Urbano Frío / Baja Adherencia"},
        "Lusail International Circuit (Catar)": {"factor_abrasion": 1.35, "tipo": "Alta Abrasión / Curvas Rápidas"},
        "Yas Marina Circuit (Abu Dhabi)": {"factor_abrasion": 1.0, "tipo": "Tracción / Nocturno"}
    }

    c_circ1, c_w1, c_w2, c_w3, c_w4 = st.columns([1.5, 1, 1, 1, 1])
    with c_circ1:
        circuito_seleccionado = st.selectbox("🏁 Circuito Oficial", list(circuitos_f1.keys()), key="nw_circuit")
    with c_w1:
        temp_amb = st.slider("🌡️ Temp. Ambiente (°C)", min_value=10, max_value=45, key="nw_temp", help="Temperatura del aire en el pit lane.")
    with c_w2:
        prob_lluvia = st.slider("🌧️ Prob. de Lluvia (%)", min_value=0, max_value=100, key="nw_rain", help="Probabilidad de precipitación según radar meteorológico AWS.")
    with c_w3:
        humedad = st.slider("💧 Humedad Relativa (%)", min_value=10, max_value=100, key="nw_hum", help="Nivel de vapor de agua en el ambiente.")
    with c_w4:
        viento = st.slider("💨 Viento (km/h)", min_value=0, max_value=60, key="nw_wind", help="Velocidad e intensidad de ráfagas en recta principal.")

    impacto_sol = 15 if prob_lluvia < 30 and humedad < 60 else (5 if prob_lluvia < 60 else 0)
    temp_pista = temp_amb + impacto_sol - (viento * 0.15)
    temp_pista = round(max(temp_amb, temp_pista), 1)

    indice_agarre = 1.0 - (abs(temp_pista - 35) * 0.008) - (prob_lluvia * 0.007)
    indice_agarre = round(max(0.1, min(1.0, indice_agarre)), 2)

    if prob_lluvia > 75 or (prob_lluvia > 50 and indice_agarre < 0.45):
        neumatico_rec, razon_rec, color_borde = "🔵 Lluvia Extrema (Wet)", "Alto riesgo de aquaplaning. Pista inundada.", "#0066FF"
        base_desgaste = 0.5
    elif prob_lluvia > 25 or indice_agarre < 0.65:
        neumatico_rec, razon_rec, color_borde = "🟢 Intermedios (Inters)", "Asfalto mixto / Condiciones de transición.", "#10B981"
        base_desgaste = 1.2
    elif temp_pista > 45:
        neumatico_rec, razon_rec, color_borde = "⚪ Duros (Hard C1/C2)", "Alta abrasión y riesgo severo de blistering térmico.", "#FFFFFF"
        base_desgaste = 1.8
    elif temp_pista < 26:
        neumatico_rec, razon_rec, color_borde = "🔴 Blandos (Soft C4/C5)", "Necesidad de encender gomas rápido por baja temperatura.", "#FF1801"
        base_desgaste = 3.5
    else:
        neumatico_rec, razon_rec, color_borde = "🟡 Medios (Medium C3)", "Ventana operativa ideal. Balance perfecto degradación/agarre.", "#F59E0B"
        base_desgaste = 2.3

    info_circuito = circuitos_f1[circuito_seleccionado]
    factor_pista = info_circuito["factor_abrasion"]
    desgaste_por_vuelta = round(base_desgaste * factor_pista * (1 + (max(0, temp_pista - 30) * 0.01)), 2)
    vida_util_vueltas = int(100 / max(0.5, desgaste_por_vuelta))

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # --- INDICADORES Y TARJETA RESUMEN ---
    col_g1, col_g2, col_g3 = st.columns([1, 1, 1.2])
    with col_g1:
        fig_grip = go.Figure(go.Indicator(
            mode="gauge+number",
            value=indice_agarre * 100,
            title={'text': "Nivel de Agarre (Grip Index)", 'font': {'color': '#94A3B8', 'size': 16}},
            number={'suffix': "%", 'font': {'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': color_borde},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 40], 'color': "rgba(255, 24, 1, 0.2)"},
                    {'range': [40, 75], 'color': "rgba(245, 158, 11, 0.2)"},
                    {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.2)"}],
            }
        ))
        fig_grip.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=260, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_grip, use_container_width=True, key="chart_gauge_grip_pro")

    with col_g2:
        fig_temp = go.Figure(go.Indicator(
            mode="gauge+number",
            value=temp_pista,
            title={'text': "Temperatura de Asfalto", 'font': {'color': '#94A3B8', 'size': 16}},
            number={'suffix': "°C", 'font': {'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, 60], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#FF1801" if temp_pista > 45 else ("#38BDF8" if temp_pista < 25 else "#F59E0B")},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 25], 'color': "rgba(56, 189, 248, 0.2)"},
                    {'range': [25, 45], 'color': "rgba(16, 185, 129, 0.2)"},
                    {'range': [45, 60], 'color': "rgba(255, 24, 1, 0.2)"}],
            }
        ))
        fig_temp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=260, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_temp, use_container_width=True, key="chart_gauge_temp_pro")

    with col_g3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95)); padding: 22px; border-radius: 12px; height: 260px; display: flex; flex-direction: column; justify-content: center; border-left: 4px solid {color_borde}; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                <span style='color: #94A3B8; font-weight: 700; font-size: 0.75rem; letter-spacing: 1.5px; text-transform: uppercase;'>DESGASTE ESTIMADO POR CIRCUITO</span>
                <div style='display: flex; justify-content: space-between; align-items: baseline; margin-top: 15px;'>
                    <span style='color: #E2E8F0; font-size: 0.95rem;'>Tasa por vuelta:</span>
                    <strong style='color: #FFFFFF; font-size: 1.35rem;'>{desgaste_por_vuelta}% /vta</strong>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: baseline; margin-top: 10px;'>
                    <span style='color: #E2E8F0; font-size: 0.95rem;'>Vida útil estimada:</span>
                    <strong style='color: #10B981; font-size: 1.35rem;'>~{vida_util_vueltas} vueltas</strong>
                </div>
                <div style='margin-top: 15px; font-size: 0.85rem; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;'>
                    Perfil de pista: <span style='color: #F8FAFC; font-weight: 500;'>{info_circuito["tipo"]}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- BANNER DE RECOMENDACIÓN PIRELLI ---
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95)); padding: 20px 24px; border-radius: 12px; border-left: 6px solid {color_borde}; border: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; margin-top: 20px; margin-bottom: 25px;'>
            <div>
                <span style='color: #94A3B8; font-weight: 800; font-size: 0.75rem; letter-spacing: 1.5px; text-transform: uppercase;'>RECOMENDACIÓN ESTRATÉGICA PIRELLI • {circuito_seleccionado.split('(')[0]}</span>
                <h3 style='color: {color_borde}; margin: 5px 0 0 0; font-weight: 900;'>{neumatico_rec}</h3>
                <p style='color: #E2E8F0; margin: 4px 0 0 0; font-size: 0.9rem;'>{razon_rec}</p>
            </div>
            <div style='text-align: right; font-size: 2.2rem;'>
                ⚙️
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- GRÁFICA DE EVOLUCIÓN DE PISTA DURANTE EL STINT ---
    st.markdown("<b style='color: #FFFFFF; font-size: 0.95rem;'>📈 Simulación de Evolución de Agarre en el Stint (Primeras 30 Vueltas):</b>", unsafe_allow_html=True)
    
    vueltas_sim = list(range(1, 31))
    grip_evolucion = [round(min(100, max(20, (indice_agarre * 100) + (v * 0.4) if v <= 8 else (indice_agarre * 100) + 3.2 - ((v - 8) * (desgaste_por_vuelta * 0.15)))), 1) for v in vueltas_sim]
    
    df_evolucion = pd.DataFrame({
        "Vuelta": vueltas_sim,
        "Índice de Agarre Proyectado (%)": grip_evolucion
    })

    fig_evo = px.line(
        df_evolucion, x="Vuelta", y="Índice de Agarre Proyectado (%)",
        markers=True,
        template="plotly_dark"
    )
    fig_evo.update_traces(line_color=color_borde, line_width=3, marker_size=7)
    fig_evo.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=10, l=10, r=10),
        height=280,
        xaxis_title="<b>Vueltas de Carrera</b>",
        yaxis_title="<b>Nivel de Adherencia (%)</b>",
        yaxis=dict(range=[0, 105])
    )
    fig_evo.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)')
    fig_evo.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)')

    st.plotly_chart(fig_evo, use_container_width=True, key="chart_track_evolution_pro")

    st.markdown("</div>", unsafe_allow_html=True)
    
with tab6:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>💵 Cost Cap War Room & Gestor Financiero FIA (Edición Élite)</div>", unsafe_allow_html=True)
    st.write(
        "Centro de control financiero avanzado. Administra el tope presupuestario personalizado, "
        "controla daños por accidentes imprevistos y evalúa las restricciones de túnel de viento (Regla ATR)."
    )

    # --- INICIALIZAR ESTADOS DE SESIÓN PARA LOS WIDGETS ---
    if "input_cc_base" not in st.session_state:
        st.session_state["input_cc_base"] = 135.0
    if "slider_cc_aero" not in st.session_state:
        st.session_state["slider_cc_aero"] = 48.5
    if "slider_cc_motor" not in st.session_state:
        st.session_state["slider_cc_motor"] = 35.0
    if "slider_cc_chasis" not in st.session_state:
        st.session_state["slider_cc_chasis"] = 25.0
    if "slider_cc_ops" not in st.session_state:
        st.session_state["slider_cc_ops"] = 18.0
    if "slider_cc_crash" not in st.session_state:
        st.session_state["slider_cc_crash"] = 4.0

    # --- PRESETS FINANCIEROS RÁPIDOS (ACTUALIZAN DIRECTAMENTE LAS LLAVES DE LOS WIDGETS) ---
    st.markdown("<b style='color: #38BDF8; font-size: 0.9rem;'>⚡ Estrategias Financieras Rápidas (Presets):</b>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        if st.button("🚀 Desarrollo Agresivo (Alto Riesgo)", use_container_width=True, key="btn_cc_agresivo"):
            st.session_state["slider_cc_aero"] = 62.0
            st.session_state["slider_cc_motor"] = 42.0
            st.session_state["slider_cc_chasis"] = 32.0
            st.session_state["slider_cc_ops"] = 22.0
            st.session_state["slider_cc_crash"] = 6.5
            st.session_state["input_cc_base"] = 135.0
            st.rerun()
            
    with col_p2:
        if st.button("⚖️ Fábrica Equilibrada (Estándar)", use_container_width=True, key="btn_cc_equilibrado"):
            st.session_state["slider_cc_aero"] = 48.5
            st.session_state["slider_cc_motor"] = 35.0
            st.session_state["slider_cc_chasis"] = 25.0
            st.session_state["slider_cc_ops"] = 18.0
            st.session_state["slider_cc_crash"] = 4.0
            st.session_state["input_cc_base"] = 135.0
            st.rerun()
            
    with col_p3:
        if st.button("🛡️ Modo Supervivencia / Ahorro", use_container_width=True, key="btn_cc_ahorro"):
            st.session_state["slider_cc_aero"] = 35.0
            st.session_state["slider_cc_motor"] = 25.0
            st.session_state["slider_cc_chasis"] = 18.0
            st.session_state["slider_cc_ops"] = 12.0
            st.session_state["slider_cc_crash"] = 2.0
            st.session_state["input_cc_base"] = 135.0
            st.rerun()

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    # --- CONTROLES Y SLIDERS CON AYUDA (HELP) ---
    col_cc1, col_cc2 = st.columns(2)
    with col_cc1:
        presupuesto_base = st.number_input(
            "Límite Personalizado / Base ($M):", 
            min_value=50.0, max_value=300.0, step=0.5, 
            key="input_cc_base",
            help="Establece el tope presupuestario total autorizado (Límite FIA estándar: $135M)."
        )
        gasto_aero = st.slider(
            "Desarrollo Aerodinámico y Túnel ($M):", 
            min_value=10.0, max_value=150.0, step=0.5, 
            key="slider_cc_aero",
            help="Invierte en carga aerodinámica y CFD. Mejora significativamente el paso por curva y el rendimiento general."
        )
        gasto_motor = st.slider(
            "Unidad de Potencia e Integración ($M):", 
            min_value=10.0, max_value=150.0, step=0.5, 
            key="slider_cc_motor",
            help="Optimiza la fiabilidad y potencia de la Power Unit. Afecta la velocidad punta en rectas y la resistencia mecánica."
        )
        gasto_crash = st.slider(
            "Impacto por Accidentes y Daños (Crash Damage) ($M):", 
            min_value=0.0, max_value=25.0, step=0.5, 
            key="slider_cc_crash",
            help="Reserva financiera destinada a reparar chasis destruidos, alerones y piezas rotas por incidentes en pista."
        )

    with col_cc2:
        gasto_chasis = st.slider(
            "Chasis, Manufactura y Peso ($M):", 
            min_value=10.0, max_value=150.0, step=0.5, 
            key="slider_cc_chasis",
            help="Enfocado en reducir el peso del monoplaza y mejorar la rigidez estructural. Agiliza el comportamiento en curvas lentas."
        )
        gasto_operaciones = st.slider(
            "Logística y Operaciones ($M):", 
            min_value=5.0, max_value=100.0, step=0.5, 
            key="slider_cc_ops",
            help="Cubre costos de transporte global de carga, viajes del personal, salarios de fábrica y operaciones generales de pista."
        )

        # Catálogo ampliado de mejoras
        upgrades_disponibles = {
            "Evolución de Ala Delantera y Morro ($1.8M)": {"costo": 1.8, "ganancia": 0.08},
            "Actualización menor - Suelo y Difusor ($2.5M)": {"costo": 2.5, "ganancia": 0.12},
            "Geometría de Conductos de Freno - Cooling ($1.2M)": {"costo": 1.2, "ganancia": 0.04},
            "Paquete de Alta Carga - Circuitos Ratoneros ($3.5M)": {"costo": 3.5, "ganancia": 0.18},
            "Paquete de Baja Carga - Especificación Monza ($4.2M)": {"costo": 4.2, "ganancia": 0.22},
            "Nuevos Deflectores de Pontones y Espejos ($2.1M)": {"costo": 2.1, "ganancia": 0.09},
            "Rediseño de Beam Wing / Ala Trasera ($1.6M)": {"costo": 1.6, "ganancia": 0.07},
            "Optimización de Suspensión Pull/Push-rod ($3.1M)": {"costo": 3.1, "ganancia": 0.15},
            "Paquete Mayor - Rediseño Total de Pontones ($5.8M)": {"costo": 5.8, "ganancia": 0.35}
        }
        
        paquetes_seleccionados = st.multiselect(
            "Paquetes de Mejoras en Pista (Catálogo Ampliado):", 
            options=list(upgrades_disponibles.keys()),
            key="cc_upgrades_pro",
            help="Selecciona actualizaciones específicas para el monoplaza. Cada mejora reduce segundos por vuelta pero consume presupuesto y horas de túnel de viento."
        )

    # --- CÁLCULOS FINANCIEROS Y RESTRICCIÓN ATR (TÚNEL DE VIENTO) ---
    costo_upgrades_val = sum(upgrades_disponibles[p]["costo"] for p in paquetes_seleccionados)
    ganancia_tiempo_total = round(sum(upgrades_disponibles[p]["ganancia"] for p in paquetes_seleccionados), 2)
    gasto_total = round(gasto_aero + gasto_motor + gasto_chasis + gasto_operaciones + gasto_crash + costo_upgrades_val, 2)
    remanente = round(presupuesto_base - gasto_total, 2)

    # Cálculo dinámico de horas/porcentaje de túnel de viento (Regla ATR)
    factor_atr = max(60, round(100 - (len(paquetes_seleccionados) * 3) - (max(0, gasto_aero - 50) * 0.4)))

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

    # --- KPIS FINANCIEROS Y TÉCNICOS (4 COLUMNAS) ---
    kpi_f1, kpi_f2, kpi_f3, kpi_f4 = st.columns(4)
    with kpi_f1:
        st.metric(label="Presupuesto Autorizado", value=f"${presupuesto_base}M", delta="Límite Personalizado")
    with kpi_f2:
        st.metric(label="Gasto Acumulado", value=f"${gasto_total}M", delta="Incluye Accidentes")
    with kpi_f3:
        st.metric(label="Remanente en Caja", value=f"${remanente}M", delta="Margen financiero", delta_color="normal" if remanente >= 0 else "inverse")
    with kpi_f4:
        st.metric(label="Asignación Túnel (ATR)", value=f"{factor_atr}%", delta="Horas legales FIA")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- AUDITORÍA Y GRÁFICA CIRCULAR / DONUT LIMPIA ---
    col_res_cc, col_graf_cc = st.columns([1, 1.4])

    with col_res_cc:
        if remanente >= 0:
            cumplimiento = "✅ DENTRO DEL LÍMITE PRESUPUESTARIO"
            color_estado = "#10B981"
            detalle_sancion = f"Operación financiera limpia. Restricción aerodinámica FIA aplicada al {factor_atr}% de capacidad base."
        elif remanente >= -7.0:
            cumplimiento = "⚠️ SOBREPASO MENOR (<$7M)"
            color_estado = "#F59E0B"
            detalle_sancion = "Déficit presupuestario leve por reparaciones o evolución. Riesgo moderado de auditoría."
        else:
            cumplimiento = "❌ DÉFICIT FINANCIERO SEVERO"
            color_estado = "#FF1801"
            detalle_sancion = "Exceso crítico de gastos sobre el límite establecido. Sanción deportiva inminente."

        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.9)); padding: 22px; border-radius: 14px; border: 1px solid {color_estado}; box-shadow: 0 4px 20px rgba(0,0,0,0.4);'>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 1.2rem; margin-right: 8px;'>📋</span>
                    <h4 style='color: {color_estado}; margin:0;'>Auditoría Financiera & ATR</h4>
                </div>
                <p style='margin: 6px 0; color: #E2E8F0;'><strong>Estado del Límite:</strong> <span style='color: {color_estado}; font-weight: bold;'>{cumplimiento}</span></p>
                <p style='margin: 6px 0; color: #94A3B8; font-size: 0.9rem;'>{detalle_sancion}</p>
                <hr style='border: 1px solid rgba(255,255,255,0.1); margin: 14px 0;'>
                <div style='background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;'>
                    <span style='color: #38BDF8; font-weight: bold; display: block; margin-bottom: 4px;'>💡 Factor de Impacto en Pista:</span>
                    <small style='color: #CBD5E1;'>Mejora neta acumulada de ritmo: <b>-{ganancia_tiempo_total}s/vuelta</b> frente al coste de <b>${gasto_crash}M</b> en daños por accidentes.</small>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_graf_cc:
        df_costos = pd.DataFrame({
            "Rubro": ["Aerodinámica", "Unidad de Potencia", "Chasis", "Operaciones", "Accidentes", "Mejoras"],
            "Costo ($M)": [gasto_aero, gasto_motor, gasto_chasis, gasto_operaciones, gasto_crash, costo_upgrades_val]
        })
        
        fig_donut = px.pie(
            df_costos, names="Rubro", values="Costo ($M)", hole=0.65,
            title="<b>Distribución Global del Presupuesto</b>",
            color_discrete_sequence=["#FF1801", "#38BDF8", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"],
            template="plotly_dark"
        )
        fig_donut.update_traces(
            textposition='inside', 
            textinfo='percent',
            hoverinfo='label+value+percent'
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=10, l=10, r=10),
            height=360,
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=-0.12, 
                xanchor="center", 
                x=0.5,
                font=dict(size=10)
            )
        )
        st.plotly_chart(fig_donut, use_container_width=True, key="chart_cost_cap_donut_elite_v2")

    st.markdown("</div>", unsafe_allow_html=True)
    
with tab7:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🚦 Simulador de Luces de Salida & Tiempo de Reacción F1</div>", unsafe_allow_html=True)
    st.write(
        "Pon a prueba tus reflejos como piloto oficial de Fórmula 1. Espera a que se apaguen las 5 luces rojas "
        "y presiona el botón de reacción lo más rápido posible."
    )

    # Inicializar historial y estados en session_state
    if "history_tiempos" not in st.session_state:
        st.session_state["history_tiempos"] = []
    if "fase_semaforo_v3" not in st.session_state:
        st.session_state["fase_semaforo_v3"] = "idle"

    fase = st.session_state["fase_semaforo_v3"]

    if fase == "idle":
        st.markdown("""
            <div style='background: rgba(255,255,255,0.02); padding: 35px; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.05); margin: 15px 0;'>
                <h3 style='color: #F8FAFC; margin-bottom: 8px;'>¿Listo para la Largada desde la Pole?</h3>
                <p style='color: #94A3B8; font-size: 0.9rem;'>Presiona el botón para iniciar el procedimiento oficial de la FIA.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Iniciar Procedimiento de Salida", use_container_width=True, key="btn_start_v3", type="primary"):
            st.session_state["fase_semaforo_v3"] = "waiting"
            st.session_state["delay_semaforo"] = np.random.uniform(1.5, 3.5)
            st.rerun()

    elif fase == "waiting":
        st.markdown("""
            <div style='background: rgba(239, 68, 68, 0.06); padding: 40px; border-radius: 12px; text-align: center; border: 1px solid rgba(239, 68, 68, 0.3); margin: 15px 0;'>
                <h1 style='color: #EF4444; letter-spacing: 15px; margin: 0;'>🔴 🔴 🔴 🔴 🔴</h1>
                <h4 style='color: #F8FAFC; margin-top: 15px;'>MANTÉN LA CALMA — ESPERA EL APAGÓN</h4>
            </div>
        """, unsafe_allow_html=True)

        # Botón de penalización por salida falsa (Jump Start)
        if st.button("⚡ ¡ACELERAR ANTES DE TIEMPO (SALTO)!", use_container_width=True, key="btn_jump_v3"):
            st.session_state["fase_semaforo_v3"] = "jump"
            st.rerun()

        # Pausa controlada para el apagón de luces
        time.sleep(st.session_state["delay_semaforo"])
        st.session_state["tiempo_verde"] = time.time()
        st.session_state["fase_semaforo_v3"] = "ready"
        st.rerun()

    elif fase == "ready":
        st.markdown("""
            <div style='background: rgba(16, 185, 129, 0.08); padding: 40px; border-radius: 12px; text-align: center; border: 1px solid rgba(16, 185, 129, 0.4); margin: 15px 0;'>
                <h1 style='color: #10B981; letter-spacing: 15px; margin: 0;'>🟢 🟢 🟢 🟢 🟢</h1>
                <h3 style='color: #10B981; margin-top: 15px; font-weight: bold;'>¡APAGÓN DE LUCES! ¡YA!</h3>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ ¡REACCIONAR AHORA!", use_container_width=True, key="btn_react_v3", type="primary"):
            reaccion = int((time.time() - st.session_state["tiempo_verde"]) * 1000)
            st.session_state["ultimo_ms"] = reaccion
            st.session_state["history_tiempos"].append(reaccion)
            st.session_state["fase_semaforo_v3"] = "done"
            st.rerun()

    elif fase == "jump":
        st.markdown("""
            <div style='background: rgba(239, 68, 68, 0.08); padding: 25px; border-radius: 12px; border: 1px solid #EF4444; text-align: center; margin: 15px 0;'>
                <h3 style='color: #EF4444; margin-top: 0;'>❌ ¡SALIDA FALSA (JUMP START)!</h3>
                <p style='color: #F8FAFC;'>Te moviste antes de que se apagaran las luces. Sanción aplicada.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Intentar Nuevamente", use_container_width=True, key="btn_retry_jump_v3"):
            st.session_state["fase_semaforo_v3"] = "idle"
            st.rerun()

    elif fase == "done":
        ms = st.session_state["ultimo_ms"]
        if ms < 200:
            msg = "🏆 ¡Reflejos de Élite F1 (Nivel Verstappen/Hamilton)!"
            color = "#10B981"
        elif ms < 260:
            msg = "🔥 ¡Excelente tiempo de reacción! Zona de puntos."
            color = "#38BDF8"
        elif ms < 320:
            msg = "👍 Buen ritmo, pero puedes afinar los reflejos."
            color = "#F59E0B"
        else:
            msg = "🐢 Salida tardía. ¡Te adelantaron en la curva 1!"
            color = "#EF4444"

        st.markdown(f"""
            <div style='background: rgba(15, 23, 42, 0.85); padding: 30px; border-radius: 12px; border: 1px solid {color}; text-align: center; margin: 15px 0;'>
                <div style='font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;'>Cronometraje Oficial FIA</div>
                <h1 style='color: {color}; font-size: 3.5rem; margin: 8px 0;'>{ms} ms</h1>
                <h4 style='color: #F8FAFC; margin-bottom: 0;'>{msg}</h4>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Nueva Prueba de Salida", use_container_width=True, key="btn_again_v3"):
            st.session_state["fase_semaforo_v3"] = "idle"
            st.rerun()

    # --- GRÁFICA DE EVOLUCIÓN E HISTORIAL DE TIEMPOS ---
    if len(st.session_state["history_tiempos"]) > 0:
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<b style='color: #FFFFFF; font-size: 0.95rem;'>📈 Evolución de Tus Tiempos de Reacción (Historial de Intentos):</b>", unsafe_allow_html=True)
        
        df_intentos = pd.DataFrame({
            "Intento": [f"Intento {i+1}" for i in range(len(st.session_state["history_tiempos"]))],
            "Tiempo (ms)": st.session_state["history_tiempos"]
        })
        
        fig_hist = px.line(
            df_intentos, x="Intento", y="Tiempo (ms)",
            markers=True,
            template="plotly_dark"
        )
        fig_hist.update_traces(line_color="#38BDF8", line_width=3, marker_size=9)
        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=10, r=10),
            height=280,
            xaxis_title=None,
            yaxis_title="<b>Milisegundos (ms)</b>"
        )
        fig_hist.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)')
        fig_hist.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)')
        
        st.plotly_chart(fig_hist, use_container_width=True, key="chart_historial_reaccion_v3")

    st.markdown("</div>", unsafe_allow_html=True)
    
with tab8:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛑 Centro de Comando Estratégico: Simulador de Stints & Lluvia</div>", unsafe_allow_html=True)
    st.write(
        "Centro de mando avanzado para la toma de decisiones en condiciones secas, mixtas o de lluvia extrema. "
        "Utiliza los escenarios tácticos rápidos o personaliza la estrategia de compuestos Pirelli."
    )

    # --- SELECTOR DE ESCENARIOS TÁCTICOS (PRESETS INTELIGENTES) ---
    st.markdown("<b style='color: #38BDF8; font-size: 0.9rem;'>⚡ Escenarios Tácticos Rápidos (Presets de Muro de Boxes):</b>", unsafe_allow_html=True)
    col_preset1, col_preset2, col_preset3 = st.columns(3)
    
    with col_preset1:
        preset_seco = st.button("☀️ Gran Premio Seco (Estándar)", use_container_width=True, key="btn_dry")
    with col_preset2:
        preset_sc = st.button("🟡 Safety Car / Oportunista", use_container_width=True, key="btn_sc")
    with col_preset3:
        preset_lluvia = st.button("🌧️ Riesgo de Lluvia Inminente", use_container_width=True, key="btn_rain")

    # Lógica de valores según el escenario seleccionado
    if preset_sc:
        default_pit, default_goma, default_vuelta, default_comp = 19.0, 1.8, 15, "Soft (C5)"
    elif preset_lluvia:
        default_pit, default_goma, default_vuelta, default_comp = 25.0, 2.5, 20, "Intermediate"
    else:
        default_pit, default_goma, default_vuelta, default_comp = 21.8, 1.4, 22, "Medium (C3)"

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    # --- SUB-PESTAÑAS INTERNAS DE NAVEGACIÓN ---
    sub_t1, sub_t2, sub_t3 = st.tabs(["📊 Matriz de Stints (Gantt)", "⚙️ Simulador de Undercut & Clima", "📈 Curva de Degradación de Neumáticos"])

    # ==========================================
    # SUB-PESTAÑA 1: MATRIZ DE STINTS Y GRÁFICA
    # ==========================================
    with sub_t1:
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            filtro_vista = st.selectbox(
                "Filtrar Agrupación de Monoplazas:", 
                ["Toda la Parrilla (20 Monoplazas)", "Top 10 / Zona de Puntos", "Equipos de Punta (Top Teams)"], 
                key="sub_filtro_vista_v2"
            )
        with col_g2:
            compuesto_inicial = st.selectbox(
                "Tu Compuesto Inicial (Stint 1):", 
                ["Medium (C3)", "Soft (C5)", "Hard (C1)", "Intermediate", "Wet"], 
                index=["Medium (C3)", "Soft (C5)", "Hard (C1)", "Intermediate", "Wet"].index(default_comp) if default_comp in ["Medium (C3)", "Soft (C5)", "Hard (C1)", "Intermediate", "Wet"] else 0,
                key="sub_c_init_v2"
            )

        vuelta_parada_usuario = default_vuelta
        delta_pit = default_pit
        delta_goma_fresca = default_goma

        # Filtrado de pilotos
        pilotos_base = globals().get('TODOS_OS_PILOTOS_2024', [
            "Max Verstappen", "Sergio Pérez", "Charles Leclerc", "Carlos Sainz",
            "Lando Norris", "Oscar Piastri", "Lewis Hamilton", "George Russell",
            "Fernando Alonso", "Lance Stroll", "Yuki Tsunoda", "Daniel Ricciardo",
            "Alexander Albon", "Logan Sargeant", "Valtteri Bottas", "Guanyu Zhou",
            "Esteban Ocon", "Pierre Gasly", "Kevin Magnussen", "Nico Hülkenberg"
        ])

        if "Top 10" in filtro_vista:
            pilotos_activos = pilotos_base[:10]
        elif "Punta" in filtro_vista:
            pilotos_activos = [p for p in pilotos_base if any(eq in p for eq in ["Verstappen", "Pérez", "Leclerc", "Sainz", "Norris", "Piastri", "Hamilton", "Russell"])]
        else:
            pilotos_activos = pilotos_base

        pilotos_con_usuario = ["🏎️ TU MONOPLAZA"] + pilotos_activos

        # Generación de stints dinámicos
        gantt_data = []
        total_vueltas_carrera = 55

        for i, piloto in enumerate(pilotos_con_usuario):
            if piloto == "🏎️ TU MONOPLAZA":
                c1 = compuesto_inicial
                if c1 == "Intermediate":
                    c2 = "Wet" if preset_lluvia else "Medium (C3)"
                elif c1 == "Wet":
                    c2 = "Intermediate"
                else:
                    c2 = "Hard (C1)" if "Soft" in c1 or "Medium" in c1 else "Medium (C3)"
                p_split = vuelta_parada_usuario
            elif "Verstappen" in piloto or "Pérez" in piloto:
                c1, c2 = ("Intermediate", "Wet") if preset_lluvia else ("Medium (C3)", "Hard (C1)")
                p_split = vuelta_parada_usuario + (1 if i % 2 == 0 else -1)
            elif "Leclerc" in piloto or "Sainz" in piloto:
                c1, c2 = ("Wet", "Intermediate") if preset_lluvia else ("Soft (C5)", "Hard (C1)")
                p_split = max(5, vuelta_parada_usuario - 2)
            else:
                c1, c2 = ("Intermediate", "Hard (C1)") if preset_lluvia else (("Medium (C3)", "Hard (C1)") if i % 2 == 0 else ("Soft (C5)", "Medium (C3)"))
                p_split = max(8, min(48, vuelta_parada_usuario + (i % 4 - 2)))

            p_split = min(max(5, p_split), total_vueltas_carrera - 5)

            gantt_data.append({"Driver": piloto, "Compound": c1, "Start": 1, "Finish": p_split, "Duration": p_split - 1, "Stint": "Stint 1"})
            gantt_data.append({"Driver": piloto, "Compound": c2, "Start": p_split, "Finish": total_vueltas_carrera, "Duration": total_vueltas_carrera - p_split, "Stint": "Stint 2"})

        df_gantt = pd.DataFrame(gantt_data)

        # Paleta de colores oficial Pirelli
        color_compuestos = {
            "Soft (C5)": "#EF4444",      
            "Medium (C3)": "#F59E0B",    
            "Hard (C1)": "#94A3B8",      
            "Intermediate": "#10B981",   
            "Wet": "#3B82F6"             
        }

        fig_gantt = px.bar(
            df_gantt, x="Duration", y="Driver", base="Start", orientation="h", color="Compound",
            hover_name="Driver", hover_data={"Stint": True, "Start": True, "Finish": True, "Duration": True, "Driver": False},
            color_discrete_map=color_compuestos,
            template="plotly_dark", category_orders={"Driver": pilotos_con_usuario[::-1]}
        )
        fig_gantt.update_yaxes(categoryorder="array", categoryarray=pilotos_con_usuario[::-1])
        fig_gantt.add_vline(x=vuelta_parada_usuario, line_dash="dot", line_color="#FF1801", line_width=2.5,
                            annotation_text=f"Tu Parada (V.{vuelta_parada_usuario})", annotation_position="top right",
                            annotation_font=dict(size=12, color="#FF1801"))
        fig_gantt.update_layout(
            title=dict(text=f"<b>Estrategia Visual de Stints y Compuestos Pirelli</b> — Meta: Vuelta {vuelta_parada_usuario}", font=dict(size=15, color="#FFFFFF")),
            xaxis_title="<b>Vueltas de Carrera</b>", yaxis_title=None,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=20, l=10, r=10), height=480,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0.4)')
        )
        fig_gantt.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)', dtick=5)
        fig_gantt.update_yaxes(showgrid=False)

        st.plotly_chart(fig_gantt, use_container_width=True, key="chart_gantt_ultra_v3")

    # ==========================================
    # SUB-PESTAÑA 2: SIMULADOR AVANZADO
    # ==========================================
    with sub_t2:
        st.markdown("<b style='color: #FFFFFF;'>Ajuste Fino de Parámetros Operativos del Monoplaza:</b>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            delta_pit = st.slider("Pérdida en Pit-Lane (s):", min_value=18.0, max_value=32.0, value=default_pit, step=0.1, key="sim_delta_pit_v3")
        with col_s2:
            delta_goma_fresca = st.slider("Ganancia de Ritmo (s/v):", min_value=0.5, max_value=3.0, value=default_goma, step=0.1, key="sim_delta_goma_v3")
        with col_s3:
            vuelta_parada_usuario = st.slider("Vuelta Exacta de Parada:", min_value=5, max_value=45, value=default_vuelta, step=1, key="sim_vuelta_parada_v3")

        vueltas_ventaja_necesarias = round(delta_pit / delta_goma_fresca, 1)

        mk1, mk2, mk3 = st.columns(3)
        with mk1:
            st.metric("Ventana Óptima de Undercut", f"{vueltas_ventaja_necesarias} vls", "Margen seguro")
        with mk2:
            st.metric("Costo Estático en Pit", f"{delta_pit}s", "Pérdida neta")
        with mk3:
            st.metric("Vuelta Seleccionada", f"V.{vuelta_parada_usuario}", "Box Target")

    # ==========================================
    # SUB-PESTAÑA 3: CURVA DE DEGRADACIÓN TÉCNICA (NUEVO)
    # ==========================================
    with sub_t3:
        st.markdown("<b style='color: #FFFFFF;'>📈 Análisis de Comportamiento y Desgaste del Compuesto Seleccionado:</b>", unsafe_allow_html=True)
        st.write(f"Simulación teórica de la pérdida de ritmo por vuelta debido al desgaste físico del compuesto **{compuesto_inicial}**.")

        # Generar datos matemáticos de degradación según el compuesto seleccionado
        vueltas_stint = list(range(1, 31))
        if "Soft" in compuesto_inicial:
            degradacion = [round(0.0 + (i * 0.14) + (0.015 * (i**1.2)), 2) for i in range(len(vueltas_stint))]
            color_linea = "#EF4444"
        elif "Medium" in compuesto_inicial:
            degradacion = [round(0.0 + (i * 0.08) + (0.008 * (i**1.1)), 2) for i in range(len(vueltas_stint))]
            color_linea = "#F59E0B"
        elif "Hard" in compuesto_inicial:
            degradacion = [round(0.0 + (i * 0.04) + (0.003 * (i**1.05)), 2) for i in range(len(vueltas_stint))]
            color_linea = "#94A3B8"
        elif "Intermediate" in compuesto_inicial:
            degradacion = [round(0.0 + (i * 0.12) + (0.02 * (i**1.25)), 2) for i in range(len(vueltas_stint))]
            color_linea = "#10B981"
        else: # Wet
            degradacion = [round(0.0 + (i * 0.10) + (0.01 * (i**1.15)), 2) for i in range(len(vueltas_stint))]
            color_linea = "#3B82F6"

        df_deg = pd.DataFrame({
            "Vuelta de Stint": vueltas_stint,
            "Pérdida de Tiempo Acumulada (s)": degradacion
        })

        fig_deg = px.line(
            df_deg, x="Vuelta de Stint", y="Pérdida de Tiempo Acumulada (s)",
            markers=True,
            template="plotly_dark",
            title=f"Curva de Degradación — Compuesto {compuesto_inicial}"
        )
        fig_deg.update_traces(line_color=color_linea, line_width=3, marker_size=6)
        fig_deg.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=20, l=10, r=10),
            height=320,
            xaxis_title="<b>Vueltas con el Neumático</b>",
            yaxis_title="<b>Pérdida vs Vuelta 1 (s)</b>"
        )
        fig_deg.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)')
        fig_deg.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.06)')

        st.plotly_chart(fig_deg, use_container_width=True, key="chart_degradacion_pro")

    # --- REPORTE TÁCTICO INTELIGENTE INFERIOR ---
    efectividad_undercut = "ALTA 🟢" if vueltas_ventaja_necesarias <= 3.5 else ("MODERADA 🟡" if vueltas_ventaja_necesarias <= 5.0 else "BAJA 🔴")
    condicion_pista = "Lluvia / Mixta 🌧️" if preset_lluvia else "Seco ☀️"
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95)); padding: 16px 20px; border-radius: 10px; border: 1px solid rgba(56,189,248,0.3); margin-top: 20px;'>
            <div style='display: flex; align-items: center; margin-bottom: 6px;'>
                <span style='font-size: 1.1rem; margin-right: 8px;'>🎯</span>
                <b style='color: #38BDF8; font-size: 1rem;'>Estado del Muro de Boxes ({condicion_pista}):</b>
            </div>
            <p style='color: #E2E8F0; font-size: 0.9rem; line-height: 1.4; margin: 0;'>
                Estrategia fijada en la <b>vuelta {vuelta_parada_usuario}</b> con compuesto inicial <b>{compuesto_inicial}</b>. 
                Ventana de undercut necesaria: <b>{vueltas_ventaja_necesarias} vueltas</b> (Efectividad Táctica: <b>{efectividad_undercut}</b>).
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
with tab9:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>💵 Fantasy F1 Auto-Optimizer & Value Engine</div>", unsafe_allow_html=True)
    st.write(
        "Algoritmo avanzado de optimización financiera y deportiva. Calcula la alineación de pilotos ideal "
        "maximizando el rendimiento bajo el límite presupuestario y evaluando la eficiencia de costos (ROI)."
    )

    # --- CONTROLES SUPERIORES ORGANIZADOS ---
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        presupuesto_max = st.slider("Presupuesto Disponible para Alineación ($M):", min_value=30.0, max_value=60.0, value=52.0, step=0.5, key="slider_presupuesto_fantasy_pro_v2")
    with col_f2:
        criterio_opt = st.selectbox(
            "Criterio de Optimización:", 
            ["Máxima Puntuación Total", "Mejor Eficiencia (ROI Puntos/$M)"], 
            key="select_criterio_opt_v2"
        )

    # --- ALGORITMO DE OPTIMIZACIÓN INTELIGENTE ---
    mejor_puntaje = -1
    mejor_par = None
    mejor_costo = 0
    mejor_eficiencia = -1

    pilotos_keys = list(FANTASY_DB.keys())
    for i in range(len(pilotos_keys)):
        for j in range(i + 1, len(pilotos_keys)):
            p1 = pilotos_keys[i]
            p2 = pilotos_keys[j]
            costo_par = FANTASY_DB[p1]["costo"] + FANTASY_DB[p2]["costo"]
            puntos_par = FANTASY_DB[p1]["puntos"] + FANTASY_DB[p2]["puntos"]
            eficiencia_par = puntos_par / costo_par if costo_par > 0 else 0

            if costo_par <= presupuesto_max:
                if criterio_opt == "Máxima Puntuación Total" and puntos_par > mejor_puntaje:
                    mejor_puntaje = puntos_par
                    mejor_par = (p1, p2)
                    mejor_costo = costo_par
                elif criterio_opt == "Mejor Eficiencia (ROI Puntos/$M)" and eficiencia_par > mejor_eficiencia:
                    mejor_eficiencia = eficiencia_par
                    mejor_puntaje = puntos_par
                    mejor_par = (p1, p2)
                    mejor_costo = costo_par

    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    if mejor_par:
        st.success("🏆 **¡Alineación Óptima Detectada por el Algoritmo!**")
        
        presupuesto_restante = round(presupuesto_max - mejor_costo, 1)
        eficiencia_alineacion = round(mejor_puntaje / mejor_costo, 2) if mejor_costo > 0 else 0

        # --- PANEL DE MÉTRICAS AVANZADAS (4 COLUMNAS) ---
        m_opt1, m_opt2, m_opt3, m_opt4 = st.columns(4)
        with m_opt1:
            st.metric(label="Costo Alineación", value=f"${mejor_costo}M", delta=f"Límite: ${presupuesto_max}M")
        with m_opt2:
            st.metric(label="Restante en Caja", value=f"${presupuesto_restante}M", delta="Ahorro financiero")
        with m_opt3:
            st.metric(label="Puntos Proyectados", value=f"{mejor_puntaje} pts", delta="Rendimiento")
        with m_opt4:
            st.metric(label="Eficiencia (ROI)", value=f"{eficiencia_alineacion} pts/$M", delta="Valor por millón")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- TARJETAS VISUALES DE LOS PILOTOS SELECCIONADOS ---
        col_opt1, col_opt2 = st.columns(2)
        
        for idx, p_sel in enumerate(mejor_par):
            p_data = FANTASY_DB[p_sel]
            roi_piloto = round(p_data['puntos'] / p_data['costo'], 2)
            with (col_opt1 if idx == 0 else col_opt2):
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(16,185,129,0.06), rgba(15,23,42,0.8)); padding: 20px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <span style='font-size: 0.75rem; color: #10B981; font-weight: bold; text-transform: uppercase;'>Slot Titular #{idx+1}</span>
                            <span style='background: rgba(16,185,129,0.15); color: #10B981; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;'>ROI: {roi_piloto} pts/$M</span>
                        </div>
                        <h3 style='color: #F8FAFC; margin: 5px 0 12px 0;'>🏎️ {p_sel}</h3>
                        <div style='display: flex; justify-content: space-between; font-size: 0.9rem; color: #94A3B8; background: rgba(0,0,0,0.2); padding: 8px 12px; border-radius: 6px;'>
                            <span>Costo: <b style='color: #F8FAFC;'>${p_data['costo']}M</b></span>
                            <span>Puntos 2024: <b style='color: #F8FAFC;'>{p_data['puntos']} pts</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- MAPA DE VALOR LIMPIO Y LEGIBLE (SCATTER PLOT) ---
        st.markdown("<b style='color: #FFFFFF; font-size: 0.95rem;'>📊 Mapa de Valor de la Parrilla (Costo vs Puntos):</b>", unsafe_allow_html=True)
        st.write("Pasa el cursor sobre cualquier punto para ver los detalles del piloto. Los ganadores de la alineación aparecen etiquetados.")

        df_fantasy_plot = pd.DataFrame.from_dict(FANTASY_DB, orient='index').reset_index()
        df_fantasy_plot.columns = ["Piloto", "Costo", "Puntos"]
        df_fantasy_plot["Seleccionado"] = df_fantasy_plot["Piloto"].apply(lambda x: "Titular Óptimo 🏆" if x in mejor_par else "Resto de la Parrilla")
        
        # Truco para mostrar texto SOLO en los pilotos seleccionados y evitar que se sature la gráfica
        df_fantasy_plot["Label_Texto"] = df_fantasy_plot.apply(
            lambda row: f"<b>{row['Piloto']}</b> 🏆" if row["Piloto"] in mejor_par else "", axis=1
        )

        fig_fantasy = px.scatter(
            df_fantasy_plot, x="Costo", y="Puntos", color="Seleccionado",
            text="Label_Texto",
            hover_name="Piloto",
            hover_data={"Costo": True, "Puntos": True, "Label_Texto": False, "Seleccionado": False},
            color_discrete_map={"Titular Óptimo 🏆": "#10B981", "Resto de la Parrilla": "#64748B"},
            template="plotly_dark"
        )
        fig_fantasy.update_traces(
            textposition='top center', 
            marker=dict(size=13, line=dict(width=1.5, color='rgba(255,255,255,0.3)'))
        )
        fig_fantasy.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=20, l=10, r=10), height=420,
            xaxis_title="<b>Costo del Piloto ($M)</b>", yaxis_title="<b>Puntos Históricos 2024</b>",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_fantasy.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')
        fig_fantasy.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)')

        st.plotly_chart(fig_fantasy, use_container_width=True, key="chart_fantasy_optimizer_pro_v2")

    else:
        st.warning("⚠️ No se encontró ninguna combinación válida con el presupuesto seleccionado. Aumenta el límite en el control deslizante superior.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- EXPANSOR DE DATOS CON EFICIENCIA CALCULADA ---
    with st.expander("📊 Consultar Base de Datos Completa de Fantasy (FANTASY_DB)"):
        df_fantasy = pd.DataFrame.from_dict(FANTASY_DB, orient='index').reset_index()
        df_fantasy.columns = ["Piloto Oficial", "Costo ($M)", "Puntos Históricos 2024"]
        df_fantasy["Eficiencia (Pts/$M)"] = round(df_fantasy["Puntos Históricos 2024"] / df_fantasy["Costo ($M)"], 2)
        st.dataframe(df_fantasy.sort_values(by="Puntos Históricos 2024", ascending=False), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)
    
with tab10:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛠️ Asistente Táctico Inteligente con Transmisión de Radio (Team Radio AI)</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(8, 12, 22, 0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(59,130,246,0.3); text-align: center; margin-bottom: 20px;'>
            <span style='font-size: 0.8rem; color: #38BDF8; font-weight: 800; letter-spacing: 2px; display:block; margin-bottom: 6px;'>📡 CANAL DE RADIO ACTIVO - INGENIERO DE PISTA FIA</span>
            <div style='font-size: 1.3rem; letter-spacing: 3px; color: #FF1801; font-weight: 900;'>
                📶 ▂▃▅▆▇█▇▆▅▃▂ 📡 ▂▃▅▆▇█▇▆▅▃▂ 📶
            </div>
            <small style='color: #94A3B8; font-style: italic;'>Agente conversacional inteligente listo para resolver dudas de estrategia, clima y telemetría</small>
        </div>
    """, unsafe_allow_html=True)

    # Variables de respaldo seguras en caso de ejecución independiente
    d_pit = locals().get('delta_pit', 21.8)
    v_ventaja = locals().get('vueltas_ventaja_necesarias', 15.5)
    v_parada = locals().get('vuelta_parada_usuario', 22)
    n_activo = locals().get('nombre_activo', 'Escudería F1')
    p_puntos = locals().get('promedio_puntos', 25.0)
    pods = locals().get('podios', 12)
    efec = locals().get('efectividad', 75.0)
    grip = locals().get('indice_agarre', 0.85)

    # Botones de acceso rápido para transmisiones de radio comunes
    st.markdown("<p style='font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;'>💬 <b>Transmisiones rápidas sugeridas:</b></p>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    
    if "radio_msg" not in st.session_state:
        st.session_state["radio_msg"] = ""

    with q_col1:
        if st.button("🏁 Ventana Undercut", use_container_width=True, key="r_btn_1"):
            st.session_state["radio_msg"] = "Dime la estrategia de undercut y paradas"
    with q_col2:
        if st.button("📈 Rendimiento / Puntos", use_container_width=True, key="r_btn_2"):
            st.session_state["radio_msg"] = "Cuál es el rendimiento y puntos del equipo"
    with q_col3:
        if st.button("🏆 Análisis de Podios", use_container_width=True, key="r_btn_3"):
            st.session_state["radio_msg"] = "Cuantos podios tenemos esta temporada"
    with q_col4:
        if st.button("⛅ Estado de Gomas", use_container_width=True, key="r_btn_4"):
            st.session_state["radio_msg"] = "Cómo está el desgaste de gomas y el clima"

    pregunta_usuario = st.chat_input("Transmita mensaje por radio al ingeniero de boxes...", key="chat_input_radio_ai")
    
    # Evaluar si se presionó un botón de acceso rápido
    if st.session_state["radio_msg"]:
        pregunta_usuario = st.session_state["radio_msg"]
        st.session_state["radio_msg"] = "" # Limpiar estado

    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta_usuario)
        with st.chat_message("assistant", avatar="🤖"):
            p = pregunta_usuario.lower()
            if any(x in p for x in ["undercut", "parar", "boxes", "estrategia"]):
                respuesta = f"[RADIO 📡] Analizando ventana táctica. Con un delta de {d_pit}s en pit-lane y {v_ventaja} vueltas óptimas con neumático fresco, recomendamos buscar el undercut inmediato en la vuelta {v_parada}."
            elif any(x in p for x in ["puntos", "promedio", "rendimiento"]):
                respuesta = f"[RADIO 📡] Telemetría confirmada: {n_activo} registra un promedio de {p_puntos} puntos por Gran Premio en 2024."
            elif any(x in p for x in ["podio", "podios", "victorias"]):
                respuesta = f"[RADIO 📡] Análisis histórico de temporada: El equipo acumula {pods} podios oficiales ({efec}% de conversión)."
            elif any(x in p for x in ["neumático", "goma", "desgaste", "clima"]):
                respuesta = f"[RADIO 📡] Reporte de gomas recibido. El Grip Index actual es de {grip}. Mantendremos la ventana de temperatura óptima."
            else:
                respuesta = f"[RADIO 📡] Mensaje recibido fuerte y claro desde el muro de boxes de {n_activo}. El monoplaza opera al {efec}% de efectividad óptima."
            st.write(respuesta)
            
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <hr style='border-color: rgba(255,255,255,0.08); margin-top: 50px;'>
    <div style='text-align: center; color: #64748B; font-size: 0.9rem; padding-bottom: 25px;'>
        <strong>Forza F1 World Elite Supreme - Edición Temporada 2024 V24.6 (FastF1 Telemetry Redesign Pro)</strong><br>
        Plataforma Suprema con FastF1 Multi-Channel Telemetry, Pit-Stop Gantt, Cost Cap War Room, Fantasy Optimizer, Radio IA & Live Data Editor<br>
        Desarrollado con Excelencia Absoluta para el Primer Lugar © 2026
    </div>
""", unsafe_allow_html=True)
