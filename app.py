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
st.set_page_config(page_title="DataSocio OS | Intelligence", page_icon="📈", layout="wide")

# CSS para reordenar y embellecer
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Header & Prólogo */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 1px solid #334155;
        margin-bottom: 2rem;
    }
    
    /* Tarjetas de Beneficios */
    .feature-box {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border-top: 4px solid #38bdf8;
        text-align: center;
        height: 100%;
    }

    /* Caja de Login Central */
    .auth-card {
        background: #1e293b;
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #38bdf8;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        margin-top: 2rem;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #1d4ed8);
        color: white; border: none; font-weight: bold; border-radius: 8px;
        height: 3em;
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

# --- PANTALLA DE INICIO REESTRUCTURADA ---
if not st.session_state.logged_in:
    # 1. HEADER Y PRÓLOGO (ARRIBA DE TODO)
    st.markdown("""
        <div class="hero-container">
            <h1 style='color: #38bdf8; font-size: 3.5rem; margin-bottom: 0;'>DataSocio Intelligence OS</h1>
            <p style='font-size: 1.3rem; color: #94a3b8;'>La navaja suiza para la extracción de leads y análisis de mercado.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. BENEFICIOS (EN EL MEDIO)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="feature-box"><h3>🔍 Extracción</h3><p>Rastreo automático de Emails y WhatsApp en segundos.</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="feature-box"><h3>🧠 Análisis</h3><p>Detección de reputación y sentimiento del objetivo.</p></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="feature-box"><h3>📊 Reportes</h3><p>Exportación directa a Excel profesional (XLSX).</p></div>', unsafe_allow_html=True)

    st.write("") # Espaciador
    st.write("")

    # 3. LOGIN CENTRALIZADO
    _, col_auth, _ = st.columns([1, 1.5, 1])
    with col_auth:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("🔐 Acceso Protegido")
        mode = st.radio("Acción:", ["Ingresar", "Registrarse"], horizontal=True)
        
        u = st.text_input("Usuario", placeholder="Tu nombre de usuario")
        p = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        if mode == "Ingresar":
            if st.button("🚀 ENTRAR AL DASHBOARD"):
                res = db.search(User.username == u)
                if res and res[0]['password'] == hash_p(p):
                    st.session_state.logged_in = True
                    st.session_state.user_now = u
                    st.rerun()
                else: st.error("Error: Credenciales incorrectas.")
        else:
            if st.button("🎁 CREAR MI CUENTA"):
                if not db.search(User.username == u):
                    db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                    st.success("¡Cuenta creada! Ya puedes ingresar.")
                else: st.error("El usuario ya existe.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD OPERATIVO (LOGUEADO) ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.title(f"👤 {st.session_state.user_now}")
    st.metric("CRÉDITOS DISPONIBLES", user_rec['credits'])
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

st.title("🚀 Consola de Operaciones")
urls_input = st.text_area("📋 Lista de URLs (una por línea):", height=150)

if st.button("⚡ EJECUTAR EXTRACCIÓN"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    
    if not urls:
        st.warning("Ingrese URLs.")
    elif len(urls) > user_rec['credits']:
        st.error("No tienes créditos suficientes.")
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
                    "URL": url,
                    "Emails": ", ".join(emails),
                    "Teléfonos": ", ".join(tels),
                    "Análisis": "Positivo" if "excelente" in text.lower() else "Neutral"
                })
                bar.progress((i+1)/len(urls))
            except:
                results.append({"URL": url, "Emails": "Fallo", "Teléfonos": "-", "Análisis": "-"})

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads')
            
            st.download_button(
                label="📥 DESCARGAR REPORTE EXCEL (.xlsx)",
                data=output.getvalue(),
                file_name=f"Reporte_{st.session_state.user_now}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.rerun()

st.write("---")
st.caption("DataSocio Engine v8.1 | Pro Business Suite | i5 Win11")
