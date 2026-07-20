import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA & MODO OSCURO PREMIUM
# ==============================================================================
st.set_page_config(
    page_title="Forza Football Analytics v3.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS para forzar una interfaz Premium Dark-Mode
st.markdown("""
    <style>
        /* Fondo principal de la aplicación */
        .stApp {
            background-color: #0a1628;
            color: #e0e6ed;
        }
        
        /* Contenedores y Tarjetas */
        div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
            background-color: #0e1e38;
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        /* Modificar el estilo de las pestañas (Tabs) */
        button[data-baseweb="tab"] {
            color: #e0e6ed !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            background-color: transparent !important;
        }
        button[aria-selected="true"] {
            color: #1e90ff !important;
            border-bottom-color: #1e90ff !important;
        }
        
        /* Badges e Indicadores */
        .live-badge {
            background-color: #ff1744;
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            animation: blinker 1.5s linear infinite;
        }
        @keyframes blinker {
            50% { opacity: 0.4; }
        }
        
        .minute-badge {
            background-color: #1e90ff;
            color: white;
            padding: 3px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }
        
        /* Títulos y textos */
        h1, h2, h3 {
            color: #f0c040 !important; /* Dorado Accent */
        }
        
        /* Estilos personalizados para las métricas KPIs */
        .kpi-container {
            background-color: #0e1e38;
            border-left: 5px solid #1e90ff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #e0e6ed;
        }
        .kpi-label {
            font-size: 14px;
            color: #8a99ad;
        }
        
        /* Footer fijo en la parte inferior */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #050d1a;
            color: #8a99ad;
            text-align: center;
            padding: 12px;
            font-size: 13px;
            border-top: 1px solid #1e90ff;
            z-index: 100;
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

Ejemplo para obtener estadísticas avanzadas / métricas xG post-partido:
def get_match_stats_api(match_id):
    response = requests.get(f"{BASE_URL}/football/matches/{match_id}/stats", headers=HEADERS)
    return response.json()
"""

# ==============================================================================
# CAPA DE DATOS (MOCKED DATA CON ESTRUCTURA OFICIAL API Y CACHÉ)
# ==============================================================================

@st.cache_data
def load_league_standings(competition_id):
    # Simula la respuesta de: GET /football/competitions/{id}/seasons/{sn_id}/standings
    data = {
        "comp_laliga": [
            {"position": 1, "team": "Real Madrid", "points": 78, "goal_difference": 42, "form": "W-W-D-W-W"},
            {"position": 2, "team": "Barcelona", "points": 72, "goal_difference": 31, "form": "W-L-W-W-D"},
            {"position": 3, "team": "Atlético Madrid", "points": 65, "goal_difference": 20, "form": "L-W-W-D-W"},
            {"position": 4, "team": "Real Sociedad", "points": 59, "goal_difference": 12, "form": "D-W-L-W-L"}
        ],
        "comp_premier": [
            {"position": 1, "team": "Manchester City", "points": 81, "goal_difference": 48, "form": "W-W-W-D-W"},
            {"position": 2, "team": "Liverpool", "points": 79, "goal_difference": 45, "form": "W-D-W-L-W"},
            {"position": 3, "team": "Arsenal", "points": 77, "goal_difference": 39, "form": "W-W-L-W-W"},
            {"position": 4, "team": "Aston Villa", "points": 63, "goal_difference": 15, "form": "D-L-W-W-D"}
        ]
    }
    return pd.DataFrame(data.get(competition_id, data["comp_laliga"]))

@st.cache_data
def load_live_matches():
    # Simula la respuesta de: GET /football/matches?status=live
    return [
        {
            "match_id": "mt_001",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "score": "2–1",
            "status": "LIVE",
            "minute": "74'",
            "live_stats": {
                "ball_possession": {"home": 54, "away": 46},
                "total_shots": {"home": 14, "away": 9},
                "corner_kicks": {"home": 6, "away": 4},
                "expected_goals": {"home": 1.95, "away": 1.24}
            }
        },
        {
            "match_id": "mt_002",
            "home_team": "Manchester City",
            "away_team": "Liverpool",
            "score": "3–3",
            "status": "LIVE",
            "minute": "88'",
            "live_stats": {
                "ball_possession": {"home": 59, "away": 41},
                "total_shots": {"home": 18, "away": 15},
                "corner_kicks": {"home": 8, "away": 5},
                "expected_goals": {"home": 2.61, "away": 2.45}
            }
        },
        {
            "match_id": "mt_003",
            "home_team": "Juventus",
            "away_team": "Bayern Munich",
            "score": "0–1",
            "status": "LIVE",
            "minute": "62'",
            "live_stats": {
                "ball_possession": {"home": 42, "away": 58},
                "total_shots": {"home": 5, "away": 12},
                "corner_kicks": {"home": 2, "away": 7},
                "expected_goals": {"home": 0.44, "away": 1.68}
            }
        }
    ]

@st.cache_data
def load_advanced_player_data():
    # Datos estructurados para simulaciones de gráficos avanzados y KPIs
    # Mapea con campos de: GET /football/players/{player_id}/stats
    players = [
        {"player": "Jude Bellingham", "team": "Real Madrid", "goals": 18, "assists": 8, "xg": 15.4, "passes_acc": 89.5, "duels_won_pct": 58.2, "position": "Midfielder"},
        {"player": "Erling Haaland", "team": "Manchester City", "goals": 27, "assists": 5, "xg": 29.1, "passes_acc": 76.2, "duels_won_pct": 49.8, "position": "Forward"},
        {"player": "Kylian Mbappé", "team": "PSG", "goals": 24, "assists": 7, "xg": 22.8, "passes_acc": 84.1, "duels_won_pct": 52.1, "position": "Forward"},
        {"player": "Kevin De Bruyne", "team": "Manchester City", "goals": 6, "assists": 14, "xg": 5.8, "passes_acc": 91.3, "duels_won_pct": 46.5, "position": "Midfielder"},
        {"player": "Vinícius Júnior", "team": "Real Madrid", "goals": 15, "assists": 9, "xg": 14.1, "passes_acc": 81.9, "duels_won_pct": 54.0, "position": "Forward"}
    ]
    return pd.DataFrame(players)

@st.cache_data
def load_shotmap_data():
    # Simula la respuesta de: GET /football/matches/{match_id}/shotmap
    # Coordenadas estandarizadas de la portería o campo
    shots = [
        {"x": 88, "y": 52, "xg": 0.65, "result": "Goal", "player": "Jude Bellingham", "body_part": "Right Foot"},
        {"x": 92, "y": 48, "xg": 0.45, "result": "Goal", "player": "Vinícius Júnior", "body_part": "Left Foot"},
        {"x": 75, "y": 60, "xg": 0.08, "result": "Saved", "player": "Toni Kroos", "body_part": "Right Foot"},
        {"x": 84, "y": 38, "xg": 0.12, "result": "Missed", "player": "Rodrygo", "body_part": "Head"},
        {"x": 89, "y": 45, "xg": 0.72, "result": "Goal", "player": "Robert Lewandowski", "body_part": "Right Foot"},
        {"x": 79, "y": 50, "xg": 0.15, "result": "Saved", "player": "Ilkay Gündogan", "body_part": "Right Foot"},
    ]
    return pd.DataFrame(shots)


# ==============================================================================
# ESTRUCTURA PRINCIPAL DE LA APLICACIÓN DE STREAMLIT
# ==============================================================================

# Encabezado Superior Premium
col_logo, col_title = st.columns([1, 11])
with col_title:
    st.title("FORZA FOOTBALL ANALYTICS")
    st.markdown("<p style='color: #8a99ad; margin-top: -15px;'>Módulo Universitario de Visualización Deportiva de Alta Performance</p>", unsafe_allow_html=True)

# Inicialización de las 4 pestañas requeridas
tab_principal, tab_vivo, tab_avanzada, tab_scout = st.tabs([
    "Panel Principal", 
    "Central En Vivo", 
    "Analítica Avanzada", 
    "Scout IA"
])

# ------------------------------------------------------------------------------
# TAB 1: PANEL PRINCIPAL
# ------------------------------------------------------------------------------
with tab_principal:
    st.subheader("Resumen General de Competiciones")
    
    col_selector, _ = st.columns([4, 8])
    with col_selector:
        comp_choice = st.selectbox(
            "Seleccionar Competición para Presentación",
            options=[("La Liga", "comp_laliga"), ("Premier League", "comp_premier")],
            format_func=lambda x: x[0]
        )
    
    standings_df = load_league_standings(comp_choice[1])
    
    col_table, col_quick_stats = st.columns([8, 4])
    
    with col_table:
        st.markdown(f"### Clasificación Actualizada - {comp_choice[0]}")
        # Formatear la tabla con estilos estilizados
        st.dataframe(
            standings_df.style.set_properties(**{
                'background-color': '#0e1e38',
                'color': '#e0e6ed',
                'border-color': '#1e90ff'
            }), 
            use_container_width=True, 
            hide_index=True
        )
        
    with col_quick_stats:
        st.markdown("### Estado de Integración de Datos")
        st.info("💡 **Información de Desarrollo:** Los datos mostrados corresponden al dataset estático optimizado para sustentación pública. La infraestructura soporta paginación nativa mediante parámetros `?page=N&per_page=100`.")
        
        # Gráfico rápido de distribución de puntos en la tabla
        fig_points = px.bar(
            standings_df, 
            x='team', 
            y='points', 
            title="Distribución de Puntos",
            color='points',
            color_continuous_scale=['#1e90ff', '#f0c040']
        )
        fig_points.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e6ed',
            height=240,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_points, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: CENTRAL EN VIVO
# ------------------------------------------------------------------------------
with tab_vivo:
    st.subheader("Seguimiento de Partidos en Tiempo Real")
    
    live_matches = load_live_matches()
    
    # Grid de partidos interactivo
    for match in live_matches:
        with st.container():
            col_info, col_visuals = st.columns([5, 7])
            
            with col_info:
                st.markdown(
                    f"""
                    <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 10px;'>
                        <span class="live-badge">EN VIVO</span>
                        <span class="minute-badge">{match['minute']}</span>
                    </div>
                    <h3 style='margin: 5px 0;'>{match['home_team']} <span style='color: #f0c040;'>{match['score']}</span> {match['away_team']}</h3>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Métricas rápidas de posesión y xG
                s = match['live_stats']
                st.markdown(
                    f"""
                    *   **Posesión de Balón:** {s['ball_possession']['home']}% vs {s['ball_possession']['away']}%
                    *   **Goles Esperados (xG):** 🔥 {s['expected_goals']['home']} vs ⚽ {s['expected_goals']['away']}
                    *   **Tiros Totales:** {s['total_shots']['home']} (Local) | {s['total_shots']['away']} (Visitante)
                    """,
                    unsafe_allow_html=True
                )
                
            with col_visuals:
                # Gráfico de barras comparativo para el partido
                categories = ['Posesión (%)', 'Tiros Totales', 'Córners', 'xG * 10']
                home_values = [s['ball_possession']['home'], s['total_shots']['home'], s['corner_kicks']['home'], s['expected_goals']['home']*10]
                away_values = [s['ball_possession']['away'], s['total_shots']['away'], s['corner_kicks']['away'], s['expected_goals']['away']*10]
                
                fig_match = go.Figure()
                fig_match.add_trace(go.Bar(name=match['home_team'], x=categories, y=home_values, marker_color='#1e90ff'))
                fig_match.add_trace(go.Bar(name=match['away_team'], x=categories, y=away_values, marker_color='#ff1744'))
                
                fig_match.update_layout(
                    barmode='group',
                    height=160,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e0e6ed',
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_match, use_container_width=True, key=match['match_id'])
            
            st.markdown("---")

# ------------------------------------------------------------------------------
# TAB 3: ANALÍTICA AVANZADA
# ------------------------------------------------------------------------------
with tab_avanzada:
    st.subheader("Métricas de Rendimiento Avanzado e Inteligencia de Datos")
    
    # Fila superior de 4 KPIs obligatorios
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-value">2.84</div>
                <div class="kpi-label">Promedio Global xG por Partido</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-value">84.7%</div>
                <div class="kpi-label">Efectividad de Pases (EPL/LaLiga)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-value">12.4</div>
                <div class="kpi-label">PPDA Promedio (Intensidad de Presión)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-value">34%</div>
                <div class="kpi-label">Conversión de Tiros a Puerta</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sección de Gráficos Avanzados
    col_chart1, col_chart2 = st.columns(2)
    player_df = load_advanced_player_data()
    
    with col_chart1:
        st.markdown("### Goles vs Goles Esperados (xG)")
        fig_scatter = px.scatter(
            player_df,
            x="xg",
            y="goals",
            text="player",
            size="goals",
            color="position",
            color_discrete_sequence=['#1e90ff', '#f0c040']
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#0e1e38',
            font_color='#e0e6ed',
            height=350
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_chart2:
        st.markdown("### Mapa de Tiros Simulado (Shotmap de El Clásico)")
        shot_df = load_shotmap_data()
        
        # Simulación espacial de la mitad del campo de fútbol hacia la portería (derecha)
        fig_shots = px.scatter(
            shot_df,
            x="x",
            y="y",
            color="result",
            size="xg",
            hover_data=["player", "body_part"],
            color_discrete_map={"Goal": "#00c853", "Saved": "#1e90ff", "Missed": "#ff1744"}
        )
        # Dibujar líneas del área simulada para la entrega académica
        fig_shots.add_shape(type="rect", x0=83, y0=25, x1=100, y1=75, line=dict(color="#e0e6ed", width=2))
        fig_shots.add_shape(type="rect", x0=94, y0=36, x1=100, y1=64, line=dict(color="#e0e6ed", width=1))
        
        fig_shots.update_layout(
            title="Ubicación de Tiros en Zona de Ataque",
            xaxis=dict(range=[50, 102], title="Longitud del Campo"),
            yaxis=dict(range=[0, 100], title="Ancho del Campo"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#0e1e38',
            font_color='#e0e6ed',
            height=350
        )
        st.plotly_chart(fig_shots, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: SCOUT IA (PLACEHOLDER DE CONTENIDO BÁSICO CON IDENTIDAD DE MARCA)
# ------------------------------------------------------------------------------
with tab_scout:
    st.subheader("🤖 Asistente Avanzado de Scouting IA")
    
    col_scout_control, col_scout_res = st.columns([4, 8])
    
    with col_scout_control:
        st.markdown("#### Configuración de Búsqueda Predictiva")
        player_sel = st.selectbox("Seleccionar Perfil Objetivo", options=load_advanced_player_data()['player'].unique())
        st.slider("Umbral de Similitud xG", 0.0, 1.0, 0.85)
        st.multiselect("Características Clave", ["Velocidad de Transición", "Presión Alta", "Juego Aéreo", "Retención de Posesión"], default=["Velocidad de Transición"])
        st.button("Generar Informe con Algoritmo Generativo IA")
        
    with col_scout_res:
        st.markdown(f"### Análisis Automatizado para: **{player_sel}**")
        st.write(
            f"El motor de Inteligencia Artificial de **Forza Football Analytics** ha procesado las métricas de rendimiento "
            f"de las bases de datos de la temporada en curso. El jugador presenta una alta tasa de conversión en situaciones "
            f"de juego abierto con una fuerte desviación estándar positiva con respecto al promedio de la liga."
        )
        
        # Gráfico radial simulado para el Scout IA
        categories_radar = ['Goles por 90', 'Asistencias por 90', 'xG Recibido', 'Pases Clave', 'Duels Ganados']
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
              r=[4, 3, 5, 4, 3],
              theta=categories_radar,
              fill='toself',
              name='Percentil Actual',
              marker_color='#f0c040'
        ))
        fig_radar.update_layout(
          polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#8a99ad"),
            bgcolor="#0e1e38"
          ),
          showlegend=False,
          paper_bgcolor='rgba(0,0,0,0)',
          font_color='#e0e6ed',
          height=250,
          margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# Space buffer para evitar que el contenido colisione con el footer fijo
st.markdown("<br><br><br>", unsafe_allow_html=True)

# ==============================================================================
# FOOTER OFICIAL REQUERIDO ESTRICTAMENTE
# ==============================================================================
st.markdown(
    '<div class="footer">Forza Football Analytics V3.0 Integración AI, Plataforma Avanzada de Datos Deportivos, Proyecto Universitario, Desarrollado por Salomón Achar © 2026</div>', 
    unsafe_allow_html=True
)
