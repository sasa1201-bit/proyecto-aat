import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN ESTÉTICA PREMIUM Y ESTADO DE SESIÓN
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

# Inicialización de estados
if "id_seleccionado" not in st.session_state:
    st.session_state.update({
        "id_seleccionado": 541, 
        "nombre_seleccionado": "Real Madrid", 
        "logo_seleccionado": "https://media.api-sports.io/football/teams/541.png",
        "pais_seleccionado": "Spain"
    })

st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; }
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3 { color: #000000 !important; }
        .premium-card { background-color: #ffffff !important; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .section-title { color: #000000 !important; font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; }
        .live-score { color: #4f46e5 !important; font-weight: 900 !important; margin: 0 15px !important; }
    </style>
""", unsafe_allow_html=True)

# API
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

@st.cache_data(ttl=600)
def buscar_equipo_api(nombre):
    if not nombre or len(nombre) < 3: return []
    res = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre}", headers=HEADERS)
    return res.json().get("response", []) if res.status_code == 200 else []

# =========================================================================
# INTERFAZ Y LÓGICA
# =========================================================================
st.markdown("<h1>⚽ Forza Fútbol Live</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas"])

with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    busqueda = st.text_input("Busca un club:", value="Real Madrid")
    
    if len(busqueda) >= 3:
        resultados = buscar_equipo_api(busqueda)
        if resultados:
            # Crear diccionario para el selectbox
            opciones = {f"{i['team']['name']}": i['team'] for i in resultados}
            seleccion = st.selectbox("Selecciona equipo:", options=list(opciones.keys()))
            if seleccion:
                t = opciones[seleccion]
                st.session_state.update({
                    "id_seleccionado": t['id'], 
                    "nombre_seleccionado": t['name'], 
                    "logo_seleccionado": t['logo']
                })
    
    # Tarjeta de Equipo con Escudo Activo
    st.markdown(f"""
        <div style='display: flex; align-items: center; padding: 10px;'>
            <img src='{st.session_state.logo_seleccionado}' width='80' style='margin-right: 20px;'>
            <h1>{st.session_state.nombre_seleccionado}</h1>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Resultados con Escudo
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>⏮️ Últimos Resultados</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #e2e8f0;'>
            <img src='{st.session_state.logo_seleccionado}' width='40' style='margin-right: 15px;'>
            <span><b>{st.session_state.nombre_seleccionado}</b> vs Rival (Simulado) - Resultado 3:1</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔴 Marcadores en Vivo</div>", unsafe_allow_html=True)
    # Lógica de partidos en vivo desde API
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
    if res_live.status_code == 200:
        data = res_live.json().get("response", [])
        if not data:
            st.info("No hay partidos en vivo en este momento.")
        for match in data[:5]: # Mostramos los 5 primeros
            h = match['teams']['home']
            a = match['teams']['away']
            st.markdown(f"""
                <div style='display: flex; align-items: center; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee;'>
                    <div><img src='{h['logo']}' width='30'> {h['name']}</div>
                    <div class='live-score'>{match['goals']['home']} - {match['goals']['away']}</div>
                    <div>{a['name']} <img src='{a['logo']}' width='30'></div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📈 Analítica de Volumen</div>", unsafe_allow_html=True)
    st.bar_chart(pd.DataFrame({'Partidos': [12, 8, 5]}, index=['Liga España', 'Premier League', 'Liga MX']))
    st.markdown("</div>", unsafe_allow_html=True)
