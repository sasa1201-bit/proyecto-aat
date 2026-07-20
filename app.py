import os
import streamlit as st
import pandas as pd
import numpy as np
import httpx
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Try importing streamlit_folium and folium for the map component
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Forza Football Analytics V3.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CUSTOM CSS - PREMIUM DARK NAVY DESIGN SPEC
# ==========================================
st.markdown("""
<style>
    /* Global Styles & Dark Navy Theme */
    .stApp {
        background-color: #0a0e1a;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide default streamlit header / footer elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Container styling with rounded borders */
    .custom-container {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Metric / KPI card styling */
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
    
    /* Live match score badge container */
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
    
    /* Recent results item with green side bar */
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
    
    /* Footer styling */
    .app-footer {
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        padding: 30px 0;
        border-top: 1px solid #1e293b;
        margin-top: 40px;
    }
    
    /* Tabs styling override */
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
    
    /* DataFrame / Tables styling */
    dataframe, table {
        background-color: #131b2e !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# API CONFIGURATION & HELPERS
# ==========================================
API_BASE = "https://api.thestatsapi.com/api"
API_KEY = os.getenv("THESTATSAPI_KEY", "")

def get_headers():
    return {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

@st.cache_data(ttl=300)
def fetch_from_api(endpoint: str, params: dict = None):
    if not API_KEY:
        return None
    url = f"{API_BASE}{endpoint}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=get_headers(), params=params)
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None

# ==========================================
# FALLBACK DUMMY DATA STRUCTURES
# ==========================================
DUMMY_STANDINGS = pd.DataFrame([
    {"Position": 1, "Team": "Real Madrid", "P": 22, "W": 17, "D": 4, "L": 1, "GF": 52, "GA": 14, "Pts": 55},
    {"Position": 2, "Team": "Barcelona", "P": 22, "W": 15, "D": 5, "L": 2, "GF": 48, "GA": 20, "Pts": 50},
    {"Position": 3, "Team": "Atletico Madrid", "P": 22, "W": 13, "D": 6, "L": 3, "GF": 41, "GA": 22, "Pts": 45},
    {"Position": 4, "Team": "Athletic Club", "P": 22, "W": 12, "D": 5, "L": 5, "GF": 36, "GA": 21, "Pts": 41},
    {"Position": 5, "Team": "Real Sociedad", "P": 22, "W": 10, "D": 7, "L": 5, "GF": 32, "GA": 24, "Pts": 37},
])

DUMMY_FIXTURES = [
    {"date": "2026-03-01 20:00", "home": "Real Madrid", "away": "Athletic Club", "status": "Scheduled"},
    {"date": "2026-03-02 18:30", "home": "Barcelona", "away": "Real Sociedad", "status": "Scheduled"},
    {"date": "2026-03-02 21:00", "home": "Atletico Madrid", "away": "Valencia", "status": "Scheduled"},
]

DUMMY_SQUAD = pd.DataFrame([
    {"Jersey": 1, "Name": "Thibaut Courtois", "Age": 33, "Position": "Goalkeeper"},
    {"Jersey": 2, "Name": "Dani Carvajal", "Age": 34, "Position": "Defender"},
    {"Jersey": 3, "Name": "Éder Militão", "Age": 28, "Position": "Defender"},
    {"Jersey": 4, "Name": "David Alaba", "Age": 33, "Position": "Defender"},
    {"Jersey": 5, "Name": "Jude Bellingham", "Age": 22, "Position": "Midfielder"},
    {"Jersey": 7, "Name": "Vinícius Júnior", "Age": 25, "Position": "Forward"},
    {"Jersey": 8, "Name": "Federico Valverde", "Age": 27, "Position": "Midfielder"},
    {"Jersey": 9, "Name": "Kylian Mbappé", "Age": 27, "Position": "Forward"},
    {"Jersey": 10, "Name": "Luka Modrić", "Age": 40, "Position": "Midfielder"},
    {"Jersey": 11, "Name": "Rodrygo Goes", "Age": 25, "Position": "Forward"},
    {"Jersey": 14, "Name": "Aurélien Tchouaméni", "Age": 26, "Position": "Midfielder"},
])

DUMMY_RECENT_RESULTS = [
    {"match": "Real Madrid 3 - 1 Villarreal", "date": "Feb 24, 2026", "result": "WIN"},
    {"match": "Real Madrid 2 - 0 Sevilla", "date": "Feb 18, 2026", "result": "WIN"},
    {"match": "Real Madrid 1 - 1 Atletico Madrid", "date": "Feb 12, 2026", "result": "DRAW"},
    {"match": "Real Madrid 4 - 2 Las Palmas", "date": "Feb 05, 2026", "result": "WIN"},
]

# ==========================================
# APP HEADER & API CHECK BANNER
# ==========================================
st.markdown("<h1 style='text-align: center; color: #f8fafc; margin-bottom: 0;'>⚽ FORZA FOOTBALL ANALYTICS V3.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-top: 5px;'>AI Integration & Advanced Sports Data Platform</p>", unsafe_allow_html=True)

if not API_KEY:
    st.info("ℹ️ **THESTATSAPI_KEY environment variable not detected.** Operating with full simulated production data fallback. To connect live feeds, set your API key.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# TABS SETUP
# ==========================================
tab_main, tab_live, tab_analytics, tab_scout = st.tabs([
    "📊 Main Panel", 
    "⚡ Live Center", 
    "📈 Advanced Analytics", 
    "🤖 AI Scout"
])

# ==========================================
# TAB 1: MAIN PANEL
# ==========================================
with tab_main:
    st.markdown("### League Overview & Standings")
    
    # Try fetching real competitions if API key exists
    comps_data = fetch_from_api("/football/competitions")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("La Liga Standings (2025/26)")
        
        # Attempt to pull real standings for La Liga (comp_3039 or first available)
        standings_df = DUMMY_STANDINGS
        if comps_data and isinstance(comps_data, dict) and "data" in comps_data:
            # Look for a valid competition or season if possible, otherwise use fallback
            pass
            
        st.dataframe(standings_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Upcoming Fixtures")
        for f in DUMMY_FIXTURES:
            st.markdown(f"""
            <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #1e293b;">
                <div style="font-size: 0.75rem; color: #94a3b8;">{f['date']}</div>
                <div style="font-weight: 600; font-size: 0.95rem; margin-top: 4px;">{f['home']} vs {f['away']}</div>
                <div style="font-size: 0.75rem; color: #3b82f6; margin-top: 2px;">{f['status']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: LIVE CENTER
# ==========================================
with tab_live:
    st.markdown("### Live Match Center")
    
    # Required simulated live match row: Real Madrid vs Barcelona, score 2-1, 74th minute
    st.markdown("""
    <div class="live-match-box">
        <div class="live-badge">🔴 LIVE • 74'</div>
        <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 15px;">
            <div style="text-align: right; flex: 1;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #f8fafc;">Real Madrid</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Santiago Bernabéu</div>
            </div>
            <div style="padding: 0 25px; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800; color: #3b82f6; letter-spacing: 2px;">2 - 1</div>
                <div style="font-size: 0.75rem; color: #22c55e; font-weight: 600;">HT 1-0</div>
            </div>
            <div style="text-align: left; flex: 1;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #f8fafc;">Barcelona</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Visitors</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("In-Play Match Statistics")
        
        stats_data = [
            ("Ball Possession", "54%", "46%"),
            ("Total Shots", "14", "11"),
            ("Shots on Target", "6", "4"),
            ("Corner Kicks", "5", "3"),
            ("Yellow Cards", "2", "3"),
            ("Fouls", "10", "12")
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
        st.subheader("Live Match Timeline")
        
        timeline_events = [
            ("71'", "Goal!", "Barcelona (L. Yamal)", "⚽"),
            ("55'", "Goal!", "Real Madrid (K. Mbappé)", "⚽"),
            ("46'", "Substitution", "Real Madrid (L. Modrić ON)", "🔄"),
            ("HT", "Half Time", "Score: 1 - 0", "⏱️"),
            ("28'", "Goal!", "Real Madrid (J. Bellingham)", "⚽"),
            ("14'", "Yellow Card", "Barcelona (Gavi)", "🟨")
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
# TAB 3: ADVANCED ANALYTICS
# ==========================================
with tab_analytics:
    st.markdown("### Club Advanced Analytics & Deep Dive")
    
    # 4 KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Club Profile</div>
            <div class="metric-value" style="font-size: 1.2rem; color: #3b82f6;">Real Madrid CF</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">La Liga • Spain</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Effectiveness %</div>
            <div class="metric-value">77.3%</div>
            <div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">+4.2% vs league avg</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Avg Goals / Match</div>
            <div class="metric-value">2.36</div>
            <div style="font-size: 0.75rem; color: #3b82f6; margin-top: 4px;">52 GF in 22 matches</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">W / D / L Record</div>
            <div class="metric-value" style="font-size: 1.3rem;">17 - 4 - 1</div>
            <div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">86% unbeaten rate</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row for Recent Results & Calendar
    col_a1, col_a2 = st.columns([1, 1])
    
    with col_a1:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Recent Results")
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
        st.subheader("Match Schedule & Calendar")
        selected_date = st.date_input("Highlight Match Date", value=datetime.today().date())
        st.markdown(f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #1e293b; margin-top: 15px;">
            <div style="font-size: 0.85rem; color: #3b82f6; font-weight: 600;">Selected Date Focus: {selected_date.strftime('%B %d, %Y')}</div>
            <div style="font-size: 0.9rem; color: #f8fafc; margin-top: 8px;">No official fixture scheduled directly on this date. Next match window opens in 4 days.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Squad Table
    st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
    st.subheader("Team Squad Roster")
    st.dataframe(DUMMY_SQUAD, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Radar Chart & Map section
    col_a3, col_a4 = st.columns(2)
    
    with col_a3:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Performance Radar Profile")
        
        categories = ['Goal Power', 'Effectiveness', 'Volume', 'Consistency', 'Defensive Solidity']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[92, 85, 88, 90, 84],
            theta=categories,
            fill='toself',
            name='Real Madrid',
            line_color='#3b82f6',
            fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        fig_radar.update_polar(
            bgcolor='#0f172a',
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='#1e293b', linecolor='#1e293b'),
            angularaxis=dict(gridcolor='#1e293b', linecolor='#1e293b')
        )
        fig_radar.update_layout(
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
        st.subheader("Club Region (Madrid, Spain)")
        
        if FOLIUM_AVAILABLE:
            m = folium.Map(location=[40.4168, -3.7038], zoom_start=12, tiles="CartoDB dark_matter")
            folium.Marker(
                [40.4168, -3.7038],
                popup="Santiago Bernabéu Stadium",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            st_folium(m, height=320, use_container_width=True)
        else:
            # Fallback Map using Plotly Scatter Mapbox or Scattergeo if folium missing
            map_df = pd.DataFrame({'lat': [40.4168], 'lon': [-3.7038], 'name': ['Santiago Bernabéu']})
            fig_map = px.scatter_mapbox(map_df, lat='lat', lon='lon', text='name', zoom=11, height=320)
            fig_map.update_layout(
                mapbox_style="carto-darkmatter",
                paper_bgcolor='#131b2e',
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Bar chart and Area chart section
    col_a5, col_a6 = st.columns(2)
    
    with col_a5:
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        st.subheader("Match Volume by League")
        league_data = pd.DataFrame({
            'League': ['La Liga', 'UEFA Champions League', 'Copa del Rey', 'Supercopa'],
            'Matches': [22, 8, 4, 2]
        })
        fig_bar = px.bar(league_data, x='League', y='Matches', color='Matches', color_continuous_scale='Blues')
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
        st.subheader("Total Goals by Competition (Reddish Tones)")
        goal_data = pd.DataFrame({
            'Competition': ['La Liga', 'UCL', 'Copa del Rey', 'Supercopa'],
            'Goals': [52, 18, 9, 5]
        })
        fig_area = px.area(goal_data, x='Competition', y='Goals', markers=True)
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
# TAB 4: AI SCOUT
# ==========================================
with tab_scout:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #131b2e 0%, #0f172a 100%); border: 1px solid #1e293b; border-radius: 16px; padding: 40px; text-align: center; max-width: 700px; margin: 0 auto; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);">
        <div style="font-size: 3rem; margin-bottom: 15px;">🤖⚽</div>
        <h2 style="color: #f8fafc; font-weight: 700; margin-bottom: 15px;">AI Scout — Coming Soon</h2>
        <p style="color: #94a3b8; font-size: 1.05rem; line-height: 1.6; margin-bottom: 25px;">
            Advanced player discovery and match intelligence module under development. Powered by generative AI models and real-time telemetry from TheStatsAPI feed vectors.
        </p>
        <div style="display: inline-block; background-color: #1e293b; color: #3b82f6; padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
            Module Release: Q3 2026
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# FOOTER SPECIFICATION
# ==========================================
st.markdown("""
<div class="app-footer">
    Forza Football Analytics V3.0 AI Integration, Advanced Sports Data Platform, University Project, Developed by Salomón Achar © 2026
</div>
""", unsafe_allow_html=True)
