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

# CSS para integrar el botón en la Sidebar y mejorar el look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    :root { --primary-bg: #0f172a; --accent: #38bdf8; --success: #10b981; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--primary-bg); }

    /* Estilo del Prólogo (Mantenemos como pediste) */
    .hero-section {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 3rem 2rem; border-radius: 24px; border: 2px solid #334155;
        text-align: center; margin-bottom: 2rem;
    }
    .step-card {
        background: #1e293b; padding: 1.5rem; border-radius: 15px;
        border-top: 4px solid var(--accent); text-align: center; height: 100%;
    }

    /* Mejora de la Consola Operativa */
    .console-box {
        background: #1e293b; padding: 2.5rem; border-radius: 20px;
        border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .stTextArea textarea {
        background-color: #0f172a !important; color: #38bdf8 !important;
        border: 1px solid #334155 !important; border-radius: 10px !important;
    }

    /* Botón de Salida en Sidebar */
    .stSidebar [data-testid="stVerticalBlock"] > div:first-child {
        margin-top: -20px;
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

# --- LÓGICA DE ACCESO (PRÓLOGO + LOGIN) ---
if not st.session_state.logged_in:
    # EL PRÓLOGO TAL CUAL ESTABA
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8; font-size: 3rem;'>DataSocio Intelligence OS</h1>
            <p style='color: #cbd5e1; font-size: 1.2rem;'>Extracción masiva de datos y análisis de reputación.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:white;'>⚙️ ¿Cómo funciona el sistema?</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="step-card"><h3>1. Inyección</h3><p>Ingresas las URLs de los negocios.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="step-card"><h3>2. Rastreo</h3><p>Análisis de código HTML buscando contactos.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="step-card"><h3>3. Inteligencia</h3><p>IA clasifica el sentimiento comercial.</p></div>', unsafe_allow_html=True)

    st.write("---")
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        mode = st.radio("Acción:", ["Ingresar", "Registrarse"], horizontal=True)
        u = st.text_input("Usuario").strip()
        p = st.text_input("Contraseña", type="password").strip()
        if mode == "Ingresar" and st.button("🚀 ENTRAR"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("❌ Credenciales incorrectas.")
        if mode == "Registrarse" and st.button("📝 CREAR CUENTA"):
            if u and p and not db.search(User.username == u):
                db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                st.success("✅ ¡Cuenta creada! Ya podés ingresar.")
    st.stop()

# --- INTERFAZ OPERATIVA (SIDEBAR CON SALIDA ARRIBA) ---
user_data = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    # EL BOTÓN DE SALIDA AHORA ESTÁ AQUÍ ARRIBA
    if st.button("⬅️ CERRAR SESIÓN", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_now = None
        st.rerun()
    
    st.markdown(f"## 👤 {st.session_state.user_now}")
    st.metric("CRÉDITOS", user_data['credits'])
    st.write("---")
    st.markdown("### 💎 Plan Suscriptor")
    st.markdown('<a href="#" class="pay-link">💳 OBTENER MÁS</a>', unsafe_allow_html=True)

# --- CUERPO PRINCIPAL MEJORADO ---
st.markdown("<h1 style='color: #38bdf8;'>🛠️ Consola Operativa</h1>", unsafe_allow_html=True)

st.markdown('<div class="console-box">', unsafe_allow_html=True)
urls_input = st.text_area("📋 Lista de URLs (una por línea):", height=150, placeholder="https://ejemplo.com.ar")
if st.button("⚡ EJECUTAR INTELIGENCIA", use_container_width=True):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    if urls and user_data['credits'] >= len(urls):
        results = []
        bar = st.progress(0)
        for i, url in enumerate(urls):
            try:
                db.update({'credits': user_data['credits'] - (i+1)}, User.username == st.session_state.user_now)
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=7)
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                tels = list(set(re.findall(r'\+?\d{10,13}', text)))
                results.append({"url": url, "emails": emails, "tels": tels})
            except:
                results.append({"url": url, "emails": [], "tels": []})
            bar.progress((i+1)/len(urls))
        st.session_state.last_run = results
        st.rerun()
    elif not urls: st.warning("⚠️ URLs inválidas.")
    else: st.error("❌ Créditos insuficientes.")
st.markdown('</div>', unsafe_allow_html=True)

# Resultados en tarjetas nítidas
if 'last_run' in st.session_state:
    st.write("### 💎 Resultados")
    for r in st.session_state.last_run:
        with st.container():
            st.markdown(f"""
                <div style='background:#1e293b; padding:20px; border-radius:12px; border-left:6px solid #38bdf8; margin-bottom:15px;'>
                    <h4 style='margin:0; color:#38bdf8;'>🔗 {r['url']}</h4>
                    <p style='margin:10px 0 0 0; color:#cbd5e1;'>
                        <b>Emails:</b> {', '.join(r['emails']) if r['emails'] else 'No detectados'}<br>
                        <b>Teléfonos:</b> {', '.join(r['tels']) if r['tels'] else 'No detectados'}
                    </p>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
st.caption("DataSocio Engine v9.5 | Win11 i5 | Paso del Rey")
