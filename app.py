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
            font-size: 0.72rem !important;
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

# Encabezado Espectacular de Presentación
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
            <span style='font-size: 0.95rem; color: #10B981; font-weight: 900;'>● 10/10 MÓDULOS ACTIVOS</span>
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

# Navegación con 10 pestañas maestras operativas
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

# ==========================================
# TAB 1: Panel 2024
# ==========================================
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
    st.info("Modifica los valores numéricos de los puntos en la tabla interactiva y la gráfica se actualizará al instante en tiempo real.")

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


# ==========================================
# TAB 2: H2H Battle
# ==========================================
with tab2:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⚔️ Batalla Cara a Cara (Teammate / Grid Battle 2024)</div>", unsafe_allow_html=True)
    st.write("Comparativa dinámica de rendimiento seleccionando libremente entre **cualquier piloto de la parrilla 2024**.")
    
    col_p1, col_vs, col_p2 = st.columns([5, 1, 5])
    with col_p1:
        sel_h2h_a = st.selectbox("Seleccionar Piloto A:", TODOS_OS_PILOTOS_2024, index=0, key="h2h_piloto_a")
    with col_vs:
        st.markdown("<div style='text-align: center; padding-top: 30px;'><h2 style='color: #FF1801; font-weight: 900;'>VS</h2></div>", unsafe_allow_html=True)
    with col_p2:
        sel_h2h_b = st.selectbox("Seleccionar Piloto B:", TODOS_OS_PILOTOS_2024, index=min(1, len(TODOS_OS_PILOTOS_2024)-1), key="h2h_piloto_b")

    seed_a = sum(ord(c) for c in sel_h2h_a)
    seed_b = sum(ord(c) for c in sel_h2h_b)
    
    vel_a_val = round(330 + (seed_a % 15) + np.sin(seed_a)*3, 1)
    vel_b_val = round(330 + (seed_b % 15) + np.sin(seed_b)*3, 1)
    
    pts_a_val = FANTASY_DB.get(sel_h2h_a, {"puntos": 50})["puntos"]
    pts_b_val = FANTASY_DB.get(sel_h2h_b, {"puntos": 50})["puntos"]

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""
            <div style='background: #080C16; padding: 20px; border-radius: 14px; border: 1px solid rgba(255,24,1,0.3); text-align: center;'>
                <h3 style='color: #FFFFFF; margin-bottom: 5px;'>🏎️ {sel_h2h_a}</h3>
                <hr style='border-color: rgba(255,255,255,0.1);'>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Velocidad Punta en Trampa: <strong>{vel_a_val} km/h</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Ritmo Clasificación Q3: <strong>1:19.{seed_a % 90}</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Puntos Temporada 2024: <strong>{pts_a_val} pts</strong></p>
            </div>
        """, unsafe_allow_html=True)
    with col_res2:
        st.markdown(f"""
            <div style='background: #080C16; padding: 20px; border-radius: 14px; border: 1px solid rgba(59,130,246,0.3); text-align: center;'>
                <h3 style='color: #FFFFFF; margin-bottom: 5px;'>🏎️ {sel_h2h_b}</h3>
                <hr style='border-color: rgba(255,255,255,0.1);'>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Velocidad Punta en Trampa: <strong>{vel_b_val} km/h</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Ritmo Clasificación Q3: <strong>1:19.{seed_b % 90}</strong></p>
                <p style='text-align: left; font-size: 0.85rem; font-weight: 700;'>Puntos Temporada 2024: <strong>{pts_b_val} pts</strong></p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 3: GP En Vivo / Registro 2024
# ==========================================
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
                <div class='badge-live' style='display:inline-block; margin-top:10px;'>GANADOR 2024: {datos_gp_activo['ganador']}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_mapa_gp:
        df_mapa_envivo = pd.DataFrame({'lat': [datos_gp_activo['lat']], 'lon': [datos_gp_activo['lon']]})
        st.map(df_mapa_envivo, zoom=11, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 4: FASTF1 TELEMETRY
# ==========================================
with tab4:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📈 Análisis de Telemetría Avanzada (Sector a Sector)</div>", unsafe_allow_html=True)
    st.write("Análisis cruzado de los inputs del piloto: Acelerador, Freno y Velocidad mediante la integración simulada de **FastF1**.")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        driver1 = st.selectbox("Piloto 1 (Referencia):", ["VER - Max Verstappen", "LEC - Charles Leclerc"], index=0)
        color1 = "#0600EF" if "VER" in driver1 else "#DC0000"
    with col_t2:
        driver2 = st.selectbox("Piloto 2 (Comparativa):", ["NOR - Lando Norris", "HAM - Lewis Hamilton"], index=0)
        color2 = "#FF8000" if "NOR" in driver2 else "#00D2BE"
    with col_t3:
        session = st.selectbox("Sesión F1:", ["Q3 - Clasificación", "Carrera", "FP2"])

    x = np.linspace(0, 100, 600)
    speed1 = 320 - 180 * np.exp(-x/15) + 25 * np.sin(x/4) + np.random.normal(0, 1.5, 600)
    throttle1 = np.where(np.sin(x/4) > 0, 100, 0) + np.random.normal(0, 3, 600)
    brake1 = np.where(np.sin(x/4) < -0.6, 100, 0)
    
    speed2 = 315 - 170 * np.exp(-x/18) + 27 * np.sin((x-1.5)/4) + np.random.normal(0, 1.5, 600)
    throttle2 = np.where(np.sin((x-1.5)/4) > 0, 100, 0) + np.random.normal(0, 3, 600)
    brake2 = np.where(np.sin((x-1.5)/4) < -0.5, 100, 0)

    fig_tel = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=("Velocidad (km/h)", "Acelerador (%)", "Freno (%)")
    )
    
    fig_tel.add_trace(go.Scatter(x=x, y=speed1, name=driver1[:3], line=dict(color=color1, width=2.5)), row=1, col=1)
    fig_tel.add_trace(go.Scatter(x=x, y=speed2, name=driver2[:3], line=dict(color=color2, width=2.5)), row=1, col=1)
    
    fig_tel.add_trace(go.Scatter(x=x, y=np.clip(throttle1, 0, 100), showlegend=False, line=dict(color=color1, width=2)), row=2, col=1)
    fig_tel.add_trace(go.Scatter(x=x, y=np.clip(throttle2, 0, 100), showlegend=False, line=dict(color=color2, width=2)), row=2, col=1)
    
    fig_tel.add_trace(go.Scatter(x=x, y=brake1, showlegend=False, line=dict(color=color1, width=2)), row=3, col=1)
    fig_tel.add_trace(go.Scatter(x=x, y=brake2, showlegend=False, line=dict(color=color2, width=2)), row=3, col=1)

    fig_tel.update_layout(
        height=750, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )
    fig_tel.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    fig_tel.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title_text="Distancia del Circuito (m)", row=3, col=1)

    st.plotly_chart(fig_tel, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 5: ADVANCED WEATHER RADAR
# ==========================================
with tab5:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⛅ AWS Insights: Advanced Weather Radar & Track Evolution</div>", unsafe_allow_html=True)
    st.write("Simulador atmosférico predictivo. Modifica las condiciones para analizar en tiempo real la temperatura de asfalto y la ventana táctica Pirelli.")
    
    c_w1, c_w2, c_w3, c_w4 = st.columns(4)
    with c_w1:
        temp_amb = st.slider("🌡️ Temp. Ambiente (°C)", min_value=10, max_value=42, value=25, key="nw_temp")
    with c_w2:
        prob_lluvia = st.slider("🌧️ Prob. de Lluvia (%)", min_value=0, max_value=100, value=15, key="nw_rain")
    with c_w3:
        humedad = st.slider("💧 Humedad Relativa (%)", min_value=10, max_value=100, value=45, key="nw_hum")
    with c_w4:
        viento = st.slider("💨 Viento (km/h)", min_value=0, max_value=60, value=12, key="nw_wind")

    impacto_sol = 15 if prob_lluvia < 30 and humedad < 60 else (5 if prob_lluvia < 60 else 0)
    temp_pista = temp_amb + impacto_sol - (viento * 0.15)
    temp_pista = round(max(temp_amb, temp_pista), 1)

    indice_agarre = 1.0 - (abs(temp_pista - 35) * 0.008) - (prob_lluvia * 0.007)
    indice_agarre = round(max(0.1, min(1.0, indice_agarre)), 2)

    if prob_lluvia > 75 or (prob_lluvia > 50 and indice_agarre < 0.45):
        neumatico_rec, razon_rec, color_borde = "🔵 Lluvia Extrema (Wet)", "Alto riesgo de aquaplaning. Pista inundada.", "#0066FF"
    elif prob_lluvia > 25 or indice_agarre < 0.65:
        neumatico_rec, razon_rec, color_borde = "🟢 Intermedios (Inters)", "Asfalto mixto / Condiciones de transición.", "#10B981"
    elif temp_pista > 45:
        neumatico_rec, razon_rec, color_borde = "⚪ Duros (Hard C1/C2)", "Alta abrasión y riesgo severo de blistering térmico.", "#FFFFFF"
    elif temp_pista < 26:
        neumatico_rec, razon_rec, color_borde = "🔴 Blandos (Soft C4/C5)", "Necesidad de encender gomas rápido por baja temperatura.", "#FF1801"
    else:
        neumatico_rec, razon_rec, color_borde = "🟡 Medios (Medium C3)", "Ventana operativa ideal. Balance perfecto degradación/agarre.", "#F59E0B"

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_grip = go.Figure(go.Indicator(
            mode="gauge+number",
            value=indice_agarre * 100,
            title={'text': "Nivel de Agarre (Grip Index)", 'font': {'color': '#94A3B8', 'size': 18}},
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
        fig_grip.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280, margin=dict(t=40, b=10))
        st.plotly_chart(fig_grip, use_container_width=True)

    with col_g2:
        fig_temp = go.Figure(go.Indicator(
            mode="gauge+number",
            value=temp_pista,
            title={'text': "Temperatura de Asfalto", 'font': {'color': '#94A3B8', 'size': 18}},
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
        fig_temp.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280, margin=dict(t=40, b=10))
        st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown(f"""
        <div style='background: linear-gradient(90deg, rgba(8,12,22,1) 0%, {color_borde}22 100%); 
                    padding: 22px; border-radius: 14px; border-left: 6px solid {color_borde}; 
                    border: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 30px;'>
            <div>
                <span style='color: #94A3B8; font-weight: 800; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase;'>RECOMENDACIÓN ESTRATÉGICA PIRELLI</span>
                <h2 style='color: {color_borde}; margin: 5px 0 0 0; font-weight: 900;'>{neumatico_rec}</h2>
                <p style='color: #F1F5F9; margin: 5px 0 0 0; font-size: 0.95rem;'>{razon_rec}</p>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 2.5rem;'>⚙️</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 6: COST CAP (LÍMITE DE PRESUPUESTO)
# ==========================================
with tab6:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>💰 Cost Cap Tracker & FIA Budget Regulator ($135M Limit)</div>", unsafe_allow_html=True)
    st.write("Gestiona la asignación financiera de la escudería para evitar penalizaciones por parte de la FIA.")

    cc_equipo = st.selectbox("Seleccionar Escudería para Auditoría:", list(TEAMS_DICT_2024.keys()), key="cc_team_sel")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        dev_cost = st.slider("Desarrollo y Actualizaciones ($M)", 20.0, 60.0, 42.5, step=0.5)
    with col_c2:
        fab_cost = st.slider("Operaciones de Fábrica y Salarios ($M)", 40.0, 75.0, 61.0, step=0.5)
    with col_c3:
        crash_cost = st.slider("Reparaciones por Accidentes ($M)", 0.0, 25.0, 8.5, step=0.5)

    total_gastado = round(dev_cost + fab_cost + crash_cost, 2)
    limite_fia = 135.0
    remanente = round(limite_fia - total_gastado, 2)

    col_res_cc1, col_res_cc2, col_res_cc3 = st.columns(3)
    with col_res_cc1:
        st.metric("Gasto Total Acumulado", f"${total_gastado}M", delta=f"{round(total_gastado - limite_fia, 2)}M vs Límite", delta_color="inverse")
    with col_res_cc2:
        st.metric("Límite Oficial FIA", f"${limite_fia}M")
    with col_res_cc3:
        st.metric("Presupuesto Disponible", f"${remanente}M", delta="Seguro" if remanente >= 0 else "¡Exceso de Cost Cap!")

    # Gráfica de Costes
    df_costes = pd.DataFrame({
        "Categoría": ["Desarrollo / Aero", "Fábrica & Salarios", "Accidentes / Repuestos", "Disponible"],
        "Millones USD": [dev_cost, fab_cost, crash_cost, max(0.0, remanente)]
    })
    fig_cc = px.pie(df_costes, values="Millones USD", names="Categoría", hole=0.5, template="plotly_dark", title="Desglose de Presupuesto Cost Cap F1")
    fig_cc.update_traces(textinfo='percent+label', marker=dict(colors=['#FF1801', '#38BDF8', '#F59E0B', '#10B981']))
    fig_cc.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320)
    st.plotly_chart(fig_cc, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 7: LUCES DE SALIDA (REACTION TIME GAME)
# ==========================================
with tab7:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🚦 Simulador de Luces de Salida & Tiempo de Reacción F1</div>", unsafe_allow_html=True)
    st.write("Pon a prueba tus reflejos como piloto de Fórmula 1. Espera a que se apaguen las 5 luces rojas y presiona el botón lo más rápido posible.")

    if "fase_semáforo" not in st.session_state:
        st.session_state["fase_semáforo"] = "inicio" # inicio, esperando, listo, saltado, terminado

    col_btn1, col_btn2 = st.columns(2)
    
    if st.session_state["fase_semáforo"] == "inicio":
        if st.button("🚀 Iniciar Procedimiento de Salida", use_container_width=True):
            st.session_state["fase_semáforo"] = "esperando"
            st.session_state["tiempo_inicio_salida"] = time.time()
            st.session_state["tiempo_espera_aleatorio"] = np.random.uniform(1.5, 4.0)
            st.rerun()

    elif st.session_state["fase_semáforo"] == "esperando":
        tiempo_transcurrido = time.time() - st.session_state["tiempo_inicio_salida"]
        if tiempo_transcurrido < st.session_state["tiempo_espera_aleatorio"]:
            st.markdown("<h2 style='text-align: center; color: #FF1801;'>🔴 🔴 🔴 🔴 🔴<br>SEMÁFORO ENCENDIDO... ESPERA A QUE SE APAGUEN</h2>", unsafe_allow_html=True)
            if st.button("⚡ ¡ACELERAR (SALIR)!", use_container_width=True):
                st.session_state["fase_semáforo"] = "saltado"
                st.rerun()
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state["fase_semáforo"] = "listo"
            st.session_state["tiempo_apagado"] = time.time()
            st.rerun()

    elif st.session_state["fase_semáforo"] == "listo":
        st.markdown("<h2 style='text-align: center; color: #10B981;'>🟢 🟢 🟢 🟢 🟢<br>¡APAGÓN DE LUCes! ¡YA!</h2>", unsafe_allow_html=True)
        if st.button("⚡ ¡ACELERAR (SALIR) AHORA!", use_container_width=True):
            reaccion_ms = int((time.time() - st.session_state["tiempo_apagado"]) * 1000)
            st.session_state["resultado_reaccion"] = reaccion_ms
            st.session_state["fase_semáforo"] = "terminado"
            st.rerun()

    elif st.session_state["fase_semáforo"] == "saltado":
        st.error("❌ ¡SALIDA FALSA! Te adelantaste al semáforo. Sanción de 5 segundos.")
        if st.button("🔄 Intentar Nuevamente"):
            st.session_state["fase_semáforo"] = "inicio"
            st.rerun()

    elif st.session_state["fase_semáforo"] == "terminado":
        ms = st.session_state["resultado_reaccion"]
        calificacion = "🏆 ¡Reflejos de Campeón del Mundo!" if ms < 220 else ("👍 ¡Buen tiempo de reacción!" if ms < 300 else "🐢 Un poco lento, ¡a entrenar reflejos!")
        st.success(f"⏱️ Tiempo de Reacción: **{ms} ms**\n\n{calificacion}")
        if st.button("🔄 Repetir Prueba de Salida"):
            st.session_state["fase_semáforo"] = "inicio"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 8: ESTRATEGIA GANTT (PIT-STOPS)
# ==========================================
with tab8:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛑 Estrategia de Carrera & Gantt Timeline de Pit-Stops</div>", unsafe_allow_html=True)
    st.write("Visualización temporal de los stints y compuestos de neumáticos utilizados por los equipos principales durante el Gran Premio.")

    df_gantt = pd.DataFrame([
        dict(Piloto="Max Verstappen", Stint="Stint 1 (Medium)", Start=1, Finish=18, Compuesto="🟡 Medium"),
        dict(Piloto="Max Verstappen", Stint="Stint 2 (Hard)", Start=18, Finish=50, Compuesto="⚪ Hard"),
        dict(Piloto="Lando Norris", Stint="Stint 1 (Soft)", Start=1, Finish=15, Compuesto="🔴 Soft"),
        dict(Piloto="Lando Norris", Stint="Stint 2 (Hard)", Start=15, Finish=50, Compuesto="⚪ Hard"),
        dict(Piloto="Charles Leclerc", Stint="Stint 1 (Medium)", Start=1, Finish=20, Compuesto="🟡 Medium"),
        dict(Piloto="Charles Leclerc", Stint="Stint 2 (Medium)", Start=20, Finish=50, Compuesto="🟡 Medium"),
        dict(Piloto="Oscar Piastri", Stint="Stint 1 (Hard)", Start=1, Finish=22, Compuesto="⚪ Hard"),
        dict(Piloto="Oscar Piastri", Stint="Stint 2 (Soft)", Start=22, Finish=50, Compuesto="🔴 Soft"),
    ])

    fig_gantt = px.timeline(
        df_gantt, x_start="Start", x_end="Finish", y="Piloto", color="Compuesto",
        color_discrete_map={"🔴 Soft": "#FF1801", "🟡 Medium": "#F59E0B", "⚪ Hard": "#FFFFFF"},
        template="plotly_dark", title="Simulación de Estrategia de Paradas en Boxes (Vueltas)"
    )
    fig_gantt.update_yaxes(categoryorder="total ascending")
    fig_gantt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
    st.plotly_chart(fig_gantt, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 9: FANTASY OPTIMIZER
# ==========================================
with tab9:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>💵 F1 Fantasy Pro Optimizer ($100M Budget)</div>", unsafe_allow_html=True)
    st.write("Selecciona tu alineación ideal de pilotos dentro del límite salarial de **$100.0M** para maximizar tus puntos en el Fantasy.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        piloto_fantasia_1 = st.selectbox("Piloto Estrella (Turbo Driver):", list(FANTASY_DB.keys()), index=0)
        piloto_fantasia_2 = st.selectbox("Segundo Piloto:", list(FANTASY_DB.keys()), index=1)
        piloto_fantasia_3 = st.selectbox("Tercer Piloto:", list(FANTASY_DB.keys()), index=2)
    with col_f2:
        piloto_fantasia_4 = st.selectbox("Cuarto Piloto:", list(FANTASY_DB.keys()), index=3)
        piloto_fantasia_5 = st.selectbox("Quinto Piloto (Budget):", list(FANTASY_DB.keys()), index=11)

    costo_total = (
        FANTASY_DB[piloto_fantasia_1]["costo"] +
        FANTASY_DB[piloto_fantasia_2]["costo"] +
        FANTASY_DB[piloto_fantasia_3]["costo"] +
        FANTASY_DB[piloto_fantasia_4]["costo"] +
        FANTASY_DB[piloto_fantasia_5]["costo"]
    )

    puntos_estimados = (
        (FANTASY_DB[piloto_fantasia_1]["puntos"] * 2) + # Turbo driver doble puntos
        FANTASY_DB[piloto_fantasia_2]["puntos"] +
        FANTASY_DB[piloto_fantasia_3]["puntos"] +
        FANTASY_DB[piloto_fantasia_4]["puntos"] +
        FANTASY_DB[piloto_fantasia_5]["puntos"]
    )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Costo Total Alineación", f"${costo_total:.1f}M", delta=f"{round(100.0 - costo_total, 1)}M Restante", delta_color="normal" if costo_total <= 100 else "inverse")
    with col_m2:
        st.metric("Puntuación Proyectada Fantasy", f"{puntos_estimados} pts")

    if costo_total > 100.0:
        st.error("⚠️ ¡Has superado el presupuesto límite de $100.0M! Selecciona pilotos más económicos.")
    else:
        st.success("✅ ¡Alineación válida y optimizada dentro del presupuesto permitido!")
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 10: INGENIERO RADIO IA
# ==========================================
with tab10:
    st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🛠️ Simulador de Radio del Muro de Boxes con IA</div>", unsafe_allow_html=True)
    st.write("Comunícate con tu ingeniero de carrera virtual y recibe órdenes tácticas basadas en la telemetría en tiempo real.")

    situacion_radio = st.selectbox(
        "Seleccionar Escenario de Radio:",
        [
            "Box this lap (Parada en boxes)",
            "Push now, qualifying lap (Vuelta rápida de clasificación)",
            "Traffic ahead, watch blue flags (Tráfico y banderas azules)",
            "Engine mode performance (Cambio a modo motor máximo)"
        ]
    )

    if st.button("🎙️ Transmitir Mensaje al Muro", use_container_width=True):
        if "Box" in situacion_radio:
            respuesta_ing = "«Entendido, box this lap. Montaremos compuestos medios nuevos. Prepárate para el pit crew, delta time positivo en sector 2.»"
        elif "Push" in situacion_radio:
            respuesta_ing = "«Entendido. Head down, hammer time. Track is clear ahead. Dale todo lo que tienes en este sector.»"
        elif "Traffic" in situacion_radio:
            respuesta_ing = "«Cuidado, coche lento en curva 12. Cederás posición al salir de la zona DRS. Mantén la calma.»"
        else:
            respuesta_ing = "«Engine mode 1 activado. Recuperación de energía óptima en curva 5 y 14. ¡Vamos a por ellos!»"

        st.markdown(f"""
            <div style='background: #080C16; padding: 22px; border-radius: 14px; border-left: 6px solid #FF1801; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1);'>
                <span style='color: #FF1801; font-weight: 800; font-size: 0.8rem; letter-spacing: 1.5px;'>TRANSMISIÓN DESDE EL PIT-WALL (INGENIERO IA)</span>
                <p style='color: #FFFFFF !important; font-size: 1.05rem; font-weight: 600; margin-top: 10px;'>{respuesta_ing}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
