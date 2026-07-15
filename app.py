import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random 

# =========================================================================
# CONFIGURACIÓN ESTÉTICA ESTILO ESPN (Rojo, Negro, Blanco, Gris)
# =========================================================================
st.set_page_config(page_title="Forza Fútbol Dashboard", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-color: #F4F4F4 !important;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        }
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #000000 !important;
        }
        button[data-baseweb="tab"] { color: #000000 !important; }
        button[data-baseweb="tab"] p {
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.05rem !important;
            text-transform: uppercase !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            color: #000000 !important;
            background-color: #ffffff !important;
            border-radius: 4px !important;
            border: 1px solid #cccccc !important;
        }
        .premium-card {
            background-color: #ffffff !important;
            padding: 24px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border-top: 4px solid #CC0000;
        }
        .section-title {
            color: #000000 !important;
            font-size: 1.3rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }
        .live-team-name {
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.15rem !important;
            text-transform: uppercase;
        }
        .live-score {
            color: #CC0000 !important;
            font-weight: 900 !important;
            font-size: 1.4rem !important;
            margin: 0 15px !important;
        }
        .live-league-label {
            color: #666666 !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='margin-bottom: 30px; border-bottom: 4px solid #000000; padding-bottom: 10px;'>
        <h1 style='color: #CC0000 !important; font-size: 2.8rem; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 0px;'>⚽ FORZA FÚTBOL</h1>
        <p style='color: #000000 !important; font-size: 1rem; font-weight: 700; text-transform: uppercase;'>Líder Mundial en Deportes | Centro de Estadísticas</p>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# FUNCIONES MODULARES DE INTERFAZ (UI) CON VALIDACIÓN DE LOGOS
# =========================================================================
def validar_logo(url):
    if url and str(url).startswith('http'):
        return url
    return "https://cdn-icons-png.flaticon.com/512/825/825588.png"

def dibujar_cabecera_equipo(nombre, logo, pais):
    html = f"""
    <div style="display: flex; align-items: center; padding: 25px; background-color: #ffffff; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 25px; border-top: 4px solid #CC0000;">
        <div style="flex-shrink: 0; margin-right: 30px; background: #F4F4F4; padding: 15px; border-radius: 50%; width: 110px; height: 110px; display: flex; justify-content: center; align-items: center; border: 1px solid #E5E5E5;">
            <img src="{validar_logo(logo)}" style="max-width: 80px; max-height: 80px; object-fit: contain;">
        </div>
        <div style="flex-grow: 1;">
            <p style="font-size: 0.85rem; margin:0; font-weight: 800; text-transform: uppercase; color: #666666 !important;">PERFIL DEL CLUB</p>
            <h1 style="margin: 0; color: #000000 !important; font-size: 2.8rem; font-weight: 900; letter-spacing: -1px; text-transform: uppercase;">
                {nombre}
            </h1>
            <div style="margin-top: 10px; display: flex; gap: 15px; flex-wrap: wrap;">
                <span style="background-color: #CC0000; color: #ffffff !important; padding: 6px 12px; border-radius: 3px; font-size: 0.85rem; font-weight: 800; text-transform: uppercase;">
                    📍 {pais}
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dibujar_tarjeta_previo(row):
    logo_l = validar_logo(row.get('Logo Local'))
    logo_v = validar_logo(row.get('Logo Visita'))
    html = f"""
    <div style='padding: 14px 0; border-bottom: 1px solid #E5E5E5;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <span style='font-weight: 800; display: flex; align-items: center; font-size: 1.05rem;'>
                <img src="{logo_l}" width="28" height="28" style="margin-right: 8px; object-fit: contain;"> {row['Local']} 
                <span style='margin: 0 8px; color: #999999; font-weight: 500;'>vs</span> 
                {row['Visita']} <img src="{logo_v}" width="28" height="28" style="margin-left: 8px; object-fit: contain;">
            </span>
            <span style='font-weight: 900; color: #CC0000 !important; font-size: 1.2rem;'>{int(row['Goles Local'])} - {int(row['Goles Visita'])}</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin-top: 6px;'>
            <span style='font-size: 0.75rem; font-weight: 800; color: #666666 !important; text-transform: uppercase;'>🏆 {row['Competencia']}</span>
            <span style='font-size: 0.75rem; font-weight: 700; color: #999999 !important;'>📅 {row['Fecha']}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dibujar_tarjeta_proximo(row):
    logo_l = validar_logo(row.get('Logo Local'))
    logo_v = validar_logo(row.get('Logo Visita'))
    html = f"""
    <div style='padding: 14px 0; border-bottom: 1px solid #E5E5E5;'>
        <div style='font-weight: 800; display: flex; align-items: center; font-size: 1.05rem;'>
            <img src="{logo_l}" width="28" height="28" style="margin-right: 8px; object-fit: contain;"> {row['Local']} 
            <span style='margin: 0 8px; color: #999999; font-weight: 500;'>vs</span> 
            {row['Visita']} <img src="{logo_v}" width="28" height="28" style="margin-left: 8px; object-fit: contain;">
        </div>
        <div style='display: flex; justify-content: space-between; margin-top: 6px;'>
            <span style='font-size: 0.75rem; font-weight: 800; color: #666666 !important; text-transform: uppercase;'>🏆 {row['Competencia']}</span>
            <span style='font-size: 0.75rem; color: #CC0000 !important; font-weight: 800;'>📅 {row['Fecha']}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def dibujar_tarjeta_en_vivo(row):
    logo_l = validar_logo(row.get('Logo L'))
    logo_v = validar_logo(row.get('Logo V'))
    html = f"""
    <div style='padding: 18px; background-color: #ffffff; border-radius: 4px; margin-bottom: 14px; border: 1px solid #E5E5E5; border-left: 4px solid #CC0000;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='display: flex; align-items: center;'>
                <img src="{logo_l}" width="32" height="32" style="margin-right: 12px; object-fit: contain;">
                <span class='live-team-name'>{row['Local']}</span>
                <span class='live-score'>{row['Goles L']} - {row['Goles V']}</span>
                <span class='live-team-name'>{row['Visita']}</span>
                <img src="{logo_v}" width="32" height="32" style="margin-left: 12px; object-fit: contain;">
            </div>
            <div style='text-align: right;'>
                <span style='background-color: #CC0000; color: #ffffff !important; padding: 4px 12px; border-radius: 2px; font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px;'>⏱️ {row['Minuto']}'</span>
                <div class='live-league-label' style='margin-top: 8px;'>🏆 {row['Liga']}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# =========================================================================
# CONFIGURACIÓN DE LA API Y RESPALDO
# =========================================================================
API_KEY = "acb867b68f5987d9c226e48c12c090e3"
HEADERS = {'x-apisports-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

st.sidebar.markdown("### 🔄 Control de Datos")
if st.sidebar.button("Forzar Sincronización"):
    st.cache_data.clear()

def generar_respaldo_dinamico(nombre_equipo, pais_equipo):
    pais_normalizado = str(pais_equipo).strip().lower()
    random.seed(nombre_equipo)
    competencia = "Liga Profesional"
    rivales = ["Club A", "Club B", "Club C", "Club D", "Club E"]
    partidos = []
    for i in range(4):
        partidos.append({"Fecha": "2026-07-10", "Competencia": competencia, "Local": rivales[i], "Logo Local": "", "Goles Local": random.randint(0,4), "Goles Visita": random.randint(0,3), "Visita": nombre_equipo, "Logo Visita": "", "Estado": "FT"})
    return partidos

@st.cache_data(ttl=300, show_spinner=False)
def obtener_calendario_equipo(id_equipo, nombre_equipo, pais_equipo):
    return generar_respaldo_dinamico(nombre_equipo, pais_equipo), "local_respaldo"

# [RESTO DE TU LÓGICA DE APP...]
# Asegúrate de mantener tus llamadas a las funciones:
# dibujar_tarjeta_previo(row), dibujar_tarjeta_proximo(row), etc.
