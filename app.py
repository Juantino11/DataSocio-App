import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
from io import BytesIO
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DataSocio OS | Elite Intelligence", page_icon="⚡", layout="wide")

# CSS para Contraste Máximo y Ubicación de Salida
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    :root {
        --primary-bg: #0f172a;
        --card-bg: #1e293b;
        --text-main: #ffffff;
        --accent: #38bdf8;
        --success: #10b981;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--primary-bg); color: var(--text-main); }
    
    /* Botón Cerrar Sesión (Superior Izquierda) */
    .st-emotion-cache-1av5p16 { 
        position: fixed; top: 10px; left: 10px; z-index: 1000;
    }

    /* Estilo de Tarjetas de Inicio */
    .hero-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 3rem 2rem; border-radius: 24px; border: 2px solid #334155;
        text-align: center; margin-bottom: 2rem;
    }
    
    h1, h2, h3 { color: var(--accent) !important; font-weight: 800 !important; }

    /* Botón PRO con contraste mejorado */
    .pay-link {
        display: block; padding: 15px; background: var(--success);
        color: #000000 !important; text-decoration: none; border-radius: 12px;
        text-align: center; font-weight: 900; font-size: 1.1rem;
        border: 2px solid #ffffff; margin-top: 10px;
    }
    .pay-link:hover { background: #059669; transform: scale(1.02); transition: 0.2s; }

    /* Tarjetas de Resultados */
    .result-card {
        background: #1e293b; padding: 1.5rem; border-radius: 16px;
        border: 1px solid #334155; border-left: 8px solid var(--accent);
        margin-bottom: 1rem;
    }
    
    .data-badge {
        background: #0ea5e9; color: white; padding: 4px 12px;
        border-radius: 20px; font-weight: bold; font-size: 0.85rem;
        margin-right: 8px; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
db = TinyDB('usuarios_db.json')
User = Query()
def hash_p(password): return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_now = None

# --- SALIDA EN ESQUINA SUPERIOR IZQUIERDA ---
if st.session_state.logged_in:
    st.sidebar.markdown("""<style> [data-testid="stSidebarNav"] {display: none;} </style>""", unsafe_allow_html=True)
    with st.container():
        col_exit, _ = st.columns([1, 8])
        with col_exit:
            if st.button("⬅️ SALIR"):
                st.session_state.logged_in = False
                st.rerun()

# --- PANTALLA DE INICIO ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-section">
            <h1>DataSocio Intelligence OS</h1>
            <p style="color: #cbd5e1;">Comando central de extracción y análisis de prospectos.</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_auth, _ = st.columns([1, 1.3, 1])
    with col_auth:
        mode = st.radio("Acción:", ["Ingresar", "Registrarse"], horizontal=True)
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("ACCEDER AHORA"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Error en credenciales.")
    st.stop()

# --- PANEL OPERATIVO ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.user_now}")
    st.markdown(f"**Créditos:** `{user_rec['credits']}`")
    st.write("---")
    st.markdown("### 🚀 Subir de Nivel")
    st.write("Obtené escaneos ilimitados.")
    # Botón con contraste mejorado (Texto negro sobre fondo verde brillante)
    st.markdown('<a href="#" class="pay-link">💳 SUSCRIBIRSE PRO</a>', unsafe_allow_html=True)

st.title("🛠️ Consola de Inteligencia")
urls_input = st.text_area("📋 URLs a investigar:", height=100)

if st.button("⚡ INICIAR EXTRACCIÓN"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    if not urls:
        st.warning("⚠️ URLs inválidas.")
    elif len(urls) > user_rec['credits']:
        st.error("❌ Créditos insuficientes.")
    else:
        results = []
        bar = st.progress(0)
        for i, url in enumerate(urls):
            try:
                db.update({'credits': user_rec['credits'] - 1}, User.username == st.session_state.user_now)
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                results.append({"url": url, "emails": emails, "tels": tels, "status": "⭐ Positivo" if "excelente" in text.lower() else "⚖️ Neutral"})
                bar.progress((i+1)/len(urls))
            except:
                results.append({"url": url, "emails": [], "tels": [], "status": "❌ Error"})
        st.session_state.last_run = results

if 'last_run' in st.session_state:
    for r in st.session_state.last_run:
        st.markdown(f"""
            <div class="result-card">
                <h4 style="margin:0;">🔗 {r['url']}</h4>
                <div style="margin-top:10px;">
                    <span class="data-badge">📧 {len(r['emails'])} Emails</span>
                    <span class="data-badge">📞 {len(r['tels'])} Teléfonos</span>
                    <span class="data-badge" style="background:#475569;">🛡️ {r['status']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio v9.2 | UX Refined | Win11 i5")
