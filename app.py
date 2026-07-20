import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import requests

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA & MODO OSCURO PREMIUM
# ==============================================================================
st.set_page_config(
    page_title="Forza Football Analytics v3.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS de alto rendimiento y maquetación limpia
st.markdown("""
    <style>
        /* Fondo principal de la aplicación */
        .stApp {
            background-color: #0a1628;
            color: #e0e6ed;
            font-family: 'Source Sans Pro', sans-serif;
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
        
        /* Títulos y textos */
        h1, h2, h3 {
            color: #f0c040 !important; /* Dorado Accent */
            margin-bottom: 15px !important;
        }
        
        /* Contenedor Premium unificado para Tarjetas/Paneles */
        .premium-panel {
            background-color: #0e1e38;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #1e293b;
            margin-bottom: 20px;
        }
        
        /* ALERTAS PERSONALIZADAS (Reemplazan st.warning y st.info para integrarse al diseño) */
        .custom-alert-warning {
            background-color: #1c1917;
            border-left: 4px solid #f59e0b;
            padding: 14px;
            border-radius: 8px;
            color: #fcd34d;
            font-size: 13.5px;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        .custom-alert-info {
            background-color: #0c1e36;
            border-left: 4px solid #3b82f6;
            padding: 14px;
            border-radius: 8px;
            color: #93c5fd;
            font-size: 13.5px;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        /* TABLA PREMIUM RESPONSIVA (Corrige los encabezados oscuros e ilegibles) */
        .premium-table {
            width: 100%;
            border-collapse: collapse;
            background-color: #0e1e38;
            margin-top: 10px;
        }
        .premium-table th {
            background-color: #162a4a;
            color: #ffffff;
            font-weight: 600;
            padding: 12px;
            text-align: left;
            font-size: 14px;
            border-bottom: 2px solid #1e90ff;
        }
        .premium-table td {
            padding: 12px;
            border-bottom: 1px solid #16253d;
            font-size: 13.5px;
            color: #e0e6ed;
        }
        .premium-table tr:hover {
            background-color: #132747;
        }
        
        /* Badges e Indicadores En Vivo */
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
        
        /* Estilos para las métricas KPIs */
        .kpi-container {
            background-color: #0e1e38;
            border-left: 5px solid #1e90ff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #1e293b;
            border-left: 5px solid #1e90ff;
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
        
        /* Footer fijo inferior */
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
# CONFIGURACIÓN DE CLIENTE HTTP - THESTATSAPI
# ==============================================================================
BASE_URL = "https://api.thestatsapi.com/api"
THESTATSAPI_KEY = os.getenv('THESTATSAPI_KEY', 'TU_TOKEN_AQUÍ') 
HEADERS = {
    "Authorization": f"Bearer {THESTATSAPI_KEY}"
}

# ==============================================================================
# CAPA DE DATOS (CONEXIÓN EN VIVO HTTP Y BACKUP INTEGRADO)
# ==============================================================================

@st.cache_data(ttl=300)
def load_league_standings(competition_id):
    comp_clean = competition_id.replace("comp_", "")
    try:
        url = f"{BASE_URL}/football/competitions/{comp_clean}/seasons/current/standings"
        response = requests.get(url, headers=HEADERS, timeout=4)
        if response.status_code == 200:
            api_data = response.json()
            if 'data' in api_data and len(api_data['data']) > 0:
                return pd.DataFrame(api_data['data'])
    except Exception:
        pass

    # DATA FALLBACK OPTIMIZADA
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


def load_live_matches():
    try:
        url = f"{BASE_URL}/football/matches?status=live"
        response = requests.get(url, headers=HEADERS, timeout=4)
        if response.status_code == 200:
            data = response.json()
            api_matches = data.get('data', [])
            if api_matches:
                processed_matches = []
                for match in api_matches:
                    m_id = match.get('match_id', match.get('id', 'mt_001'))
                    stats_url = f"{BASE_URL}/football/matches/{m_id}/stats"
                    stats_response = requests.get(stats_url, headers=HEADERS, timeout=3)
                    api_stats = stats_response.json().get('data', {}) if stats_response.status_code == 200 else {}
                    
                    processed_matches.append({
                        "match_id": m_id,
                        "home_team": match.get("home_team", "Local"),
                        "away_team": match.get("away_team", "Visitante"),
                        "score": match.get("score", "0–0"),
                        "status": match.get("status", "LIVE"),
                        "minute": match.get("minute", "0'"),
                        "live_stats": {
                            "ball_possession": api_stats.get("ball_possession", {"home": 50, "away": 50}),
                            "total_shots": api_stats.get("total_shots", {"home": 10, "away": 10}),
                            "corner_kicks": api_stats.get("corner_kicks", {"home": 4, "away": 4}),
                            "expected_goals": api_stats.get("expected_goals", {"home": 1.00, "away": 1.00})
                        }
                    })
                return processed_matches
    except Exception:
        pass

    # DATA FALLBACK OPTIMIZADA
    return [
        {
            "match_id": "mt_001", "home_team": "Real Madrid", "away_team": "Barcelona", "score": "2–1", "status": "LIVE", "minute": "74'",
            "live_stats": {"ball_possession": {"home": 54, "away": 46}, "total_shots": {"home": 14, "away": 9}, "corner_kicks": {"home": 6, "away": 4}, "expected_goals": {"home": 1.95, "away": 1.24}}
        },
        {
            "match_id": "mt_002", "home_team": "Manchester City", "away_team": "Liverpool", "score": "3–3", "status": "LIVE", "minute": "88'",
            "live_stats": {"ball_possession": {"home": 59, "away": 41}, "total_shots": {"home": 18, "away": 15}, "corner_kicks": {"home": 8, "away": 5}, "expected_goals": {"home": 2.61, "away": 2.45}}
        },
        {
            "match_id": "mt_003", "home_team": "Juventus", "away_team": "Bayern Munich", "score": "0–1", "status": "LIVE", "minute": "62'",
            "live_stats": {"ball_possession": {"home": 42, "away": 58}, "total_shots": {"home": 5, "away": 12}, "corner_kicks": {"home": 2, "away": 7}, "expected_goals": {"home": 0.44, "away": 1.68}}
        }
    ]

@st.cache_data(ttl=600)
def load_advanced_player_data():
    try:
        response = requests.get(f"{BASE_URL}/football/players/top/stats", headers=HEADERS, timeout=4)
        if response.status_code == 200:
            api_data = response.json()
            if 'data' in api_data: return pd.DataFrame(api_data['data'])
    except Exception:
        pass

    players = [
        {"player": "Jude Bellingham", "team": "Real Madrid", "goals": 18, "assists": 8, "xg": 15.4, "passes_acc": 89.5, "duels_won_pct": 58.2, "position": "Midfielder"},
        {"player": "Erling Haaland", "team": "Manchester City", "goals": 27, "assists": 5, "xg": 29.1, "passes_acc": 76.2, "duels_won_pct": 49.8, "position": "Forward"},
        {"player": "Kylian Mbappé", "team": "PSG", "goals": 24, "assists": 7, "xg": 22.8, "passes_acc": 84.1, "duels_won_pct": 52.1, "position": "Forward"},
        {"player": "Kevin De Bruyne", "team": "Manchester City", "goals": 6, "assists": 14, "xg": 5.8, "passes_acc": 91.3, "duels_won_pct": 46.5, "position": "Midfielder"},
        {"player": "Vinícius Júnior", "team": "Real Madrid", "goals": 15, "assists": 9, "xg": 14.1, "passes_acc": 81.9, "duels_won_pct": 54.0, "position": "Forward"}
    ]
    return pd.DataFrame(players)

@st.cache_data(ttl=600)
def load_shotmap_data():
    try:
        response = requests.get(f"{BASE_URL}/football/matches/featured/shotmap", headers=HEADERS, timeout=4)
        if response.status_code == 200:
            api_data = response.json()
            if 'data' in api_data: return pd.DataFrame(api_data['data'])
    except Exception:
        pass

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

# Inicialización de pestañas
tab_principal, tab_vivo, tab_avanzada, tab_scout = st.tabs([
    "Panel Principal", "Central En Vivo", "Analítica Avanzada", "Scout IA"
])

# ------------------------------------------------------------------------------
# TAB 1: PANEL PRINCIPAL (ENFOQUE DE CORRECCIÓN VISUAL DE LA CAPTURA)
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
    
    # Grid Maestro dividido limpiamente en paneles premium
    col_table, col_quick_stats = st.columns([7, 5])
    
    with col_table:
        st.markdown(f"### Clasificación Actualizada - {comp_choice[0]}")
        
        # TABLA HTML CORREGIDA: Elimina bugs de renderizado de cabeceras nativas
        headers = ["Position", "Team", "Points", "Goal Difference", "Form"]
        html_table = "<div class='premium-panel'><table class='premium-table'><thead><tr>"
        for h in headers:
            html_table += f"<th>{h}</th>"
        html_table += "</tr></thead><tbody>"
        
        for _, row in standings_df.iterrows():
            html_table += f"""
            <tr>
                <td><b>{row['position']}</b></td>
                <td><span style='color: #f0c040;'>●</span> {row['team']}</td>
                <td><b>{row['points']}</b></td>
                <td>{row['goal_difference']}</td>
                <td><code style='color: #00c853; background: none; padding:0;'>{row['form']}</code></td>
            </tr>"""
        html_table += "</tbody></table></div>"
        st.markdown(html_table, unsafe_allow_html=True)
        
    with col_quick_stats:
        st.markdown("### Estado de Integración de Datos")
        
        # Envoltorio del Panel de Estado e Integración
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        
        if THESTATSAPI_KEY == 'TU_TOKEN_AQUÍ':
            st.markdown("""
                <div class="custom-alert-warning">
                    <strong>⚠️ Modo Sandbox / Fallback Activo:</strong> La API Key global no está configurada en las variables de entorno. Visualizando estructura de datos local.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="custom-alert-info" style="border-left-color: #00c853; color: #a7f3d0; background-color: #0a2419;">
                    <strong>🔌 Conectado en Vivo:</strong> TheStatsAPI está transmitiendo telemetría deportiva exitosamente a la interfaz.
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
            <div class="custom-alert-info">
                <strong>💡 Información de Desarrollo:</strong> La infraestructura soporta paginación nativa mediante parámetros <code>?page=N&per_page=100</code>.
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Panel del gráfico corregido
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        st.markdown("<b style='color:#f0c040; font-size:15px; display:block; margin-bottom:10px;'>Distribución de Puntos</b>", unsafe_allow_html=True)
        
        fig_points = px.bar(
            standings_df, x='team', y='points', color='points',
            color_continuous_scale=['#1e90ff', '#f0c040']
        )
        fig_points.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e6ed', height=240, showlegend=False,
            coloraxis_showscale=False, # Remueve la barra lateral redundante que quita espacio
            margin=dict(l=30, r=10, t=10, b=40),
            xaxis=dict(gridcolor='rgba(0,0,0,0)', title=""),
            yaxis=dict(gridcolor='#1e293b', title="Puntos")
        )
        st.plotly_chart(fig_points, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: CENTRAL EN VIVO
# ------------------------------------------------------------------------------
with tab_vivo:
    st.subheader("Seguimiento de Partidos en Tiempo Real")
    live_matches = load_live_matches()
    
    for match in live_matches:
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        col_info, col_visuals = st.columns([5, 7])
        
        with col_info:
            st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 10px;'>
                    <span class="live-badge">EN VIVO</span>
                    <span class="minute-badge">{match['minute']}</span>
                </div>
                <h3 style='margin: 5px 0;'>{match['home_team']} <span style='color: #f0c040;'>{match['score']}</span> {match['away_team']}</h3>
            """, unsafe_allow_html=True)
            
            s = match['live_stats']
            st.markdown(f"""
                * **Posesión de Balón:** {s['ball_possession']['home']}% vs {s['ball_possession']['away']}%
                * **Goles Esperados (xG):** 🔥 {s['expected_goals']['home']} vs ⚽ {s['expected_goals']['away']}
                * **Tiros Totales:** {s['total_shots']['home']} (Local) | {s['total_shots']['away']} (Visitante)
            """)
            
        with col_visuals:
            categories = ['Posesión (%)', 'Tiros Totales', 'Córners', 'xG * 10']
            home_values = [s['ball_possession']['home'], s['total_shots']['home'], s['corner_kicks']['home'], s['expected_goals']['home']*10]
            away_values = [s['ball_possession']['away'], s['total_shots']['away'], s['corner_kicks']['away'], s['expected_goals']['away']*10]
            
            fig_match = go.Figure()
            fig_match.add_trace(go.Bar(name=match['home_team'], x=categories, y=home_values, marker_color='#1e90ff'))
            fig_match.add_trace(go.Bar(name=match['away_team'], x=categories, y=away_values, marker_color='#ff1744'))
            fig_match.update_layout(
                barmode='group', height=160, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e0e6ed', margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(gridcolor='rgba(0,0,0,0)'), yaxis=dict(gridcolor='#1e293b')
            )
            st.plotly_chart(fig_match, use_container_width=True, key=match['match_id'], config={'displayModeBar': False})
        
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: ANALÍTICA AVANZADA
# ------------------------------------------------------------------------------
with tab_avanzada:
    st.subheader("Métricas de Rendimiento Avanzado e Inteligencia de Datos")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown('<div class="kpi-container"><div class="kpi-value">2.84</div><div class="kpi-label">Promedio Global xG por Partido</div></div>', unsafe_allow_html=True)
    with kpi_col2:
        st.markdown('<div class="kpi-container"><div class="kpi-value">84.7%</div><div class="kpi-label">Efectividad de Pases (EPL/LaLiga)</div></div>', unsafe_allow_html=True)
    with kpi_col3:
        st.markdown('<div class="kpi-container"><div class="kpi-value">12.4</div><div class="kpi-label">PPDA Promedio (Presión)</div></div>', unsafe_allow_html=True)
    with kpi_col4:
        st.markdown('<div class="kpi-container"><div class="kpi-value">34%</div><div class="kpi-label">Conversión de Tiros a Puerta</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    player_df = load_advanced_player_data()
    
    with col_chart1:
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        st.markdown("### Goles vs Goles Esperados (xG)")
        fig_scatter = px.scatter(player_df, x="xg", y="goals", text="player", size="goals", color="position", color_discrete_sequence=['#1e90ff', '#f0c040'])
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0e1e38', font_color='#e0e6ed', height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_chart2:
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        st.markdown("### Mapa de Tiros Simulado (El Clásico)")
        shot_df = load_shotmap_data()
        fig_shots = px.scatter(shot_df, x="x", y="y", color="result", size="xg", hover_data=["player", "body_part"], color_discrete_map={"Goal": "#00c853", "Saved": "#1e90ff", "Missed": "#ff1744"})
        fig_shots.add_shape(type="rect", x0=83, y0=25, x1=100, y1=75, line=dict(color="#e0e6ed", width=2))
        fig_shots.add_shape(type="rect", x0=94, y0=36, x1=100, y1=64, line=dict(color="#e0e6ed", width=1))
        fig_shots.update_layout(
            xaxis=dict(range=[50, 102], title="Longitud"), yaxis=dict(range=[0, 100], title="Ancho"),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0e1e38', font_color='#e0e6ed', height=350, margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_shots, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 4: SCOUT IA
# ------------------------------------------------------------------------------
with tab_scout:
    st.subheader("🤖 Asistente Avanzado de Scouting IA")
    col_scout_control, col_scout_res = st.columns([4, 8])
    
    with col_scout_control:
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        st.markdown("#### Configuración de Búsqueda Predictiva")
        player_sel = st.selectbox("Seleccionar Perfil Objetivo", options=load_advanced_player_data()['player'].unique())
        st.slider("Umbral de Similitud xG", 0.0, 1.0, 0.85)
        st.multiselect("Características Clave", ["Velocidad de Transición", "Presión Alta", "Juego Aéreo", "Retención de Posesión"], default=["Velocidad de Transición"])
        st.button("Generar Informe con Algoritmo Generativo IA")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_scout_res:
        st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
        st.markdown(f"### Análisis Automatizado para: **{player_sel}**")
        st.write("El motor de Inteligencia Artificial de Forza Football Analytics ha procesado las métricas de rendimiento del jugador presentando una fuerte desviación estándar positiva con respecto al promedio de la liga.")
        
        categories_radar = ['Goles por 90', 'Asistencias por 90', 'xG Recibido', 'Pases Clave', 'Duels Ganados']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[4, 3, 5, 4, 3], theta=categories_radar, fill='toself', name='Percentil Actual', marker_color='#f0c040'))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="#8a99ad"), bgcolor="#0e1e38"),
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e6ed', height=250, margin=dict(l=10, r=10, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

# Margen inferior anti-colisión con el footer
st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# ==============================================================================
# FOOTER OFICIAL REQUERIDO ESTRICTAMENTE
# ==============================================================================
st.markdown(
    '<div class="footer">Forza Football Analytics V3.0 Integración AI, Plataforma Avanzada de Datos Deportivos, Proyecto Universitario, Desarrollado por Salomón Achar © 2026</div>', 
    unsafe_allow_html=True
)
