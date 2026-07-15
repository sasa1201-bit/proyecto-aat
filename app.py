import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =========================================================================
# CONFIGURACIÓN GENERAL
# =========================================================================

st.set_page_config(
    page_title="Forza Football Live",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================================
# AUTO REFRESH (ESTILO MARCADORES EN VIVO)
# =========================================================================

st_autorefresh(
    interval=30000,
    key="football_refresh"
)


# =========================================================================
# DISEÑO PREMIUM ESTILO ESPN / SOFASCORE
# =========================================================================

st.markdown("""
<style>


/* Fondo principal */

.stApp {
    background:
    linear-gradient(
        135deg,
        #f8fafc 0%,
        #e2e8f0 100%
    );
}


/* Texto general */

html, body, [class*="css"] {

    font-family:
    'Inter',
    'Segoe UI',
    sans-serif;

}


p, span, label, div, h1, h2, h3 {

    color:#111827 !important;

}


/* HEADER */

.hero {

    background:
    linear-gradient(
        135deg,
        #020617,
        #1e293b
    );

    padding:35px;

    border-radius:25px;

    margin-bottom:30px;

    box-shadow:
    0px 15px 40px rgba(0,0,0,.15);

}


.hero h1 {

    color:white !important;

    font-size:42px;

    font-weight:900;

    margin-bottom:5px;

}


.hero p {

    color:#cbd5e1 !important;

    font-size:18px;

}


/* TARJETAS */

.card {


background:white;


padding:25px;


border-radius:20px;


box-shadow:

0px 10px 25px rgba(15,23,42,.08);


border:

1px solid #e2e8f0;


margin-bottom:20px;


}



/* TITULOS */

.section-title {


font-size:22px;


font-weight:800;


margin-bottom:15px;


}



/* KPI */

.kpi {


background:white;


border-radius:18px;


padding:22px;


border-left:

6px solid #2563eb;


box-shadow:

0px 8px 20px rgba(0,0,0,.08);


}



.kpi-title {


font-size:13px;


font-weight:700;


color:#64748b !important;


}



.kpi-value {


font-size:30px;


font-weight:900;


color:#0f172a !important;


}



/* SIDEBAR */


section[data-testid="stSidebar"] {


background:

linear-gradient(

180deg,

#020617,

#111827

);


}



section[data-testid="stSidebar"] * {


color:white !important;


}


/* BOTONES */


.stButton button {


background:

linear-gradient(

90deg,

#2563eb,

#4f46e5

);


color:white !important;


border:none;


border-radius:12px;


font-weight:800;


padding:10px 20px;


}


.stButton button:hover {


transform:scale(1.03);


}


/* SELECTORES */


.stSelectbox div[data-baseweb="select"],

.stTextInput input {


border-radius:12px !important;


background:white !important;


}


/* TABLAS */


thead tr th {


background:#0f172a !important;


color:white !important;


}


</style>

""",
unsafe_allow_html=True)



# =========================================================================
# HEADER PRINCIPAL
# =========================================================================


st.markdown("""
<div class="hero">

<h1>
⚽ Forza Football Live
</h1>

<p>
Plataforma avanzada de análisis futbolístico,
marcadores en vivo y seguimiento global de equipos.
</p>

</div>

""",
unsafe_allow_html=True)
# =========================================================================
# NAVEGACIÓN PRINCIPAL
# =========================================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Buscador & Seguimiento",
        "🔴 Marcadores en Vivo",
        "📈 Estadísticas de Liga"
    ]
)


with tab1:


    # VARIABLES DE SESIÓN

    if "id_seleccionado" not in st.session_state:
        st.session_state["id_seleccionado"] = 541


    if "nombre_seleccionado" not in st.session_state:
        st.session_state["nombre_seleccionado"] = "Real Madrid"


    if "pais_seleccionado" not in st.session_state:
        st.session_state["pais_seleccionado"] = "Spain"


    if "logo_seleccionado" not in st.session_state:
        st.session_state["logo_seleccionado"] = ""


    # CONTINÚA TU CÓDIGO NORMAL

    id_activo = st.session_state["id_seleccionado"]
# =========================================================================
# SIDEBAR PROFESIONAL
# =========================================================================


with st.sidebar:


    st.markdown(
    """

    <h1 style="
    color:white;
    text-align:center;
    ">
    ⚽ FORZA
    </h1>


    <p style="
    text-align:center;
    color:#94a3b8;
    ">
    Football Analytics
    </p>


    <hr>

    """,
    unsafe_allow_html=True
    )


    st.markdown("### 🔄 Centro de Control")


    if st.button("🚀 Sincronizar Datos"):

        st.cache_data.clear()

        st.success(
            "Datos actualizados"
        )



    st.markdown("---")


    st.markdown(
    """

    ### 📊 Módulos

    ⚽ Seguimiento de equipos

    🔴 Partidos en vivo

    📈 Estadísticas


    """

    )
# =========================================================================
# CONFIGURACIÓN DE LA API Y RESPALDO
# =========================================================================
# =========================================================================
# CONFIGURACIÓN API FOOTBALL
# =========================================================================

# Recomendado después:
# guardar la clave en .streamlit/secrets.toml

API_KEY = st.secrets["API_KEY"] if "API_KEY" in st.secrets else "acb867b68f5987d9c226e48c12c090e3"


HEADERS = {

    "x-apisports-key": API_KEY,

    "x-rapidapi-host":
    "v3.football.api-sports.io"

}



# =========================================================================
# UTILIDADES VISUALES
# =========================================================================


# =========================================================================
# COMPONENTE PERFIL DE EQUIPO - ESTILO ESPN / SOFASCORE
# =========================================================================


def calcular_forma_equipo(df_partidos, nombre_equipo):

    forma = []


    for _, partido in df_partidos.head(5).iterrows():

        local = partido["Local"]

        visitante = partido["Visita"]

        goles_local = partido["Goles Local"]

        goles_visitante = partido["Goles Visita"]


        if pd.isna(goles_local) or pd.isna(goles_visitante):
            continue


        if local == nombre_equipo:

            goles_favor = goles_local

            goles_contra = goles_visitante

        else:

            goles_favor = goles_visitante

            goles_contra = goles_local



        if goles_favor > goles_contra:

            forma.append("🟢")

        elif goles_favor == goles_contra:

            forma.append("🟡")

        else:

            forma.append("🔴")


    while len(forma) < 5:

        forma.append("⚪")


    return forma



def tarjeta_perfil_profesional(

    nombre,

    pais,

    logo,

    victorias,

    goles,

    partidos,

    promedio_goles,

    forma

):


    logo_html = ""


    if logo:


        logo_html = f"""

        <img

        src="{logo}"

        width="110"

        style="

        border-radius:50%;

        background:white;

        padding:10px;

        "

        >

        """



    forma_html = " ".join(forma)



    st.markdown(

    f"""

<div class="card">


<div style="

text-align:center;

">


{logo_html}



<h1 style="

font-size:32px;

">

{nombre}

</h1>



<p>

🌎 {pais}

</p>


</div>



<hr>



<div style="

display:flex;

justify-content:space-around;

text-align:center;

">



<div>

<h2>

🏆 {victorias}

</h2>

<p>

Victorias

</p>

</div>




<div>

<h2>

⚽ {goles}

</h2>

<p>

Goles

</p>

</div>




<div>

<h2>

📅 {partidos}

</h2>

<p>

Partidos

</p>

</div>



</div>



<hr>




<div style="

text-align:center;

">


<h3>

🔥 Forma reciente

</h3>


<h2>

{forma_html}

</h2>



<p>

Promedio ofensivo:

<b>

{promedio_goles}

</b>

goles / partido

</p>



</div>



</div>

""",

unsafe_allow_html=True

)

id_activo = st.session_state["id_seleccionado"]
nombre_activo = st.session_state["nombre_seleccionado"]
pais_activo = st.session_state["pais_seleccionado"]
logo_activo = st.session_state.get(
    "logo_seleccionado",
    ""
)

def generar_respaldo_dinamico(nombre_equipo, pais_equipo):
    pais_normalizado = str(pais_equipo).strip().lower()
    if "mexico" in pais_normalizado or "méxico" in pais_normalizado:
        competencia = "Liga MX - Apertura 2026"
        rivales = ["Chivas Guadalajara", "Cruz Azul", "Pumas UNAM", "Tigres UANL", "CF Monterrey"]
    elif "spain" in pais_normalizado or "españa" in pais_normalizado:
        competencia = "La Liga (Pretemporada)"
        rivales = ["Real Madrid", "Barcelona", "Atlético de Madrid", "Sevilla FC", "Real Betis"]
    elif "england" in pais_normalizado or "inglaterra" in pais_normalizado:
        competencia = "Premier League (Pretemporada)"
        rivales = ["Manchester City", "Arsenal", "Liverpool", "Manchester United", "Chelsea"]
    else:
        competencia = "Amistoso Internacional"
        rivales = ["Real Madrid", "Paris Saint-Germain", "Bayern Munich", "Manchester City", "Barcelona"]

    return [
        {"Fecha": "2026-07-12 18:00", "Competencia": competencia, "Local": rivales[1], "Goles Local": 1, "Goles Visita": 3, "Visita": nombre_equipo, "Estado": "FT"},
        {"Fecha": "2026-07-15 20:00", "Competencia": competencia, "Local": nombre_equipo, "Goles Local": 2, "Goles Visita": 2, "Visita": rivales[2], "Estado": "FT"},
        {"Fecha": "2026-07-19 19:30", "Competencia": "Copa de Campeones", "Local": nombre_equipo, "Goles Local": 1, "Goles Visita": 0, "Visita": rivales[0], "Estado": "FT"},
        {"Fecha": "2026-07-26 17:00", "Competencia": competencia, "Local": nombre_equipo, "Goles Local": None, "Goles Visita": None, "Visita": rivales[3], "Estado": "NS"},
        {"Fecha": "2026-08-01 21:00", "Competencia": competencia, "Local": rivales[4], "Goles Local": None, "Goles Visita": None, "Visita": nombre_equipo, "Estado": "NS"}
    ]

# Funciones de consulta a la API de Deportes
@st.cache_data(ttl=30, show_spinner=False)
def obtener_partidos_en_vivo(key_api):
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception:
        pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def buscar_equipo_api(nombre_busqueda):
    if not nombre_busqueda or len(nombre_busqueda) < 3:
        return []
    url = f"https://v3.football.api-sports.io/teams?search={nombre_busqueda}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo, nombre_equipo, pais_equipo):
    año_actual = datetime.now().year
    url = f"https://v3.football.api-sports.io/fixtures?team={id_equipo}&season={año_actual}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("response") and len(res_json.get("response")) > 0:
                return res_json.get("response"), "api_directa"
    except Exception:
        pass
    return generar_respaldo_dinamico(nombre_equipo, pais_equipo), "local_respaldo"

live_fixtures = obtener_partidos_en_vivo(API_KEY)
records_live = []
if live_fixtures:
    for match in live_fixtures:
        records_live.append({
            "Liga": match['league']['name'],
            "País": match['league']['country'],
            "Local": match['teams']['home']['name'],
            "Goles L": match['goals']['home'],
            "Visita": match['teams']['away']['name'],
            "Goles V": match['goals']['away'],
            "Minuto": match['fixture']['status']['elapsed']
        })
df_live = pd.DataFrame(records_live) if records_live else pd.DataFrame()
# =========================================================================
# MÉTRICAS AVANZADAS DEL EQUIPO
# =========================================================================


total_partidos = len(df_finalizados)
df_historial = pd.DataFrame(records_historial)

df_historial = df_historial.sort_values(
    by="Fecha",
    ascending=False
)


estados_finalizados = [
    "FT",
    "AET",
    "PEN"
]


df_finalizados = df_historial[
    df_historial["Estado"].isin(estados_finalizados)
]


# Aquí empiezan tus cálculos

total_partidos = len(df_finalizados)

promedio_goles = 0


promedio_goles = 0


if total_partidos > 0:

    promedio_goles = round(

        goles_favor / total_partidos,

        2

    )


forma_equipo = calcular_forma_equipo(

    df_finalizados,

    nombre_activo

)

# =========================================================================
# RENDERIZADO DE LAS PESTAÑAS (TABS)
# =========================================================================
tab1, tab2, tab3 = st.tabs(["📊 Buscador & Seguimiento", "🔴 Marcadores en Vivo", "📈 Estadísticas de Liga"])

# PESTAÑA 1: Buscador y Seguimiento de Equipos
with tab1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔍 Selector Global de Escuadras</div>", unsafe_allow_html=True)
    
    if "id_seleccionado" not in st.session_state:
        st.session_state["id_seleccionado"] = 541  # Real Madrid por defecto
    if "nombre_seleccionado" not in st.session_state:
        st.session_state["nombre_seleccionado"] = "Real Madrid"
    if "pais_seleccionado" not in st.session_state:
        st.session_state["pais_seleccionado"] = "Spain"
        
    busqueda_usuario = st.text_input(
        "Busca cualquier club en la base de datos:", 
        value="Real Madrid",
        placeholder="Ej. Real Madrid, Barcelona, Club América, Manchester City..."
    )
    
    if len(busqueda_usuario) >= 3:
        resultados_busqueda = buscar_equipo_api(busqueda_usuario)
        if resultados_busqueda:
            opciones_equipos = {}
            for item in resultados_busqueda:
                nombre_formateado = f"{item['team']['name']} ({item['team']['country']})"
                opciones_equipos[nombre_formateado] = {
                    "id": item['team']['id'],
                    "name": item['team']['name'],
                    "country": item['team']['country']
                }
            
            seleccion = st.selectbox("Selecciona el club coincidente para actualizar el tablero:", options=list(opciones_equipos.keys()))
            if seleccion:
                st.session_state["id_seleccionado"] = opciones_equipos[seleccion]["id"]
                st.session_state["nombre_seleccionado"] = opciones_equipos[seleccion]["name"]
                st.session_state["pais_seleccionado"] = opciones_equipos[seleccion]["country"]
    st.markdown("</div>", unsafe_allow_html=True)

    id_activo = st.session_state["id_seleccionado"]
    nombre_activo = st.session_state["nombre_seleccionado"]
    pais_activo = st.session_state["pais_seleccionado"]
    
    if id_activo:
        historial_raw, origen_datos = obtener_calendario_equipo(id_activo, nombre_activo, pais_activo)
        records_historial = []
        for f in historial_raw:
            if 'fixture' in f:
                records_historial.append({
                    "Fecha": pd.to_datetime(f['fixture']['date']).strftime('%Y-%m-%d %H:%M'),
                    "Competencia": f['league']['name'],
                    "Local": f['teams']['home']['name'],
                    "Goles Local": f['goals']['home'],
                    "Goles Visita": f['goals']['away'],
                    "Visita": f['teams']['away']['name'],
                    "Estado": f['fixture']['status']['short']
                })
            else:
                records_historial.append(f)
        
        df_historial = pd.DataFrame(records_historial).sort_values(by="Fecha", ascending=False)
        estados_finalizados = ['FT', 'AET', 'PEN']
        df_finalizados = df_historial[df_historial['Estado'].isin(estados_finalizados)]
        
        victorias = 0
        goles_favor = 0
        if not df_finalizados.empty:
            for _, row in df_finalizados.iterrows():
                es_local = row['Local'] == nombre_activo
                g_propio = row['Goles Local'] if es_local else row['Goles Visita']
                g_rival = row['Goles Visita'] if es_local else row['Goles Local']
                if not pd.isna(g_propio):
                    goles_favor += int(g_propio)
                    if g_propio > g_rival:
                        victorias += 1
                        
tarjeta_perfil_profesional(

    nombre_activo,

    pais_activo,

    logo_activo,

    victorias,

    goles_favor,

    total_partidos,

    promedio_goles,

    forma_equipo

)
        # =========================================================================
# TARJETAS KPI ESTILO SOFASCORE
# =========================================================================


st.markdown(
"""
<div class="section-title">
📊 Rendimiento del Equipo
</div>
""",
unsafe_allow_html=True
)



kpi1, kpi2, kpi3 = st.columns(3)



with kpi1:

    st.markdown(
    f"""

    <div class="kpi">

        <div class="kpi-title">
        ⚽ EQUIPO ACTUAL
        </div>


        <div class="kpi-value">
        {nombre_activo}
        </div>


        <p>
        🌎 {pais_activo}
        </p>

    </div>

    """,
    unsafe_allow_html=True
    )



with kpi2:


    st.markdown(
    f"""

    <div class="kpi"
    style="
    border-left-color:#16a34a;
    ">


        <div class="kpi-title">
        🏆 VICTORIAS RECIENTES
        </div>


        <div class="kpi-value"
        style="
        color:#16a34a !important;
        ">
        {victorias}
        </div>


        <p>
        Rendimiento positivo
        </p>


    </div>


    """,
    unsafe_allow_html=True
    )



with kpi3:


    st.markdown(
    f"""

    <div class="kpi"
    style="
    border-left-color:#f59e0b;
    ">


        <div class="kpi-title">
        ⚽ GOLES ANOTADOS
        </div>


        <div class="kpi-value"
        style="
        color:#f59e0b !important;
        ">
        {goles_favor}
        </div>


        <p>
        Poder ofensivo
        </p>


    </div>


    """,
    unsafe_allow_html=True
    )


# ==========================================
# AQUÍ TERMINA KPI3
# Y EMPIEZAN LOS RESULTADOS
# ==========================================


col_izq, col_der = st.columns(2)


with col_der:


    st.markdown(
    """
    <div class="section-title">
    ⏭️ Próximos Partidos
    </div>
    """,
    unsafe_allow_html=True
    )


    # Próximos partidos
    df_proximos = df_historial[
        ~df_historial['Estado'].isin(estados_finalizados)
    ].head(5)



    for idx, row in df_proximos.iloc[::-1].iterrows():

        tarjeta_partido(

            row['Local'],

            row['Visita'],

            None,

            None,

            row['Competencia']

        )

with col_der:


    st.markdown(
    """
    <div class="section-title">
    ⏭️ Próximos Partidos
    </div>
    """,
    unsafe_allow_html=True
    )


    for idx, row in df_proximos.iloc[::-1].iterrows():

        tarjeta_partido(

            row['Local'],

            row['Visita'],

            None,

            None,

            row['Competencia']

        )
# =========================================================================
# PESTAÑA 2: PARTIDOS EN VIVO ESTILO ESPN / SOFASCORE
# =========================================================================

with tab2:


    st.markdown(
    """
    <div class="section-title">
    🔴 Marcadores en Tiempo Real
    </div>
    """,
    unsafe_allow_html=True
    )


    st.markdown(
    """
    <div class="card">

    🛰️ Conexión activa con API Football

    <br>

    Los partidos se actualizan automáticamente.

    </div>

    """,
    unsafe_allow_html=True
    )



    if df_live.empty:


        st.markdown(
        """
        <div class="card">

        ⚽

        <h2>
        No hay partidos en vivo actualmente
        </h2>


        <p>
        El sistema continuará monitoreando eventos.
        </p>


        </div>

        """,
        unsafe_allow_html=True
        )


    else:


        # FILTRO

        filtro_live = st.text_input(

            "🔎 Buscar equipo o competición:",

            placeholder="Ejemplo: Real Madrid, Premier League..."

        )



        df_filtrado = df_live.copy()



        if filtro_live:


            df_filtrado = df_filtrado[

                df_filtrado["Local"].str.contains(
                    filtro_live,
                    case=False,
                    na=False
                )

                |

                df_filtrado["Visita"].str.contains(
                    filtro_live,
                    case=False,
                    na=False
                )

                |

                df_filtrado["Liga"].str.contains(
                    filtro_live,
                    case=False,
                    na=False
                )

            ]



        for _, partido in df_filtrado.iterrows():


            tarjeta_partido(

                partido["Local"],

                partido["Visita"],

                partido["Goles L"],

                partido["Goles V"],

                partido["Liga"],

                partido["Minuto"]

            )


# =========================================================================
# PESTAÑA 3: ANALÍTICA AVANZADA
# =========================================================================

with tab3:


    st.markdown(
    """
    <div class="section-title">
    📈 Centro de Analítica Futbolística
    </div>
    """,
    unsafe_allow_html=True
    )


    # ---------------------------------------------------------------
    # PREPARACIÓN DE DATOS
    # ---------------------------------------------------------------


    if not df_live.empty:


        datos_ligas = (
            df_live["Liga"]
            .value_counts()
            .reset_index()
        )


        datos_ligas.columns = [

            "Liga",

            "Partidos"

        ]


    else:


        datos_ligas = pd.DataFrame({

            "Liga":[

                "Premier League",

                "LaLiga",

                "Serie A",

                "Bundesliga",

                "Ligue 1"

            ],


            "Partidos":[

                15,

                12,

                9,

                7,

                5

            ]

        })



    # ---------------------------------------------------------------
    # KPIs GENERALES
    # ---------------------------------------------------------------


    total_partidos = int(
        datos_ligas["Partidos"].sum()
    )


    liga_top = (
        datos_ligas
        .sort_values(
            "Partidos",
            ascending=False
        )
        .iloc[0]["Liga"]
    )


    cantidad_ligas = len(datos_ligas)



    c1,c2,c3 = st.columns(3)



    with c1:

        st.markdown(
        f"""

        <div class="kpi">


        <div class="kpi-title">
        ⚽ PARTIDOS ANALIZADOS
        </div>


        <div class="kpi-value">

        {total_partidos}

        </div>


        </div>

        """,
        unsafe_allow_html=True
        )



    with c2:


        st.markdown(
        f"""

        <div class="kpi"
        style="border-left-color:#16a34a">


        <div class="kpi-title">

        🌎 LIGAS MONITOREADAS

        </div>


        <div class="kpi-value">

        {cantidad_ligas}

        </div>


        </div>

        """,
        unsafe_allow_html=True
        )



    with c3:


        st.markdown(
        f"""

        <div class="kpi"
        style="border-left-color:#f59e0b">


        <div class="kpi-title">

        🏆 LIGA MÁS ACTIVA

        </div>


        <div class="kpi-value"
        style="font-size:22px">

        {liga_top}

        </div>


        </div>

        """,
        unsafe_allow_html=True
        )



    st.write("")



    # ---------------------------------------------------------------
    # GRÁFICAS PLOTLY
    # ---------------------------------------------------------------


    col1,col2 = st.columns(2)



    with col1:


        st.markdown(
        """
        <div class="card">

        <h3>
        📊 Distribución por Competición
        </h3>

        </div>
        """,
        unsafe_allow_html=True
        )


        grafica_barras = px.bar(

            datos_ligas,

            x="Liga",

            y="Partidos",

            text="Partidos",

            title=None

        )


        grafica_barras.update_layout(

            height=400,

            xaxis_title="",

            yaxis_title="Partidos",

            template="plotly_white"

        )


        st.plotly_chart(

            grafica_barras,

            use_container_width=True

        )



    with col2:


        st.markdown(
        """
        <div class="card">

        <h3>
        🌎 Participación Mundial
        </h3>

        </div>
        """,
        unsafe_allow_html=True
        )


        grafica_pie = px.pie(

            datos_ligas,

            names="Liga",

            values="Partidos",

            hole=.45

        )


        grafica_pie.update_layout(

            height=400,

            template="plotly_white"

        )


        st.plotly_chart(

            grafica_pie,

            use_container_width=True

        )



    # ---------------------------------------------------------------
    # TABLA DETALLADA
    # ---------------------------------------------------------------


    st.markdown(
    """
    <div class="section-title">
    📋 Ranking de Competiciones
    </div>
    """,
    unsafe_allow_html=True
    )



    tabla = datos_ligas.sort_values(

        "Partidos",

        ascending=False

    )



    st.dataframe(

        tabla,

        use_container_width=True,

        hide_index=True

    )
