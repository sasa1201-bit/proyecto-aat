import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN ESTÉTICA (Copia exacta de tu diseño funcional)
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

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
# FUNCIONES LÓGICAS (Las que ya teníamos y funcionaban)
# =========================================================================
@st.cache_data(ttl=300)
def obtener_historial_real(id_equipo):
    año = datetime.now().year
    url = f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season={año}"
    res = requests.get(url, headers=HEADERS)
    return res.json().get("response", []) if res.status_code == 200 else []

# =========================================================================
# INTERFAZ
# =========================================================================
st.markdown("<h1>⚽ Forza Fútbol Live</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas de Liga"])

with tab1:
    # Selector
    busqueda = st.text_input("Busca un club:", value="Real Madrid")
    if len(busqueda) >= 3:
        res = requests.get(f"https://v3.football.api-sports.io/teams?search={busqueda}", headers=HEADERS)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data:
                opciones = {f"{i['team']['name']}": i['team'] for i in data}
                sel = st.selectbox("Selecciona:", list(opciones.keys()))
                t = opciones[sel]
                st.session_state.update({"id": t['id'], "name": t['name'], "logo": t['logo']})

    # Mostrar equipo seleccionado
    st.markdown(f"<div class='premium-card'><h2><img src='{st.session_state.get('logo')}'> {st.session_state.get('name')}</h2></div>", unsafe_allow_html=True)

    # Resultados Reales (Divididos parejo)
    col1, col2 = st.columns(2)
    historial = obtener_historial_real(st.session_state.get('id', 541))
    
    with col1:
        st.markdown("<div class='premium-card'><div class='section-title'>⏮️ Anteriores</div>", unsafe_allow_html=True)
        for m in [f for f in historial if f['fixture']['status']['short'] == 'FT'][:5]:
            st.write(f"{m['teams']['home']['name']} {m['goals']['home']} - {m['goals']['away']} {m['teams']['away']['name']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='premium-card'><div class='section-title'>⏭️ Próximos</div>", unsafe_allow_html=True)
        for m in [f for f in historial if f['fixture']['status']['short'] == 'NS'][:5]:
            st.write(f"{m['teams']['home']['name']} vs {m['teams']['away']['name']} - {m['fixture']['date'][11:16]}")
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='premium-card'><div class='section-title'>🔴 En Vivo</div>", unsafe_allow_html=True)
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
    if res_live.status_code == 200:
        for m in res_live.json().get("response", [])[:8]:
            st.write(f"⏱️ {m['fixture']['status']['elapsed']}' | {m['teams']['home']['name']} {m['goals']['home']} - {m['goals']['away']} {m['teams']['away']['name']}")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='premium-card'><div class='section-title'>📊 Estadísticas</div>", unsafe_allow_html=True)
    st.bar_chart(pd.DataFrame({'Partidos': [15, 10, 8]}, index=['Liga MX', 'La Liga', 'Premier']))
    st.markdown("</div>", unsafe_allow_html=True)
