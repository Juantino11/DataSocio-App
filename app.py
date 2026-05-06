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
st.set_page_config(page_title="DataSocio OS | Acceso", page_icon="📈", layout="wide")

# CSS para el nuevo orden
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    .hero-container {
        text-align: center;
        padding: 1.5rem 1rem;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    .auth-card {
        background: #1e293b;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #38bdf8;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        margin-bottom: 3rem;
    }

    .feature-box {
        background: #1e293b;
        padding: 1.2rem;
        border-radius: 12px;
        border-top: 3px solid #38bdf8;
        text-align: center;
        height: 100%;
        font-size: 0.9rem;
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

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_now = None

# --- PANTALLA DE INICIO (ORDEN INVERTIDO) ---
if not st.session_state.logged_in:
    # 1. TÍTULO
    st.markdown("""
        <div class="hero-container">
            <h1 style='color: #38bdf8; font-size: 3rem; margin-bottom: 1rem;'>DataSocio Intelligence OS</h1>
        </div>
    """, unsafe_allow_html=True)

    # 2. LOGIN AL CENTRO (PRIMERO)
    _, col_auth, _ = st.columns([1, 1.5, 1])
    with col_auth:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("🔐 Acceso al Sistema")
        mode = st.radio("Acción:", ["Ingresar", "Registrarse"], horizontal=True)
        
        u = st.text_input("Usuario", placeholder="Tu usuario")
        p = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        if mode == "Ingresar":
            if st.button("🚀 ENTRAR AHORA"):
                res = db.search(User.username == u)
                if res and res[0]['password'] == hash_p(p):
                    st.session_state.logged_in = True
                    st.session_state.user_now = u
                    st.rerun()
                else: st.error("Credenciales incorrectas.")
        else:
            if st.button("🎁 CREAR CUENTA"):
                if not db.search(User.username == u):
                    db.insert({'username': u, 'password': hash_p(p), 'credits': 10})
                    st.success("¡Cuenta lista! Ingresa ahora.")
                else: st.error("El usuario ya existe.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. PRÓLOGO/BENEFICIOS (ABAJO)
    st.write("---")
    st.markdown("<p style='text-align: center; color: #94a3b8;'>¿Qué podés hacer con nuestra Suite?</p>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="feature-box"><h3>🔍 Extracción</h3><p>Obtené Emails y WhatsApp de cualquier sitio web en segundos.</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="feature-box"><h3>🧠 Análisis</h3><p>IA que detecta automáticamente la reputación del objetivo.</p></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="feature-box"><h3>📊 Reportes</h3><p>Exportá tus resultados a un Excel profesional listo para usar.</p></div>', unsafe_allow_html=True)
    st.stop()

# --- PANEL OPERATIVO (UNA VEZ LOGUEADO) ---
user_rec = db.search(User.username == st.session_state.user_now)[0]

with st.sidebar:
    st.title(f"👤 {st.session_state.user_now}")
    st.metric("CRÉDITOS", user_rec['credits'])
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

st.title("🚀 Consola Operativa")
urls_input = st.text_area("📋 URLs a investigar:", height=150)

if st.button("⚡ EJECUTAR INTELIGENCIA"):
    urls = [u.strip() for u in urls_input.split('\n') if u.strip().startswith('http')]
    
    if not urls:
        st.warning("Ingrese URLs.")
    elif len(urls) > user_rec['credits']:
        st.error("Créditos insuficientes.")
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
                    "Sentimiento": "Positivo" if "excelente" in text.lower() else "Neutral"
                })
                bar.progress((i+1)/len(urls))
            except:
                results.append({"URL": url, "Emails": "Fallo", "Teléfonos": "-", "Sentimiento": "-"})

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads')
            
            st.download_button(
                label="📥 DESCARGAR EXCEL (.xlsx)",
                data=output.getvalue(),
                file_name=f"DataSocio_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.rerun()

st.write("---")
st.caption("DataSocio Engine v8.2 | Fast Access | i5 Win11")
