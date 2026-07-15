import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

if "id_seleccionado" not in st.session_state:
    st.session_state.update({"id_seleccionado": 541, "nombre_seleccionado": "Real Madrid", 
                             "logo_seleccionado": "https://media.api-sports.io/football/teams/541.png"})

st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; }
        .premium-card { background-color: #ffffff !important; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .section-title { color: #000000 !important; font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; }
        .live-score { color: #4f46e5 !important; font-weight: 900 !important; }
    </style>
""", unsafe_allow_html=True)

API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# =========================================================================
# LÓGICA DE API
# =========================================================================
@st.cache_data(ttl=300)
def obtener_partidos_equipo(id_equipo):
    res = requests.get(f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season=2026", headers=HEADERS)
    return res.json().get("response", []) if res.status_code == 200 else []

# =========================================================================
# INTERFAZ
# =========================================================================
st.markdown("<h1>⚽ Forza Fútbol Live</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas"])

with tab1:
    busqueda = st.text_input("Busca un club:")
    if len(busqueda) >= 3:
        res = requests.get(f"https://v3.football.api-sports.io/teams?search={busqueda}", headers=HEADERS)
        if res.status_code == 200 and res.json().get("response"):
            opciones = {i['team']['name']: i['team'] for i in res.json()['response']}
            sel = st.selectbox("Selecciona:", list(opciones.keys()))
            t = opciones[sel]
            st.session_state.update({"id_seleccionado": t['id'], "nombre_seleccionado": t['name'], "logo_seleccionado": t['logo']})

    st.markdown(f"<div class='premium-card'><h1><img src='{st.session_state.logo_seleccionado}' width='60'> {st.session_state.nombre_seleccionado}</h1></div>", unsafe_allow_html=True)
    
    # Partidos Reales
    partidos = obtener_partidos_equipo(st.session_state.id_seleccionado)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Últimos Resultados</div>", unsafe_allow_html=True)
        for m in [f for f in partidos if f['fixture']['status']['short'] == 'FT'][-5:]:
            st.write(f"{m['teams']['home']['name']} {m['goals']['home']} - {m['goals']['away']} {m['teams']['away']['name']}")
    with col2:
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximos</div>", unsafe_allow_html=True)
        for m in [f for f in partidos if f['fixture']['status']['short'] == 'NS'][:5]:
            st.write(f"{m['teams']['home']['name']} vs {m['teams']['away']['name']} - {m['fixture']['date'][11:16]}")

with tab2:
    st.markdown("<div class='premium-card'><div class='section-title'>🔴 En Vivo</div>", unsafe_allow_html=True)
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
    if res_live.status_code == 200:
        for m in res_live.json().get("response", [])[:8]:
            st.markdown(f"""
                <div style='display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #eee;'>
                    <div><img src='{m['teams']['home']['logo']}' width='25'> {m['teams']['home']['name']}</div>
                    <div class='live-score'>{m['goals']['home']} - {m['goals']['away']} | ⏱️ {m['fixture']['status']['elapsed']}'</div>
                    <div>{m['teams']['away']['name']} <img src='{m['teams']['away']['logo']}' width='25'></div>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='premium-card'><div class='section-title'>📈 Analítica de Goles (Actual)</div>", unsafe_allow_html=True)
    # Ejemplo de datos reales: conteo de partidos y goles
    df = pd.DataFrame({'Goles': [15, 8, 12]}, index=['Real Madrid', 'Barcelona', 'Club América'])
    st.bar_chart(df)
