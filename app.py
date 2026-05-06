import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import hashlib
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="DataSocio OS | Intelligence Suite", page_icon="🌐", layout="wide")

# CSS para un look de plataforma SaaS Profesional
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .main-card {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #38bdf8, #1d4ed8);
        color: white; border: none; padding: 0.75rem; border-radius: 8px;
        font-weight: bold; width: 100%; transition: all 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
db = TinyDB('usuarios_db.json')
User = Query()

def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

# --- LÓGICA DE SESIÓN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_now = None

# --- AUTH UI ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.title("🌐 DataSocio OS")
        st.write("Bienvenido a la suite de inteligencia de datos.")
        mode = st.radio("Acceso", ["Ingresar", "Registrarse"], horizontal=True)
        
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        
        if mode == "Ingresar" and st.button("Acceder al Sistema"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Acceso denegado")
        
        if mode == "Registrarse" and st.button("Crear Nueva Cuenta"):
            if not db.search(User.username == u):
                db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                st.success("Cuenta creada. Ya puedes ingresar.")
            else: st.error("El usuario ya existe")
    st.stop()

# --- PANEL DE CONTROL (LOGUEADO) ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title(st.session_state.user_now)
    st.metric("CRÉDITOS", user_rec['credits'])
    
    st.write("---")
    st.write("💎 **UPGRADE PLAN**")
    if st.button("Cargar 500 Créditos"):
        db.update({'credits': user_rec['credits'] + 500}, User.username == st.session_state.user_now)
        st.rerun()
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# --- INTERFAZ OPERATIVA ---
st.title("🚀 Intelligence Console")
st.write("Sustracción y análisis de activos en tiempo real.")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    urls_input = st.text_area("📋 Inserte objetivos (URLs separadas por línea):", height=150, help="El sistema procesará cada enlace de forma individual.")
    
    c1, c2, c3 = st.columns(3)
    with c1: deep_scan = st.checkbox("Escaneo Profundo (Emails/Tels)", value=True)
    with c2: social_scan = st.checkbox("Rastreo de Redes", value=True)
    with c3: sentiment_analysis = st.checkbox("Análisis de Sentimiento", value=True)
    
    if st.button("⚡ INICIAR OPERACIÓN DE EXTRACCIÓN"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        
        if not urls:
            st.warning("Ingrese al menos una URL válida.")
        elif len(urls) > user_rec['credits']:
            st.error("Créditos insuficientes.")
        else:
            final_results = []
            progress_bar = st.progress(0)
            
            for i, url in enumerate(urls):
                try:
                    db.update({'credits': user_rec['credits'] - 1}, User.username == st.session_state.user_now)
                    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    text = soup.get_text()
                    
                    # Inteligencia de Datos
                    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                    tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                    
                    # Análisis de Sentimiento Básico (Detección de Palabras Clave)
                    score = "Neutral"
                    if sentiment_analysis:
                        pos = ['excelente', 'mejor', 'increíble', 'servicio', 'calidad', 'garantía']
                        neg = ['malo', 'pobre', 'error', 'falla', 'queja', 'caro']
                        p_count = sum(1 for w in pos if w in text.lower())
                        n_count = sum(1 for w in neg if w in text.lower())
                        if p_count > n_count: score = "Positivo"
                        elif n_count > p_count: score = "Negativo"

                    final_results.append({
                        "Objetivo": url,
                        "Emails": ", ".join(emails[:3]),
                        "Teléfonos": ", ".join(tels[:3]),
                        "Sentimiento": score,
                        "Status": "Completado"
                    })
                    progress_bar.progress((i+1)/len(urls))
                except:
                    final_results.append({"Objetivo": url, "Status": "Fallo de conexión"})

            st.success("Operación finalizada.")
            df = pd.DataFrame(final_results)
            st.table(df) # Presentación más limpia
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Exportar Inteligencia (CSV)", csv, "intelligence_report.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")
st.caption(f"DataSocio Engine v7.0 | {st.session_state.user_now} | i5 Win11 Node")
