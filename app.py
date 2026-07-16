import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN ESTÉTICA PREMIUM (Estilo ESPN / Dark Mode)
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

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
        .section-title { color: #FFFFFF !important; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #334155; padding-bottom: 8px; }
        .live-team-name { color: #FFFFFF !important; font-weight: 800 !important; font-size: 1.15rem !important; }
        .live-score { color: #EF4444 !important; font-weight: 900 !important; font-size: 1.5rem !important; margin: 0 15px !important; background: #000000; padding: 4px 12px; border-radius: 6px; }
        .live-league-label { color: #94A3B8 !important; font-weight: 600 !important; font-size: 0.85rem !important; }
        .pulse-minute { background-color: #EF4444; color: #FFFFFF !important; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 800; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] { background-color: #0F172A !important; color: #FFFFFF !important; border: 1px solid #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("<div style='margin-bottom: 30px; display: flex; align-items: center; gap: 15px;'><div style='background-color: #EF4444; width: 8px; height: 60px; border-radius: 4px;'></div><div><h1 style='color: #FFFFFF !important; font-size: 2.5rem; font-weight: 900; margin: 0;'>FORZA FÚTBOL LIVE</h1><p style='color: #94A3B8 !important; font-size: 1rem; margin: 0; text-transform: uppercase; letter-spacing: 2px;'>Motor Analítico de Rendimiento Deportivo</p></div></div>", unsafe_allow_html=True)

# Configuración API
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo(key_api):
    try: response = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS); return response.json().get("response", []) if response.status_code == 200 else []
    except: return []

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3: return []
    try: response = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}", headers=HEADERS); return response.json().get("response", []) if response.status_code == 200 else []
    except: return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo, nombre_equipo, pais_equipo):
    try:
        res_pasados = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&last=15", headers=HEADERS)
        res_futuros = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&next=5", headers=HEADERS)
        partidos = []
        if res_pasados.status_code == 200: partidos.extend(res_pasados.json().get("response", []))
        if res_futuros.status_code == 200: partidos.extend(res_futuros.json().get("response", []))
        return (partidos, "api_directa") if partidos else (generar_respaldo(nombre_equipo, pais_equipo), "local_respaldo")
    except: return generar_respaldo(nombre_equipo, pais_equipo), "local_respaldo"

def generar_respaldo(n, p): return [{"Fecha": "2026-07-20 18:00", "Competencia": "Liga Test", "Local": n, "Goles Local": 2, "Goles Visita": 1, "Visita": "Rival", "Estado": "FT"}]

live_fixtures = obtener_partidos_en_vivo(API_KEY)
df_live = pd.DataFrame([{"Liga": m['league']['name'], "Logo_Liga": m['league']['logo'], "Local": m['teams']['home']['name'], "Logo_L": m['teams']['home']['logo'], "Goles L": m['goals']['home'] or 0, "Visita": m['teams']['away']['name'], "Logo_V": m['teams']['away']['logo'], "Goles V": m['goals']['away'] or 0, "Minuto": m['fixture']['status']['elapsed']} for m in live_fixtures]) if live_fixtures else pd.DataFrame()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Panel Principal", "🔴 Central En Vivo", "📈 Analítica Avanzada", "🤖 Scout IA"])

# (Lógica de tab1, tab2 y tab3 se mantienen igual...)
# ... (omito parte redundante para brevedad, solo pega esta lógica de IA en el tab4)

with tab4:
    st.markdown("<div class='premium-card'><div class='section-title'>🤖 Scout IA - Análisis Táctico</div>", unsafe_allow_html=True)
    
    # Supongamos que ya tienes los cálculos (victorias, promedio_goles, etc) en tab1
    # Asegúrate de usar las mismas variables de cálculo que en tab1
    pregunta_usuario = st.chat_input(f"Pregunta a la IA sobre el rendimiento del equipo...")
    
    if pregunta_usuario:
        with st.chat_message("user", avatar="👤"): st.write(pregunta_usuario)
        with st.chat_message("assistant", avatar="🤖"):
            p_low = pregunta_usuario.lower()
            if "gol" in p_low:
                st.write(f"Basado en los datos, el equipo promedia {promedio_goles} goles por partido actualmente.")
            elif "ganar" in p_low or "victoria" in p_low:
                st.write(f"El equipo registra {victorias} victorias. Su efectividad actual es del {efectividad}%.")
            else:
                st.write(f"He analizado el historial. El equipo presenta un rendimiento {'óptimo' if efectividad >= 50 else 'deficiente'} con {victorias} victorias en su registro reciente.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #334155; margin-top: 40px;'><div style='text-align: center; color: #64748B; font-size: 0.9rem;'>Forza Football Analytics V3.0 | Proyecto Salomón Achar © 2026</div>", unsafe_allow_html=True)
