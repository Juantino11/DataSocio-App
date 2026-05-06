import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import hashlib
from io import BytesIO
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DataSocio OS | Intelligence", page_icon="⚡", layout="wide")

# CSS Refinado para Legibilidad y Flujo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    :root { --primary-bg: #0f172a; --accent: #38bdf8; --success: #10b981; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--primary-bg); }

    .fixed-logout { position: fixed; top: 20px; left: 20px; z-index: 9999; }
    
    .hero-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 3rem 2rem; border-radius: 24px; border: 2px solid #334155;
        text-align: center; margin-bottom: 2rem;
    }
    
    .how-it-works {
        background: rgba(56, 189, 248, 0.05);
        padding: 2rem; border-radius: 20px; border: 1px dashed var(--accent);
        margin: 2rem 0;
    }

    .step-card {
        background: #1e293b; padding: 1.5rem; border-radius: 15px;
        border-top: 4px solid var(--accent); text-align: center; height: 100%;
    }

    .pay-link {
        display: block; padding: 12px; background: var(--success);
        color: #000000 !important; text-decoration: none; border-radius: 10px;
        text-align: center; font-weight: 800; border: 2px solid #ffffff;
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

# --- FIX LOGIN: Botón de salida ---
if st.session_state.logged_in:
    st.markdown('<div class="fixed-logout">', unsafe_allow_html=True)
    if st.button("⬅️ SALIR"):
        st.session_state.logged_in = False
        st.session_state.user_now = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA DE INICIO (PRÓLOGO + CÓMO FUNCIONA) ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8; font-size: 3rem;'>DataSocio Intelligence OS</h1>
            <p style='color: #cbd5e1; font-size: 1.2rem;'>Extracción masiva de datos y análisis de reputación en tiempo real.</p>
        </div>
    """, unsafe_allow_html=True)

    # SECCIÓN: CÓMO FUNCIONA
    st.markdown("<h2 style='text-align:center; color:white;'>⚙️ ¿Cómo funciona el sistema?</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="step-card">
            <h3>1. Inyección</h3>
            <p>Ingresas las URLs de los negocios o directorios que te interesan.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="step-card">
            <h3>2. Rastreo Profundo</h3>
            <p>Nuestro motor analiza el código HTML buscando patrones de emails y teléfonos válidos.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="step-card">
            <h3>3. Inteligencia</h3>
            <p>La IA clasifica el sentimiento del sitio para darte una idea de su reputación comercial.</p>
        </div>""", unsafe_allow_html=True)

    st.write("---")

    # PANEL DE ACCESO
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h3 style='text-align:center; color:white;'>🔐 Acceso</h3>", unsafe_allow_html=True)
        mode = st.radio("Acción:", ["Ingresar", "Registrarse"], horizontal=True)
        u = st.text_input("Usuario").strip()
        p = st.text_input("Contraseña", type="password").strip()
        
        if mode == "Ingresar" and st.button("🚀 ENTRAR"):
            # Buscamos al usuario de forma explícita
            res = db.search(User.username == u)
            if res:
                if res[0]['password'] == hash_p(p):
                    st.session_state.logged_in = True
                    st.session_state.user_now = u
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.error("❌ El usuario no existe.")
        
        if mode == "Registrarse" and st.button("📝 CREAR CUENTA"):
            if u and p:
                if not db.search(User.username == u):
                    db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                    st.success("✅ ¡Cuenta creada! Ahora selecciona 'Ingresar'.")
                else:
                    st.error("⚠️ Este usuario ya está en nuestra red.")
            else:
                st.warning("⚠️ Completa los campos.")
    st.stop()

# --- INTERFAZ OPERATIVA ---
# Recuperar datos frescos del usuario
user_data = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.markdown(f"## 👤 {st.session_state.user_now}")
    st.metric("CRÉDITOS", user_data['credits'])
    st.write("---")
    st.markdown("### 💎 Plan Suscriptor")
    st.markdown('<a href="#" class="pay-link">💳 OBTENER MÁS</a>', unsafe_allow_html=True)

st.markdown("<h1 style='color: #38bdf8; margin-top: 40px;'>🛠️ Consola Operativa</h1>", unsafe_allow_html=True)

# Lógica de extracción (igual a la anterior pero verificando créditos antes de cada loop)
with st.container():
    urls_input = st.text_area("📋 Lista de URLs:", height=100, placeholder="https://ejemplo.com")
    if st.button("⚡ EJECUTAR"):
        urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
        if urls:
            results = []
            bar = st.progress(0)
            for i, url in enumerate(urls):
                # Verificación de crédito en tiempo real
                current_user = db.search(User.username == st.session_state.user_now)[0]
                if current_user['credits'] > 0:
                    try:
                        db.update({'credits': current_user['credits'] - 1}, User.username == st.session_state.user_now)
                        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=7)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        text = soup.get_text()
                        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                        tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                        results.append({"url": url, "emails": emails, "tels": tels})
                    except:
                        results.append({"url": url, "emails": [], "tels": []})
                else:
                    st.error("Sin créditos.")
                    break
                bar.progress((i+1)/len(urls))
            st.session_state.last_run = results
            st.rerun()

# Mostrar hallazgos
if 'last_run' in st.session_state:
    for r in st.session_state.last_run:
        st.markdown(f"""<div style='background:#1e293b; padding:15px; border-radius:10px; border-left:5px solid #38bdf8; margin-bottom:10px;'>
            <strong>🔗 {r['url']}</strong><br>
            📧 {', '.join(r['emails']) if r['emails'] else 'N/A'} | 📞 {', '.join(r['tels']) if r['tels'] else 'N/A'}
        </div>""", unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v9.4 | Paso del Rey | Win11 i5")
