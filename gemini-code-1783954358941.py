import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN ESTÉTICA PREMIUM
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; }
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3 { color: #000000 !important; }
        button[data-baseweb="tab"] { color: #000000 !important; }
        button[data-baseweb="tab"] p { color: #000000 !important; font-weight: 700 !important; }
        .premium-card { background-color: #ffffff !important; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .section-title { color: #000000 !important; font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; }
        .live-team-name { color: #000000 !important; font-weight: 800 !important; }
        .live-score { color: #4f46e5 !important; font-weight: 900 !important; margin: 0 15px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #000000 !important;'>⚽ Forza Fútbol Live</h1>", unsafe_allow_html=True)

# =========================================================================
# LÓGICA DE API Y DATOS
# =========================================================================
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

@st.cache_data(ttl=600)
def buscar_equipo_api(nombre):
    if not nombre or len(nombre) < 3: return []
    res = requests.get(f"https://v3.football.api-sports.io/teams?search={nombre}", headers=HEADERS)
    return res.json().get("response", []) if res.status_code == 200 else []

# =========================================================================
# INTERFAZ
# =========================================================================
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas"])

with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    busqueda = st.text_input("Busca un club:", value="Real Madrid")
    
    if "id_seleccionado" not in st.session_state:
        st.session_state.update({"id_seleccionado": 541, "nombre_seleccionado": "Real Madrid", "logo_seleccionado": "https://media.api-sports.io/football/teams/541.png"})

    if len(busqueda) >= 3:
        resultados = buscar_equipo_api(busqueda)
        if resultados:
            opciones = {f"{i['team']['name']} ({i['team']['country']})": i['team'] for i in resultados}
            seleccion = st.selectbox("Selecciona:", options=list(opciones.keys()))
            if seleccion:
                t = opciones[seleccion]
                st.session_state.update({"id_seleccionado": t['id'], "nombre_seleccionado": t['name'], "logo_seleccionado": t['logo']})
    
    # Tarjeta de Equipo con Logo
    st.markdown(f"""
        <div style='display: flex; align-items: center; padding: 10px;'>
            <img src='{st.session_state.logo_seleccionado}' width='60' style='margin-right: 20px;'>
            <h2>{st.session_state.nombre_seleccionado}</h2>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.info("Visualizando marcadores en tiempo real.")

with tab3:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.bar_chart(pd.DataFrame({'Partidos': [10, 5, 8]}, index=['Liga A', 'Liga B', 'Liga C']), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
