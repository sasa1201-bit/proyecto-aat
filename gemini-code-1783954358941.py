import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="Forza Football Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto refresco cada minuto
st_autorefresh(interval=60000, key="refresh")

API_KEY = "TU_API_KEY"

HEADERS = {
    "x-apisports-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

# ==========================================================
# CSS PROFESIONAL
# ==========================================================

st.markdown("""

<style>

html, body, [class*="css"]{
    color:#000000;
}

.stApp{
    background:#f4f6fb;
}

section[data-testid="stSidebar"]{
    background:#111827;
}

section[data-testid="stSidebar"] *{
    color:white;
}

h1,h2,h3,h4,h5{
    color:black !important;
}

p{
    color:black;
}

label{
    color:black !important;
    font-weight:600;
}

.stTextInput label{
    color:black !important;
}

.stSelectbox label{
    color:black !important;
}

div[data-baseweb="select"]{
    color:black;
}

div[data-baseweb="input"]{
    color:black;
}

div[data-baseweb="select"] span{
    color:black;
}

.card{

    background:white;

    border-radius:18px;

    padding:20px;

    margin-bottom:20px;

    box-shadow:0px 3px 15px rgba(0,0,0,.08);

}

.score{

    font-size:25px;

    font-weight:bold;

    color:#1d4ed8;

}

.win{

color:green;

font-weight:bold;

}

.draw{

color:orange;

font-weight:bold;

}

.lose{

color:red;

font-weight:bold;

}

</style>

""", unsafe_allow_html=True)

# ==========================================================
# SESSION STATE
# ==========================================================

if "team_id" not in st.session_state:

    st.session_state.team_id=541

    st.session_state.team_name="Real Madrid"

    st.session_state.team_logo="https://media.api-sports.io/football/teams/541.png"

# ==========================================================
# FUNCIONES API
# ==========================================================

@st.cache_data(ttl=300)

def buscar_equipos(nombre):

    url=f"https://v3.football.api-sports.io/teams?search={nombre}"

    r=requests.get(url,headers=HEADERS)

    if r.status_code==200:

        return r.json()["response"]

    return []

@st.cache_data(ttl=300)

def obtener_partidos(team):

    url=f"https://v3.football.api-sports.io/fixtures?team={team}&season=2026"

    r=requests.get(url,headers=HEADERS)

    if r.status_code==200:

        return r.json()["response"]

    return []

@st.cache_data(ttl=300)

def obtener_estadisticas(team):

    url=f"https://v3.football.api-sports.io/teams/statistics?league=140&season=2026&team={team}"

    r=requests.get(url,headers=HEADERS)

    if r.status_code==200:

        return r.json()["response"]

    return None

@st.cache_data(ttl=300)

def partidos_vivo():

    url="https://v3.football.api-sports.io/fixtures?live=all"

    r=requests.get(url,headers=HEADERS)

    if r.status_code==200:

        return r.json()["response"]

    return []

# ==========================================================
# TITULO
# ==========================================================

st.title("⚽ FORZA FOOTBALL PRO")

st.write("Dashboard profesional de estadísticas en tiempo real")

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("Buscar Club")

texto=st.sidebar.text_input(
    "Nombre del equipo"
)

if len(texto)>=3:

    equipos=buscar_equipos(texto)

    if len(equipos)>0:

        nombres=[x["team"]["name"] for x in equipos]

        elegido=st.sidebar.selectbox(
            "Selecciona",
            nombres
        )

        equipo=[x for x in equipos if x["team"]["name"]==elegido][0]

        st.session_state.team_id=equipo["team"]["id"]

        st.session_state.team_name=equipo["team"]["name"]

        st.session_state.team_logo=equipo["team"]["logo"]

st.sidebar.image(
    st.session_state.team_logo,
    width=150
)

st.sidebar.markdown(
    f"## {st.session_state.team_name}"
)

# ==========================================================
# TABS
# ==========================================================

tab1,tab2,tab3,tab4=st.tabs(

[
"🏟 Equipo",

"🔴 En Vivo",

"📊 Estadísticas",

"📈 Dashboard"

]

)

# ==========================================================
# TAB EQUIPO
# ==========================================================

with tab1:

    partidos=obtener_partidos(
        st.session_state.team_id
    )

    st.markdown("<div class='card'>",unsafe_allow_html=True)

    col1,col2=st.columns([1,5])

    with col1:

        st.image(
            st.session_state.team_logo,
            width=120
        )

    with col2:

        st.header(
            st.session_state.team_name
        )

        st.write(
            "Información oficial del club y calendario."
        )

    st.markdown("</div>",unsafe_allow_html=True)

    izquierda,derecha=st.columns(2)

    # ==========================================
    # ÚLTIMOS PARTIDOS
    # ==========================================

    with izquierda:

        st.subheader("📅 Últimos encuentros")

        terminados=[

            x for x in partidos

            if x["fixture"]["status"]["short"]=="FT"

        ]

        terminados=terminados[-5:]

        terminados.reverse()

        for partido in terminados:

            fecha=datetime.fromisoformat(

                partido["fixture"]["date"].replace("Z","+00:00")

            ).strftime("%d/%m/%Y")

            casa=partido["teams"]["home"]["name"]

            visita=partido["teams"]["away"]["name"]

            gh=partido["goals"]["home"]

            ga=partido["goals"]["away"]

            liga=partido["league"]["name"]

            st.markdown(f"""

<div class="card">

<b>{fecha}</b><br>

🏆 {liga}<br><br>

{casa}<br>

<h3>{gh} - {ga}</h3>

{visita}

</div>

""",unsafe_allow_html=True)

    # ==========================================
    # PRÓXIMOS PARTIDOS
    # ==========================================

    with derecha:

        st.subheader("📆 Próximos encuentros")

        futuros=[

            x for x in partidos

            if x["fixture"]["status"]["short"]=="NS"

        ]

        futuros=futuros[:5]

        for partido in futuros:

            fecha=datetime.fromisoformat(

                partido["fixture"]["date"].replace("Z","+00:00")

            ).strftime("%d/%m/%Y %H:%M")

            casa=partido["teams"]["home"]["name"]

            visita=partido["teams"]["away"]["name"]

            liga=partido["league"]["name"]

            estadio=partido["fixture"]["venue"]["name"]

            st.markdown(f"""

<div class="card">

<b>{fecha}</b><br>

🏆 {liga}<br>

🏟 {estadio}<br><br>

<b>{casa}</b>

<br>

VS

<br>

<b>{visita}</b>

</div>

""",unsafe_allow_html=True)

            st.markdown(f"""

<div class="card">

<b>{fecha}</b><br>

🏆 {liga}<br>

🏟 {estadio}<br><br>

<b>{casa}</b>

<br>

VS

<br>

<b>{visita}</b>

</div>

""", unsafe_allow_html=True)
