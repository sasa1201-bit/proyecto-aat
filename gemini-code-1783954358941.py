import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Forza Fútbol Live", layout="wide")

# CSS Profesional (Estilo ESPN/SofaScore)
st.markdown("""
    <style>
        .stApp { background-color: #0F172A; }
        .card { background-color: #1E293B; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; color: white; }
        .match-card { background-color: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 10px; color: #000; display: flex; justify-content: space-between; align-items: center; }
        h1, h2, h3 { color: #ffffff !important; }
        .score { font-weight: bold; font-size: 1.2rem; color: #4F46E5; }
    </style>
""", unsafe_allow_html=True)

# API
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# Estado inicial
if "id_sel" not in st.session_state:
    st.session_state.update({"id_sel": 541, "name_sel": "Real Madrid", "logo_sel": "https://media.api-sports.io/football/teams/541.png"})

st.title("⚽ Forza Fútbol Live")
tab1, tab2, tab3 = st.tabs(["🔍 Buscador", "🔴 En Vivo", "📈 Estadísticas"])

with tab1:
    busqueda = st.text_input("Busca tu equipo:")
    if len(busqueda) >= 3:
        res = requests.get(f"https://v3.football.api-sports.io/teams?search={busqueda}", headers=HEADERS)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data:
                opciones = {i['team']['name']: i['team'] for i in data}
                sel = st.selectbox("Selecciona:", list(opciones.keys()))
                t = opciones[sel]
                st.session_state.update({"id_sel": t['id'], "name_sel": t['name'], "logo_sel": t['logo']})

    # Header del equipo
    st.markdown(f"<div class='card' style='text-align:center'><h1><img src='{st.session_state.logo_sel}' width='80'> {st.session_state.name_sel}</h1></div>", unsafe_allow_html=True)
    
    # Partidos Reales
    res_fix = requests.get(f"https://v3.football.api-sports.io/fixtures?team={st.session_state.id_sel}&season=2026", headers=HEADERS)
    if res_fix.status_code == 200:
        fixtures = res_fix.json().get("response", [])
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⏮️ Últimos")
            for m in [f for f in fixtures if f['fixture']['status']['short'] == 'FT'][-3:]:
                st.markdown(f"<div class='match-card'>{m['teams']['home']['name']} <b>{m['goals']['home']} - {m['goals']['away']}</b> {m['teams']['away']['name']}</div>", unsafe_allow_html=True)
        with c2:
            st.subheader("⏭️ Próximos")
            for m in [f for f in fixtures if f['fixture']['status']['short'] == 'NS'][:3]:
                st.markdown(f"<div class='match-card'>{m['teams']['home']['name']} vs {m['teams']['away']['name']} <br><small>{m['fixture']['date'][11:16]}</small></div>", unsafe_allow_html=True)

with tab2:
    st.subheader("🔴 Marcadores en Vivo")
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
    if res_live.status_code == 200:
        for m in res_live.json().get("response", [])[:6]:
            st.markdown(f"""
                <div class='match-card'>
                    <span><img src='{m['teams']['home']['logo']}' width='20'> {m['teams']['home']['name']}</span>
                    <span class='score'>{m['goals']['home']} - {m['goals']['away']} | {m['fixture']['status']['elapsed']}'</span>
                    <span>{m['teams']['away']['name']} <img src='{m['teams']['away']['logo']}' width='20'></span>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("📊 Analítica Profesional")
    df = pd.DataFrame({'Categoría': ['Victorias', 'Empates', 'Derrotas'], 'Valores': [15, 5, 2]})
    fig = px.bar(df, x='Categoría', y='Valores', color='Categoría', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
