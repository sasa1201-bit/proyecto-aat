import os
import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Intentar importar streamlit_folium y folium para el mapa
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Forza Football Analytics V3.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS PERSONALIZADO - DISEÑO OSCURO AZUL MARINO (Forza/ESPN)
# ==========================================
st.markdown("""
<style>
    /* Estilos globales y tema azul marino oscuro */
    .stApp {
        background-color: #0a0e1a;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Ocultar elementos de cabecera y pie por defecto de streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Contenedores con bordes redondeados */
    .custom-container {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Tarjetas de métricas / KPI */
    .metric-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Contenedor del marcador en vivo */
    .live-match-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 10px 0 20px 0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 12px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Resultados recientes con barra lateral verde */
    .result-item {
        background-color: #131b2e;
        border-left: 5px solid #22c55e;
        border-radius: 4px 12px 12px 4px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #1e293b;
        border-right: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
    }
    
    /* Pie de página */
    .app-footer {
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        padding: 30px 0;
        border-top: 1px solid #1e293b;
        margin-top: 40px;
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #131b2e;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    
    dataframe, table {
        background-color: #131b2e !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONFIGURACIÓN DE API Y FUNCIONES AUXILIARES
# ==========================================
API_BASE = "https://api.thestatsapi.com/api"
API_KEY = os.getenv("THESTATSAPI_KEY", "")

def get_headers():
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers

@st.cache_data(ttl=300)
def fetch_from_api(endpoint: str, params: dict = None):
    if not API_KEY:
        return None
    url = f"{API_BASE}{endpoint}"
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{query_string}"
    try:
        req = urllib.request.Request(url, headers=get_headers())
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
    except Exception:
        pass
    return None

# ==========================================
# DATOS DE PRUEBA Y ESCUDOS DE EQUIPOS
# ==========================================
TEAM_LOGOS = {
    "Real Madrid": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "Barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Atletico Madrid": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2024_logo.svg",
    "Athletic Club": "https://upload.wikimedia.org/wikipedia/en/9/98/Athletic_Club_Bilbao_%28crest%29.svg",
    "Real Sociedad": "https://upload.wikimedia.org/wikipedia/en/f/f1/Real_Sociedad_logo.svg",
    "Valencia": "https://upload.wikimedia.org/wikipedia/en/c/ce/Valencia_CF_1919_logo.svg",
    "Villarreal": "https://upload.wikimedia.org/wikipedia/en/7/70/Villarreal_CF_logo.svg",
    "Sevilla": "https://upload.wikimedia.org/wikipedia/en/3/3b/Sevilla_FC_logo.svg"
}

DUMMY_STANDINGS = pd.DataFrame([
    {"Posición": 1, "Equipo": "Real Madrid", "PJ": 22, "G": 17, "E": 4, "P": 1, "GF": 52, "GC": 14, "Pts": 55},
    {"Posición": 2, "Equipo": "Barcelona", "PJ": 22, "G": 15, "E": 5, "P": 2, "GF": 48, "GC": 20, "Pts": 50},
    {"Posición": 3, "Equipo": "Atletico Madrid", "PJ": 22, "G": 13, "E": 6, "P": 3, "GF": 41, "GC": 22, "Pts": 45},
    {"Posición": 4, "Equipo": "Athletic Club", "PJ": 22, "G": 12, "E": 5, "P": 5, "GF": 36, "GC": 21, "Pts": 41},
    {"Posición": 5, "Equipo": "Real Sociedad", "PJ": 22, "G": 10, "E": 7, "P": 5, "GF": 32, "GC": 24, "Pts": 37},
])

DUMMY_FIXTURES = [
    {"date": "01 Mar 2026 - 20:00", "home": "Real Madrid", "away": "Athletic Club", "status": "Programado"},
    {"date": "02 Mar 2026 - 18:30", "home": "Barcelona", "away": "Real Sociedad", "status": "Programado"},
    {"date": "02 Mar 2026 - 21:00", "home": "Atletico Madrid", "away": "Valencia", "status": "Programado"},
]

DUMMY_SQUAD = pd.DataFrame([
    {"Dorsal": 1, "Nombre": "Thibaut Courtois", "Edad": 33, "Posición": "Portero"},
    {"Dorsal": 2, "Nombre": "Dani Carvajal", "Edad": 34, "Posición": "Defensa"},
    {"Dorsal": 3, "Nombre": "Éder Militão", "Edad": 28, "Posición": "Defensa"},
    {"Dorsal": 4, "Nombre": "David Alaba", "Edad": 33, "Posición": "Defensa"},
    {"Dorsal": 5, "Nombre": "Jude Bellingham", "Edad": 22, "Posición": "Centrocampista"},
    {"Dorsal": 7, "Nombre": "Vinícius Júnior", "Edad": 25, "Posición": "Delantero"},
    {"Dorsal": 8, "Nombre": "Federico Valverde", "Edad": 27, "Posición": "Centrocampista"},
    {"Dorsal": 9, "Nombre": "Kylian Mbappé", "Edad": 27, "Posición": "Delantero"},
    {"Dorsal": 10, "Nombre": "Luka Modrić", "Edad": 40, "Posición": "Centrocampista"},
    {"Dorsal": 11, "Nombre": "Rodrygo Goes", "Edad": 25, "Posición": "Delantero"},
    {"Dorsal": 14, "Nombre": "Aurélien Tchouaméni", "Edad": 26, "Posición": "Centrocampista"},
])

DUMMY_RECENT_RESULTS = [
    {"match": "Real Madrid 3 - 1 Villarreal", "date": "24 Feb 2026", "result": "VICTORIA"},
    {"match": "Real Madrid 2 - 0 Sevilla", "date": "18 Feb 2026", "result": "VICTORIA"},
    {"match": "Real Madrid 1 - 1 Atletico Madrid", "date": "12 Feb 2026", "result": "EMPATE"},
    {"match": "Real Madrid 4 - 2 Las Palmas", "date": "05 Feb 2026", "result": "VICTORIA"},
]

# ==========================================
# CABECERA Y AVISO DE API
# ==========================================
st.markdown("<h1 style='text-align: center; color: #f8fafc; margin-bottom: 0;'>⚽ FORZA FOOTBALL ANALYTICS V3.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-top: 5px;'>Plataforma Avanzada de Datos Deportivos e Integración de IA</p>", unsafe_allow_html=True)

if not API_KEY:
    st.info("ℹ️ **Variable de entorno THESTATSAPI_KEY no detectada.** Operando con datos de respaldo simulados. Para conectar feeds en vivo, configure su clave de API.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PESTAÑAS DE NAVEGACIÓN
# ==========================================
tab_main, tab_live, tab_analytics, tab_scout = st.tabs([
    "📊 Panel Principal", 
    "⚡ Centro en Vivo", 
    "📈 Análisis Avanzado", 
    "🤖 AI Scout"
])

# ==========================================
# PESTAÑA 1: PANEL PRINCIPAL
# ==========================================
with tab_main:
    st.markdown("### Resumen de la Liga y Clasificación")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Clasificación La Liga (2025/26)")
        st.dataframe(DUMMY_STANDINGS, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Próximos Partidos")
        for f in DUMMY_FIXTURES:
            logo_h = TEAM_LOGOS.get(f['home'], "")
            logo_a = TEAM_LOGOS.get(f['away'], "")
            st.markdown(f"""
            <div style="background-color: #0f172a; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #1e293b;">
                <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 4px;">{f['date']}</div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-weight: 600; font-size: 0.9rem;">
                    <span><img src="{logo_h}" width="18" style="vertical-align: middle; margin-right: 6px;">{f['home']}</span>
                    <span style="color: #64748b; font-size: 0.8rem;">vs</span>
                    <span>{f['away']}<img src="{logo_a}" width="18" style="vertical-align: middle; margin-left: 6px;"></span>
                </div>
                <div style="font-size: 0.75rem; color: #3b82f6; margin-top: 4px;">{f['status']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: CENTRO EN VIVO
# ==========================================
with tab_live:
    st.markdown("### Centro de Partidos en Directo")
    
    logo_rm = TEAM_LOGOS.get("Real Madrid", "")
    logo_barca = TEAM_LOGOS.get("Barcelona", "")
    
    st.markdown(f"""
    <div class="live-match-box">
        <div class="live-badge">🔴 EN VIVO • 74'</div>
        <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 15px;">
            <div style="text-align: right; flex: 1; display: flex; align-items: center; justify-content: flex-end; gap: 12px;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f8fafc;">Real Madrid</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Santiago Bernabéu</div>
                </div>
                <img src="{logo_rm}" width="50" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));">
            </div>
            <div style="padding: 0 25px; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800; color: #3b82f6; letter-spacing: 2px;">2 - 1</div>
                <div style="font-size: 0.75rem; color: #22c55e; font-weight: 600;">MT 1-0</div>
            </div>
            <div style="text-align: left; flex: 1; display: flex; align-items: center; justify-content: flex-start; gap: 12px;">
                <img src="{logo_barca}" width="50" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f8fafc;">Barcelona</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Visitante</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Estadísticas del Partido in-play")
        
        stats_data = [
            ("Posesión de Balón", "54%", "46%"),
            ("Tiros Totales", "14", "11"),
            ("Tiros a Puerta", "6", "4"),
            ("Saques de Esquina", "5", "3"),
            ("Tarjetas Amarillas", "2", "3"),
            ("Faltas", "10", "12")
        ]
        
        for stat, home_v, away_v in stats_data:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 0.9rem;">
                <span style="font-weight: 600; color: #f8fafc; width: 60px;">{home_v}</span>
                <span style="color: #94a3b8; text-align: center; flex: 1;">{stat}</span>
                <span style="font-weight: 600; color: #f8fafc; width: 60px; text-align: right;">{away_v}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_l2:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Cronología del Partido")
        
        timeline_events = [
            ("71'", "¡Gol!", "Barcelona (L. Yamal)", "⚽"),
            ("55'", "¡Gol!", "Real Madrid (K. Mbappé)", "⚽"),
            ("46'", "Sustitución", "Real Madrid (Entra L. Modrić)", "🔄"),
            ("MT", "Media Partida", "Marcador: 1 - 0", "⏱️"),
            ("28'", "¡Gol!", "Real Madrid (J. Bellingham)", "⚽"),
            ("14'", "Tarjeta Amarilla", "Barcelona (Gavi)", "🟨")
        ]
        
        for minute, event_type, desc, icon in timeline_events:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 0.85rem;">
                <span style="background-color: #1e293b; color: #3b82f6; padding: 2px 8px; border-radius: 4px; font-weight: 700; margin-right: 12px; width: 45px; text-align: center;">{minute}</span>
                <span style="margin-right: 8px;">{icon}</span>
                <span style="color: #f8fafc; flex: 1;"><b>{event_type}:</b> {desc}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PESTAÑA 3: ANÁLISIS AVANZADO
# ==========================================
with tab_analytics:
    st.markdown("### Análisis Avanzado y Profundo del Club")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Perfil del Club</div>
            <div class="metric-value" style="font-size: 1.2rem; color: #3b82f6;">Real Madrid CF</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">La Liga • España</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">% Efectividad</div>
            <div class="metric-value">77.3%</div>
            <div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">+4.2% vs prom. liga</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Goles Prom. / Partido</div>
            <div class="metric-value">2.36</div>
            <div style="font-size: 0.75rem; color: #3b82f6; margin-top: 4px;">52 GF en 22 partidos</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Récord V / E / D</div>
            <div class="metric-value" style="font-size: 1.3rem;">17 - 4 - 1</div>
            <div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">86% de imbatibilidad</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a1, col_a2 = st.columns([1, 1])
    
    with col_a1:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Resultados Recientes")
        for res in DUMMY_RECENT_RESULTS:
            st.markdown(f"""
            <div class="result-item">
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{res['match']}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">{res['date']}</div>
                </div>
                <div>
                    <span style="background-color: #065f46; color: #34d399; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">{res['result']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_a2:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Calendario y Programación")
        selected_date = st.date_input("Destacar Fecha de Partido", value=datetime.today().date())
        st.markdown(f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; margin-top: 15px;">
            <div style="font-size: 0.85rem; color: #3b82f6; font-weight: 600;">Fecha Seleccionada: {selected_date.strftime('%d de %B, %Y')}</div>
            <div style="font-size: 0.9rem; color: #f8fafc; margin-top: 8px;">No hay encuentros oficiales programados directamente para esta fecha. Próxima ventana en 4 días.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
    st.subheader("Plantilla del Primer Equipo")
    st.dataframe(DUMMY_SQUAD, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_a3, col_a4 = st.columns(2)
    
    with col_a3:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Perfil de Rendimiento (Radar)")
        
        categories = ['Poder Ofensivo', 'Efectividad', 'Volumen', 'Consistencia', 'Solidez Defensiva']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[92, 85, 88, 90, 84],
            theta=categories,
            fill='toself',
            name='Real Madrid',
            line_color='#3b82f6',
            fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='#0f172a',
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='#1e293b', linecolor='#1e293b'),
                angularaxis=dict(gridcolor='#1e293b', linecolor='#1e293b')
            ),
            paper_bgcolor='#131b2e',
            plot_bgcolor='#131b2e',
            font=dict(color='#f1f5f9'),
            margin=dict(t=20, b=20, l=20, r=20),
            height=320
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_a4:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Región del Club (Madrid, España)")
        
        if FOLIUM_AVAILABLE:
            m = folium.Map(location=[40.4168, -3.7038], zoom_start=12, tiles="CartoDB dark_matter")
            folium.Marker(
                [40.4168, -3.7038],
                popup="Estadio Santiago Bernabéu",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            st_folium(m, height=320, use_container_width=True)
        else:
            map_df = pd.DataFrame({'lat': [40.4168], 'lon': [-3.7038], 'name': ['Santiago Bernabéu']})
            fig_map = px.scatter_mapbox(map_df, lat='lat', lon='lon', text='name', zoom=11, height=320)
            fig_map.update_layout(
                mapbox_style="carto-darkmatter",
                paper_bgcolor='#131b2e',
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col_a5, col_a6 = st.columns(2)
    
    with col_a5:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Volumen de Partidos por Competición")
        league_data = pd.DataFrame({
            'Competición': ['La Liga', 'UEFA Champions League', 'Copa del Rey', 'Supercopa'],
            'Partidos': [22, 8, 4, 2]
        })
        fig_bar = px.bar(league_data, x='Competición', y='Partidos', color='Partidos', color_continuous_scale='Blues')
        fig_bar.update_layout(
            paper_bgcolor='#131b2e',
            plot_bgcolor='#131b2e',
            font=dict(color='#f1f5f9'),
            xaxis=dict(gridcolor='#1e293b'),
            yaxis=dict(gridcolor='#1e293b'),
            height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_a6:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Goles Totales por Competición (Tonos Rojizos)")
        goal_data = pd.DataFrame({
            'Competición': ['La Liga', 'UCL', 'Copa del Rey', 'Supercopa'],
            'Goles': [52, 18, 9, 5]
        })
        fig_area = px.area(goal_data, x='Competición', y='Goles', markers=True)
        fig_area.update_traces(line_color='#ef4444', fillcolor='rgba(239, 68, 68, 0.3)')
        fig_area.update_layout(
            paper_bgcolor='#131b2e',
            plot_bgcolor='#131b2e',
            font=dict(color='#f1f5f9'),
            xaxis=dict(gridcolor='#1e293b'),
            yaxis=dict(gridcolor='#1e293b'),
            height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_area, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PESTAÑA 4: AI SCOUT
# ==========================================
with tab_scout:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #131b2e 0%, #0f172a 100%); border: 1px solid #1e293b; border-radius: 16px; padding: 40px; text-align: center; max-width: 700px; margin: 0 auto; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);">
        <div style="font-size: 3rem; margin-bottom: 15px;">🤖⚽</div>
        <h2 style="color: #f8fafc; font-weight: 700; margin-bottom: 15px;">AI Scout — Próximamente</h2>
        <p style="color: #94a3b8; font-size: 1.05rem; line-height: 1.6; margin-bottom: 25px;">
            Módulo avanzado de descubrimiento de jugadores e inteligencia de partidos en desarrollo. Impulsado por modelos de inteligencia artificial generativa y telemetría en tiempo real de TheStatsAPI.
        </p>
        <div style="display: inline-block; background-color: #1e293b; color: #3b82f6; padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
            Lanzamiento del Módulo: Q3 2026
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# PIE DE PÁGINA (FOOTER)
# ==========================================
st.markdown("""
<div class="app-footer">
    Forza Football Analytics V3.0 AI Integration, Advanced Sports Data Platform, University Project, Developed by Salomón Achar © 2026
</div>
""", unsafe_allow_html=True)
