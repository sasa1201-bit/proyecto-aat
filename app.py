import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS REPLICADOS DE LA CAPTURA
# ==============================================================================
st.set_page_config(
    page_title="Forza Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS para clonar la interfaz premium exacta de las capturas
st.markdown("""
    <style>
        /* Fondo base de la aplicación */
        .stApp {
            background-color: #0b1322 !important;
            color: #ffffff !important;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        /* Ocultar elementos nativos innecesarios de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Contenedores / Tarjetas Modulares */
        .custom-card {
            background-color: #141f32;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #1c2a42;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
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
        
        /* Estilos de las Pestañas (Tabs Nav) */
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
        
        /* Títulos de Tarjetas Internas */
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
        
        /* Formato de métricas KPI */
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
        
        /* Widgets En Vivo */
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
        
        /* Tabla de Plantilla del Equipo */
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
        .custom-table tr:hover {
            background-color: #18263e;
        }
        
        /* Calendario Replicado */
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
        
        /* Buscador superior */
        .search-container {
            background-color: #0d1726;
            border: 1px solid #1c2a42;
            border-radius: 6px;
            padding: 8px 12px;
            color: #8fa0b5;
            font-size: 13px;
            margin-bottom: 20px;
        }
        
        /* Footer Replicado Estrictamente de la Imagen */
        .custom-footer {
            margin-top: 50px;
            border-top: 1px solid #1c2a42;
            padding: 20px 0;
            text-align: center;
            color: #8fa0b5;
            font-size: 12px;
            line-height: 1.8;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA LAYERING (MOCKED CACHED DATA CON CONVENCIÓN DE IDS)
# ==============================================================================
@st.cache_data
def get_mock_team_stats():
    return {
        "name": "Real Madrid",
        "country": "Spain",
        "efectividad": "100.0%",
        "goles_partido": "3.2",
        "record": "5 - 0 - 0"
    }

@st.cache_data
def get_mock_results():
    return [
        {"home": "Real Madrid", "away": "Alaves", "score": "5 - 0", "comp": "🏆 La Liga", "date": "📅 2026-05-14 20:00"},
        {"home": "Granada", "away": "Real Madrid", "score": "0 - 4", "comp": "🏆 La Liga", "date": "📅 2026-05-10 16:15"},
        {"home": "Real Madrid", "away": "Cadiz", "score": "3 - 0", "comp": "🏆 La Liga", "date": "📅 2026-05-04 18:30"}
    ]

# ==============================================================================
# NAVEGACIÓN Y CONFIGURACIÓN DE PESTAÑAS (TABS)
# ==============================================================================
tab_principal, tab_vivo, tab_avanzada, tab_scout = st.tabs([
    "🏠 Panel Principal", 
    "🔴 Central En Vivo", 
    "📈 Analítica Avanzada", 
    "👁️‍🗨️ Scout IA"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: PANEL PRINCIPAL
# ------------------------------------------------------------------------------
with tab_principal:
    # Caja de entrada / búsqueda simulada de la cabecera
    st.markdown('<div class="search-container">🔍 Buscar club (Ej. Arsenal, Madrid)...</div>', unsafe_allow_html=True)
    
    # Fila de KPIs Superiores
    team_info = get_mock_team_stats()
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns([3, 2, 2, 3])
    
    with kpi_col1:
        st.markdown(f"""
            <div class="team-profile-card">
                <span style="font-size: 32px;">👑</span>
                <div>
                    <div style="font-size: 16px; font-weight:700; color:#ffffff;">{team_info['name']}</div>
                    <div style="font-size: 12px; color:#8fa0b5;">{team_info['country']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
            <div class="custom-card" style="padding: 15px 20px;">
                <div class="kpi-label">Efectividad</div>
                <div class="kpi-value">{team_info['efectividad']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
            <div class="custom-card" style="padding: 15px 20px;">
                <div class="kpi-label">Goles / Partido</div>
                <div class="kpi-value">{team_info['goles_partido']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
            <div class="custom-card" style="padding: 15px 20px;">
                <div class="kpi-label">Récord (V-E-D)</div>
                <div class="kpi-value">{team_info['record']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Fila Inferior: Últimos Resultados e Historial / Calendario Actual
    body_col1, body_col2 = st.columns([6, 5])
    
    with body_col1:
        st.markdown('<div class="custom-card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏮️ ÚLTIMOS RESULTADOS</div>', unsafe_allow_html=True)
        
        for res in get_mock_results():
            st.markdown(f"""
                <div class="result-row">
                    <div class="result-team">{res['home']}</div>
                    <div class="result-center">
                        <div class="result-score">{res['score']}</div>
                        <div class="result-meta">{res['comp']} | {res['date']}</div>
                    </div>
                    <div class="result-team" style="text-align: right;">{res['away']}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with body_col2:
        st.markdown('<div class="custom-card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📅 CALENDARIO ACTUAL</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; font-size:14px; font-weight:700; color:#ffffff; margin-bottom:5px;">July 2026</div>', unsafe_allow_html=True)
        
        # Mapeo exacto del HTML del calendario de Julio 2026 (1 de Julio cae Miércoles)
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
# PESTAÑA 2: CENTRAL EN VIVO
# ------------------------------------------------------------------------------
with tab_vivo:
    st.markdown('<h3 style="color:#ffffff; font-size:18px; font-weight:700; margin-bottom:20px;">🔴 COBERTURA EN DIRECTO</h3>', unsafe_allow_html=True)
    
    # Partido 1
    st.markdown("""
        <div class="live-match-card">
            <div class="live-team-name">Real Madrid</div>
            <div class="live-center-box">
                <div class="live-score-pill">2 - 1</div>
                <div class="live-minute-pill">🕒 74'</div>
            </div>
            <div class="live-team-name" style="text-align: right;">Barcelona</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Partido 2
    st.markdown("""
        <div class="live-match-card">
            <div class="live-team-name">Arsenal</div>
            <div class="live-center-box">
                <div class="live-score-pill">0 - 0</div>
                <div class="live-minute-pill">🕒 15'</div>
            </div>
            <div class="live-team-name" style="text-align: right;">Chelsea</div>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PESTAÑA 3: ANALÍTICA AVANZADA
# ------------------------------------------------------------------------------
with tab_avanzada:
    st.markdown('<h3 style="color:#ffffff; font-size:18px; font-weight:700; margin-bottom:20px;">📈 ANALÍTICA DE DATOS</h3>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 VOLUMEN DE PARTIDOS</div>', unsafe_allow_html=True)
        # Construcción exacta del gráfico de barras de la captura
        fig_vol = go.Figure(data=[
            go.Bar(x=['La Liga', 'Premier League'], y=[1, 1], marker_color='#3b82f6', width=0.5)
        ])
        fig_vol.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8fa0b5', height=250, margin=dict(l=20,r=20,t=10,b=10),
            yaxis=dict(gridcolor='#1c2a42', range=[0, 1]), xaxis=dict(tickangle=90)
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with chart_col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚽ GOLES TOTALES POR LIGA</div>', unsafe_allow_html=True)
        # Gráfico de Área descendente exacto
        fig_goals = go.Figure()
        fig_goals.add_trace(go.Scatter(
            x=['La Liga', 'Premier League'], y=[3, 0],
            fill='tozeroy', mode='lines', line=dict(color='#ef4444', width=2),
            fillcolor='rgba(239, 68, 68, 0.8)'
        ))
        fig_goals.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8fa0b5', height=250, margin=dict(l=20,r=20,t=10,b=10),
            yaxis=dict(gridcolor='#1c2a42', range=[0, 3]), xaxis=dict(tickangle=90)
        )
        st.plotly_chart(fig_goals, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Fila Inferior de Gráficos: Radar y Ubicación Geográfica
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🕸️ PERFIL TÁCTICO RADAR</div>', unsafe_allow_html=True)
        
        categories = ['Poder Goleador', 'Efectividad', 'Volumen', 'Consistencia', 'Solidez Defensiva']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[100, 95, 75, 60, 80], theta=categories, fill='toself',
            line=dict(color='#3b82f6', width=2), fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1c2a42", angle=45, tickfont=dict(size=8)),
                angularaxis=dict(gridcolor="#1c2a42")
            ),
            paper_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=280,
            margin=dict(l=50, r=50, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with chart_col4:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🗺️ UBICACIÓN GEOGRÁFICA</div>', unsafe_allow_html=True)
        
        # Mapa Oscuro enfocado en la geolocalización de España/Madrid
        fig_map = go.Figure(go.Scattermapbox(
            lat=[40.4167], lon=[-3.7037], mode='markers+text',
            marker=go.scattermapbox.Marker(size=12, color='#ffffff'),
            text=['Madrid'], textposition='bottom center'
        ))
        fig_map.update_layout(
            mapbox=dict(
                style='carto-darkmatter', zoom=4.8,
                center=dict(lat=40.0, lon=-3.5)
            ),
            paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=280
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PESTAÑA 4: SCOUT IA (PLANTILLA COMPLETA DEL EQUIPO REPLICADA)
# ------------------------------------------------------------------------------
with tab_scout:
    # Encabezado del Partido
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:2px solid #1d73e8; margin-bottom:20px;">
            <span style="font-size:15px; font-weight:700;">Mallorca</span>
            <span style="font-size:12px; color:#8fa0b5;">🏆 La Liga | 📅 2026-08-18 19:30 <b style="color:#ffffff; margin-left:15px;">VS</b></span>
            <span style="font-size:15px; font-weight:700; text-align:right;">Real Madrid</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👥 PLANTILLA DEL EQUIPO</div>', unsafe_allow_html=True)
    
    # Tabla estructurada en HTML limpio para calcar la captura
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

# ==============================================================================
# PIE DE PÁGINA OFICIAL REPLICADO EXACTAMENTE DE LA IMAGEN
# ==============================================================================
st.markdown("""
    <div class="custom-footer">
        <b>Forza Football Analytics V3.0 (Integración AI)</b><br>
        Plataforma Avanzada de Datos Deportivos<br>
        Proyecto Universitario | Desarrollado por Salomón Achar © 2026
    </div>
""", unsafe_allow_html=True)
