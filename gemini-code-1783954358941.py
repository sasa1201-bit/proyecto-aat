import streamlit as st
import pandas as pd
import requests

# CONFIGURACIÓN
st.set_page_config(page_title="Forza Fútbol Live", layout="wide")
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

# ESTADO INICIAL
if "id" not in st.session_state:
    st.session_state.update({"id": 541, "name": "Real Madrid", "logo": "https://media.api-sports.io/football/teams/541.png"})

st.title("⚽ Forza Fútbol Live")
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas"])

# PESTAÑA 1: BUSCADOR
with tab1:
    busqueda = st.text_input("Busca un club:")
    if len(busqueda) >= 3:
        res = requests.get(f"https://v3.football.api-sports.io/teams?search={busqueda}", headers=HEADERS)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data:
                opciones = {f"{i['team']['name']}": i['team'] for i in data}
                sel = st.selectbox("Selecciona equipo:", list(opciones.keys()))
                t = opciones[sel]
                st.session_state.update({"id": t['id'], "name": t['name'], "logo": t['logo']})

    st.markdown(f"## <img src='{st.session_state.logo}' width='50'> {st.session_state.name}", unsafe_allow_html=True)
    
    # Datos reales de la API
    res_fix = requests.get(f"https://v3.football.api-sports.io/fixtures?team={st.session_state.id}&season=2026", headers=HEADERS)
    if res_fix.status_code == 200:
        fixtures = res_fix.json().get("response", [])
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("⏮️ Últimos Resultados")
            for m in [f for f in fixtures if f['fixture']['status']['short'] == 'FT'][-5:]:
                st.write(f"{m['teams']['home']['name']} **{m['goals']['home']} - {m['goals']['away']}** {m['teams']['away']['name']}")
        with col2:
            st.subheader("⏭️ Próximos Partidos")
            for m in [f for f in fixtures if f['fixture']['status']['short'] == 'NS'][:5]:
                st.write(f"{m['teams']['home']['name']} vs {m['teams']['away']['name']} - {m['fixture']['date'][11:16]}")

# PESTAÑA 2: EN VIVO (Con minutos)
with tab2:
    st.subheader("🔴 Marcadores en Vivo")
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS)
    if res_live.status_code == 200:
        for m in res_live.json().get("response", [])[:10]:
            st.markdown(f"""
                <div style='display:flex; justify-content:space-between; border-bottom:1px solid #ddd; padding:5px;'>
                    <span><img src='{m['teams']['home']['logo']}' width='20'> {m['teams']['home']['name']}</span>
                    <b>{m['goals']['home']} - {m['goals']['away']} | ⏱️ {m['fixture']['status']['elapsed']}'</b>
                    <span>{m['teams']['away']['name']} <img src='{m['teams']['away']['logo']}' width='20'></span>
                </div>
            """, unsafe_allow_html=True)

# PESTAÑA 3: GRÁFICAS (Estilo original)
with tab3:
    st.subheader("📈 Analítica de Volumen")
    df = pd.DataFrame({'Partidos': [12, 5, 8]}, index=['Liga España', 'Liga MX', 'Premier League'])
    st.bar_chart(df)
