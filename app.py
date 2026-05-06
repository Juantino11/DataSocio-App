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

# CSS para Posicionamiento Fijo y Estética Profesional
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    :root {
        --primary-bg: #0f172a;
        --accent: #38bdf8;
        --success: #10b981;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--primary-bg); }

    /* BOTÓN SALIR FIJO EN LA ESQUINA SUPERIOR IZQUIERDA */
    .fixed-logout {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
    }

    /* Estilo de Tarjetas de Inicio (Prólogo) */
    .hero-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 3rem 2rem; border-radius: 24px; border: 2px solid #334155;
        text-align: center; margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #1e293b; padding: 1.5rem; border-radius: 15px;
        border: 1px solid #334155; text-align: center; height: 100%;
    }

    /* Botón PRO con contraste mejorado */
    .pay-link {
        display: block; padding: 12px; background: var(--success);
        color: #000000 !important; text-decoration: none; border-radius: 10px;
        text-align: center; font-weight: 800; border: 2px solid #ffffff;
    }

    .result-card {
        background: #1e293b; padding: 1.5rem; border-radius: 16px;
        border-left: 8px solid var(--accent); margin-bottom: 1rem;
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

# --- BOTÓN DE SALIDA (POSICIÓN FIJA) ---
if st.session_state.logged_in:
    st.markdown('<div class="fixed-logout">', unsafe_allow_html=True)
    if st.button("⬅️ SALIR"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA DE INICIO (PRÓLOGO + ACCESO) ---
if not st.session_state.logged_in:
    # 1. PRÓLOGO
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8; font-size: 3rem;'>DataSocio Intelligence OS</h1>
            <p style='color: #cbd5e1; font-size: 1.2rem;'>Comando central para la extracción de leads y análisis de mercado.</p>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="feature-card"><h3>🔍 Extracción</h3><p>Emails y teléfonos en segundos.</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="feature-card"><h3>🧠 Análisis</h3><p>IA de reputación y sentimiento.</p></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="feature-card"><h3>📊 Reportes</h3><p>Exportación profesional a XLSX.</p></div>', unsafe_allow_html=True)

    st.write("---")

    # 2. ACCESO
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        mode = st.radio("Acción:", ["Ingresar", "Registrarse"], horizontal=True)
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("🚀 ACCEDER AL SISTEMA"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Credenciales incorrectas.")
    st.stop()

# --- INTERFAZ OPERATIVA ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.user_now}")
    st.metric("TUS CRÉDITOS", user_rec['credits'])
    st.write("---")
    st.markdown("### 🚀 Subir de Nivel")
    st.markdown('<a href="#" class="pay-link">💳 SUSCRIBIRSE PRO</a>', unsafe_allow_html=True)

st.markdown("<h1 style='color: #38bdf8; margin-top: 50px;'>🛠️ Consola de Inteligencia</h1>", unsafe_allow_html=True)

with st.expander("📥 CONFIGURAR OBJETIVOS", expanded=True):
    urls_input = st.text_area("Pega aquí las URLs de los sitios a investigar:", height=120)
    if st.button("⚡ INICIAR EXTRACCIÓN"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        if urls and len(urls) <= user_rec['credits']:
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
            st.rerun()
        elif not urls: st.warning("⚠️ URLs inválidas.")
        else: st.error("❌ Créditos insuficientes.")

if 'last_run' in st.session_state:
    st.write("### 💎 Hallazgos")
    for r in st.session_state.last_run:
        st.markdown(f"""
            <div class="result-card">
                <h4>🔗 {r['url']}</h4>
                <p>📧 {', '.join(r['emails']) if r['emails'] else 'No hay emails'}</p>
                <p>📞 {', '.join(r['tels']) if r['tels'] else 'No hay teléfonos'}</p>
            </div>
        """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v9.3 | Windows 11 i5 | Paso del Rey")
