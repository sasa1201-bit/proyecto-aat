import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA & MODO OSCURO PREMIUM (ESTILO EXACTO DE LA FOTO)
# ==============================================================================
st.set_page_config(
    page_title="Forza Football Analytics v3.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS avanzados para clonar la interfaz de las imágenes
st.markdown("""
    <style>
        /* Fondo principal de la aplicación */
        .stApp {
            background-color: #0b1322 !important;
            color: #ffffff !important;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        /* Ocultar elementos nativos de Streamlit para limpieza de interfaz */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Contenedores y Tarjetas Modulares */
        .custom-card {
            background-color: #141f32;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #1c2a42;
        }
        
        .team-profile-card {
            background-color: #141f32;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #1d73e8;
            display: flex;
            align-items: center;
            gap: 15px;
            height: 100%;
        }
        
        /* Modificar el estilo de las pestañas (Tabs) */
        div[data-baseweb="tab-list"] {
            background-color: #0b1322 !important;
            border-bottom: 1px solid #1c2a42 !important;
            gap: 24px;
        }
        button[data-baseweb="tab"] {
            color: #8fa0b5 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            padding: 12px 4px !important;
            background-color: transparent !important;
            border: none !important;
        }
        button[aria-selected="true"] {
            color: #ffffff !important;
            border-bottom: 3px solid #e24c4c !important;
        }
        
        /* Títulos de secciones internas */
        .card-title {
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.5px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Estilos para las métricas KPIs superiores */
        .kpi-label {
            font-size: 10px;
            color: #8fa0b5;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
        }
        
        /* Filas de Últimos Resultados */
        .result-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 10px;
            border-bottom: 1px solid #1c2a42;
            border-left: 3px solid #00c853;
            margin-bottom: 8px;
            background-color: #111b2c;
            border-radius: 0 6px 6px 0;
        }
        .result-team {
            font-size: 13.5px;
            font-weight: 600;
            color: #ffffff;
            width: 35%;
        }
        .result-center {
            text-align: center;
            width: 30%;
        }
        .result-score {
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 2px;
        }
        .result-meta {
            font-size: 10px;
            color: #8fa0b5;
            margin-top: 4px;
        }
        
        /* Central En Vivo: Tarjetas de Partidos */
        .live-match-card {
            background-color: #141f32;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #1c2a42;
        }
        .live-team-name {
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            width: 35%;
        }
        .live-center-box {
            text-align: center;
            width: 30%;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        .live-score-pill {
            background-color: #080d16;
            padding: 8px 24px;
            border-radius: 6px;
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 2px;
        }
        .live-minute-pill {
            background-color: #31181e;
            color: #ff4d4d;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
        }
        
        /* Calendario en Grid */
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            text-align: center;
            margin-top: 15px;
        }
        .calendar-day-name {
            font-size: 11px;
            color: #8fa0b5;
            font-weight: 600;
            padding-bottom: 5px;
        }
        .calendar-day {
            font-size: 12px;
            padding: 8px 0;
            color: #ffffff;
        }
        .calendar-day.empty {
            color: #384b66;
        }
        .calendar-day.active-today {
            background-color: #e24c4c;
            color: #ffffff;
            border-radius: 50%;
            font-weight: 700;
            width: 26px;
            height: 26px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Tabla de Plantilla */
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .custom-table th {
            text-align: left;
            padding: 12px;
            font-size: 12px;
            color: #8fa0b5;
            border-bottom: 1px solid #1c2a42;
            font-weight: 600;
        }
        .custom-table td {
            padding: 14px 12px;
            font-size: 13px;
            color: #ffffff;
            border-bottom: 1px solid #16243a;
        }
        
        /* Caja superior de búsqueda */
        .search-container {
            background-color: #0d1726;
            border: 1px solid #1c2a42;
            border-radius: 6px;
            padding: 8px 12px;
            color: #8fa0b5;
            font-size: 13px;
            margin-bottom: 20px;
        }
        
        /* Footer fijo inferior personalizado */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #0b1322;
            color: #8fa0b5;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            border-top: 1px solid #1c2a42;
            z-index: 100;
            line-height: 1.5;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GUÍA DE INTEGRACIÓN FUTURA A THESTATSAPI (DOCUMENTACIÓN DEL PROYECTO)
# ==============================================================================
"""
<!-- NOTA TÉCNICA PARA LA EVALUACIÓN DEL PROYECTO -->
Para conectar esta plataforma con la data en vivo de TheStatsAPI, se debe reemplazar 
las funciones de caché con llamadas HTTP estructuradas de la siguiente manera:

import requests

BASE_URL = "https://api.thestatsapi.com/api"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('THESTATSAPI_KEY', 'TU_TOKEN_AQUÍ')}"
}

Ejemplo para obtener partidos en vivo:
def get_live_matches_api():
    response = requests.get(f"{BASE_URL}/football/matches?status=live", headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data['data'] # Mapea directo a home_team, away_team, score, status
    return []
"""

# ==============================================================================
# CAPA DE DATOS (MOCKED DATA CON ESTRUCTURA OFICIAL API Y CACHÉ)
# ==============================================================================

@st.cache_data
def load_league_standings(competition_id):
    data = {
        "comp_laliga": [
            {"position": 1, "team": "Real Madrid", "points": 78, "goal_difference": 42, "form": "W-W-D-W-W"},
            {"position": 2, "team": "Barcelona", "points": 72, "goal_difference": 31, "form": "W-L-W-W-D"},
            {"position": 3, "team": "Atlético Madrid", "points": 65, "goal_difference": 20, "form": "L-W-W-D-W"},
            {"position": 4, "team": "Real Sociedad", "points": 59, "goal_difference": 12, "form": "D-W-L-W-L"}
        ],
        "comp_premier": [
            {"position": 1, "team": "Manchester City", "points": 81, "goal_difference": 48, "form": "W-W-W-D-W"},
            {"position": 2, "team": "Liverpool", "points": 79, "goal_difference": 45, "form": "W-D-W-L-W"}
        ]
    }
    return pd.DataFrame(data.get(competition_id, data["comp_laliga"]))

@st.cache_data
def load_live_matches():
    return [
        {
            "match_id": "mt_001",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "score": "2 - 1",
            "status": "LIVE",
            "minute": "74'",
            "live_stats": {"ball_possession": {"home": 54, "away": 46}, "total_shots": {"home": 14, "away": 9}}
        },
        {
            "match_id": "mt_002",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "score": "0 - 0",
            "status": "LIVE",
            "minute": "15'",
            "live_stats": {"ball_possession": {"home": 50, "away": 50}, "total_shots": {"home": 2, "away": 3}}
        }
    ]

@st.cache_data
def load_advanced_player_data():
    players = [
        {"player": "Jude Bellingham", "team": "Real Madrid", "goals": 18, "assists": 8, "xg": 15.4, "passes_acc": 89.5, "duels_won_pct": 58.2, "position": "Midfielder"},
        {"player": "Erling Haaland", "team": "Manchester City", "goals": 27, "assists": 5, "xg": 29.1, "passes_acc": 76.2, "duels_won_pct": 49.8, "position": "Forward"}
    ]
    return pd.DataFrame(players)

@st.cache_data
def load_shotmap_data():
    shots = [
        {"x": 88, "y": 52, "xg": 0.65, "result": "Goal", "player": "Jude Bellingham", "body_part": "Right Foot"}
    ]
    return pd.DataFrame(shots)


# ==============================================================================
# ESTRUCTURA PRINCIPAL DE LA APLICACIÓN (MAPPED TO YOUR TABS)
# ==============================================================================

tab_principal, tab_vivo, tab_avanzada, tab_scout = st.tabs([
    "Panel Principal", 
    "Central En Vivo", 
    "Analítica Avanzada", 
    "Scout IA"
])

# ------------------------------------------------------------------------------
# TAB 1: PANEL PRINCIPAL (CLONADO DE LA CAPTURA 1)
# ------------------------------------------------------------------------------
with tab_principal:
    # Caja de búsqueda superior
    st.markdown('<div class="search-container">Buscar club (Ej. Arsenal, Madrid)...</div>', unsafe_allow_html=True)
    
    # Fila de KPIs
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns([3, 2, 2, 3])
    
    with kpi_col1:
        st.markdown("""
            <div class="team-profile-card">
                <span style="font-size: 30px;">👑</span>
                <div>
                    <div style="font-size: 15px; font-weight:700; color:#ffffff;">Real Madrid</div>
                    <div style="font-size: 12px; color:#8fa0b5;">Spain</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown("""
            <div class="custom-card" style="padding: 15px 20px;">
                <div class="kpi-label">Efectividad</div>
                <div class="kpi-value">100.0%</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown("""
            <div class="custom-card" style="padding: 15px 20px;">
                <div class="kpi-label">Goles / Partido</div>
                <div class="kpi-value">3.2</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown("""
            <div class="custom-card" style="padding: 15px 20px;">
                <div class="kpi-label">Récord (V-E-D)</div>
                <div class="kpi-value">5 - 0 - 0</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Fila de Resultados y Calendario
    body_col1, body_col2 = st.columns([7, 5])
    
    with body_col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏮️ ÚLTIMOS RESULTADOS</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="result-row">
                <div class="result-team">Real Madrid</div>
                <div class="result-center">
                    <div class="result-score">5 - 0</div>
                    <div class="result-meta">🏆 La Liga | 📅 2026-05-14 20:00</div>
                </div>
                <div class="result-team" style="text-align: right;">Alaves</div>
            </div>
            <div class="result-row">
                <div class="result-team">Granada</div>
                <div class="result-center">
                    <div class="result-score">0 - 4</div>
                    <div class="result-meta">🏆 La Liga | 📅 2026-05-10 16:15</div>
                </div>
                <div class="result-team" style="text-align: right;">Real Madrid</div>
            </div>
            <div class="result-row">
                <div class="result-team">Real Madrid</div>
                <div class="result-center">
                    <div class="result-score">3 - 0</div>
                    <div class="result-meta">🏆 La Liga | 📅 2026-05-04 18:30</div>
                </div>
                <div class="result-team" style="text-align: right;">Cadiz</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with body_col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📅 CALENDARIO ACTUAL</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; font-size:13px; font-weight:700; color:#ffffff; margin-bottom:5px;">July 2026</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="calendar-grid">
                <div class="calendar-day-name">dom</div><div class="calendar-day-name">lun</div><div class="calendar-day-name">mar</div>
                <div class="calendar-day-name">mié</div><div class="calendar-day-name">jue</div><div class="calendar-day-name">vie</div><div class="calendar-day-name">sáb</div>
                
                <div class="calendar-day empty"></div><div class="calendar-day empty"></div><div class="calendar-day empty"></div>
                <div class="calendar-day">1</div><div class="calendar-day">2</div><div class="calendar-day">3</div><div class="calendar-day">4</div>
                
                <div class="calendar-day">5</div><div class="calendar-day">6</div><div class="calendar-day">7</div>
                <div class="calendar-day">8</div><div class="calendar-day">9</div><div class="calendar-day">10</div><div class="calendar-day">11</div>
                
                <div class="calendar-day">12</div><div class="calendar-day">13</div><div class="calendar-day">14</div>
                <div class="calendar-day">15</div><div class="calendar-day">16</div><div class="calendar-day">17</div><div class="calendar-day">18</div>
                
                <div class="calendar-day">19</div>
                <div class="calendar-day"><div class="active-today">20</div></div>
                <div class="calendar-day">21</div><div class="calendar-day">22</div><div class="calendar-day">23</div><div class="calendar-day">24</div><div class="calendar-day">25</div>
                
                <div class="calendar-day">26</div><div class="calendar-day">27</div><div class="calendar-day">28</div>
                <div class="calendar-day">29</div><div class="calendar-day">30</div><div class="calendar-day">31</div><div class="calendar-day empty"></div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: CENTRAL EN VIVO (CLONADO DE LA CAPTURA 2)
# ------------------------------------------------------------------------------
with tab_vivo:
    st.markdown('<h3 style="color:#ffffff; font-size:16px; font-weight:700; margin-bottom:15px; letter-spacing:0.5px;">🔴 COBERTURA EN DIRECTO</h3>', unsafe_allow_html=True)
    
    # Bucle adaptado sobre tu función original load_live_matches
    for match in load_live_matches():
        st.markdown(f"""
            <div class="live-match-card">
                <div class="live-team-name">{match['home_team']}</div>
                <div class="live-center-box">
                    <div class="live-score-pill">{match['score']}</div>
                    <div class="live-minute-pill">⏱️ {match['minute']}</div>
                </div>
                <div class="live-team-name" style="text-align: right;">{match['away_team']}</div>
            </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: ANALÍTICA AVANZADA (CLONADO DE LAS CAPTURAS 3 Y 4)
# ------------------------------------------------------------------------------
with tab_avanzada:
    st.markdown('<h3 style="color:#ffffff; font-size:16px; font-weight:700; margin-bottom:20px; letter-spacing:0.5px;">📈 ANALÍTICA DE DATOS</h3>', unsafe_allow_html=True)
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 VOLUMEN DE PARTIDOS</div>', unsafe_allow_html=True)
        fig_vol = go.Figure(data=[
            go.Bar(x=['La Liga', 'Premier League'], y=[1, 1], marker_color='#3b82f6', width=0.4)
        ])
        fig_vol.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8fa0b5', height=240, margin=dict(l=30,r=30,t=10,b=10),
            yaxis=dict(gridcolor='#1c2a42', range=[0, 1]), xaxis=dict(tickangle=90)
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_graph2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚽ GOLES TOTALES POR LIGA</div>', unsafe_allow_html=True)
        fig_goals = go.Figure()
        fig_goals.add_trace(go.Scatter(
            x=['La Liga', 'Premier League'], y=[3, 0],
            fill='tozeroy', mode='lines', line=dict(color='#ef4444', width=2),
            fillcolor='rgba(239, 68, 68, 0.85)'
        ))
        fig_goals.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8fa0b5', height=240, margin=dict(l=30,r=30,t=10,b=10),
            yaxis=dict(gridcolor='#1c2a42', range=[0, 3]), xaxis=dict(tickangle=90)
        )
        st.plotly_chart(fig_goals, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Segunda fila de analítica avanzada (Radar y Mapa)
    col_graph3, col_graph4 = st.columns(2)
    
    with col_graph3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕸️ PERFIL TÁCTICO RADAR</div>', unsafe_allow_html=True)
        categories = ['Poder Goleador', 'Efectividad', 'Volumen', 'Consistencia', 'Solidez Defensiva']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[100, 95, 75, 60, 80], theta=categories, fill='toself',
            line=dict(color='#3b82f6', width=2), fillcolor='rgba(59, 130, 246, 0.25)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1c2a42", angle=45, tickfont=dict(size=8)),
                angularaxis=dict(gridcolor="#1c2a42")
            ),
            paper_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=260,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_graph4:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🗺️ UBICACIÓN GEOGRÁFICA</div>', unsafe_allow_html=True)
        fig_map = go.Figure(go.Scattermapbox(
            lat=[40.4167], lon=[-3.7037], mode='markers+text',
            marker=go.scattermapbox.Marker(size=10, color='#ffffff'),
            text=['Madrid'], textposition='bottom center'
        ))
        fig_map.update_layout(
            mapbox=dict(
                style='carto-darkmatter', zoom=4.8,
                center=dict(lat=40.0, lon=-3.5)
            ),
            paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=260
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 4: SCOUT IA (CLONADO DE LA CAPTURA 5 - PLANTILLA DEL EQUIPO)
# ------------------------------------------------------------------------------
with tab_scout:
    # Encabezado estilizado del partido
    st.markdown("""
        <div style="display:flex; justify-content:between; align-items:center; padding:8px 0; border-bottom:2px solid #1d73e8; margin-bottom:25px;">
            <span style="font-size:14px; font-weight:700; width:30%;">Mallorca</span>
            <span style="font-size:12px; color:#8fa0b5; text-align:center; width:40%;">🏆 La Liga | 📅 2026-08-18 19:30 <b style="color:#ffffff; margin-left:10px;">VS</b></span>
            <span style="font-size:14px; font-weight:700; text-align:right; width:30%;">Real Madrid</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👥 PLANTILLA DEL EQUIPO</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Nombre</th>
                    <th>Edad</th>
                    <th>Posición</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>1</td><td><b>Thibaut Courtois</b></td><td>34</td><td>Goalkeeper</td></tr>
                <tr><td>3</td><td><b>Éder Militão</b></td><td>28</td><td>Defender</td></tr>
                <tr><td>22</td><td><b>Antonio Rüdiger</b></td><td>33</td><td>Defender</td></tr>
                <tr><td>5</td><td><b>Jude Bellingham</b></td><td>23</td><td>Midfielder</td></tr>
                <tr><td>8</td><td><b>Federico Valverde</b></td><td>27</td><td>Midfielder</td></tr>
                <tr><td>7</td><td><b>Vinícius Júnior</b></td><td>26</td><td>Attacker</td></tr>
                <tr><td>9</td><td><b>Kylian Mbappé</b></td><td>27</td><td>Attacker</td></tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Margen inferior para que el contenido no colisione con el footer fijo
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# ==============================================================================
# FOOTER OFICIAL REQUERIDO ESTRICTAMENTE (ESTILO EXACTO DE LA FOTO)
# ==============================================================================
st.markdown(
    """
    <div class="footer">
        <b>Forza Football Analytics V3.0 (Integración AI)</b><br>
        Plataforma Avanzada de Datos Deportivos<br>
        Proyecto Universitario | Desarrollado por Salomón Achar © 2026
    </div>
    """, 
    unsafe_allow_html=True
)
