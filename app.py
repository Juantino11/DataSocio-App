import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import hashlib
from io import BytesIO
from tinydb import TinyDB, Query

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DataSocio OS | Business Intelligence", page_icon="📈", layout="wide")

# CSS Mejorado para el Prólogo y la Suite
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 3rem; border-radius: 20px; border: 1px solid #38bdf8;
        margin-bottom: 2rem; text-align: center;
    }
    .feature-card {
        background: #1e293b; padding: 1.5rem; border-radius: 12px;
        border-left: 5px solid #38bdf8; margin: 10px 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #1d4ed8);
        color: white; border: none; font-weight: bold; border-radius: 8px;
    }
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

# --- PANTALLA DE INICIO (PRÓLOGO + AUTH) ---
if not st.session_state.logged_in:
    # 1. PRÓLOGO
    st.markdown("""
        <div class="hero-section">
            <h1 style='color: #38bdf8; font-size: 3rem;'>DataSocio Intelligence OS</h1>
            <p style='font-size: 1.2rem; color: #94a3b8;'>Transformá la web en tu base de datos personal. Inteligencia comercial al alcance de un clic.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="feature-card"><h3>🔍 Extracción</h3><p>Rastreo masivo de emails, teléfonos y contactos de cualquier URL.</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="feature-card"><h3>🧠 Análisis</h3><p>IA básica que detecta el sentimiento y reputación de cada sitio web.</p></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="feature-card"><h3>📊 Reportes</h3><p>Descargá tus leads en Excel profesional listos para tu equipo de ventas.</p></div>', unsafe_allow_html=True)

    st.write("---")

    # 2. LOGIN/REGISTRO
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        mode = st.radio("Acceso al Sistema", ["Ingresar", "Registrarse"], horizontal=True)
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        
        if mode == "Ingresar" and st.button("🚀 Acceder Ahora"):
            res = db.search(User.username == u)
            if res and res[0]['password'] == hash_p(p):
                st.session_state.logged_in = True
                st.session_state.user_now = u
                st.rerun()
            else: st.error("Credenciales inválidas.")
        
        if mode == "Registrarse" and st.button("🎁 Crear Cuenta (10 Créditos Gratis)"):
            if not db.search(User.username == u):
                db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                st.success("¡Cuenta creada! Ya podés ingresar.")
            else: st.error("El usuario ya existe.")
    st.stop()

# --- PANEL OPERATIVO (LOGUEADO) ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.title(f"👤 {st.session_state.user_now}")
    st.metric("CRÉDITOS DISPONIBLES", user_rec['credits'])
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.info("Socio, cada escaneo consume 1 crédito de tu balance.")

st.title("🚀 Intelligence Dashboard")

urls_input = st.text_area("📋 Lista de objetivos (URLs):", height=120)

if st.button("⚡ INICIAR EXTRACCIÓN MAESTRA"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    
    if not urls:
        st.warning("Ingrese URLs válidas.")
    elif len(urls) > user_rec['credits']:
        st.error("No tenés créditos suficientes.")
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
                
                results.append({
                    "URL Objetivo": url,
                    "Emails Encontrados": ", ".join(emails),
                    "Teléfonos/WhatsApp": ", ".join(tels),
                    "Análisis Sentimiento": "Positivo" if "excelente" in text.lower() else "Neutral"
                })
                bar.progress((i+1)/len(urls))
            except:
                results.append({"URL Objetivo": url, "Emails Encontrados": "Error de conexión", "Teléfonos/WhatsApp": "-", "Análisis Sentimiento": "-"})

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # --- MOTOR DE EXPORTACIÓN EXCEL PROFESIONAL ---
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads Extraídos')
            
            excel_data = output.getvalue()
            st.download_button(
                label="📥 DESCARGAR REPORTE EXCEL (.xlsx)",
                data=excel_data,
                file_name=f"Reporte_DataSocio_{int(time.time())}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.rerun()

st.write("---")
st.caption(f"DataSocio Engine v8.0 | Argentina | i5 Windows 11")
